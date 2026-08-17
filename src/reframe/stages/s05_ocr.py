"""Stage 05 — OCR.

Reads ``frames/kept/`` · Writes OCR records onto each screen.

Chrome regions only — title bar, tab strip, activity name — with raw text and
per-word confidence kept intact.

What this stage does *not* do is decide anything. Its output is a hint for stage 06
and a cross-check for ``confidence.py``. A band that reads as noise produces a
record with no title and a warning, never a best guess: on this footage an OCR
error and a fabrication look identical three files downstream.
"""

from __future__ import annotations

from rich.progress import track

from reframe.config import OcrRegion
from reframe.manifest import OcrRecord, OcrWord
from reframe.paths import sibling_frame
from reframe.stages.base import StageContext, StageError
from reframe.timecode import format_timecode
from reframe.vision import read_image
from reframe.vision.ocr import (
    OcrUnavailableError,
    Word,
    group_by_gaps,
    join_text,
    read_words,
)
from reframe.vision.warp import crop


def run(ctx: StageContext) -> None:
    manifest = ctx.manifest
    manifest.requires("05", "04")
    if not manifest.screens:
        raise StageError("no screens to read — run stage 04 first")

    ocr = ctx.pipeline.ocr
    manifest.invalidate_from("05")

    unreadable: list[str] = []
    missing_frames = 0

    for screen in track(manifest.screens, description="  reading chrome", console=ctx.console):
        frame = manifest.frame(screen.representative_frame)
        kept_path = sibling_frame(ctx.absolute(frame.path), "kept")
        if not kept_path.exists():
            # Stage 04 kept this frame, so the file should be here. Say so rather
            # than leaving an empty OCR record that looks like an unreadable band.
            screen.ocr = None
            missing_frames += 1
            continue

        image = read_image(kept_path)
        try:
            per_region = {
                region: read_words(crop(image, rect), psm=ocr.psm)
                for region, rect in ocr.enabled_rects()
            }
        except OcrUnavailableError as exc:
            raise StageError(str(exc)) from exc

        screen.ocr = _record(per_region, min_confidence=ocr.min_word_confidence)
        if screen.ocr.title_raw is None:
            unreadable.append(screen.id)

    _report(ctx, unreadable, missing_frames)


def _record(
    per_region: dict[OcrRegion, list[Word]], *, min_confidence: float
) -> OcrRecord:
    """Assemble one screen's OCR record.

    Every word is kept, including the ones below ``min_word_confidence``, so that a
    screen sent to review can be explained by what was actually read rather than by
    an absence.
    """
    title_words = per_region.get("title", [])
    tab_words = per_region.get("tabs", [])
    activity_words = per_region.get("activity", [])

    title_raw, title_confidence = join_text(title_words, min_confidence=min_confidence)
    activity_raw, _ = join_text(activity_words, min_confidence=min_confidence)

    return OcrRecord(
        title_raw=title_raw,
        title_confidence=title_confidence,
        tabs_raw=group_by_gaps(tab_words, min_confidence=min_confidence),
        activity_raw=activity_raw,
        words=[
            OcrWord(region=region, text=word.text, confidence=word.confidence)
            for region, words in per_region.items()
            for word in words
        ],
    )


def _report(ctx: StageContext, unreadable: list[str], missing_frames: int) -> None:
    manifest = ctx.manifest
    total = len(manifest.screens)
    read_count = total - len(unreadable) - missing_frames
    ctx.say(f"  {read_count} of {total} screens have a readable title band")

    if missing_frames:
        manifest.warn(
            "05",
            f"{missing_frames} kept frame(s) were missing from frames/kept/ — re-run "
            "stage 04, which owns that directory",
        )

    if not unreadable:
        return
    manifest.warn(
        "05",
        f"{len(unreadable)} screen(s) had no title word above "
        f"ocr.min_word_confidence ({ctx.pipeline.ocr.min_word_confidence:g}) — check "
        "ocr.region_rects against a frame in frames/kept/ before lowering the bar",
    )
    for screen_id in unreadable:
        screen = manifest.screen(screen_id)
        manifest.escalate(
            "05",
            t_ms_start=screen.t_ms_start,
            t_ms_end=screen.t_ms_end,
            reason="title-unreadable",
            detail=(
                "no word in the title band cleared ocr.min_word_confidence, so this "
                "screen has no OCR cross-check and rests on the model alone"
            ),
            frame_ids=[screen.representative_frame],
        )
    first = manifest.screen(unreadable[0])
    ctx.say(
        f"  [yellow]![/yellow] {len(unreadable)} unreadable title band(s), first at "
        f"{format_timecode(first.t_ms_start)}"
    )
