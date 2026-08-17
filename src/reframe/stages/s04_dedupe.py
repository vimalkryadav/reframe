"""Stage 04 — Dedupe.

Reads ``frames/clean/`` and config · Writes ``frames/kept/``, dedupe records and
the initial screen records.

Reduces ~900 frames to a few dozen distinct screens. Two rules carry the stage:

**Compare the title band, not the whole frame.** That band is what identifies a
screen. The inherited whole-frame percentage-difference method inverts on handheld
footage — shake alone exceeds the threshold, so nothing looks like a duplicate and
every frame survives as a "distinct screen" (DEC-007).

**Compare against the last kept frame, not the previous frame.** Comparing
against the previous frame collapses a slow scroll to nothing, because each
individual step falls below threshold. This mistake is already on record in the
consuming project's loop; it is not worth re-learning.
"""

from __future__ import annotations

import shutil

from rich.progress import track

from reframe.manifest import DedupeRecord, ScreenRecord
from reframe.paths import sibling_frame
from reframe.stages.base import StageContext, StageError
from reframe.timecode import format_timecode
from reframe.vision import read_image
from reframe.vision.hashing import combined_distance, hamming_distance, perceptual_hash
from reframe.vision.warp import crop


def run(ctx: StageContext) -> None:
    manifest = ctx.manifest
    manifest.requires("04", "03")
    dedupe = ctx.pipeline.dedupe
    band_rect = (
        dedupe.band_rect[0],
        dedupe.band_rect[1],
        dedupe.band_rect[2],
        dedupe.band_rect[3],
    )

    manifest.invalidate_from("04")
    manifest.screens = []
    kept_dir = ctx.frames_dir("kept", create=True)
    for stale in kept_dir.glob("*.jpg"):
        stale.unlink()

    kept_indices: list[int] = []
    gap_suppressed: list[int] = []
    last_band_hash: str | None = None
    last_full_hash: str | None = None
    last_kept_index: int | None = None

    for index, frame in enumerate(
        track(manifest.frames, description="  hashing bands ", console=ctx.console)
    ):
        clean_path = sibling_frame(ctx.absolute(frame.path), "clean")
        if not clean_path.exists():
            # Not rectified, so not comparable. Already escalated by stage 02;
            # recording no dedupe verdict is the honest state.
            frame.dedupe = None
            continue

        image = read_image(clean_path)
        band = crop(image, band_rect)
        if band.size == 0:
            raise StageError(
                f"dedupe.band_rect {list(band_rect)} falls outside the "
                f"{image.shape[1]}×{image.shape[0]} canonical frame — band_rect is in "
                "canonical coordinates, so it must be re-measured whenever "
                "rectify.canonical_size changes"
            )

        band_hash = perceptual_hash(band)
        full_hash = perceptual_hash(image)

        if last_band_hash is None or last_full_hash is None or last_kept_index is None:
            frame.dedupe = DedupeRecord(
                band_hash=band_hash, distance_from_last_kept=None, kept=True
            )
            kept_indices.append(index)
            last_band_hash, last_full_hash, last_kept_index = band_hash, full_hash, index
            _copy_kept(ctx, index)
            continue

        score = combined_distance(
            band=hamming_distance(band_hash, last_band_hash),
            full_frame=hamming_distance(full_hash, last_full_hash),
            full_frame_weight=dedupe.full_frame_weight,
        )
        distinct = score > dedupe.hash_distance
        wide_enough = (index - last_kept_index) >= dedupe.min_gap_frames
        keep = distinct and wide_enough
        if distinct and not wide_enough:
            gap_suppressed.append(index)

        frame.dedupe = DedupeRecord(
            band_hash=band_hash, distance_from_last_kept=score, kept=keep
        )
        if keep:
            kept_indices.append(index)
            last_band_hash, last_full_hash, last_kept_index = band_hash, full_hash, index
            _copy_kept(ctx, index)

    if not kept_indices:
        raise StageError(
            "no frames were kept — stage 03 produced no cleanable frames, or every "
            "frame hashed identically. Check frames/clean/ before tuning thresholds"
        )

    _build_screens(ctx, kept_indices)
    _report_gap_suppression(ctx, gap_suppressed)

    comparable = sum(1 for f in manifest.frames if f.dedupe is not None)
    ctx.say(
        f"  {len(manifest.screens)} screens from {comparable} comparable frames "
        f"(hash_distance {dedupe.hash_distance}, full_frame_weight "
        f"{dedupe.full_frame_weight:g})"
    )


def _copy_kept(ctx: StageContext, index: int) -> None:
    """Copy the cleaned frame into ``frames/kept/``.

    The cleaned copy rather than the rectified one: this is the only committed
    frame set, and it should be the pixels OCR and the model actually read, so a
    reviewer disputing an identification is looking at the same evidence.
    """
    raw_path = ctx.absolute(ctx.manifest.frames[index].path)
    shutil.copy2(sibling_frame(raw_path, "clean"), sibling_frame(raw_path, "kept"))


def _build_screens(ctx: StageContext, kept_indices: list[int]) -> None:
    """One screen per kept frame, spanning until the next keep.

    Every comparable frame folded into a screen is listed, because cross-frame
    agreement is a confidence signal in stage 06 and it can only be computed from
    membership that survived into the manifest.
    """
    frames = ctx.manifest.frames
    screens: list[ScreenRecord] = []

    for position, start in enumerate(kept_indices):
        end = kept_indices[position + 1] if position + 1 < len(kept_indices) else len(frames)
        members = [f for f in frames[start:end] if f.dedupe is not None]
        if not members:  # pragma: no cover - the kept frame itself is always a member
            continue
        screens.append(
            ScreenRecord(
                id=f"s_{position:03d}",
                representative_frame=frames[start].id,
                frame_ids=[f.id for f in members],
                t_ms_start=members[0].t_ms,
                t_ms_end=members[-1].t_ms,
            )
        )
    ctx.manifest.screens = screens


def _report_gap_suppression(ctx: StageContext, suppressed: list[int]) -> None:
    """Escalate frames that looked distinct but were held back by min_gap_frames.

    The cap exists to suppress flicker during a transition, and most of what it
    catches is exactly that. But a screen visible for a single frame would be
    dropped by the same rule, and losing a screen without saying so is the failure
    this tool exists to prevent — so every suppressed frame is named.
    """
    if not suppressed:
        return
    frames = ctx.manifest.frames
    gap = ctx.pipeline.dedupe.min_gap_frames
    ctx.manifest.warn(
        "04",
        f"{len(suppressed)} frame(s) differed enough to keep but fell within "
        f"dedupe.min_gap_frames ({gap}) of the previous keep — lower it if a "
        "short-lived screen is missing from the catalogue",
    )
    for index in suppressed:
        ctx.manifest.escalate(
            "04",
            t_ms_start=frames[index].t_ms,
            t_ms_end=frames[index].t_ms,
            reason="gap-suppressed",
            detail=(
                "this frame differed enough from the last kept screen to be one of its "
                f"own, but dedupe.min_gap_frames ({gap}) held it back"
            ),
            frame_ids=[frames[index].id],
        )
    first = frames[suppressed[0]].t_ms
    ctx.say(
        f"  [yellow]![/yellow] {len(suppressed)} frame(s) suppressed by min_gap_frames, "
        f"first at {format_timecode(first)}"
    )
