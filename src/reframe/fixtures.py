"""Ground truth, and the regression check that makes tuning a ratchet.

The improvement loop only compounds if corrections survive. Fix video 1's misses
without recording them and you will silently regress at video 4 (DEC-015).

Fixtures hold **two kinds of fact**, and conflating them breaks verification
(DEC-019):

| Kind | Examples | Property of | A change means |
| --- | --- | --- | --- |
| **Stable observation** | a screen present at a timestamp, | the *footage* — | **regression**, |
| | its name, its module | true forever | fails verify |
| **Time-varying** | bucket, matched route | the *project* now | **drift**, reported |

The distinction is forced by the loop itself. Video 1 first reports
``Study Images → new``; after you build it, the same video correctly reports
``built``. Treating that as a regression would make ``verify`` cry wolf on every
video after the first build — and a verification step people learn to ignore is
worse than none, because it destroys the ratchet it exists to protect.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field

from reframe.manifest import Bucket, Manifest, ScreenRecord
from reframe.timecode import format_timecode, parse_timecode

# How far a fixtured timestamp may sit from a screen's span and still be the same
# sighting, expressed in sampling intervals rather than seconds so it holds at any
# sample.fps. Two intervals covers a screen boundary landing on either side of a
# sample.
_TOLERANCE_INTERVALS = 2


class FixtureError(ValueError):
    """A fixture file is missing or malformed."""


class FixtureScreen(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    t: str
    # Stable: properties of the footage. A change here is a regression.
    name: str | None = None
    module: str | None = None
    # Time-varying: a property of the consuming project at `inventory_commit`.
    bucket: Bucket | None = None
    note: str | None = None

    def t_ms(self) -> int:
        return parse_timecode(self.t)


class MissedSpan(BaseModel):
    """A stretch the run failed to catalogue, recorded so progress is provable."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_: str = Field(alias="from")
    to: str
    note: str | None = None

    def span_ms(self) -> tuple[int, int]:
        return parse_timecode(self.from_), parse_timecode(self.to)


class Fixture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str
    # Which snapshot of the consuming project the buckets below were true against,
    # so drift can always be explained rather than merely noticed.
    inventory_commit: str | None = None
    screens: list[FixtureScreen] = Field(default_factory=list)
    missed_spans: list[MissedSpan] = Field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> Self:
        if not path.exists():
            raise FixtureError(f"no fixture at {path}")
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise FixtureError(f"{path} must contain a YAML mapping")
        try:
            return cls.model_validate(loaded)
        except Exception as exc:
            raise FixtureError(f"{path} is not a valid fixture:\n{exc}") from exc


Status = Literal["regression", "drift", "unfixtured", "gap", "closed"]


@dataclass(frozen=True)
class Finding:
    status: Status
    slug: str
    t_ms: int
    message: str

    @property
    def is_failure(self) -> bool:
        """Only regressions fail. Everything else is information."""
        return self.status == "regression"

    def render(self) -> str:
        marks: dict[Status, str] = {
            "regression": "[bold red]✗ REGRESSION[/bold red]",
            "drift": "[yellow]~ drift      [/yellow]",
            "unfixtured": "[cyan]? unfixtured [/cyan]",
            "gap": "[yellow]· gap        [/yellow]",
            "closed": "[green]✓ closed     [/green]",
        }
        return f"{marks[self.status]} {self.slug} @ {format_timecode(self.t_ms)}  {self.message}"


def record(manifest: Manifest) -> str:
    """Render a fixture from a run the operator has just validated.

    Written as commented YAML rather than dumped, because the file is meant to be
    *edited*: the run is a starting point and the human's corrections are the point
    of the exercise. Screens the run could not name are emitted with ``name: null``
    so there is an obvious blank to fill in rather than a missing line to notice.
    """
    video = manifest.video
    commit = manifest.inventory.commit if manifest.inventory else None
    lines = [
        f"# Ground truth for {video.slug}, recorded from a validated run.",
        "#",
        "# Two kinds of fact live here and verify treats them differently (DEC-019):",
        "#",
        "#   name, module, and the presence of a screen at a timestamp are STABLE.",
        "#     They are properties of the footage and are true forever. If a later run",
        "#     disagrees, that is a REGRESSION and `reframe verify` fails.",
        "#",
        "#   bucket is TIME-VARYING. It is a property of the consuming project at the",
        "#     commit recorded below. new -> built after you build something is DRIFT,",
        "#     which is reported and expected, not a failure.",
        "#",
        "# Edit freely: correct a name the model misread, delete a screen that is not",
        "# really there, and add a missed_spans entry for anything the run walked past.",
        "# A missed span is not a failure — it is a gap you can prove you closed later.",
        "",
        f"slug: {video.slug}",
    ]
    lines.append(
        f"inventory_commit: {commit}" if commit else "inventory_commit: null  # not classified"
    )
    lines.append("")

    if not manifest.screens:
        lines.append("screens: []")
    else:
        lines.append("screens:")
        for screen in manifest.screens:
            lines.extend(_screen_block(screen))

    lines.extend(
        [
            "",
            "# Spans this run failed to catalogue. Add one per stretch of footage that",
            "# shows a screen the catalogue above does not contain, e.g.:",
            '#   - {from: "31:10", to: "33:40", note: "scroll through the order list"}',
            "missed_spans: []",
        ]
    )
    return "\n".join(lines) + "\n"


