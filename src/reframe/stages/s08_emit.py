"""Stage 08 — Emit.

Reads the manifest · Writes ``manifest.json`` and the three Markdown files.

``manifest.json`` is the join key for everything; the Markdown is rendered from it
and never hand-edited, so a re-run cannot drift from the data.

The stage also refuses to emit silently over an incomplete run. A catalogue whose
screens were never identified, or whose earlier stages ran under a different
configuration, is exactly the confident-looking-but-wrong artifact this tool exists
to prevent — so the gaps are written into the documents themselves rather than left
for the reader to notice.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from reframe import render
from reframe.config import section_hashes
from reframe.manifest import StageId
from reframe.paths import display_path
from reframe.stages.base import StageContext, StageError
from reframe.timecode import format_timecode

# Stages whose absence changes what the documents mean. Stage 07 is not here:
# a catalogue without a build queue is still a useful catalogue, and the queue
# says so itself.
_EXPECTED: tuple[StageId, ...] = ("01", "02", "03", "04", "05", "06")


def run(ctx: StageContext) -> None:
    manifest = ctx.manifest
    manifest.requires("08", "06")
    manifest.invalidate_from("08")

    _note_incomplete(ctx)
    _note_stale(ctx)

    out_dir = ctx.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    written = [
        _write(out_dir / render.CATALOG_NAME, render.render_catalog(manifest)),
        _write(out_dir / render.QUEUE_NAME, render.render_queue(manifest)),
        _write(out_dir / render.REVIEW_NAME, render.render_review(manifest)),
    ]
    for path in written:
        ctx.say(f"  wrote {display_path(path, ctx.paths.repo_root)}")

    _publish(ctx, written)
    _summarise(ctx)


def _write(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def _note_incomplete(ctx: StageContext) -> None:
    """Record any expected stage that never ran, as a warning in the documents."""
    missing = [stage for stage in _EXPECTED if stage not in ctx.manifest.stages_completed]
    if not missing:
        return
    ctx.manifest.warn(
        "08",
        f"stage(s) {', '.join(missing)} have not run, so these documents describe a "
        "partial pipeline — treat every count in them as a floor, not a total",
    )


def _note_stale(ctx: StageContext) -> None:
    """Record any stage whose config has moved since it ran.

    Emitting from a mixed run is legitimate — you might deliberately re-render
    without re-sampling — but the reader has to be told, because nothing in the
    finished Markdown would otherwise reveal that two configurations contributed.
    """
    stale = ctx.manifest.stale_stages(section_hashes(ctx.pipeline))
    if not stale:
        return
    ctx.manifest.warn(
        "08",
        f"stage(s) {', '.join(stale)} last ran under a different configuration than the "
        "one recorded here — re-run them, or read these documents knowing that parts of "
        "them were produced under different settings",
    )
    ctx.say(f"  [yellow]![/yellow] emitting with stale stage(s): {', '.join(stale)}")


def _publish(ctx: StageContext, written: list[Path]) -> None:
    """Copy the Markdown to the project's own docs, if the profile asks for one.

    ``out/<slug>/`` is always written first and stays the source of truth; this is an
    additional destination so a catalogue can live beside the consuming project's
    evidence folders.
    """
    profile = ctx.config.project
    if profile is None or profile.publish_to is None:
        return
    destination = profile.publish_to / ctx.slug
    try:
        destination.mkdir(parents=True, exist_ok=True)
        for path in written:
            shutil.copy2(path, destination / path.name)
    except OSError as exc:
        # Publishing is a convenience. Failing the run after the real outputs are
        # already on disk would be worse than saying so and stopping here.
        ctx.manifest.warn("08", f"could not publish to {destination}: {exc}")
        ctx.say(f"  [yellow]![/yellow] publish to {destination} failed: {exc}")
        return
    ctx.say(f"  published to {destination}")


def _summarise(ctx: StageContext) -> None:
    manifest = ctx.manifest
    buckets: dict[str, int] = {}
    for screen in manifest.screens:
        if screen.classification is not None:
            bucket = screen.classification.bucket
            buckets[bucket] = buckets.get(bucket, 0) + 1
    review = len(manifest.review_spans)

    if buckets:
        ctx.say("  " + " · ".join(f"{count} {name}" for name, count in sorted(buckets.items())))
    if review:
        first = min(span.t_ms_start for span in manifest.review_spans)
        ctx.say(
            f"  {review} item(s) need a human, first at {format_timecode(first)} — "
            f"read {render.REVIEW_NAME} before building from this"
        )
    elif manifest.screens:
        # Silence here is not automatically good news on a first pass.
        ctx.say(
            "  nothing escalated — check the screen count against the footage before "
            "trusting that"
        )
    if not manifest.screens:
        raise StageError("no screens to emit — the pipeline produced an empty catalogue")
