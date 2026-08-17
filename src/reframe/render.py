"""Markdown rendering. Reads the manifest, writes text, decides nothing.

The three Markdown files are **generated from ``manifest.json`` and never
hand-edited**, so a re-run cannot drift from the data. Corrections go into
``fixtures/<slug>.yaml``; anything typed into these files is lost on the next run,
which is why each one says so at the top.

Nothing here computes a verdict or a bucket. If a number looks wrong in the
Markdown it is wrong in the manifest, and this module is the wrong place to fix it.
"""

from __future__ import annotations

from reframe.manifest import Bucket, Manifest, ReviewSpan, ScreenRecord
from reframe.timecode import format_timecode

_GENERATED = (
    "<!-- Generated from manifest.json by `reframe`. Do not edit: the next run "
    "overwrites this file. Record corrections in fixtures/<slug>.yaml instead. -->"
)

CATALOG_NAME = "SCREEN_CATALOG.md"
QUEUE_NAME = "BUILD_QUEUE.md"
REVIEW_NAME = "NEEDS_REVIEW.md"


def _header(manifest: Manifest, title: str) -> list[str]:
    video = manifest.video
    lines = [
        _GENERATED,
        "",
        f"# {title} — {video.slug}",
        "",
        f"- **Source:** `{video.source_path}`",
        f"- **Duration:** {format_timecode(int(video.duration_s * 1000))} · "
        f"{video.width}×{video.height} @ {video.fps:g} fps",
        f"- **Frames sampled:** {len(manifest.frames)} · "
        f"**kept:** {len(manifest.kept_frames())} · **screens:** {len(manifest.screens)}",
        f"- **Config hash:** `{manifest.config_hash}`",
    ]
    if manifest.inventory is not None:
        inventory = manifest.inventory
        lines.append(
            f"- **Classified against:** {inventory.project} at commit "
            f"`{inventory.commit or 'unverified'}` ({inventory.entry_count} entries)"
        )
    lines.append("")
    return lines


def _warnings_section(manifest: Manifest) -> list[str]:
    """Warnings go near the top of every file, not in a footnote.

    A cap that truncated the run or a stage that could not do its job changes how
    the rest of the document should be read, and a reader who stops halfway must
    not have missed it.
    """
    if not manifest.warnings:
        return []
    lines = ["## ⚠️ Warnings from this run", ""]
    for warning in manifest.warnings:
        where = (
            f" @ {format_timecode(warning.t_ms_start)}" if warning.t_ms_start is not None else ""
        )
        lines.extend([f"- **[stage {warning.stage}]**{where} {warning.message}"])
    lines.append("")
    return lines


def render_catalog(manifest: Manifest) -> str:
    """Every distinct screen, in the order it appears in the footage.

    Column shape follows the catalogue format the consuming workflow already uses —
    ``# | ~sec | Screen | Module | Key content`` — deliberately, so the two can be
    read side by side.
    """
    lines = _header(manifest, "Screen catalogue")
    lines.extend(_warnings_section(manifest))

    if not manifest.screens:
        lines.extend(["No screens were catalogued.", ""])
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "## Screens",
            "",
            "| # | ~time | Screen | Module | Bucket | Confidence | Key content |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for index, screen in enumerate(manifest.screens, start=1):
        identity = screen.identity
        classification = screen.classification
        name = identity.name if identity and identity.name else "**unread**"
        module = (identity.module if identity and identity.module else None) or (
            classification.module if classification and classification.module else "—"
        )
        bucket = classification.bucket if classification else "—"
        lines.append(
            f"| {index} | {format_timecode(screen.t_ms_start)} | {name} | {module} | "
            f"{bucket} | {_confidence_cell(screen)} | {_content_cell(screen)} |"
        )
    lines.append("")

    lines.extend(_evidence_section(manifest))
    return "\n".join(lines) + "\n"


def _confidence_cell(screen: ScreenRecord) -> str:
    if screen.confidence is None:
        return "—"
    mark = "" if screen.confidence.verdict == "accepted" else " ⚠️"
    return f"{screen.confidence.score:.2f}{mark}"


