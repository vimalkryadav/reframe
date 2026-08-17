"""Stage 03 — Clean.

Reads ``frames/rect/`` · Writes ``frames/clean/``.

Applied to a copy. ``frames/rect/`` stays untouched because every step here trades
away some of the fine detail that makes a small label readable, and the right
combination differs per video — which is why each step is separately switchable in
config and discovered during validation rather than assumed here.

Frames that stage 02 declined to rectify have no input to clean. They are left
alone rather than approximated: their spans are already escalated, and a cleaned
copy of a frame nobody could rectify would look exactly like a good one.
"""

from __future__ import annotations

from rich.progress import track

from reframe.paths import sibling_frame
from reframe.stages.base import StageContext, StageError
from reframe.vision import Image, read_image, write_image
from reframe.vision.enhance import align_to, apply_clahe, reduce_moire, suppress_glare


def run(ctx: StageContext) -> None:
    manifest = ctx.manifest
    manifest.requires("03", "02")
    clean = ctx.pipeline.clean

    manifest.invalidate_from("03")
    clean_dir = ctx.frames_dir("clean", create=True)
    for stale in clean_dir.glob("*.jpg"):
        stale.unlink()

    steps = [
        name
        for name, enabled in (
            ("align", clean.align),
            ("clahe", clean.clahe.enabled),
            ("deglare", clean.deglare.enabled),
            ("moire", clean.moire.enabled),
        )
        if enabled
    ]
    ctx.say(f"  steps: {' → '.join(steps) if steps else 'none (pass-through copy)'}")

    processed = 0
    skipped = 0
    aligned = 0
    # The alignment reference is the previous frame *before* enhancement.
    # Correlating an un-enhanced frame against an enhanced one measures the
    # contrast change as much as the movement.
    previous_base: Image | None = None

    for frame in track(manifest.frames, description="  cleaning      ", console=ctx.console):
        rect_path = sibling_frame(ctx.absolute(frame.path), "rect")
        if not rect_path.exists():
            skipped += 1
            continue

        base = read_image(rect_path)
        if clean.align and previous_base is not None:
            base, shift = align_to(base, previous_base)
            if shift != (0.0, 0.0):
                aligned += 1
        previous_base = base

        image = base
        if clean.clahe.enabled:
            image = apply_clahe(image, clip=clean.clahe.clip, grid=clean.clahe.grid)
        if clean.deglare.enabled:
            image = suppress_glare(image, max_correction=clean.deglare.max_correction)
        if clean.moire.enabled:
            image = reduce_moire(image, sigma=clean.moire.sigma)

        write_image(sibling_frame(ctx.absolute(frame.path), "clean"), image)
        processed += 1

    if processed == 0:
        raise StageError(
            "no rectified frames to clean — stage 02 rectified nothing, so check "
            "rectify.min_quad_confidence and rectify.aspect_bounds before going further"
        )

    ctx.say(
        f"  {processed} cleaned"
        + (f", {aligned} nudged into alignment" if clean.align else "")
        + (f", {skipped} skipped (not rectified)" if skipped else "")
    )
