"""Everything the pipeline needs from the source file: probe, hash, sample.

Wraps ``ffprobe`` and ``ffmpeg`` and nothing else. No pipeline logic lives here —
stage 00 decides what to do with a probe and stage 01 decides what to name a
frame; this module only reports what the file says and hands back pixels.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Final

_SEQUENCE_PATTERN: Final = "_seq_%06d.jpg"
_SEQUENCE_GLOB: Final = "_seq_*.jpg"
_HASH_CHUNK: Final = 1024 * 1024


class VideoToolError(RuntimeError):
    """ffmpeg/ffprobe is missing, or refused to read the file.

    Always fatal: a partially-sampled video would produce a catalogue with a
    hole in it, which is the one failure mode this tool exists to prevent.
    """


@dataclass(frozen=True)
class VideoMetadata:
    """What the container claims. Reported, not interpreted."""

    width: int
    height: int
    fps: float
    duration_s: float
    # Display rotation from the stream's display matrix (or the legacy `rotate`
    # tag). Phone video routinely carries rotation here rather than in the
    # pixels, and reading it wrong gives a sideways screen that corner detection
    # will still happily "find".
    rotation: int
    codec: str | None

    @property
    def display_size(self) -> tuple[int, int]:
        """Size as a player would show it, with rotation applied."""
        if abs(self.rotation) % 180 == 90:
            return self.height, self.width
        return self.width, self.height



def _binary(name: str) -> str:
    found = shutil.which(name)
    if found is None:
        raise VideoToolError(
            f"{name} is not on PATH — reframe cannot read video without it.\n"
            f"  macOS:  brew install ffmpeg\n"
            f"  linux:  apt install ffmpeg"
        )
    return found


def _run(args: list[str]) -> str:
    try:
        # Fixed argv, never a shell string: nothing here interpolates user text
        # into a command line.
        completed = subprocess.run(args, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip().splitlines()
        tail = detail[-1] if detail else f"exit status {exc.returncode}"
        raise VideoToolError(f"{Path(args[0]).name} failed: {tail}") from exc
    return completed.stdout


def sha256_file(path: Path) -> str:
    """Hash the source video.

    Recorded in the manifest so that a different file arriving under the same
    name is a hard error rather than a silent reprocess (DEC-013).
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(_HASH_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_rate(value: object) -> float | None:
    """Parse ffprobe's ``"30000/1001"`` rate strings."""
    if not isinstance(value, str) or "/" not in value:
        return None
    try:
        fraction = Fraction(value)
    except (ZeroDivisionError, ValueError):
        return None
    if fraction == 0:
        return None
    return float(fraction)


def _parse_rotation(stream: dict[str, object]) -> int:
    """Read rotation from the display matrix, falling back to the legacy tag.

    Normalised to 0/90/180/270 rather than kept as ffprobe's signed value, so the
    manifest reads the same whichever ffmpeg version produced it.
    """
    raw: object = None
    side_data = stream.get("side_data_list")
    if isinstance(side_data, list):
        for entry in side_data:
            if isinstance(entry, dict) and "rotation" in entry:
                raw = entry["rotation"]
                break
    if raw is None:
        tags = stream.get("tags")
        if isinstance(tags, dict):
            raw = tags.get("rotate")
    if raw is None:
        return 0
    try:
        degrees = round(float(str(raw)))
    except ValueError:
        return 0
    return degrees % 360


def probe(path: Path) -> VideoMetadata:
    """Read resolution, frame rate, duration, codec and rotation."""
    if not path.exists():
        raise VideoToolError(f"no such video: {path}")
    output = _run(
        [
            _binary("ffprobe"),
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
    )
    try:
        payload: object = json.loads(output)
    except json.JSONDecodeError as exc:
        raise VideoToolError(f"ffprobe returned output that is not JSON for {path}") from exc
    if not isinstance(payload, dict):
        raise VideoToolError(f"ffprobe returned an unexpected shape for {path}")

    streams = payload.get("streams")
    stream: dict[str, object] | None = None
    if isinstance(streams, list):
        for candidate in streams:
            if isinstance(candidate, dict) and candidate.get("codec_type") == "video":
                stream = candidate
                break
    if stream is None:
        raise VideoToolError(f"{path} contains no video stream")

    width = stream.get("width")
    height = stream.get("height")
    if not isinstance(width, int) or not isinstance(height, int):
        raise VideoToolError(f"{path}: ffprobe reported no usable frame size")

    fps = _parse_rate(stream.get("avg_frame_rate")) or _parse_rate(stream.get("r_frame_rate"))
    if fps is None:
        raise VideoToolError(
            f"{path}: ffprobe reported no frame rate — a variable-rate file needs "
            "remuxing before it can be sampled deterministically"
        )

    duration = _first_float(stream.get("duration"), _format_duration(payload))
    if duration is None:
        raise VideoToolError(f"{path}: ffprobe reported no duration")

    codec = stream.get("codec_name")
    return VideoMetadata(
        width=width,
        height=height,
        fps=fps,
        duration_s=duration,
        rotation=_parse_rotation(stream),
        codec=codec if isinstance(codec, str) else None,
    )


def _format_duration(payload: dict[str, object]) -> object:
    container = payload.get("format")
    if isinstance(container, dict):
        return container.get("duration")
    return None


def _first_float(*values: object) -> float | None:
    for value in values:
        if value is None:
            continue
        try:
            parsed = float(str(value))
        except ValueError:
            continue
        if parsed > 0:
            return parsed
    return None


def sample_frames(
    source: Path,
    dest_dir: Path,
    *,
    fps: float,
    quality: int,
    max_frames: int,
) -> list[Path]:
    """Extract frames at a fixed rate into ``dest_dir``, returned in order.

    One decode pass, ``fps`` filter, sequential names. The nth returned file is
    the nth sample on a grid starting at t=0, which is what makes frame ids
    reproducible across re-runs — the caller derives each timestamp from its
    index rather than trusting a side index that can drift (DEC-004).

    Rotation is left to ffmpeg's own autorotate rather than re-applied here: two
    rotations cancel into a sideways screen that corner detection would accept.
    Stage 01 checks the emitted size against the probed display size instead, so a
    mis-rotation is caught rather than assumed away.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    for stale in dest_dir.glob(_SEQUENCE_GLOB):
        stale.unlink()

    _run(
        [
            _binary("ffmpeg"),
            "-hide_banner",
            "-v",
            "error",
            "-nostdin",
            "-i",
            str(source),
            "-vf",
            f"fps={fps}",
            "-q:v",
            str(quality),
            "-frames:v",
            str(max_frames),
            "-f",
            "image2",
            str(dest_dir / _SEQUENCE_PATTERN),
        ]
    )
    return sorted(dest_dir.glob(_SEQUENCE_GLOB))


def frame_size(path: Path) -> tuple[int, int]:
    """Width and height of an extracted frame, for the rotation cross-check."""
    from PIL import Image

    with Image.open(path) as image:
        return image.width, image.height
