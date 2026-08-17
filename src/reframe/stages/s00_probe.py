"""Stage 00 — Probe.

Reads the video file · Writes ``videos/<slug>/config.yaml``, ``source.txt``,
and the initial ``out/<slug>/manifest.json``.

The generated config is the point of this stage. Every threshold, crop, corner
override and alias in the entire pipeline lives in that file rather than in
Python, so a validation round is a YAML edit (DEC-014).

The generated file deliberately contains almost nothing live. Keys are emitted
commented-out, because a per-video file that pins every value would freeze this
video against ``configs/defaults.yaml`` forever — and defaults improving across
videos is the mechanism by which accuracy compounds. Uncomment a key when *this*
video needs to disagree.
"""

from __future__ import annotations

import math
from pathlib import Path

from rich.console import Console

from reframe import video as videotool
from reframe.config import ConfigError, resolve_config
from reframe.manifest import Manifest, VideoInfo
from reframe.paths import Paths
from reframe.stages.base import StageError
from reframe.timecode import format_timecode

_SLUG_HINT = "slugs name every output path — use letters, digits, dashes and underscores"


def probe(
    paths: Paths,
    source: Path,
    slug: str,
    *,
    force: bool = False,
    console: Console | None = None,
) -> Manifest:
    """Register a video: probe it, hash it, and generate its tuning config."""
    say = (console or Console()).print
    _validate_slug(slug)

    source = source.expanduser().resolve()
    metadata = videotool.probe(source)
    digest = videotool.sha256_file(source)

    config_path = paths.video_config(slug)
    if config_path.exists() and not force:
        raise StageError(
            f"{config_path.relative_to(paths.repo_root)} already exists — "
            "edit it, or pass --force to regenerate it and lose your tuning"
        )

    manifest_path = paths.manifest(slug)
    existing = Manifest.load(manifest_path) if manifest_path.exists() else None
    if existing is not None and existing.video.sha256 != digest:
        # A different file under the same slug invalidates every frame id, every
        # timestamp and every note anyone has written against this video.
        if not force:
            raise StageError(
                f"slug {slug!r} is already registered to a different file\n"
                f"  registered: {existing.video.source_path}\n"
                f"              sha256 {existing.video.sha256[:12]}…\n"
                f"  given:      {source}\n"
                f"              sha256 {digest[:12]}…\n"
                "  use a new slug, or --force to discard the existing run"
            )
        say("[yellow]![/yellow] source file changed — discarding the previous run's records")
        existing = None

    _write_source_record(paths, slug, source, digest)
    _write_video_config(config_path, slug, source, metadata)

    # Resolve after writing, so the hash covers the file this run will actually
    # read. No project layer here: stage 00 predates the choice of project, and
    # nothing it derives is project-specific.
    resolved = resolve_config(paths, slug, project=None)

    info = VideoInfo(
        slug=slug,
        source_path=str(source),
        sha256=digest,
        duration_s=metadata.duration_s,
        width=metadata.width,
        height=metadata.height,
        fps=metadata.fps,
        rotation=metadata.rotation,
        codec=metadata.codec,
    )

    if existing is None:
        manifest = Manifest(config_hash=resolved.config_hash, video=info)
    else:
        # Same file, re-probed: keep the frames and screens already recorded.
        manifest = existing
        manifest.video = info
        manifest.config_hash = resolved.config_hash

    manifest.clear_stage("00")
    if metadata.rotation:
        manifest.warn(
            "00",
            f"source carries a {metadata.rotation}° rotation flag; frames are sampled "
            f"as {metadata.display_size[0]}×{metadata.display_size[1]} and stage 01 "
            "verifies that orientation",
        )
    manifest.mark_complete("00", {})
    manifest.save(manifest_path)

    say(
        f"  probed  {source.name}  "
        f"{metadata.width}×{metadata.height} @ {metadata.fps:g} fps, "
        f"{format_timecode(int(metadata.duration_s * 1000))}"
        + (f", rotation {metadata.rotation}°" if metadata.rotation else "")
    )
    return manifest


def _validate_slug(slug: str) -> None:
    if not slug or not all(char.isalnum() or char in "-_" for char in slug):
        raise ConfigError(f"invalid slug {slug!r} — {_SLUG_HINT}")


