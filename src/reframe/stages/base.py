"""What every stage is handed, and what every stage is allowed to do.

A stage orchestrates: it reads the manifest, calls into ``vision/`` or ``model/``
for the actual computation, and writes the manifest back. It holds no algorithm.
That split is what lets a stage be exercised against a folder of fixture frames
with no video anywhere in sight.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from reframe.config import PipelineConfig, ResolvedConfig
from reframe.manifest import Manifest
from reframe.paths import FrameSet, Paths


@dataclass(frozen=True)
class StageContext:
    """Everything a stage needs and nothing it does not."""

    paths: Paths
    config: ResolvedConfig
    manifest: Manifest
    console: Console
    # `reframe run --no-refresh` — skips regenerating the inventory in stage 07.
    # Off by default because a stale inventory reports finished work as `new`.
    no_refresh: bool = False

    @property
    def slug(self) -> str:
        return self.config.slug

    @property
    def pipeline(self) -> PipelineConfig:
        return self.config.pipeline

    @property
    def out_dir(self) -> Path:
        return self.paths.out_dir(self.slug)

    def frames_dir(self, frame_set: FrameSet, *, create: bool = False) -> Path:
        path = self.paths.frames_dir(self.slug, frame_set)
        if create:
            path.mkdir(parents=True, exist_ok=True)
        return path

    def absolute(self, manifest_relative: str) -> Path:
        """Resolve a manifest path (relative to out/<slug>/) to a real file."""
        return self.out_dir / manifest_relative

    def relative(self, path: Path) -> str:
        """Store paths relative to out/<slug>/ so a moved checkout still reads."""
        return path.resolve().relative_to(self.out_dir.resolve()).as_posix()

    def save(self) -> None:
        self.manifest.save(self.paths.manifest(self.slug))

    def say(self, message: str) -> None:
        self.console.print(message)


class StageError(RuntimeError):
    """A stage could not run at all — a missing binary, an unreadable video.

    Distinct from a stage that ran and found something it could not resolve;
    that case records a warning and escalates a span, and the run continues.
    """
