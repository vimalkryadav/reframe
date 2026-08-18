"""Configuration: three layers, resolved once, hashed into the manifest.

    1  configs/defaults.yaml       generic tool defaults          committed
    2  projects/<name>.yaml        which project                  gitignored
    3  videos/<slug>/config.yaml   which video                    committed

Two rules are enforced by the shape of the models below rather than by review:

**No tunable has a default in Python.** Every field that a validation round
might move is declared without a default, so a key missing from
``configs/defaults.yaml`` is a startup error instead of a hidden literal
(DEC-014). The only fields carrying defaults are ones layer 1 must *not* contain
because they are project knowledge.

**Unknown keys are rejected.** ``extra="forbid"`` everywhere: a mistyped
threshold that silently does nothing is the same class of failure as a
fabricated value — the run looks like it worked.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from reframe.paths import Paths
from reframe.timecode import parse_range, parse_timecode

# Keys in projects/<name>.yaml that describe the project rather than the
# pipeline. Everything else in that file is treated as a pipeline overlay.
_PROJECT_ONLY_KEYS = frozenset(
    {"project", "project_root", "inventory", "inventory_cmd", "publish_to"}
)


class ConfigError(ValueError):
    """A config file is missing, malformed, or names something it must not."""


class _Section(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


# --------------------------------------------------------------------------
# Layer 1 + 3 — the pipeline. Nothing here may name a consuming application.
# --------------------------------------------------------------------------


class SampleConfig(_Section):
    fps: float = Field(gt=0)
    quality: int = Field(ge=1, le=31)
    skip_ranges: list[tuple[str, str]]
    max_frames: int = Field(gt=0)

    @model_validator(mode="after")
    def _ranges_parse(self) -> Self:
        for pair in self.skip_ranges:
            parse_range(pair)
        return self

    def skip_ranges_ms(self) -> list[tuple[int, int]]:
        return [parse_range(pair) for pair in self.skip_ranges]


class ManualCorners(_Section):
    """Four clockwise corners from top-left, in source-frame pixels, for a span
    where automatic detection fails. A human clicks them once per stable
    segment."""

    from_: str = Field(alias="from")
    to: str
    corners: list[tuple[float, float]] = Field(min_length=4, max_length=4)

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    def span_ms(self) -> tuple[int, int]:
        return parse_timecode(self.from_), parse_timecode(self.to)


class RectifyConfig(_Section):
    canonical_size: tuple[int, int]
    smooth_window: int = Field(gt=0)
    min_quad_confidence: float = Field(ge=0.0, le=1.0)
    aspect_bounds: tuple[float, float]
    max_jump_fraction: float = Field(gt=0.0, le=1.0)
    reanchor_after_frames: int = Field(gt=1)
    manual_corners: list[ManualCorners]

    @model_validator(mode="after")
    def _window_is_odd(self) -> Self:
        if self.smooth_window % 2 == 0:
            raise ValueError("rectify.smooth_window must be odd — a median needs a middle")
        low, high = self.aspect_bounds
        if low >= high:
            raise ValueError("rectify.aspect_bounds must be [low, high] with low < high")
        return self


class ClaheConfig(_Section):
    enabled: bool
    clip: float = Field(gt=0)
    grid: int = Field(gt=0)


class DeglareConfig(_Section):
    enabled: bool
    max_correction: float = Field(ge=0.0, le=1.0)


class MoireConfig(_Section):
    enabled: bool
    sigma: float = Field(gt=0)


class CleanConfig(_Section):
    align: bool
    clahe: ClaheConfig
    deglare: DeglareConfig
    moire: MoireConfig


class DedupeConfig(_Section):
    band_rect: tuple[int, int, int, int]
    hash_distance: int = Field(ge=0)
    full_frame_weight: float = Field(ge=0.0, le=1.0)
    min_gap_frames: int = Field(ge=0)

    @model_validator(mode="after")
    def _band_has_area(self) -> Self:
        _, _, width, height = self.band_rect
        if width <= 0 or height <= 0:
            raise ValueError("dedupe.band_rect must be [x, y, w, h] with positive w and h")
        return self


OcrRegion = Literal["title", "tabs", "activity"]


class OcrConfig(_Section):
    engine: Literal["tesseract"]
    # Which bands to read, and where they are. Two keys rather than one because
    # disabling a noisy region on one video should not throw away the rectangle
    # somebody measured for the application.
    regions: list[OcrRegion]
    region_rects: dict[OcrRegion, tuple[int, int, int, int]]
    min_word_confidence: float = Field(ge=0.0, le=1.0)
    psm: int = Field(ge=0, le=13)

    @model_validator(mode="after")
    def _enabled_regions_have_rects(self) -> Self:
        missing = [region for region in self.regions if region not in self.region_rects]
        if missing:
            raise ValueError(
                f"ocr.regions names {', '.join(missing)} but ocr.region_rects has no "
                "rectangle for them — an enabled region with no geometry would be "
                "silently skipped"
            )
        return self

    def enabled_rects(self) -> list[tuple[OcrRegion, tuple[int, int, int, int]]]:
        """Regions to read, in the order config lists them."""
        return [(region, self.region_rects[region]) for region in self.regions]


class IdentifyConfig(_Section):
    montage_rows: int = Field(gt=0)
    provider: Literal["anthropic", "openai"]
    model: str
    prompt_version: int = Field(ge=1)


class ConfidenceConfig(_Section):
    accept_threshold: float = Field(ge=0.0, le=1.0)
    weights: dict[str, float]

    @model_validator(mode="after")
    def _weights_are_usable(self) -> Self:
        if not self.weights:
            raise ValueError("confidence.weights must name at least one signal")
        total = sum(self.weights.values())
        if total <= 0:
            raise ValueError("confidence.weights must sum to something positive")
        return self


class ClassifyConfig(_Section):
    fuzzy_threshold: float = Field(ge=0.0, le=1.0)
    # How close a rejected match must come to fuzzy_threshold to be worth a
    # human's time. Governs the review list only — the candidate is recorded
    # either way.
    near_miss_margin: float = Field(ge=0.0, le=1.0)
    aliases: dict[str, str]
    # Absent from layer 1 by design — which modules exist is project knowledge,
    # so this arrives from projects/<name>.yaml. Empty means everything is in
    # scope, matching projects/_example.yaml.
    modules_in_scope: list[str] = Field(default_factory=list)
    # Screens that exist but are incomplete. Also project knowledge, and also a
    # human's answer: `partial` means the footage shows tabs, columns or dialogs
    # the built component lacks, which cannot be read off the inventory (see
    # CONTRACT.md). Stage 07 escalates candidates; this list is where the
    # reviewer's confirmation lands.
    partial_labels: list[str] = Field(default_factory=list)


class PipelineConfig(_Section):
    """The fully-resolved tuning surface. This is what gets hashed."""

    sample: SampleConfig
    rectify: RectifyConfig
    clean: CleanConfig
    dedupe: DedupeConfig
    ocr: OcrConfig
    identify: IdentifyConfig
    confidence: ConfidenceConfig
    classify: ClassifyConfig


# --------------------------------------------------------------------------
# Layer 2 — the project profile. Never committed, never named in src/.
# --------------------------------------------------------------------------


class ProjectProfile(_Section):
    """Where the consuming project is and how to ask it what it has built.

    ``project_root`` and ``inventory_cmd`` are optional in the file but stage 07
    refuses to classify without them unless ``--no-refresh`` is passed: an
    unverifiable inventory is a stale inventory (DEC-018).
    """

    name: str
    project_root: Path | None
    inventory: Path
    inventory_cmd: str | None
    publish_to: Path | None


class ResolvedConfig(_Section):
    slug: str
    pipeline: PipelineConfig
    project: ProjectProfile | None
    config_hash: str
    # Which files contributed, in order. Recorded so a surprising threshold can
    # be traced to the layer that set it.
    layers: list[str]


# --------------------------------------------------------------------------
# Loading and layering
# --------------------------------------------------------------------------


def _read_yaml(path: Path) -> dict[str, object]:
    if not path.exists():
        raise ConfigError(f"config file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ConfigError(f"{path} must contain a YAML mapping at the top level")
    return {str(key): value for key, value in loaded.items()}


def deep_merge(base: Mapping[str, object], overlay: Mapping[str, object]) -> dict[str, object]:
    """Recursive merge; scalars and lists replace, mappings merge.

    Lists replace deliberately. A per-video ``skip_ranges`` is a complete
    statement about that video, not an addition to a generic default — and an
    accumulating list would make the resolved config depend on layer order in a
    way nobody could predict from reading the files.
    """
    merged: dict[str, object] = dict(base)
    for key, value in overlay.items():
        current = merged.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            merged[key] = deep_merge(current, value)
        else:
            merged[key] = value
    return merged


def split_project_yaml(raw: Mapping[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    """Separate a project profile into its own keys and its pipeline overlay."""
    profile = {key: value for key, value in raw.items() if key in _PROJECT_ONLY_KEYS}
    overlay = {key: value for key, value in raw.items() if key not in _PROJECT_ONLY_KEYS}
    return profile, overlay


def compute_config_hash(pipeline: PipelineConfig) -> str:
    """Hash the resolved pipeline — not the layers, not the file bytes.

    Only the resolved result matters: two different sets of layers that resolve
    to the same values should produce the same output, and reformatting a YAML
    file should not invalidate a run. Paths from the project profile are
    excluded because they are environment, not tuning; the inventory commit is
    recorded separately in the manifest.
    """
    payload = pipeline.model_dump(mode="json", by_alias=True)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def section_hashes(pipeline: PipelineConfig) -> dict[str, str]:
    """Hash each top-level section separately.

    The whole-config hash tells you *something* changed; these tell you *what*.
    Each stage records the section hashes it consumed, so raising
    ``dedupe.hash_distance`` marks stages 04 onwards stale and leaves stages
    01–03 alone — otherwise every tuning edit would demand a full re-sample and
    the staleness notice would be ignored within a day.
    """
    payload = pipeline.model_dump(mode="json", by_alias=True)
    hashes: dict[str, str] = {}
    for section, value in payload.items():
        blob = json.dumps(value, sort_keys=True, separators=(",", ":"))
        hashes[section] = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
    return hashes


def load_project_profile(paths: Paths, name: str) -> tuple[ProjectProfile, dict[str, object]]:
    """Load ``projects/<name>.yaml``, returning the profile and its overlay."""
    path = paths.project_profile(name)
    if not path.exists():
        raise ConfigError(
            f"no project profile at {path}\n"
            f"  copy projects/_example.yaml to projects/{name}.yaml and fill it in"
        )
    raw = _read_yaml(path)
    profile_keys, overlay = split_project_yaml(raw)

    inventory = profile_keys.get("inventory")
    if not isinstance(inventory, str) or not inventory.strip():
        raise ConfigError(f"{path} must set `inventory:` — see CONTRACT.md")

    def _optional_path(key: str) -> Path | None:
        value = profile_keys.get(key)
        if value is None:
            return None
        if not isinstance(value, str):
            raise ConfigError(f"{path}: `{key}` must be a path string or null")
        return _resolve_against_repo(paths, value)

    declared_name = profile_keys.get("project")
    profile = ProjectProfile(
        name=str(declared_name) if declared_name is not None else name,
        project_root=_optional_path("project_root"),
        inventory=_resolve_against_repo(paths, inventory),
        inventory_cmd=(
            str(profile_keys["inventory_cmd"]) if profile_keys.get("inventory_cmd") else None
        ),
        publish_to=_optional_path("publish_to"),
    )
    return profile, overlay


def _resolve_against_repo(paths: Paths, value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate
    return (paths.repo_root / candidate).resolve()


def resolve_config(paths: Paths, slug: str, project: str | None = None) -> ResolvedConfig:
    """Layer 1 → 2 → 3 and validate the result once.

    The per-video file may be absent, which is what ``reframe init`` sees before
    it writes one; every other caller has already been through stage 00.
    """
    layers: list[str] = []

    defaults_path = paths.defaults_config
    merged = _read_yaml(defaults_path)
    layers.append(str(defaults_path.relative_to(paths.repo_root)))

    profile: ProjectProfile | None = None
    if project is not None:
        profile, overlay = load_project_profile(paths, project)
        merged = deep_merge(merged, overlay)
        layers.append(f"projects/{project}.yaml")

    video_path = paths.video_config(slug)
    if video_path.exists():
        merged = deep_merge(merged, _read_yaml(video_path))
        layers.append(str(video_path.relative_to(paths.repo_root)))

    try:
        pipeline = PipelineConfig.model_validate(merged)
    except Exception as exc:  # pydantic raises ValidationError; report the layers
        raise ConfigError(
            f"resolved config is invalid for {slug!r}\n"
            f"  layers: {' → '.join(layers)}\n"
            f"{exc}"
        ) from exc

    return ResolvedConfig(
        slug=slug,
        pipeline=pipeline,
        project=profile,
        config_hash=compute_config_hash(pipeline),
        layers=layers,
    )
