"""Confidence: agreement between independent signals.

**Confidence is never the model's self-report.** A model rating its own work is not
a measurement — it is another output from the same process that produced the answer,
and it fails in the same direction (DEC-009). What is measurable is whether
*independent* signals agree:

| Signal | What it asks |
| --- | --- |
| ``ocr_agreement`` | Does the model's name match the OCR'd title string? |
| ``cross_frame`` | Do repeat sightings of the same screen get the same name? |
| ``framing`` | Did stage 02 flag this span as partial, lost or interpolated? |
| ``legibility`` | Contrast, blur and glare over the title band. |
| ``inventory_match`` | Does the name resolve to a known activity? (stage 07 feeds back) |

Weights come from config. A signal with no weight configured takes no part, which
is how ``inventory_match`` stays opt-in: it is the only signal that is a property
of the consuming project rather than of the footage.

Two rules make a missing signal honest:

**An unmeasurable signal is dropped, not scored zero.** Zero would punish a screen
for a measurement nobody took; one would flatter it. The weights are renormalised
over the signals that exist.

**A score computed from too little evidence cannot be accepted.** Renormalising
means one strong signal alone can reach any score, and one signal is an opinion
rather than agreement — so coverage is tracked and gates the verdict separately
from the threshold.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from reframe.manifest import Framing, RectifyMethod, Verdict
from reframe.text import normalise_label, similarity

# Fraction of the configured weight that must be measurable before a score is
# treated as agreement rather than as a single opinion. This encodes what the word
# "agreement" means, not how good is good enough — that is
# confidence.accept_threshold in config.
MIN_SIGNAL_COVERAGE: Final = 0.5

# How much each rectification outcome is worth as evidence that the pixels can be
# trusted. Not tunables: they follow directly from what stage 02 recorded, and
# nothing in a validation round would move them. `manual` scores full marks
# because a human placed those corners.
_METHOD_QUALITY: Final[dict[RectifyMethod, float]] = {
    "auto": 1.0,
    "manual": 1.0,
    "interpolated": 0.7,
    "failed": 0.0,
}
_FRAMING_QUALITY: Final[dict[Framing, float]] = {
    "full": 1.0,
    "partial": 0.25,
    "lost": 0.0,
}


@dataclass(frozen=True)
class Confidence:
    score: float
    signals: dict[str, float]
    coverage: float
    verdict: Verdict
    # Why the verdict is `review`, for NEEDS_REVIEW.md. None when accepted.
    reason: str | None = None
    missing: tuple[str, ...] = field(default_factory=tuple)


def combine(
    signals: Mapping[str, float | None],
    weights: Mapping[str, float],
    *,
    accept_threshold: float,
    unreadable: str | None = None,
) -> Confidence:
    """Weighted agreement over the signals that could be measured.

    ``unreadable`` short-circuits everything: when the model itself reported that it
    could not read the band, no arithmetic over the other signals should be allowed
    to produce an accepted screen.
    """
    measured = {
        name: value
        for name, value in signals.items()
        if value is not None and weights.get(name, 0.0) > 0
    }
    missing = tuple(
        sorted(name for name in weights if name not in measured and weights[name] > 0)
    )
    total_weight = sum(weight for name, weight in weights.items() if weight > 0)
    measured_weight = sum(weights[name] for name in measured)

    coverage = round(measured_weight / total_weight, 4) if total_weight > 0 else 0.0
    if measured_weight <= 0:
        score = 0.0
    else:
        score = round(
            sum(weights[name] * value for name, value in measured.items()) / measured_weight, 4
        )

    verdict, reason = _decide(
        score=score,
        coverage=coverage,
        accept_threshold=accept_threshold,
        unreadable=unreadable,
        missing=missing,
    )
    return Confidence(
        score=score,
        signals={name: round(value, 4) for name, value in sorted(measured.items())},
        coverage=coverage,
        verdict=verdict,
        reason=reason,
        missing=missing,
    )


def _decide(
    *,
    score: float,
    coverage: float,
    accept_threshold: float,
    unreadable: str | None,
    missing: tuple[str, ...],
) -> tuple[Verdict, str | None]:
    if unreadable:
        return "review", f"the model could not read this screen: {unreadable}"
    if coverage < MIN_SIGNAL_COVERAGE:
        return "review", (
            f"only {coverage:.0%} of the confidence signals could be measured "
            f"(missing: {', '.join(missing)}) — not enough independent evidence to accept"
        )
    if score < accept_threshold:
        return "review", (
            f"confidence {score:.2f} is below confidence.accept_threshold "
            f"{accept_threshold:.2f}"
        )
    return "accepted", None


# --------------------------------------------------------------------------
# The individual signals. Each returns None when it cannot be measured.
# --------------------------------------------------------------------------


def ocr_agreement(model_name: str | None, ocr_title: str | None) -> float | None:
    """Does the model's name match what OCR read off the same band?

    None when either side is absent — an OCR engine that read nothing has not
    disagreed with anything, and treating silence as disagreement would push every
    hard-to-read screen into review twice over.
    """
    if not model_name or not ocr_title:
        return None
    return similarity(model_name, ocr_title)


def cross_frame_agreement(names: Sequence[str | None]) -> float | None:
    """Do repeat sightings of the same screen get the same name?

    ``names`` are the model's readings of every sighting that looks like this
    screen. None for a single sighting: there is nothing to agree with, and
    scoring a lone sighting 1.0 would invent corroboration.

    Agreement is measured by similarity to the most common reading rather than by
    exact equality, so one OCR-grade character slip does not read as a
    contradiction.
    """
    present = [name for name in names if name]
    if len(present) < 2:
        return None
    # The modal reading is chosen on normalised text so that casing and stray
    # punctuation do not split one screen's votes across several spellings.
    modal, _ = Counter(normalise_label(name) for name in present).most_common(1)[0]
    return round(sum(similarity(name, modal) for name in present) / len(present), 4)


def framing_quality(
    records: Sequence[tuple[RectifyMethod, Framing]],
) -> float | None:
    """How much stage 02 trusted the geometry behind these frames.

    The worst frame in the span decides it. A screen whose span includes one frame
    where the display ran off camera is a screen that might be missing a column,
    and averaging that away is exactly the kind of confident summary this tool
    exists to avoid.
    """
    if not records:
        return None
    return round(
        min(
            min(_METHOD_QUALITY.get(method, 0.0), _FRAMING_QUALITY.get(framing, 0.0))
            for method, framing in records
        ),
        4,
    )
