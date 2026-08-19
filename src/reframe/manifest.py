"""The manifest — the contract between stages and between runs.

Each stage reads it, adds its own records, and writes it back. It gets a schema
rather than a dict because it is the join key for every output file and the only
thing a later run has to go on.

Two properties are deliberate and easy to break:

**No wall-clock, no randomness, no ``generated_at``.** A re-run of stages 00–05,
07 and 08 must reproduce the file byte-for-byte given the same inputs, because
only ``frames/kept/`` is committed and everything else is re-extracted on demand
(DEC-013). If you want a timestamp, the caller stamps one outside the manifest.

**Missing is a valid state.** Every field a stage might fail to determine is
optional and stays ``None`` rather than being filled with something plausible.
A stage that cannot do its job records a warning instead (see ``StageWarning``), and
that warning reaches ``NEEDS_REVIEW.md``.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field

from reframe import MANIFEST_SCHEMA_VERSION, __version__

StageId = Literal["00", "01", "02", "03", "04", "05", "06", "07", "08"]
RectifyMethod = Literal["auto", "interpolated", "manual", "failed"]
Framing = Literal["full", "partial", "lost"]
Verdict = Literal["accepted", "review"]
Bucket = Literal["built", "partial", "new", "other"]
# `subset` is not a weaker `fuzzy`: it means one name's words are wholly inside
# the other's, which scores 1.0 and is genuinely undecidable from the strings
# alone. Kept distinct so a reviewer can see why it was not accepted.
MatchKind = Literal["exact", "alias", "fuzzy", "subset", "none"]


class _Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StageWarning(_Record):
    """A stage saying it could not fully do its job.

    Owned by the stage that raised it so a re-run can replace its own warnings
    without duplicating them or erasing another stage's — stages are
    independently re-runnable and must be idempotent.
    """

    stage: StageId
    message: str
    # Where in the footage, when the warning is about a span of video.
    t_ms_start: int | None = None
    t_ms_end: int | None = None


class ReviewSpan(_Record):
    """A stretch of footage a human has to watch, with why.

    Framing failures land here from stage 02 and low-confidence screens from
    stage 06. Both end up in ``NEEDS_REVIEW.md`` ordered by time.
    """

    t_ms_start: int
    t_ms_end: int
    reason: str
    detail: str | None = None
    frame_ids: list[str] = Field(default_factory=list)


class VideoInfo(_Record):
    slug: str
    source_path: str
    sha256: str
    duration_s: float
    width: int
    height: int
    fps: float
    # Phone video routinely carries rotation in metadata rather than in the
    # pixels. Read it wrong and corner detection happily "finds" a sideways
    # screen, so it is recorded explicitly and applied by stage 01.
    rotation: int = 0
    codec: str | None = None

    def expected_samples_at(self, fps: float) -> int:
        """How many frames a full pass at ``fps`` should produce.

        Only used to tell a ``max_frames`` truncation apart from a short video —
        a cap that was hit has to be distinguishable from normal completion.
        """
        return max(math.floor(self.duration_s * fps) + 1, 0)


class RectifyRecord(_Record):
    method: RectifyMethod
    corners: list[tuple[float, float]] | None
    quad_confidence: float
    framing: Framing


class DedupeRecord(_Record):
    band_hash: str
    # The combined score: title-band hash distance plus the full-frame distance
    # weighted by dedupe.full_frame_weight. Fractional because the weight is, and
    # rounding it to an int here would hide why a frame sat just under threshold.
    #
    # None on the first kept frame — there is nothing to compare against, and
    # zero would be a lie.
    distance_from_last_kept: float | None
    kept: bool


class FrameRecord(_Record):
    id: str
    t_ms: int
    # Path to the raw sample, relative to out/<slug>/. The rectified, cleaned and
    # kept copies share this basename and are derived (see paths.sibling_frame)
    # rather than stored, so four paths cannot disagree.
    path: str
    rectify: RectifyRecord | None = None
    dedupe: DedupeRecord | None = None


class OcrWord(_Record):
    region: str
    text: str
    confidence: float


class OcrRecord(_Record):
    """Raw OCR with per-word confidence. A hint for stage 06 and a cross-check in
    ``confidence.py`` — never the source of a screen's identity on its own."""

    title_raw: str | None
    title_confidence: float | None
    tabs_raw: list[str] = Field(default_factory=list)
    activity_raw: str | None = None
    words: list[OcrWord] = Field(default_factory=list)