def _write_source_record(paths: Paths, slug: str, source: Path, digest: str) -> None:
    """Record where the video came from without committing it.

    Source files are gitignored, so the repo holds the path and the hash. That is
    enough to detect a swapped file and enough for a reviewer to find the
    original.
    """
    path = paths.source_record(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{source}\nsha256:{digest}\n", encoding="utf-8")


def _write_video_config(
    path: Path, slug: str, source: Path, metadata: videotool.VideoMetadata
) -> None:
    display_width, display_height = metadata.display_size
    # The one value worth deriving: a generic cap of 2000 is meaningless per
    # video, whereas the number of samples this video actually yields makes a
    # truncation warning mean something. No coefficient — duration × fps.
    frame_budget = math.ceil(metadata.duration_s) + 1

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _CONFIG_TEMPLATE.format(
            slug=slug,
            source_name=source.name,
            probe_summary=(
                f"{metadata.width}×{metadata.height}"
                + (
                    f" (displayed {display_width}×{display_height}, "
                    f"rotation {metadata.rotation}°)"
                    if metadata.rotation
                    else ""
                )
                + f" · {metadata.fps:g} fps · {format_timecode(int(metadata.duration_s * 1000))}"
                + (f" · {metadata.codec}" if metadata.codec else "")
            ),
            frame_budget=frame_budget,
        ),
        encoding="utf-8",
    )


# Written by stage 00, then owned by whoever tunes this video. Values are
# commented out on purpose: an uncommented key overrides configs/defaults.yaml
# for good, so only uncomment what this video genuinely needs to disagree about.
_CONFIG_TEMPLATE = """\
# {slug} — per-video config. THE tuning surface for this video.
#
# Generated by stage 00 from {source_name}
#   {probe_summary}
#
# Layers, each overriding the one before:
#   configs/defaults.yaml      generic tool defaults      committed
#   projects/<name>.yaml       which project              gitignored
#   videos/{slug}/config.yaml  THIS FILE                  committed
#
# Only the keys below that are UNCOMMENTED override the defaults. Leave a key
# commented until this video actually needs to disagree — that way improvements
# to configs/defaults.yaml keep reaching this video.
#
# NEVER name a consuming application in this file. Project knowledge lives in
# projects/<name>.yaml and CI fails the build if it leaks (DEC-017).

sample:
  # Sized from this video's duration, so a truncation warning means something.
  # Sampling more than this records a warning rather than silently stopping.
  max_frames: {frame_budget}

  # Frames per second. Raise for fast navigation; costs linear time and disk.
  # fps: 1.0

  # Spans where the screen is not visible at all — intros, desk shots, the
  # camera being picked up. Skipped frames leave a gap in the frame ids, which
  # is honest: nothing was sampled there.
  # skip_ranges:
  #   - ["0:00", "0:12"]

# rectify:
#   # Output size of the warped screen. band_rect and the OCR regions are in
#   # THESE coordinates, so moving this means re-measuring both.
#   canonical_size: [1600, 1000]
#   # Median window for smoothing detected corners. Higher = steadier, slower to
#   # follow genuine reframing. Must be odd.
#   smooth_window: 9
#   # Below this, detection is interpolated from neighbours instead of trusted.
#   min_quad_confidence: 0.55
#   # Corners for spans where detection fails, clockwise from top-left in
#   # SOURCE-frame pixels. Click them once per stable segment.
#   manual_corners:
#     - {{from: "4:10", to: "6:30", corners: [[210, 88], [1720, 120], [1700, 980], [190, 940]]}}

# clean:
#   # Each step is separately switchable because the right combination differs
#   # per video and is discovered during validation.
#   align: true
#   clahe: {{enabled: true, clip: 2.0, grid: 8}}
#   deglare: {{enabled: true, max_correction: 0.3}}
#   # Moiré reduction costs fine detail. Enable only if the interference pattern
#   # is measurably harming OCR on THIS video.
#   moire: {{enabled: false, sigma: 0.6}}

# dedupe:
#   # Title + tab band in canonical coordinates [x, y, w, h] — the region that
#   # actually identifies a screen. Re-measure if this app's chrome sits
#   # elsewhere; this is the first thing to check when the screen count is wrong.
#   band_rect: [0, 0, 1600, 190]
#   # Lower = more screens kept. Tune this second.
#   hash_distance: 12
#   full_frame_weight: 0.3
#   min_gap_frames: 2

# ocr:
#   min_word_confidence: 0.4
#   psm: 7

# identify:
#   # Strips per montage sheet. Lower this before blaming the prompt.
#   montage_rows: 20

# confidence:
#   # Below this a screen is escalated to NEEDS_REVIEW.md instead of accepted.
#   # Never raise it to make the review list shorter.
#   accept_threshold: 0.75

# classify:
#   # Name corrections caused by THIS video's footage quality. A misread caused
#   # by the app itself belongs in projects/<name>.yaml so every video inherits
#   # the fix.
#   aliases: {{}}
"""