def _content_cell(screen: ScreenRecord) -> str:
    identity = screen.identity
    if identity is None:
        return "—"
    parts: list[str] = []
    if identity.tabs:
        parts.append("tabs: " + ", ".join(identity.tabs))
    if identity.dialog:
        parts.append(f"dialog: {identity.dialog}")
    if identity.description:
        parts.append(identity.description)
    return "; ".join(parts) if parts else "—"


def _evidence_section(manifest: Manifest) -> list[str]:
    """Per-screen provenance: the frame, the timestamp, how it was matched.

    Kept in the catalogue rather than left to the manifest because this is what a
    reviewer needs to disagree with a row — which frame to open, and what the
    classification was based on.
    """
    lines = ["## Evidence", ""]
    for screen in manifest.screens:
        identity = screen.identity
        name = identity.name if identity and identity.name else "unread screen"
        lines.append(
            f"### {screen.id} · {format_timecode(screen.t_ms_start)}–"
            f"{format_timecode(screen.t_ms_end)} · {name}"
        )
        lines.append("")
        lines.append(f"- Frame: `{screen.representative_frame}` ({len(screen.frame_ids)} sampled)")
        if screen.ocr is not None:
            title = screen.ocr.title_raw or "(unreadable)"
            confidence = (
                f" at {screen.ocr.title_confidence:.2f}"
                if screen.ocr.title_confidence is not None
                else ""
            )
            lines.append(f"- OCR title: `{title}`{confidence}")
        if screen.confidence is not None:
            signals = ", ".join(
                f"{name}={value:.2f}" for name, value in screen.confidence.signals.items()
            )
            lines.append(
                f"- Confidence: {screen.confidence.score:.2f} "
                f"({screen.confidence.verdict}) — {signals or 'no signals measured'}"
            )
        if screen.classification is not None:
            lines.extend(_classification_lines(screen))
        lines.append("")
    return lines


def _classification_lines(screen: ScreenRecord) -> list[str]:
    classification = screen.classification
    if classification is None:
        return []
    lines = [
        f"- Classified `{classification.bucket}` via {classification.match_kind}"
        + (f" ({classification.match_score:.2f})" if classification.match_kind != "none" else "")
        + (f" → `{classification.matched_label}`" if classification.matched_label else "")
        + (f" at `{classification.route}`" if classification.route else "")
    ]
    if classification.possible_match is not None:
        possible = classification.possible_match
        lines.append(
            f"- Closest inventory entry: `{possible.label}` at {possible.score:.2f} "
            "(below threshold — not treated as a match)"
        )
    if classification.component_paths:
        lines.append("- Components: " + ", ".join(f"`{p}`" for p in classification.component_paths))
    if classification.note:
        lines.append(f"- Note: {classification.note}")
    return lines


def render_queue(manifest: Manifest) -> str:
    """``new`` and ``partial`` screens only, grouped by module."""
    lines = _header(manifest, "Build queue")
    lines.extend(_warnings_section(manifest))

    if manifest.inventory is None:
        lines.extend(
            [
                "> This video has not been classified against a project inventory, so there "
                "is no build queue. Re-run stage 07 with `--project <name>`.",
                "",
            ]
        )
        return "\n".join(lines) + "\n"

    queued = [
        screen
        for screen in manifest.screens
        if screen.classification is not None and screen.classification.bucket in ("new", "partial")
    ]
    if not queued:
        lines.extend(["Nothing to build from this video — every screen it shows is built.", ""])
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            f"{len(queued)} screen(s) to build, grouped by module. `partial` first: an "
            "existing component that needs extending is usually the cheapest win.",
            "",
        ]
    )
    for bucket in ("partial", "new"):
        section = [screen for screen in queued if _bucket_of(screen) == bucket]
        if not section:
            continue
        lines.extend([f"## {bucket} ({len(section)})", ""])
        for module, screens in _by_module(section):
            lines.extend([f"### {module}", ""])
            for screen in screens:
                lines.extend(_queue_item(screen))
            lines.append("")
    return "\n".join(lines) + "\n"


