"""Stage 07 — Classify.

Reads identity records and ``inventory.json`` · Writes classification records.

The stage that turns a catalogue into a work plan:

    built     name resolves to a live route          regression-check only
    partial   route exists but the video shows more  targeted extension
    new       no route, or deliberately unbuilt      full build
    other     module outside current scope           catalogue, don't build

**The inventory is refreshed before this stage runs, every time.** The loop is
*process video N → build those screens → process video N+1*, so the inventory is
out of date the moment you finish building, and a stale one reports screens as
``new`` that were completed last week. The generating commit is compared against
the project's ``HEAD`` and **a mismatch aborts the run** (DEC-018). It is never a
warning: a warning about a stale classification is indistinguishable from a correct
classification once it has been written into a Markdown file.
"""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from reframe import confidence as scoring
from reframe import inventory as inv
from reframe.config import ProjectProfile
from reframe.manifest import (
    ClassificationRecord,
    ConfidenceRecord,
    InventoryRef,
    ScreenRecord,
)
from reframe.stages.base import StageContext, StageError
from reframe.text import normalise_label
from reframe.timecode import format_timecode

_GIT_TIMEOUT_S = 30
_EXPORT_TIMEOUT_S = 600


def run(ctx: StageContext) -> None:
    manifest = ctx.manifest
    manifest.requires("07", "06")
    profile = ctx.config.project
    if profile is None:
        raise StageError(
            "stage 07 classifies against a project inventory — pass --project <name> "
            "(see projects/_example.yaml and CONTRACT.md)"
        )

    manifest.invalidate_from("07")

    if ctx.no_refresh:
        _warn_unverified(ctx, profile)
    else:
        _refresh(ctx, profile)

    inventory = _load(profile)
    if not ctx.no_refresh:
        _assert_fresh(ctx, profile, inventory)

    manifest.inventory = InventoryRef(
        project=profile.name,
        commit=inventory.generated_from.commit,
        path=str(profile.inventory),
        entry_count=len(inventory.entries),
    )

    _classify(ctx, inventory)
    _rescore(ctx)
    _report(ctx)


# --------------------------------------------------------------------------
# Freshness
# --------------------------------------------------------------------------


