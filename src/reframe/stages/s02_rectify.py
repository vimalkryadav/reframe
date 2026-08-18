"""Stage 02 — Rectify.

Reads ``frames/raw/`` and config · Writes ``frames/rect/`` and rectify records.

**This is the highest-risk stage.** Every later stage assumes rectified input, and
rectification is also the larger half of the dedupe fix — hand shake displaces the
whole frame by more than any sane difference threshold until the screen is warped
back to a fixed rectangle (DEC-005, DEC-007).

Detection degrades in steps and never fakes success (DEC-006):

    confident detection      auto           use it
    weak or noisy            interpolated   infer from neighbouring frames
    fails across a span      manual         use corners from config for that span
    screen out of frame      failed         write no frame, escalate the span

The last row is the one that matters. A cut-off screen warped to a full rectangle
looks perfect and is missing a column — so a frame that cannot be rectified
honestly does not get written at all, and its span goes to ``NEEDS_REVIEW.md``.
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
from rich.progress import track

from reframe.config import ManualCorners
from reframe.manifest import Framing, RectifyMethod, RectifyRecord
from reframe.paths import sibling_frame
from reframe.stages.base import StageContext, StageError
from reframe.timecode import format_timecode
from reframe.vision import read_image, write_image
from reframe.vision.quad import (
    Quad,
    detect_screen_quad,
    has_settled,
    interpolate_gaps,
    is_plausible_successor,
    median_smooth,
    order_corners,
)
from reframe.vision.warp import warp_to_canonical


def run(ctx: StageContext) -> None:
    manifest = ctx.manifest
    manifest.requires("02", "01")
    if not manifest.frames:
        raise StageError("no frames to rectify — run stage 01 first")

    rectify = ctx.pipeline.rectify
    canonical = (rectify.canonical_size[0], rectify.canonical_size[1])

    manifest.invalidate_from("02")
    rect_dir = ctx.frames_dir("rect", create=True)
    for stale in rect_dir.glob("*.jpg"):
        stale.unlink()

    detected, pinned, rejected_jumps, reanchors = _detect_all(ctx)
    smoothed = median_smooth(detected, rectify.smooth_window, pinned=pinned)
    # A gap is only bridged across the smoothing window. Beyond that, inferring a
    # screen position for footage nobody looked at is a fabrication.
    filled, interpolated = interpolate_gaps(smoothed, max_span=rectify.smooth_window)

    methods = _write_rectified(ctx, filled, pinned, interpolated, canonical)

    if rejected_jumps:
        manifest.warn(
            "02",
            f"{rejected_jumps} detection(s) were discarded for jumping too far from the "
            "previous frame — a screen cannot move that fast, so something else was found",
        )
    # Never silent: a re-anchor means the detector decided the camera was
    # re-aimed. If it decided wrong, every frame after it is a confident crop of
    # something that is not the screen — the one outcome worse than dropping
    # them. So each one is escalated with its own timestamp, not merely counted.
    for start, end in reanchors:
        frames = manifest.frames[start : end + 1]
        manifest.escalate(
            "02",
            t_ms_start=frames[0].t_ms,
            t_ms_end=frames[-1].t_ms,
            reason="reanchor",
            detail=(
                "detection re-acquired the screen at a new position here, after "
                f"{rectify.reanchor_after_frames} consecutive frames agreed on it. "
                "Confirm this is the camera being moved and not a bright object — "
                "if it is wrong, every frame after this point is a confident crop "
                "of the wrong thing"
            ),
            frame_ids=[f.id for f in frames],
        )
    _escalate_framing(ctx)
    _report(ctx, methods)


def _detect_all(
    ctx: StageContext,
) -> tuple[list[Quad | None], list[bool], int, list[tuple[int, int]]]:
    """Detect or read corners for every frame. Weak detections become gaps.

    A weak detection is dropped to ``None`` rather than used, so that the
    interpolation pass gets a chance to infer better corners from neighbours. The
    measured confidence is only kept when the corners themselves are kept.
    """
    rectify = ctx.pipeline.rectify
    aspect_bounds = (rectify.aspect_bounds[0], rectify.aspect_bounds[1])

    detected: list[Quad | None] = []
    pinned: list[bool] = []
    rejected_jumps = 0
    # Frame-index spans where the detector re-acquired, so each one can be
    # escalated with a timestamp. "Check the re-anchors" is not actionable
    # without saying which moments to check.
    reanchors: list[tuple[int, int]] = []
    last_accepted: Quad | None = None
    # Over-budget detections held back pending a verdict. If they turn out to
    # agree on a new position the camera was re-aimed and they are kept; if the
    # run breaks they were never a screen and they stay dropped.
    pending: list[tuple[int, Quad]] = []

    def _discard_pending() -> None:
        nonlocal rejected_jumps
        rejected_jumps += len(pending)
        pending.clear()

    for frame in track(
        ctx.manifest.frames, description="  detecting screen", console=ctx.console
    ):
        manual = _manual_for(rectify.manual_corners, frame.t_ms)
        if manual is not None:
            quad = _quad_from_manual(manual)
            _discard_pending()
            detected.append(quad)
            pinned.append(True)
            last_accepted = quad
            continue
        pinned.append(False)

        image = read_image(ctx.absolute(frame.path))
        candidate = detect_screen_quad(image, aspect_bounds=aspect_bounds)
        if candidate is None or candidate.confidence < rectify.min_quad_confidence:
            _discard_pending()
            detected.append(None)
            continue

        diagonal = float(np.hypot(image.shape[1], image.shape[0]))
        if last_accepted is not None and not is_plausible_successor(
            last_accepted,
            candidate,
            frame_diagonal=diagonal,
            max_jump_fraction=rectify.max_jump_fraction,
        ):
            pending.append((len(detected), candidate))
            detected.append(None)
            run = [quad for _, quad in pending]
            if len(run) >= rectify.reanchor_after_frames and has_settled(
                run,
                frame_diagonal=diagonal,
                max_jump_fraction=rectify.max_jump_fraction,
            ):
                # The camera was re-aimed and held. Keep the frames that proved
                # it — dropping them would blank the moment of the reposition.
                for index, quad in pending:
                    detected[index] = quad
                last_accepted = run[-1]
                reanchors.append((pending[0][0], pending[-1][0]))
                pending.clear()
            continue

        _discard_pending()
        detected.append(candidate)
        last_accepted = candidate

    _discard_pending()
    return detected, pinned, rejected_jumps, reanchors


def _manual_for(spans: list[ManualCorners], t_ms: int) -> ManualCorners | None:
    for span in spans:
        start, end = span.span_ms()
        if start <= t_ms <= end:
            return span
    return None


def _quad_from_manual(span: ManualCorners) -> Quad:
    """A human's four clicks. Re-ordered but never re-measured.

    Confidence is 1.0 because a person looked at the frame — which is a better
    measurement than anything in this file, and the reason ``manual`` exists.
    """
    points = np.array(span.corners, dtype=np.float32)
    return Quad(corners=order_corners(points), confidence=1.0)


def _write_rectified(
    ctx: StageContext,
    quads: list[Quad | None],
    pinned: list[bool],
    interpolated: list[bool],
    canonical: tuple[int, int],
) -> dict[RectifyMethod, int]:
    counts: dict[RectifyMethod, int] = {"auto": 0, "interpolated": 0, "manual": 0, "failed": 0}

    for index, frame in enumerate(
        track(ctx.manifest.frames, description="  rectifying    ", console=ctx.console)
    ):
        quad = quads[index]
        if quad is None:
            # No corners we believe. Write nothing: a rectified file here would be
            # indistinguishable from a good one to every stage that follows.
            frame.rectify = RectifyRecord(
                method="failed", corners=None, quad_confidence=0.0, framing="lost"
            )
            counts["failed"] += 1
            continue

        method: RectifyMethod = (
            "manual" if pinned[index] else "interpolated" if interpolated[index] else "auto"
        )
        # A quad that reaches the frame edge is a screen running off camera. The
        # warp still happens so a reviewer can see it, but it is recorded as
        # partial and the span is escalated — never presented as a clean crop.
        framing: Framing = "partial" if quad.touches_border else "full"

        image = read_image(ctx.absolute(frame.path))
        warped = warp_to_canonical(image, quad.corners, canonical)
        write_image(sibling_frame(ctx.absolute(frame.path), "rect"), warped)

        frame.rectify = RectifyRecord(
            method=method,
            corners=[(round(x, 2), round(y, 2)) for x, y in quad.corners],
            quad_confidence=quad.confidence,
            framing=framing,
        )
        counts[method] += 1
    return counts


def _escalate_framing(ctx: StageContext) -> None:
    """Send every run of failed or partial frames to NEEDS_REVIEW.md.

    Grouped into spans rather than reported per frame: a reviewer watches
    footage, and forty consecutive lines for one bad stretch of camera handling
    is a list people stop reading.
    """
    manifest = ctx.manifest
    lost = [
        i
        for i, f in enumerate(manifest.frames)
        if f.rectify is not None and f.rectify.framing == "lost"
    ]
    partial = [
        i
        for i, f in enumerate(manifest.frames)
        if f.rectify is not None and f.rectify.framing == "partial"
    ]

    for indices, reason, detail in (
        (
            lost,
            "screen-not-found",
            "no screen could be located — nothing was rectified for this span, so "
            "any screen shown here is absent from the catalogue",
        ),
        (
            partial,
            "screen-partial",
            "the screen runs off the edge of frame — the rectified image is missing "
            "content and must not be trusted as a full screen",
        ),
    ):
        for start, end in _contiguous(indices):
            frames = manifest.frames[start : end + 1]
            manifest.escalate(
                "02",
                t_ms_start=frames[0].t_ms,
                t_ms_end=frames[-1].t_ms,
                reason=reason,
                detail=detail,
                frame_ids=[f.id for f in frames],
            )


def _contiguous(indices: list[int]) -> Iterator[tuple[int, int]]:
    """Group sorted indices into (first, last) runs."""
    if not indices:
        return
    start = previous = indices[0]
    for index in indices[1:]:
        if index == previous + 1:
            previous = index
            continue
        yield start, previous
        start = previous = index
    yield start, previous


def _report(ctx: StageContext, counts: dict[RectifyMethod, int]) -> None:
    total = sum(counts.values())
    summary = " · ".join(f"{count} {method}" for method, count in counts.items() if count)
    ctx.say(f"  {total} frames: {summary}")

    failed = counts["failed"]
    if failed:
        share = failed / total if total else 0.0
        ctx.manifest.warn(
            "02",
            f"{failed} of {total} frames ({share:.0%}) could not be rectified — "
            "supply rectify.manual_corners for those spans, or lower "
            "rectify.min_quad_confidence if detection is merely timid",
        )
    spans = [s for s in ctx.manifest.review_spans if s.reason.startswith("02:")]
    for span in spans[:5]:
        ctx.say(
            f"    [yellow]![/yellow] {format_timecode(span.t_ms_start)}–"
            f"{format_timecode(span.t_ms_end)}  {span.reason.removeprefix('02:')}"
        )
    if len(spans) > 5:
        ctx.say(f"    … and {len(spans) - 5} more span(s) — see NEEDS_REVIEW.md")