class IdentityRecord(_Record):
    """What the model read off the chrome. Structure only — never values, never
    colour (DEC-011). ``name`` is None when the model could not read one, which
    is a review, not a guess."""

    name: str | None
    # The record a heading named, kept out of `name` so a hundred visits to one
    # activity are one screen. Never a value from a data row (DEC-011) — only a
    # record the screen's own heading printed.
    record: str | None = None
    module: str | None = None
    tabs: list[str] = Field(default_factory=list)
    # The selected row of a left navigation list. On screens whose sidebar drives
    # the content, this is the identity: two views share a heading and differ only
    # here.
    section: str | None = None
    dialog: str | None = None
    description: str | None = None


class ConfidenceRecord(_Record):
    """Agreement between independent signals, not the model's self-report
    (DEC-009). ``signals`` is kept so a bad score can be attributed."""

    score: float
    signals: dict[str, float]
    verdict: Verdict


class PossibleMatch(_Record):
    """The closest inventory candidate for a screen classified ``new``.

    A fuzzy match below threshold does not silently become ``new``: claiming a
    screen is unbuilt when it is merely misspelled is exactly the
    confident-but-wrong output this tool exists to avoid.
    """

    label: str
    score: float
    route: str | None = None
    module: str | None = None


class ClassificationRecord(_Record):
    bucket: Bucket
    matched_label: str | None = None
    route: str | None = None
    module: str | None = None
    match_kind: MatchKind = "none"
    match_score: float = 0.0
    # Provenance from the inventory entry — for debugging a bad match.
    evidence: str | None = None
    possible_match: PossibleMatch | None = None
    component_paths: list[str] = Field(default_factory=list)
    note: str | None = None


class ScreenRecord(_Record):
    id: str
    representative_frame: str
    # Every kept frame folded into this screen. Cross-frame agreement is a
    # confidence signal, so the membership has to survive in the manifest.
    frame_ids: list[str] = Field(default_factory=list)
    t_ms_start: int
    t_ms_end: int
    ocr: OcrRecord | None = None
    identity: IdentityRecord | None = None
    confidence: ConfidenceRecord | None = None
    classification: ClassificationRecord | None = None


class InventoryRef(_Record):
    """Which snapshot of the consuming project the buckets were true against."""

    project: str
    commit: str | None
    path: str
    entry_count: int