def _screen_block(screen: ScreenRecord) -> list[str]:
    identity = screen.identity
    classification = screen.classification
    name = identity.name if identity and identity.name else None
    module = identity.module if identity and identity.module else None
    if module is None and classification is not None:
        module = classification.module

    block = [f'  - t: "{format_timecode(screen.t_ms_start)}"']
    block.append(f'    name: {_yaml_scalar(name)}')
    if module:
        block.append(f"    module: {_yaml_scalar(module)}")
    if classification is not None:
        block.append(f"    bucket: {classification.bucket}")

    reasons: list[str] = []
    if screen.confidence is not None and screen.confidence.verdict == "review":
        reasons.append(f"identified at {screen.confidence.score:.2f} — verify this name")
    if classification is not None and classification.possible_match is not None:
        reasons.append(
            f"resembles {classification.possible_match.label!r} "
            f"({classification.possible_match.score:.2f})"
        )
    if reasons:
        block.append(f"    note: {_yaml_scalar('; '.join(reasons))}")
    return block


def _yaml_scalar(value: str | None) -> str:
    if value is None:
        return "null"
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def compare(fixture: Fixture, manifest: Manifest, *, fps: float) -> list[Finding]:
    """Check a run against ground truth, separating regression from drift."""
    tolerance_ms = int(_TOLERANCE_INTERVALS * 1000 / fps) if fps > 0 else 2000
    # The commit the run's buckets were true against, so drift names both ends of
    # the change rather than only where it landed.
    current_commit = manifest.inventory.commit if manifest.inventory else None
    findings: list[Finding] = []
    matched_screens: set[str] = set()

    for expected in fixture.screens:
        target = expected.t_ms()
        # One run screen answers for at most one fixture entry. If two fixtured
        # screens collapsed into one, the honest report is that the second is
        # missing — not that both were renamed.
        found = _screen_at(manifest, target, tolerance_ms, taken=matched_screens)
        if found is None:
            findings.append(
                Finding(
                    status="regression",
                    slug=fixture.slug,
                    t_ms=target,
                    message=(
                        "screen no longer detected"
                        + (f" ({expected.name!r})" if expected.name else "")
                    ),
                )
            )
            continue
        matched_screens.add(found.id)
        findings.extend(_compare_screen(fixture, expected, found, current_commit))

    for screen in manifest.screens:
        if screen.id in matched_screens:
            continue
        name = screen.identity.name if screen.identity and screen.identity.name else "unread"
        findings.append(
            Finding(
                status="unfixtured",
                slug=fixture.slug,
                t_ms=screen.t_ms_start,
                message=f"screen found that the fixture does not mention: {name!r}",
            )
        )

    findings.extend(_compare_gaps(fixture, manifest, tolerance_ms))
    return sorted(findings, key=lambda finding: (finding.t_ms, finding.status))


def _compare_screen(
    fixture: Fixture,
    expected: FixtureScreen,
    found: ScreenRecord,
    current_commit: str | None,
) -> list[Finding]:
    findings: list[Finding] = []
    actual_name = found.identity.name if found.identity else None

    if expected.name and actual_name != expected.name:
        findings.append(
            Finding(
                status="regression",
                slug=fixture.slug,
                t_ms=expected.t_ms(),
                message=f"name changed: {expected.name!r} → {actual_name!r}",
            )
        )
    if expected.module:
        actual_module = (found.identity.module if found.identity else None) or (
            found.classification.module if found.classification else None
        )
        if actual_module != expected.module:
            findings.append(
                Finding(
                    status="regression",
                    slug=fixture.slug,
                    t_ms=expected.t_ms(),
                    message=f"module changed: {expected.module!r} → {actual_module!r}",
                )
            )
    if expected.bucket is not None and found.classification is not None:
        actual_bucket = found.classification.bucket
        if actual_bucket != expected.bucket:
            findings.append(
                Finding(
                    status="drift",
                    slug=fixture.slug,
                    t_ms=expected.t_ms(),
                    message=(
                        f"bucket {expected.bucket} → {actual_bucket} "
                        f"(inventory {fixture.inventory_commit or 'unknown'} → "
                        f"{current_commit or 'unverified'})"
                    ),
                )
            )
    return findings


def _compare_gaps(fixture: Fixture, manifest: Manifest, tolerance_ms: int) -> list[Finding]:
    """Report whether known gaps are still gaps.

    A recorded gap that is still missing is not a regression — it was already
    missing when it was written down — but it is not nothing either, and a run that
    finally covers one is the clearest evidence tuning is working. So both
    directions are reported and neither fails the check.
    """
    findings: list[Finding] = []
    for span in fixture.missed_spans:
        start, end = span.span_ms()
        covered = any(
            screen.t_ms_start <= end + tolerance_ms and screen.t_ms_end >= start - tolerance_ms
            for screen in manifest.screens
        )
        note = f" — {span.note}" if span.note else ""
        findings.append(
            Finding(
                status="closed" if covered else "gap",
                slug=fixture.slug,
                t_ms=start,
                message=(
                    f"known gap {span.from_}–{span.to} is now catalogued{note}"
                    if covered
                    else f"known gap {span.from_}–{span.to} still not catalogued{note}"
                ),
            )
        )
    return findings


def _screen_at(
    manifest: Manifest, t_ms: int, tolerance_ms: int, *, taken: set[str] | None = None
) -> ScreenRecord | None:
    """The nearest unclaimed screen whose span contains ``t_ms``, within tolerance."""
    claimed = taken or set()
    best: ScreenRecord | None = None
    best_distance = tolerance_ms + 1
    for screen in manifest.screens:
        if screen.id in claimed:
            continue
        if not screen.t_ms_start - tolerance_ms <= t_ms <= screen.t_ms_end + tolerance_ms:
            continue
        if screen.t_ms_start <= t_ms <= screen.t_ms_end:
            distance = 0
        else:
            distance = min(abs(t_ms - screen.t_ms_start), abs(t_ms - screen.t_ms_end))
        if distance < best_distance:
            best, best_distance = screen, distance
    return best
