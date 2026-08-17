"""Stage 01 — Sample.

Reads the video file and config · Writes ``frames/raw/`` and frame records.

Fixed-rate sampling, not scene detection: handheld footage has constant
micro-motion, so hard cuts barely register and a scene detector either fires
constantly or not at all (DEC-003).

Two properties matter more than they look:

**The frame id is the position on the sampling grid**, not a counter over the
files that survived. A frame skipped by ``sample.skip_ranges`` leaves a gap in
the ids, so editing ``skip_ranges`` never renumbers the frames after it and a
note saying "see f_000842" keeps resolving (DEC-013).

**The timestamp is in the filename.** It is derived from the grid position, so
re-extracting a screen at full resolution never depends on a side index that can
drift out of date (DEC-004).
"""

from __future__ import annotations

from pathlib import Path

from reframe import video as videotool
from reframe.manifest import FrameRecord
from reframe.paths import frame_filename, frame_id_from_index
from reframe.stages.base import StageContext, StageError
from reframe.timecode import format_timecode


def run(ctx: StageContext) -> None:
    manifest = ctx.manifest
    manifest.requires("01", "00")
    sample = ctx.pipeline.sample

    source = _verify_source(ctx)
    raw_dir = ctx.frames_dir("raw", create=True)

    # Re-sampling voids every record derived from the old frames.
    manifest.invalidate_from("01")
    manifest.frames = []
    manifest.screens = []
    _clear_frames(raw_dir)

    ctx.say(f"  sampling at {sample.fps:g} fps → {raw_dir.relative_to(ctx.out_dir)}")
    extracted = videotool.sample_frames(
        source,
        raw_dir,
        fps=sample.fps,
        quality=sample.quality,
        max_frames=sample.max_frames,
    )
    if not extracted:
        raise StageError(
            f"ffmpeg extracted no frames from {source.name} — "
            "check the file plays, and that sample.fps is not larger than the source rate"
        )

    skip_ranges = sample.skip_ranges_ms()
    records: list[FrameRecord] = []
    skipped = 0

    for index, temp_path in enumerate(extracted):
        # Grid position → timestamp. Integer milliseconds so the value is
        # identical on every re-run.
        t_ms = round(index * 1000 / sample.fps)
        if _in_any_range(t_ms, skip_ranges):
            temp_path.unlink()
            skipped += 1
            continue
        frame_id = frame_id_from_index(index)
        final_path = temp_path.with_name(frame_filename(frame_id, t_ms))
        temp_path.replace(final_path)
        records.append(
            FrameRecord(id=frame_id, t_ms=t_ms, path=ctx.relative(final_path))
        )

    manifest.frames = records
    _check_orientation(ctx, records)
    _check_cap(ctx, len(extracted))

    span = format_timecode(records[-1].t_ms) if records else "0:00"
    ctx.say(
        f"  {len(records)} frames"
        + (f", {skipped} skipped by skip_ranges" if skipped else "")
        + f", last at {span}"
    )


def _verify_source(ctx: StageContext) -> Path:
    """Confirm the registered video is still the same file.

    A different file under the same slug invalidates every frame id and every
    timestamp anyone has written down, so it is a hard error rather than a
    silent reprocess (DEC-013).
    """
    info = ctx.manifest.video
    source = Path(info.source_path)
    if not source.exists():
        raise StageError(
            f"source video is missing: {source}\n"
            f"  it is not committed by design — restore it, or re-register with "
            f"`reframe init <video> --slug {info.slug} --force`"
        )
    digest = videotool.sha256_file(source)
    if digest != info.sha256:
        raise StageError(
            f"{source} is not the file registered as {info.slug!r}\n"
            f"  registered sha256 {info.sha256[:12]}…, found {digest[:12]}…\n"
            f"  re-register with `reframe init <video> --slug {info.slug} --force` "
            "if the change is intended — every existing frame id and timestamp refers "
            "to the old file"
        )
    return source


def _clear_frames(raw_dir: Path) -> None:
    """Idempotency: a re-run replaces its output rather than adding to it."""
    for stale in raw_dir.glob("*.jpg"):
        stale.unlink()


def _in_any_range(t_ms: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= t_ms < end for start, end in ranges)


def _check_orientation(ctx: StageContext, records: list[FrameRecord]) -> None:
    """Cross-check the sampled frames against the probed display orientation.

    Rotation is applied by ffmpeg's autorotate, not re-applied here, because two
    rotations cancel into a sideways screen that corner detection would happily
    accept. That makes this check the only thing standing between a mis-rotated
    source and a whole video of confidently-wrong output — so a mismatch is
    escalated, not assumed away.
    """
    if not records:
        return
    info = ctx.manifest.video
    expected = (info.height, info.width) if abs(info.rotation) % 180 == 90 else (
        info.width,
        info.height,
    )
    actual = videotool.frame_size(ctx.absolute(records[0].path))
    if actual == expected:
        return

    swapped = actual == (expected[1], expected[0])
    detail = (
        "frames came out sideways — the rotation flag was applied twice or not at all"
        if swapped
        else "frames do not match the probed size; the source may be variable-resolution"
    )
    ctx.manifest.warn(
        "01",
        f"sampled frames are {actual[0]}×{actual[1]}, expected "
        f"{expected[0]}×{expected[1]} — {detail}",
    )
    ctx.manifest.escalate(
        "01",
        t_ms_start=records[0].t_ms,
        t_ms_end=records[-1].t_ms,
        reason="orientation-mismatch",
        detail=detail,
    )
    ctx.say(f"  [yellow]![/yellow] {detail}")


def _check_cap(ctx: StageContext, produced: int) -> None:
    """A cap that was hit is a warning in the manifest, never a silent truncation."""
    sample = ctx.pipeline.sample
    if produced < sample.max_frames:
        return
    expected = ctx.manifest.video.expected_samples_at(sample.fps)
    if expected <= sample.max_frames:
        return
    missing_from_ms = round(produced * 1000 / sample.fps)
    ctx.manifest.warn(
        "01",
        f"sample.max_frames cap of {sample.max_frames} hit — this video needs "
        f"{expected} frames at {sample.fps:g} fps, so everything after "
        f"{format_timecode(missing_from_ms)} was never sampled",
        t_ms_start=missing_from_ms,
        t_ms_end=round(ctx.manifest.video.duration_s * 1000),
    )
    ctx.manifest.escalate(
        "01",
        t_ms_start=missing_from_ms,
        t_ms_end=round(ctx.manifest.video.duration_s * 1000),
        reason="not-sampled",
        detail=f"sample.max_frames cap of {sample.max_frames} stopped sampling here",
    )
    ctx.say(
        f"  [yellow]![/yellow] max_frames cap hit — footage after "
        f"{format_timecode(missing_from_ms)} was not sampled"
    )