class Manifest(_Record):
    schema_version: int = MANIFEST_SCHEMA_VERSION
    reframe_version: str = __version__
    config_hash: str
    video: VideoInfo
    # Which stages have run, and the per-section config hashes each one consumed.
    # Together they make stale output detectable instead of confusing: mixing two
    # configurations in one catalogue silently is the failure mode to avoid.
    stages_completed: list[StageId] = Field(default_factory=list)
    stage_inputs: dict[str, dict[str, str]] = Field(default_factory=dict)
    warnings: list[StageWarning] = Field(default_factory=list)
    review_spans: list[ReviewSpan] = Field(default_factory=list)
    inventory: InventoryRef | None = None
    frames: list[FrameRecord] = Field(default_factory=list)
    screens: list[ScreenRecord] = Field(default_factory=list)

    # ---- stage bookkeeping ----------------------------------------------
    def clear_stage(self, stage: StageId) -> None:
        """Drop everything a stage previously contributed.

        Called at the top of every stage so a re-run replaces its own output
        instead of appending to it. Idempotency is not optional here: the whole
        workflow is edit-a-threshold-and-re-run-one-stage.
        """
        self.warnings = [w for w in self.warnings if w.stage != stage]
        self.review_spans = [s for s in self.review_spans if not s.reason.startswith(f"{stage}:")]
        self.stages_completed = [s for s in self.stages_completed if s != stage]
        self.stage_inputs.pop(stage, None)

    def invalidate_from(self, stage: StageId) -> None:
        """Forget every stage from ``stage`` onwards.

        Re-sampling changes which frames exist, so every record derived from them
        is void. Dropping them is the honest move: a screen record pointing at a
        frame id that no longer means the same thing is worse than no record,
        because nothing about it looks wrong.
        """
        for later in [s for s in self.stages_completed if s >= stage]:
            self.clear_stage(later)

    def mark_complete(self, stage: StageId, sections: Mapping[str, str] | None = None) -> None:
        if stage not in self.stages_completed:
            self.stages_completed.append(stage)
            self.stages_completed.sort()
        if sections is not None:
            self.stage_inputs[stage] = dict(sections)

    def stale_stages(self, current_sections: Mapping[str, str]) -> list[StageId]:
        """Completed stages whose config sections have since been edited.

        Reported rather than silently re-run: which stages to re-run is the
        operator's call, but not being told is not.
        """
        stale: list[StageId] = []
        for stage in self.stages_completed:
            recorded = self.stage_inputs.get(stage)
            if recorded is None:
                continue
            if any(current_sections.get(key) != value for key, value in recorded.items()):
                stale.append(stage)
        return stale

    def warn(
        self,
        stage: StageId,
        message: str,
        *,
        t_ms_start: int | None = None,
        t_ms_end: int | None = None,
    ) -> None:
        self.warnings.append(
            StageWarning(stage=stage, message=message, t_ms_start=t_ms_start, t_ms_end=t_ms_end)
        )

    def escalate(
        self,
        stage: StageId,
        *,
        t_ms_start: int,
        t_ms_end: int,
        reason: str,
        detail: str | None = None,
        frame_ids: list[str] | None = None,
    ) -> None:
        """Send a span to NEEDS_REVIEW.md. The reason is namespaced by stage so
        ``clear_stage`` can withdraw it on a re-run."""
        self.review_spans.append(
            ReviewSpan(
                t_ms_start=t_ms_start,
                t_ms_end=t_ms_end,
                reason=f"{stage}:{reason}",
                detail=detail,
                frame_ids=frame_ids or [],
            )
        )

    def stage_warnings(self, stage: StageId) -> list[StageWarning]:
        return [w for w in self.warnings if w.stage == stage]

    # ---- lookups --------------------------------------------------------
    def frame(self, frame_id: str) -> FrameRecord:
        for record in self.frames:
            if record.id == frame_id:
                return record
        raise KeyError(f"no frame {frame_id!r} in the manifest")

    def frames_by_id(self) -> dict[str, FrameRecord]:
        return {record.id: record for record in self.frames}

    def kept_frames(self) -> list[FrameRecord]:
        return [f for f in self.frames if f.dedupe is not None and f.dedupe.kept]

    def screen(self, screen_id: str) -> ScreenRecord:
        for record in self.screens:
            if record.id == screen_id:
                return record
        raise KeyError(f"no screen {screen_id!r} in the manifest")

    def requires(self, stage: StageId, *needed: StageId) -> None:
        """Refuse to run a stage whose inputs do not exist yet.

        No stage reaches forward and no stage guesses at absent input; running
        04 before 02 produces garbage that looks like output.
        """
        missing = [s for s in needed if s not in self.stages_completed]
        if missing:
            raise StageOrderError(
                f"stage {stage} needs stage(s) {', '.join(missing)} to have run first"
            )

    # ---- persistence ----------------------------------------------------
    def to_json(self) -> str:
        """Deterministic, human-diffable, no timestamps."""
        payload = self.model_dump(mode="json")
        return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> Self:
        if not path.exists():
            raise ManifestNotFoundError(
                f"no manifest at {path} — run `reframe init` and stage 00 first"
            )
        return cls.model_validate_json(path.read_text(encoding="utf-8"))


class ManifestNotFoundError(FileNotFoundError):
    """No manifest for this slug yet."""


class StageOrderError(RuntimeError):
    """A stage was asked to run before the stage it reads from."""