def _queue_item(screen: ScreenRecord) -> list[str]:
    identity = screen.identity
    classification = screen.classification
    name = identity.name if identity and identity.name else "**unread screen**"
    lines = [
        f"- **{name}** — {format_timecode(screen.t_ms_start)}, frame "
        f"`{screen.representative_frame}`"
    ]
    if identity is not None and identity.tabs:
        lines.append(f"  - Tabs seen: {', '.join(identity.tabs)}")
    if identity is not None and identity.dialog:
        lines.append(f"  - Dialog seen: {identity.dialog}")
    if identity is not None and identity.description:
        lines.append(f"  - Structure: {identity.description}")
    if classification is not None:
        if classification.route:
            lines.append(f"  - Existing route: `{classification.route}`")
        if classification.component_paths:
            lines.append(
                "  - Existing components: "
                + ", ".join(f"`{p}`" for p in classification.component_paths)
            )
        if classification.possible_match is not None:
            lines.append(
                f"  - ⚠️ Resembles `{classification.possible_match.label}` at "
                f"{classification.possible_match.score:.2f} — confirm it is genuinely new "
                "before building"
            )
        if classification.note:
            lines.append(f"  - {classification.note}")
    if screen.confidence is not None and screen.confidence.verdict == "review":
        lines.append(
            f"  - ⚠️ Identified at {screen.confidence.score:.2f} confidence — "
            "see NEEDS_REVIEW.md before trusting this row"
        )
    return lines


def _bucket_of(screen: ScreenRecord) -> Bucket | None:
    return screen.classification.bucket if screen.classification else None


def _by_module(screens: list[ScreenRecord]) -> list[tuple[str, list[ScreenRecord]]]:
    grouped: dict[str, list[ScreenRecord]] = {}
    for screen in screens:
        module = None
        if screen.identity is not None and screen.identity.module:
            module = screen.identity.module
        elif screen.classification is not None and screen.classification.module:
            module = screen.classification.module
        grouped.setdefault(module or "Unassigned", []).append(screen)
    return sorted(grouped.items())


def render_review(manifest: Manifest) -> str:
    """Every escalation, ordered by time so it can be watched in one pass.

    This is the file the tool exists for. A catalogue with a hole in it is worse
    than no catalogue, because a gap nobody was told about cannot be reviewed — so
    everything the pipeline could not resolve lands here with a timestamp.
    """
    lines = _header(manifest, "Needs review")
    lines.extend(_warnings_section(manifest))

    spans = sorted(manifest.review_spans, key=lambda span: (span.t_ms_start, span.reason))
    if not spans:
        lines.extend(
            [
                "Nothing was escalated: every screen was rectified, read and identified "
                "with enough confidence to accept.",
                "",
                "That is worth a moment's suspicion on a first run. Check the screen count "
                "in SCREEN_CATALOG.md against what you remember of the footage before "
                "trusting it.",
                "",
            ]
        )
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            f"{len(spans)} item(s), ordered by timestamp so you can watch them in one pass. "
            "Each says what the pipeline could not settle and what would resolve it.",
            "",
            "| ~time | span | what to check |",
            "| --- | --- | --- |",
        ]
    )
    for span in spans:
        stage, _, reason = span.reason.partition(":")
        window = format_timecode(span.t_ms_start)
        if span.t_ms_end > span.t_ms_start:
            window += f"–{format_timecode(span.t_ms_end)}"
        detail = (span.detail or "").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {window} | `{reason}` (stage {stage}) | {detail} |")
    lines.append("")

    lines.extend(_review_detail(spans))
    return "\n".join(lines) + "\n"


def _review_detail(spans: list[ReviewSpan]) -> list[str]:
    """Frame ids per item, so a reviewer can open the exact evidence."""
    lines = ["## Frames to open", ""]
    for span in spans:
        if not span.frame_ids:
            continue
        shown = ", ".join(f"`{frame_id}`" for frame_id in span.frame_ids[:12])
        overflow = f" … +{len(span.frame_ids) - 12} more" if len(span.frame_ids) > 12 else ""
        lines.append(f"- {format_timecode(span.t_ms_start)} `{span.reason}`: {shown}{overflow}")
    lines.append("")
    return lines
