"""``reframe`` — the command line.

Five commands, matching the loop the tool exists to serve:

    init      register a video and generate its tuning config
    run       every stage, start to finish
    stage     one stage, for the edit-a-threshold-and-re-run round
    fixture   record validated ground truth
    verify    re-run every fixtured video and report regressions

The CLI does no work of its own. It resolves config, loads the manifest, and
hands both to a stage — so that anything it can do, a test can do without a
terminal.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from reframe import __version__, fixtures
from reframe.config import ConfigError, resolve_config, section_hashes
from reframe.fixtures import FixtureError
from reframe.manifest import Manifest, ManifestNotFoundError, StageId, StageOrderError
from reframe.paths import RepoRootNotFoundError, load_paths
from reframe.stages import PIPELINE_STAGES, STAGE_NAMES, StageContext, StageError, run_stage
from reframe.timecode import TimecodeError, format_timecode

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Turn handheld recordings of a desktop application into a reviewed screen catalogue.",
)
console = Console()

# Stages that need to know which project they are classifying against.
_PROJECT_STAGES: frozenset[StageId] = frozenset({"07", "08"})


@contextmanager
def _guard() -> Iterator[None]:
    """Turn expected failures into one readable line and a non-zero exit.

    Expected failures are things the operator can fix: a missing config, a stage
    run out of order, an unparseable timecode. Anything else keeps its traceback,
    because an unexpected failure is a bug and hiding it would be the same
    silent-degradation problem the pipeline is built to avoid.
    """
    try:
        yield
    except (
        ConfigError,
        StageError,
        StageOrderError,
        ManifestNotFoundError,
        FixtureError,
        TimecodeError,
        RepoRootNotFoundError,
    ) as exc:
        console.print(f"[bold red]✗[/bold red] {exc}")
        raise typer.Exit(1) from exc


def _load_context(slug: str, project: str | None, *, no_refresh: bool) -> StageContext:
    paths = load_paths()
    config = resolve_config(paths, slug, project)
    manifest = Manifest.load(paths.manifest(slug))

    if manifest.config_hash != config.config_hash:
        # Not an error: changing a tunable and re-running is the whole workflow.
        # But which earlier stages are now stale has to be said out loud.
        stale = manifest.stale_stages(section_hashes(config.pipeline))
        manifest.config_hash = config.config_hash
        if stale:
            names = ", ".join(f"{s} {STAGE_NAMES[s]}" for s in stale)
            console.print(
                f"[yellow]![/yellow] config changed since these stages ran: {names}\n"
                f"  their output is stale — re-run them before trusting the catalogue"
            )
    return StageContext(
        paths=paths,
        config=config,
        manifest=manifest,
        console=console,
        no_refresh=no_refresh,
    )


def _require_project(stages: tuple[StageId, ...], project: str | None) -> None:
    needed = [s for s in stages if s in _PROJECT_STAGES]
    if needed and project is None:
        raise ConfigError(
            f"stage(s) {', '.join(needed)} classify against a project inventory — "
            "pass --project <name> (see projects/_example.yaml and CONTRACT.md)"
        )


def _print_summary(manifest: Manifest) -> None:
    kept = len(manifest.kept_frames())
    console.print(
        f"\n[bold]{manifest.video.slug}[/bold]  "
        f"{len(manifest.frames)} frames · {kept} kept · {len(manifest.screens)} screens"
    )
    for warning in manifest.warnings:
        where = ""
        if warning.t_ms_start is not None:
            where = f" @ {format_timecode(warning.t_ms_start)}"
        console.print(f"  [yellow]![/yellow] [{warning.stage}]{where} {warning.message}")
    if manifest.review_spans:
        console.print(
            f"  [cyan]?[/cyan] {len(manifest.review_spans)} span(s) need a human — "
            "see NEEDS_REVIEW.md"
        )


@app.command()
def init(
    video: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, readable=True, help="Source video file."),
    ],
    slug: Annotated[
        str, typer.Option("--slug", help="Short name for this video; names every output path.")
    ],
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite an existing config.yaml for this slug."),
    ] = False,
) -> None:
    """Probe a video and generate its per-video config (stage 00)."""
    from reframe.stages.s00_probe import probe

    with _guard():
        paths = load_paths()
        result = probe(paths, video, slug, force=force, console=console)
        console.print(
            f"\nregistered [bold]{slug}[/bold] — "
            f"{result.video.width}×{result.video.height} @ {result.video.fps:g} fps, "
            f"{format_timecode(int(result.video.duration_s * 1000))}\n"
            f"  tune it in  {paths.video_config(slug).relative_to(paths.repo_root)}\n"
            f"  then run    reframe run {slug} --project <name>"
        )


@app.command()
def run(
    slug: Annotated[str, typer.Argument(help="Video slug, as passed to `init --slug`.")],
    project: Annotated[
        str | None,
        typer.Option("--project", help="Project profile in projects/<name>.yaml."),
    ] = None,
    from_stage: Annotated[
        str | None, typer.Option("--from", help="First stage to run (default 01).")
    ] = None,
    to_stage: Annotated[
        str | None, typer.Option("--to", help="Last stage to run (default 08).")
    ] = None,
    no_refresh: Annotated[
        bool,
        typer.Option(
            "--no-refresh",
            help="Skip regenerating the project inventory. A stale inventory reports "
            "finished screens as new — only use this offline.",
        ),
    ] = False,
) -> None:
    """Run the pipeline for one video."""
    with _guard():
        stages = _stage_range(from_stage, to_stage)
        _require_project(stages, project)
        ctx = _load_context(slug, project, no_refresh=no_refresh)
        for stage_id in stages:
            run_stage(stage_id, ctx)
        _print_summary(ctx.manifest)


@app.command()
def stage(
    stage_id: Annotated[str, typer.Argument(help="Stage number, e.g. 04.")],
    slug: Annotated[str, typer.Argument(help="Video slug.")],
    project: Annotated[
        str | None, typer.Option("--project", help="Project profile in projects/<name>.yaml.")
    ] = None,
    no_refresh: Annotated[
        bool, typer.Option("--no-refresh", help="Skip regenerating the project inventory.")
    ] = False,
) -> None:
    """Re-run a single stage. This is where a tuning round lands."""
    with _guard():
        one = (_validate_stage(stage_id),)
        _require_project(one, project)
        ctx = _load_context(slug, project, no_refresh=no_refresh)
        run_stage(one[0], ctx)
        _print_summary(ctx.manifest)


@app.command()
def fixture(
    slug: Annotated[str, typer.Argument(help="Video slug whose run you have validated.")],
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite an existing fixture, discarding its corrections."),
    ] = False,
) -> None:
    """Record validated ground truth for a video.

    Run this after you have watched the video and checked the catalogue. The file it
    writes is a starting point — edit it, because your corrections are what makes
    the next tuning round a ratchet rather than a treadmill.
    """
    with _guard():
        paths = load_paths()
        manifest = Manifest.load(paths.manifest(slug))
        path = paths.fixture(slug)
        if path.exists() and not force:
            raise ConfigError(
                f"{path.relative_to(paths.repo_root)} already exists.\n"
                "  Edit it, or pass --force to regenerate it from the current run and "
                "lose the corrections already recorded in it."
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            fixtures.record(manifest, sample_fps=resolve_config(paths, slug).pipeline.sample.fps),
            encoding="utf-8",
        )
        console.print(
            f"wrote {path.relative_to(paths.repo_root)} — "
            f"{len(manifest.screens)} screen(s)\n"
            "  Now edit it: correct any misread name, delete anything that is not really "
            "there,\n  and add a missed_spans entry for every stretch the run walked past."
        )


@app.command()
def verify(
    project: Annotated[
        str | None,
        typer.Option("--project", help="Project profile, needed to re-run classification."),
    ] = None,
    slug: Annotated[
        str | None,
        typer.Option("--slug", help="Verify one video instead of every fixtured one."),
    ] = None,
    no_rerun: Annotated[
        bool,
        typer.Option(
            "--no-rerun",
            help="Compare the manifests already on disk instead of re-running the pipeline.",
        ),
    ] = False,
) -> None:
    """Re-run every fixtured video and report regressions.

    This is the gate: run it before accepting any tuning change. A change that
    improves video 3 and breaks video 1 is not an improvement.

    Only regressions fail. Drift — a bucket moving because you built something — is
    reported and expected, and so is a known gap that is still a gap.
    """
    with _guard():
        paths = load_paths()
        slugs = [slug] if slug else paths.fixtured_slugs()
        if not slugs:
            console.print(
                "no fixtures recorded yet — validate a video and run "
                "`reframe fixture <slug>` first"
            )
            return

        findings: list[fixtures.Finding] = []
        for candidate in slugs:
            findings.extend(
                _verify_one(candidate, project, rerun=not no_rerun)
            )

        _print_findings(findings, slugs)
        if any(finding.is_failure for finding in findings):
            raise typer.Exit(1)


def _verify_one(slug: str, project: str | None, *, rerun: bool) -> list[fixtures.Finding]:
    paths = load_paths()
    fixture_file = fixtures.Fixture.load(paths.fixture(slug))
    console.print(f"[bold]{slug}[/bold]")

    ctx = _load_context(slug, project, no_refresh=False)
    if rerun:
        # Re-running is the point: a fixture proves nothing about a config change
        # that was never applied to the footage. Stage 06 replays from cache, so the
        # expensive half is usually free.
        stages = PIPELINE_STAGES if project else tuple(s for s in PIPELINE_STAGES if s < "07")
        if not project:
            console.print(
                "  [yellow]![/yellow] no --project: re-running stages 01–06 only, so "
                "bucket drift cannot be checked"
            )
        for stage_id in stages:
            run_stage(stage_id, ctx)

    return fixtures.compare(fixture_file, ctx.manifest, fps=ctx.pipeline.sample.fps)


def _print_findings(findings: list[fixtures.Finding], slugs: list[str]) -> None:
    if not findings:
        console.print("✓ nothing to report — every fixtured screen still matches")
        return
    for finding in findings:
        console.print(f"  {finding.render()}")

    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.status] = counts.get(finding.status, 0) + 1
    summary = " · ".join(f"{count} {status}" for status, count in sorted(counts.items()))
    regressions = counts.get("regression", 0)
    verdict = (
        f"[bold red]{regressions} regression(s)[/bold red]"
        if regressions
        else "[green]no regressions[/green]"
    )
    console.print(f"\n{len(slugs)} video(s) verified: {summary} — {verdict}")


@app.command()
def version() -> None:
    """Print the reframe version recorded in every manifest."""
    console.print(__version__)


def _validate_stage(raw: str) -> StageId:
    normalised = raw.strip().zfill(2)
    if normalised not in PIPELINE_STAGES:
        raise StageError(
            f"{raw!r} is not a runnable stage — expected one of {', '.join(PIPELINE_STAGES)} "
            "(stage 00 runs via `reframe init`)"
        )
    # Narrowed by the membership test above.
    return normalised


def _stage_range(from_stage: str | None, to_stage: str | None) -> tuple[StageId, ...]:
    first = _validate_stage(from_stage) if from_stage else PIPELINE_STAGES[0]
    last = _validate_stage(to_stage) if to_stage else PIPELINE_STAGES[-1]
    start, end = PIPELINE_STAGES.index(first), PIPELINE_STAGES.index(last)
    if start > end:
        raise StageError(f"--from {first} is after --to {last}")
    return PIPELINE_STAGES[start : end + 1]


if __name__ == "__main__":  # pragma: no cover
    app()
