"""Matching a screen name against the inventory.

The cases here are the ones that actually went wrong on real footage, kept as
tests because the failure was silent: a screen the queue calls `built` is a
screen nobody looks at again.
"""

from __future__ import annotations

import pytest

from reframe.inventory import Inventory, InventoryEntry, resolve
from reframe.text import is_token_subset, similarity

THRESHOLD = 0.82


def inventory(*labels: str) -> Inventory:
    return Inventory(
        schema_version=1,
        project="test",
        entries=[
            InventoryEntry(label=label, aliases=[], route=f"/{i}", module="M", status="built")
            for i, label in enumerate(labels)
        ],
    )


class TestSimilarity:
    @pytest.mark.parametrize(
        ("read", "label"),
        [
            ("Medication", "Medication Reconciliation"),
            ("Orders", "Anc Orders"),
            ("Summary", "Bed Events Summary"),
        ],
    )
    def test_a_shorter_name_still_scores_high(self, read: str, label: str) -> None:
        """Documents the trap rather than asserting it is fixed here.

        token_set_ratio scores a subset 1.0, so the score alone cannot reject
        these — which is why `resolve` checks the subset relation separately.
        """
        assert similarity(read, label) >= THRESHOLD

    def test_a_character_slip_still_matches(self) -> None:
        assert similarity("Bed Boad", "Bed Board") >= 0.9

    def test_a_split_word_does_not_match(self) -> None:
        """A known limitation, asserted so it is visible rather than surprising.

        token_set_ratio compares whole words, so OCR splitting one word into two
        leaves no shared token and the score collapses — "Snapboard" against
        "Snap board" scores 0.53 and would be rejected. Not fixed here: it needs a
        different scorer, and changing scorers is what produced the subset bug
        this file documents. Worth revisiting with real examples in hand."""
        assert similarity("Snapboard", "Snap board") < 0.6


class TestIsTokenSubset:
    def test_detects_a_missing_word(self) -> None:
        assert is_token_subset("Medication", "Medication Reconciliation")

    def test_detects_an_extra_word(self) -> None:
        assert is_token_subset("Task List Signed In As Ana", "Task List")

    def test_identical_names_are_not_a_subset(self) -> None:
        assert not is_token_subset("Chart Review", "Chart Review")

    def test_a_misspelling_is_not_a_subset(self) -> None:
        """A character-level slip leaves the token sets merely different, which is
        what `similarity` is for."""
        assert not is_token_subset("Snapboard", "Snap board")


class TestResolve:
    def test_exact_name_is_built(self) -> None:
        match = resolve(
            "Chart Review", inventory("Chart Review"), aliases={}, fuzzy_threshold=THRESHOLD
        )
        assert (match.kind, match.entry is not None) == ("exact", True)

    def test_a_subset_is_escalated_not_matched(self) -> None:
        """The bug this file exists for: 29 pharmacy screens were filed as the
        clinical activity `Medication Reconciliation` at a perfect score."""
        match = resolve(
            "Medication",
            inventory("Medication Reconciliation"),
            aliases={},
            fuzzy_threshold=THRESHOLD,
        )
        assert match.kind == "subset"
        assert match.entry is None, "a subset must never resolve to an entry"
        assert match.possible is not None, "but the candidate must reach the reviewer"
        assert match.possible.label == "Medication Reconciliation"

    def test_a_genuine_misreading_still_matches(self) -> None:
        """Escalating subsets must not cost the OCR-slip case the fuzzy pass is
        for."""
        match = resolve(
            "Bed Boad", inventory("Bed Board"), aliases={}, fuzzy_threshold=THRESHOLD
        )
        assert match.kind == "fuzzy"
        assert match.entry is not None

    def test_an_alias_overrides_the_subset_rule(self) -> None:
        """A human writing the alias table has said which screen this is, and that
        outranks anything measured off the strings."""
        match = resolve(
            "Medication",
            inventory("Medication Reconciliation"),
            aliases={"Medication": "Medication Reconciliation"},
            fuzzy_threshold=THRESHOLD,
        )
        assert match.kind == "alias"
        assert match.entry is not None

    def test_an_unrelated_name_matches_nothing(self) -> None:
        match = resolve(
            "Dispensable Mapping", inventory("Bed Board"), aliases={}, fuzzy_threshold=THRESHOLD
        )
        assert match.entry is None
