"""The stage graph.

Stages are numbered, ordered, and each reads only what earlier stages wrote — no
stage reaches forward. They are loaded lazily so that a partially-built checkout
gives a clear "not implemented" instead of an import error at CLI startup, and so
that ``reframe stage 04`` does not import the Anthropic client.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Final, cast

from reframe.config import section_hashes
from reframe.manifest import StageId
from reframe.stages.base import StageContext, StageError

StageRunner = Callable[[StageContext], None]

# Stage 00 is absent: it runs before a manifest exists and is invoked by
# `reframe init`, not by `reframe stage`.
PIPELINE_STAGES: Final[tuple[StageId, ...]] = ("01", "02", "03", "04", "05", "06", "07", "08")

_MODULES: Final[dict[StageId, str]] = {
    "00": "s00_probe",
    "01": "s01_sample",
    "02": "s02_rectify",
    "03": "s03_clean",
    "04": "s04_dedupe",
    "05": "s05_ocr",
    "06": "s06_identify",
    "07": "s07_classify",
    "08": "s08_emit",
}

STAGE_NAMES: Final[dict[StageId, str]] = {
    "00": "probe",
    "01": "sample",
    "02": "rectify",
    "03": "clean",
    "04": "dedupe",
    "05": "ocr",
    "06": "identify",
    "07": "classify",
    "08": "emit",
}


# Which config sections each stage actually reads. Recorded per run so that
# editing one threshold marks only the stages downstream of it as stale — see
# config.section_hashes(). Keep this honest: a stage that reads a section it does
# not declare will not be flagged stale when that section changes.
STAGE_SECTIONS: Final[dict[StageId, tuple[str, ...]]] = {
    "00": (),
    "01": ("sample",),
    "02": ("sample", "rectify"),
    "03": ("rectify", "clean"),
    "04": ("rectify", "clean", "dedupe"),
    "05": ("rectify", "dedupe", "ocr"),
    "06": ("dedupe", "ocr", "identify", "confidence"),
    "07": ("classify", "confidence"),
    "08": ("classify", "confidence"),
}


def load_stage(stage: StageId) -> StageRunner:
    module_name = _MODULES.get(stage)
    if module_name is None:
        raise StageError(f"unknown stage {stage!r} — expected one of {', '.join(_MODULES)}")
    try:
        module = importlib.import_module(f"reframe.stages.{module_name}")
    except ModuleNotFoundError as exc:
        if exc.name is not None and exc.name.startswith("reframe.stages"):
            raise StageError(
                f"stage {stage} ({STAGE_NAMES[stage]}) is not implemented yet"
            ) from exc
        raise
    runner = getattr(module, "run", None)
    if runner is None:
        raise StageError(f"stage {stage} module defines no run()")
    return cast(StageRunner, runner)


def sections_for(stage: StageId, ctx: StageContext) -> dict[str, str]:
    """The config-section hashes this stage is about to consume."""
    current = section_hashes(ctx.pipeline)
    return {name: current[name] for name in STAGE_SECTIONS[stage] if name in current}


def run_stage(stage: StageId, ctx: StageContext) -> None:
    ctx.say(f"→ [bold]{stage} {STAGE_NAMES[stage]}[/bold]")
    load_stage(stage)(ctx)
    # Recorded after the stage succeeds, so a crashed stage is not remembered as
    # having run under this configuration.
    ctx.manifest.mark_complete(stage, sections_for(stage, ctx))
    ctx.save()


__all__ = [
    "PIPELINE_STAGES",
    "STAGE_NAMES",
    "STAGE_SECTIONS",
    "StageContext",
    "StageError",
    "StageRunner",
    "load_stage",
    "run_stage",
    "sections_for",
]