def _refresh(ctx: StageContext, profile: ProjectProfile) -> None:
    """Run the project's exporter, from the project's root."""
    if profile.project_root is None or profile.inventory_cmd is None:
        raise StageError(
            f"projects/{profile.name}.yaml must set both `project_root` and "
            "`inventory_cmd` so the inventory can be regenerated and verified.\n"
            "  Pass --no-refresh to classify against the file as it stands — but an "
            "unverifiable inventory is a stale one (DEC-018), and the run will say so."
        )
    if not profile.project_root.is_dir():
        raise StageError(f"project_root does not exist: {profile.project_root}")

    ctx.say(f"  refreshing inventory: {profile.inventory_cmd}")
    try:
        # shlex, not a shell: the command is a single program with no arguments per
        # the contract, and running it through a shell would make config a place
        # where arbitrary pipelines execute.
        completed = subprocess.run(
            shlex.split(profile.inventory_cmd),
            cwd=profile.project_root,
            capture_output=True,
            text=True,
            timeout=_EXPORT_TIMEOUT_S,
            check=False,
        )
    except FileNotFoundError as exc:
        raise StageError(
            f"could not run `{profile.inventory_cmd}` in {profile.project_root}: {exc}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise StageError(f"`{profile.inventory_cmd}` did not finish within {exc.timeout}s") from exc

    if completed.returncode != 0:
        tail = (completed.stderr or completed.stdout or "").strip().splitlines()
        raise StageError(
            f"`{profile.inventory_cmd}` failed with status {completed.returncode}\n"
            f"  {tail[-1] if tail else 'no output'}\n"
            "  the exporter is expected to fail loudly rather than emit a partial "
            "inventory (CONTRACT.md), so this is not something to work around"
        )


def _assert_fresh(ctx: StageContext, profile: ProjectProfile, inventory: inv.Inventory) -> None:
    """Abort unless the inventory was generated from the project's current HEAD."""
    if profile.project_root is None:
        return
    head = _git_head(profile.project_root)
    recorded = inventory.generated_from.commit
    if recorded is None:
        raise StageError(
            f"{profile.inventory} records no generating commit, so its freshness cannot "
            "be checked. The exporter must set generated_from.commit (CONTRACT.md)."
        )
    if head is None:
        raise StageError(
            f"{profile.project_root} is not a git checkout, so the inventory's commit "
            f"({recorded}) cannot be checked against it. Pass --no-refresh to proceed "
            "with an unverified inventory."
        )
    if not _same_commit(recorded, head):
        raise StageError(
            "the inventory is stale — it was generated from a different commit than the "
            "project's current HEAD.\n"
            f"  inventory: {recorded}\n"
            f"  HEAD:      {head[: len(recorded)] if recorded else head}\n"
            f"  regenerate it:  cd {profile.project_root} && {profile.inventory_cmd}\n"
            "  classifying against an old snapshot would report finished screens as `new`."
        )
    ctx.say(f"  inventory verified at commit {recorded}")


def _git_head(root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_S,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


def _same_commit(recorded: str, head: str) -> bool:
    """Compare by prefix: exporters commonly record an abbreviated sha."""
    shortest = min(len(recorded), len(head))
    return shortest >= 7 and recorded[:shortest].lower() == head[:shortest].lower()


def _warn_unverified(ctx: StageContext, profile: ProjectProfile) -> None:
    ctx.manifest.warn(
        "07",
        "--no-refresh: the inventory was not regenerated and its commit was not "
        "checked against the project's HEAD, so every bucket below may describe an "
        "older state of the application than the one you are building",
    )
    ctx.say(
        "  [yellow]![/yellow] --no-refresh — buckets are classified against an "
        "unverified inventory"
    )


def _load(profile: ProjectProfile) -> inv.Inventory:
    try:
        return inv.Inventory.load(profile.inventory)
    except inv.InventoryError as exc:
        raise StageError(str(exc)) from exc


# --------------------------------------------------------------------------
# Matching
# --------------------------------------------------------------------------


def _classify(ctx: StageContext, inventory: inv.Inventory) -> None:
    classify = ctx.pipeline.classify
    # One question per subject, not per sighting. A screen visited five times
    # produces five records, and five identical rows in NEEDS_REVIEW.md is a list
    # people stop reading. The counts are still in the catalogue.
    asked: set[tuple[str, str]] = set()

    for screen in ctx.manifest.screens:
        name = screen.identity.name if screen.identity else None
        match = inv.resolve(
            name,
            inventory,
            aliases=classify.aliases,
            fuzzy_threshold=classify.fuzzy_threshold,
        )

        if match.entry is None:
            screen.classification = ClassificationRecord(
                bucket="new",
                # Carry the kind through: `subset` and `none` both mean unmatched,
                # but only one of them means the score was unusable rather than low.
                match_kind=match.kind,
                match_score=match.score,
                possible_match=match.possible,
                note=_unmatched_note(name, match),
            )
            _escalate_unmatched(ctx, screen, match, asked)
            continue

        entry = match.entry
        bucket = inv.bucket_for(
            entry,
            modules_in_scope=classify.modules_in_scope,
            partial_labels=classify.partial_labels,
        )
        screen.classification = ClassificationRecord(
            bucket=bucket,
            matched_label=entry.label,
            route=entry.route,
            module=entry.module,
            match_kind=match.kind,
            match_score=match.score,
            evidence=inv.evidence_for(entry),
            component_paths=list(entry.component_paths),
            note=_matched_note(entry, bucket),
        )
        if bucket == "built":
            _escalate_partial_candidate(ctx, screen, entry, asked)


def _unmatched_note(name: str | None, match: inv.Match) -> str:
    if not name:
        return "no screen name was read, so nothing could be matched"
    if match.kind == "subset" and match.possible is not None:
        # Not a low score — an undecidable one. Saying "below threshold" here
        # would be plainly false (it scores 1.00) and would send a reviewer
        # looking for a tuning problem that does not exist.
        return (
            f"one of this name and {match.possible.label!r} contains the other's "
            "words, which scores a perfect match either way — treated as new, "
            "because a shared word is not evidence of the same screen. Confirm it "
            "and add the correction to classify.aliases if they are the same"
        )
    if match.possible is not None:
        return (
            f"closest inventory entry is {match.possible.label!r} at "
            f"{match.possible.score:.2f}, below classify.fuzzy_threshold — treated as new, "
            "but check the alias table before building it"
        )
    return "no inventory entry resembles this name"


def _matched_note(entry: inv.InventoryEntry, bucket: str) -> str | None:
    if entry.status == "disabled":
        return (
            "known and deliberately unbuilt in the project's menu — different "
            "information from never having been catalogued"
        )
    if entry.status == "stub":
        return "reachable but falls through to a placeholder page"
    if entry.status == "lookup_scoped" and bucket == "built":
        return "built, but reached through a record-scoped lookup rather than a direct route"
    return None


def _escalate_unmatched(
    ctx: StageContext,
    screen: ScreenRecord,
    match: inv.Match,
    asked: set[tuple[str, str]],
) -> None:
    """Send a near-miss to review.

    Only near-misses: a screen with no resemblance to anything in the inventory is
    simply new, and queueing it needs no human. A screen that *nearly* matched is
    the dangerous case — one misread character between "build this from scratch"
    and "this already exists".
    """
    if match.possible is None:
        return
    classify = ctx.pipeline.classify
    if match.kind != "subset" and (
        match.possible.score < classify.fuzzy_threshold - classify.near_miss_margin
    ):
        # Not a near miss — a different name. The candidate is still recorded in
        # the manifest and in the build queue; it just does not claim a reviewer's
        # attention. Without this, every genuinely-new screen drags its
        # most-similar unrelated entry into the list.
        return
    read_as = screen.identity.name if screen.identity and screen.identity.name else None
    key = ("near-miss", normalise_label(read_as or screen.id))
    if key in asked:
        return
    asked.add(key)
    ctx.manifest.escalate(
        "07",
        t_ms_start=screen.t_ms_start,
        t_ms_end=screen.t_ms_end,
        reason="contained-name" if match.kind == "subset" else "near-miss-match",
        detail=(
            (
                f"read as {read_as!r}; one of this and "
                f"{match.possible.label!r} contains the other's words. That scores "
                "1.00 whichever way round it is, so the score cannot separate a "
                "title with noise bled into it from a genuinely different, longer "
                "activity name."
            )
            if match.kind == "subset"
            else (
                f"read as {read_as!r}; closest "
                f"inventory entry {match.possible.label!r} scored "
                f"{match.possible.score:.2f}, below classify.fuzzy_threshold "
                f"{classify.fuzzy_threshold:.2f}."
            )
        )
        + " If they are the same screen, add the correction to classify.aliases; "
        "if not, it is genuinely new",
        frame_ids=[screen.representative_frame],
    )


def _escalate_partial_candidate(
    ctx: StageContext,
    screen: ScreenRecord,
    entry: inv.InventoryEntry,
    asked: set[tuple[str, str]],
) -> None:
    """Ask a human whether a built screen is actually only partially built.

    ``partial`` cannot be derived here — it needs the video compared against the
    component, and doing that automatically would mean parsing the consuming
    project, which is the coupling this contract exists to avoid. What this stage
    can do is point at the screens where the question is worth asking: the ones
    where the footage shows tabs or a dialog.
    """
    identity = screen.identity
    if identity is None or not (identity.tabs or identity.dialog):
        return
    key = ("confirm-partial", normalise_label(entry.label))
    if key in asked:
        return
    asked.add(key)
    observed = ", ".join(identity.tabs) if identity.tabs else "none"
    ctx.manifest.escalate(
        "07",
        t_ms_start=screen.t_ms_start,
        t_ms_end=screen.t_ms_end,
        reason="confirm-partial",
        detail=(
            f"{entry.label!r} is built at {entry.route or 'an unaddressable route'}; the "
            f"footage shows tabs [{observed}]"
            + (f" and a dialog {identity.dialog!r}" if identity.dialog else "")
            + ". If the component is missing any of them, add "
            f"{entry.label!r} to classify.partial_labels to move it into the build queue"
        ),
        frame_ids=[screen.representative_frame],
    )


# --------------------------------------------------------------------------
# Feeding the inventory signal back into confidence
# --------------------------------------------------------------------------


def _rescore(ctx: StageContext) -> None:
    """Add the inventory-match signal and recompute each screen's confidence.

    The signal is the last of the five and the only one that is a property of the
    consuming project rather than of the footage — which is why it arrives here
    rather than in stage 06, and why it only participates if the operator has given
    it a weight in ``confidence.weights``.
    """
    weights = ctx.pipeline.confidence.weights
    threshold = ctx.pipeline.confidence.accept_threshold
    if "inventory_match" not in weights:
        return

    for screen in ctx.manifest.screens:
        if screen.confidence is None:
            continue
        signals: dict[str, float | None] = {
            name: value
            for name, value in screen.confidence.signals.items()
            if name != "inventory_match"
        }
        signals["inventory_match"] = _inventory_signal(screen)
        result = scoring.combine(
            signals,
            weights,
            accept_threshold=threshold,
            unreadable=_unreadable(screen),
        )
        screen.confidence = ConfidenceRecord(
            score=result.score, signals=result.signals, verdict=result.verdict
        )


def _inventory_signal(screen: ScreenRecord) -> float | None:
    classification = screen.classification
    if classification is None:
        return None
    if classification.match_kind == "none":
        # Not matching is weak evidence against the reading, not no evidence: a
        # correctly-read new screen also lands here, so it scores low rather than
        # zero and the near-miss note carries the detail.
        return 0.25 if classification.possible_match is not None else 0.5
    return classification.match_score


def _unreadable(screen: ScreenRecord) -> str | None:
    if screen.identity is None:
        return "no reading was returned for this screen"
    if screen.identity.name is None:
        return "the title band could not be read"
    return None


def _report(ctx: StageContext) -> None:
    counts: dict[str, int] = {}
    for screen in ctx.manifest.screens:
        bucket = screen.classification.bucket if screen.classification else "unclassified"
        counts[bucket] = counts.get(bucket, 0) + 1
    ctx.say("  " + " · ".join(f"{count} {bucket}" for bucket, count in sorted(counts.items())))

    for screen in ctx.manifest.screens:
        classification = screen.classification
        if classification is None or classification.possible_match is None:
            continue
        ctx.say(
            f"    [yellow]![/yellow] {format_timecode(screen.t_ms_start)}  "
            f"{(screen.identity.name if screen.identity else None)!r} ≈ "
            f"{classification.possible_match.label!r} "
            f"({classification.possible_match.score:.2f}) — treated as new"
        )
