"""The inventory: what the consuming project has already built.

Reframe knows nothing about the applications it processes. The one thing it needs
from them — the list of what exists — arrives as a generic ``inventory.json`` that
the project's own exporter produces (DEC-012). This module loads that file, checks
the invariants the contract promises, and matches screen names against it.

See ``CONTRACT.md`` for the schema and for what an exporter has to do.

Matching runs in three passes and records which one succeeded, because *how* a
screen was matched is the first thing anyone debugging a wrong bucket needs:

1. ``exact`` — case-insensitive exact match on a label or one of its aliases.
2. ``alias`` — through the ``classify.aliases`` map in config; the tuning surface.
3. ``fuzzy`` — normalised similarity above ``classify.fuzzy_threshold``.

**A fuzzy match below threshold does not silently become ``new``.** It produces
``new`` *with* the closest candidate and its score attached. Claiming a screen is
unbuilt when it is merely misspelled is exactly the confident-but-wrong output this
tool exists to avoid.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field

from reframe.manifest import Bucket, MatchKind, PossibleMatch
from reframe.text import normalise_label, similarity

# The contract's four status values. `patient_scoped` is domain vocabulary the
# contract fixed before this module existed; Reframe treats it as an opaque
# marker meaning "built, but reached through a record-scoped lookup rather than a
# directly addressable route".
EntryStatus = Literal["built", "patient_scoped", "disabled", "stub"]

# How each status maps to a build-queue bucket. `disabled` and `stub` both mean
# "not built", but they are kept distinct in the inventory because `disabled` says
# somebody looked at this activity and chose not to build it — different
# information from never having heard of it, and worth carrying into the queue.
_STATUS_BUCKET: dict[EntryStatus, Bucket] = {
    "built": "built",
    "patient_scoped": "built",
    "disabled": "new",
    "stub": "new",
}


class InventoryError(ValueError):
    """The inventory is missing, malformed, or breaks a contract invariant."""


class GeneratedFrom(BaseModel):
    model_config = ConfigDict(extra="ignore")

    commit: str | None = None
    sources: list[str] = Field(default_factory=list)


class InventoryEntry(BaseModel):
    """One activity the consuming project knows about."""

    model_config = ConfigDict(extra="ignore")

    label: str
    status: EntryStatus
    aliases: list[str] = Field(default_factory=list)
    route: str | None = None
    module: str | None = None
    # Provenance only. Never affects matching — it exists so a bad match can be
    # traced back to the source that produced the entry.
    source: str | None = None
    component_paths: list[str] = Field(default_factory=list)

    def names(self) -> list[str]:
        return [self.label, *self.aliases]


class Inventory(BaseModel):
    model_config = ConfigDict(extra="ignore")

    schema_version: int = 1
    project: str = "unknown"
    generated_from: GeneratedFrom = Field(default_factory=GeneratedFrom)
    entries: list[InventoryEntry] = Field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> Self:
        if not path.exists():
            raise InventoryError(
                f"no inventory at {path}\n"
                "  it is a build artifact, not data — run the project's exporter "
                "(see CONTRACT.md)"
            )
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InventoryError(f"{path} is not valid JSON: {exc}") from exc
        try:
            inventory = cls.model_validate(payload)
        except Exception as exc:
            raise InventoryError(f"{path} does not match the inventory contract:\n{exc}") from exc
        inventory._check_invariants(path)
        return inventory

    def _check_invariants(self, path: Path) -> None:
        """Enforce what the contract promises, loudly.

        A duplicate label makes matching non-deterministic — two entries answer to
        one name and which one wins depends on file order. An alias colliding with
        a label is worse: it silently redirects a screen to the wrong route. Both
        are the exporter's bugs, and finding them here beats finding them in a
        catalogue three videos later.
        """
        seen: dict[str, str] = {}
        for entry in self.entries:
            key = normalise_label(entry.label)
            if not key:
                raise InventoryError(f"{path}: an entry has an empty label")
            if key in seen:
                raise InventoryError(
                    f"{path}: duplicate label {entry.label!r} — labels must be unique "
                    "(CONTRACT.md). If two modules genuinely share a screen name, the "
                    "exporter must disambiguate them, not collapse them"
                )
            seen[key] = entry.label

        for entry in self.entries:
            for alias in entry.aliases:
                alias_key = normalise_label(alias)
                if alias_key in seen and seen[alias_key] != entry.label:
                    raise InventoryError(
                        f"{path}: alias {alias!r} on {entry.label!r} collides with the "
                        f"label {seen[alias_key]!r} — an alias must not shadow a label"
                    )

    def by_name(self) -> dict[str, InventoryEntry]:
        """Every label and alias, normalised, pointing at its entry."""
        index: dict[str, InventoryEntry] = {}
        for entry in self.entries:
            for name in entry.names():
                index.setdefault(normalise_label(name), entry)
        return index


class Match(BaseModel):
    """The outcome of resolving one screen name against the inventory."""

    model_config = ConfigDict(extra="forbid")

    entry: InventoryEntry | None
    kind: MatchKind
    score: float
    # Set only when nothing matched well enough — the closest thing there was.
    possible: PossibleMatch | None = None


def resolve(
    name: str | None,
    inventory: Inventory,
    *,
    aliases: Mapping[str, str],
    fuzzy_threshold: float,
) -> Match:
    """Match a screen name in three passes, recording which one answered."""
    if not name or not name.strip():
        return Match(entry=None, kind="none", score=0.0)

    index = inventory.by_name()

    exact = index.get(normalise_label(name))
    if exact is not None:
        return Match(entry=exact, kind="exact", score=1.0)

    # The alias table is the tuning surface: when a validation round shows the
    # model consistently reads one screen as something else, the fix is one line
    # of YAML rather than a code change.
    corrected = _apply_aliases(name, aliases)
    if corrected is not None:
        aliased = index.get(normalise_label(corrected))
        if aliased is not None:
            return Match(entry=aliased, kind="alias", score=1.0)

    best_entry, best_score = _closest(corrected or name, inventory)
    if best_entry is None:
        return Match(entry=None, kind="none", score=0.0)
    if best_score >= fuzzy_threshold:
        return Match(entry=best_entry, kind="fuzzy", score=best_score)

    return Match(
        entry=None,
        kind="none",
        score=best_score,
        possible=PossibleMatch(
            label=best_entry.label,
            score=best_score,
            route=best_entry.route,
            module=best_entry.module,
        ),
    )


def _apply_aliases(name: str, aliases: Mapping[str, str]) -> str | None:
    """Look the name up in the config alias table, case-insensitively."""
    normalised = {normalise_label(key): value for key, value in aliases.items()}
    return normalised.get(normalise_label(name))


def _closest(name: str, inventory: Inventory) -> tuple[InventoryEntry | None, float]:
    best: InventoryEntry | None = None
    best_score = 0.0
    for entry in inventory.entries:
        for candidate in entry.names():
            score = similarity(name, candidate)
            if score > best_score:
                best, best_score = entry, score
    return best, round(best_score, 4)


def bucket_for(
    entry: InventoryEntry,
    *,
    modules_in_scope: list[str],
    partial_labels: list[str],
) -> Bucket:
    """Sort a matched entry into a build-queue bucket.

    Scope is checked first: a screen belonging to a module nobody is building
    should be catalogued rather than queued, whatever its status.

    ``partial`` needs a human. It cannot be read off the inventory — it means the
    video shows tabs, columns or dialogs the built component lacks, and knowing
    that requires comparing the two. Automating it would mean parsing the target
    project's components, which reintroduces exactly the coupling this contract
    removed, so v1 takes the reviewer's answer from
    ``classify.partial_labels`` in the project profile.
    """
    if modules_in_scope:
        in_scope = {normalise_label(module) for module in modules_in_scope}
        if normalise_label(entry.module or "") not in in_scope:
            return "other"

    bucket = _STATUS_BUCKET[entry.status]
    if bucket == "built" and _listed(entry.label, partial_labels):
        return "partial"
    return bucket


def _listed(label: str, labels: list[str]) -> bool:
    target = normalise_label(label)
    return any(normalise_label(candidate) == target for candidate in labels)


def evidence_for(entry: InventoryEntry) -> str:
    """A short provenance string for the manifest and the catalogue."""
    parts: list[str] = [entry.status]
    if entry.source:
        parts.append(entry.source)
    return " · ".join(parts)
