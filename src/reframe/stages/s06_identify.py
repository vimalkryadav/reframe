"""Stage 06 — Identify.

Reads ``frames/kept/`` and OCR records · Writes identity and confidence records.

The only stage that calls a model, and the only non-deterministic one — which is
why its responses are cached by rendered request, so a re-run with unchanged inputs
replays rather than re-queries (DEC-013).

Three passes, in order of cost:

1. **Montages.** The title band of every kept frame, ~20 per contact sheet with the
   frame id burnt in. Nine sheets instead of 196 full frames.
2. **Full frames**, only for the screens the montage pass could not resolve.
3. **Confidence**, computed in ``confidence.py`` from independent signals — never
   from the model rating its own work.

Screens below ``confidence.accept_threshold`` are not guessed. They keep whatever
was read, are marked ``verdict: review``, and their timestamps reach
``NEEDS_REVIEW.md``. Expect that list to be long on video 1; that is the tool
working.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from rich.progress import track

from reframe import confidence as scoring
from reframe import montage
from reframe.manifest import (
    ConfidenceRecord,
    Framing,
    IdentityRecord,
    RectifyMethod,
    ScreenRecord,
)
from reframe.model.backend import ModelError, ModelRefusalError
from reframe.model.client import IdentifyClient, ModelSettings
from reframe.model.prompts import PromptVersionError, format_hints
from reframe.model.schema import ScreenReading
from reframe.paths import sibling_frame
from reframe.stages.base import StageContext, StageError
from reframe.timecode import format_timecode
from reframe.vision import read_image
from reframe.vision.enhance import band_legibility
from reframe.vision.warp import crop


def run(ctx: StageContext) -> None:
    manifest = ctx.manifest
    manifest.requires("06", "05")
    if not manifest.screens:
        raise StageError("no screens to identify — run stage 04 first")

    identify = ctx.pipeline.identify
    manifest.invalidate_from("06")

    try:
        client = IdentifyClient(
            ModelSettings(
                provider=identify.provider,
                model=identify.model,
                prompt_version=identify.prompt_version,
            ),
            ctx.paths.cache_dir,
        )
        if identify.full_frames:
            # Strips cannot show a sidebar, so there is nothing for a montage pass
            # to contribute here beyond a name the full frame reads better.
            readings: dict[str, ScreenReading] = {}
        else:
            sheets = _build_sheets(ctx)
            readings = _read_sheets(ctx, client, sheets)
            _apply(ctx, readings)
        _resolve_stragglers(ctx, client, readings)
        corroborations = (
            _corroborate(ctx, client) if identify.corroborate else {}
        )
    except PromptVersionError as exc:
        raise StageError(str(exc)) from exc

    _score(ctx, corroborations)
    _report(ctx)


# --------------------------------------------------------------------------
# Pass 1 — montages
# --------------------------------------------------------------------------


def _build_sheets(
    ctx: StageContext, frame_for: Mapping[str, tuple[str, Path]] | None = None
) -> list[montage.Sheet]:
    """Montage sheets, one strip per screen.

    ``frame_for`` overrides which frame represents each screen, which is how
    the corroboration pass reads a *different* image of the same screen.
    """
    band_rect = _band_rect(ctx)
    strips: list[montage.Strip] = []

    for screen in ctx.manifest.screens:
        if frame_for is not None:
            chosen = frame_for.get(screen.id)
            if chosen is None:
                continue
            frame_id, path = chosen
        else:
            frame_id = screen.representative_frame
            maybe = _kept_path(ctx, screen)
            if maybe is None:
                continue
            path = maybe
        band = crop(read_image(path), band_rect)
        if band.size == 0:
            raise StageError(
                f"dedupe.band_rect {list(band_rect)} produced an empty crop for "
                f"{frame_id} — re-measure it against a frame in frames/kept/"
            )
        strips.append(
            montage.Strip(
                screen_id=screen.id,
                frame_id=frame_id,
                t_ms=screen.t_ms_start,
                band=band,
            )
        )

    if not strips:
        raise StageError("no kept frames on disk — re-run stage 04, which owns frames/kept/")

    sheets = montage.build_sheets(
        strips,
        ctx.paths.montages_dir(ctx.slug),
        rows_per_sheet=ctx.pipeline.identify.montage_rows,
    )
    illegible = [sheet for sheet in sheets if not sheet.legible]
    if illegible:
        ctx.manifest.warn(
            "06",
            f"{len(illegible)} of {len(sheets)} montage sheet(s) have strips only "
            f"{illegible[0].strip_height_px}px tall after scaling to the model's "
            f"{montage.MAX_SHEET_EDGE}px limit — lower identify.montage_rows "
            f"(currently {ctx.pipeline.identify.montage_rows}) before blaming the prompt",
        )
    ctx.say(f"  {len(sheets)} montage sheet(s) from {len(strips)} screens")
    return sheets


def _read_sheets(
    ctx: StageContext, client: IdentifyClient, sheets: list[montage.Sheet]
) -> dict[str, ScreenReading]:
    readings: dict[str, ScreenReading] = {}
    cached = 0

    for sheet in track(sheets, description="  reading montages", console=ctx.console):
        hints = format_hints(_hints_for(ctx, [entry.frame_id for entry in sheet.entries]))
        try:
            reading = client.read_montage(
                payload=sheet.read_bytes(),
                digest=sheet.digest,
                strip_count=len(sheet.entries),
                hints=hints,
            )
        except ModelRefusalError as exc:
            # A declined sheet is not a read of the screen. Every strip on it goes
            # to review with the reason attached.
            ctx.manifest.warn(
                "06", f"montage {sheet.index:02d} was declined by policy ({exc.category}) — "
                "the screens on that sheet are unidentified and go to review"
            )
            continue
        except ModelError as exc:
            raise StageError(f"montage {sheet.index:02d}: {exc}") from exc

        cached += 1 if reading.cached else 0
        expected = {entry.frame_id for entry in sheet.entries}
        for screen in reading.screens:
            if screen.frame_id not in expected:
                # A frame id the sheet never carried means the model mis-attributed
                # a strip. Dropping it is the only safe move: a name attached to the
                # wrong timestamp is worse than a missing name.
                ctx.manifest.warn(
                    "06",
                    f"montage {sheet.index:02d} returned an entry for {screen.frame_id!r}, "
                    "which is not on that sheet — discarded as a mis-attribution",
                )
                continue
            readings[screen.frame_id] = screen

        missing = expected - {screen.frame_id for screen in reading.screens}
        if missing:
            ctx.manifest.warn(
                "06",
                f"montage {sheet.index:02d} returned no entry for "
                f"{', '.join(sorted(missing))} — those screens fall through to the "
                "full-frame pass",
            )

    if cached:
        ctx.say(f"  {cached} of {len(sheets)} sheet(s) replayed from cache")
    return readings


# --------------------------------------------------------------------------
# Pass 2 — full frames, only for what the montage could not resolve
# --------------------------------------------------------------------------


def _resolve_stragglers(
    ctx: StageContext, client: IdentifyClient, readings: dict[str, ScreenReading]
) -> None:
    every = ctx.pipeline.identify.full_frames
    unresolved = [
        screen
        for screen in ctx.manifest.screens
        if every or screen.identity is None or screen.identity.name is None
    ]
    if not unresolved:
        return
    ctx.say(
        f"  reading {len(unresolved)} full frame(s)"
        + ("" if every else " — the montage could not resolve them")
    )

    for screen in track(unresolved, description="  reading frames  ", console=ctx.console):
        path = _kept_path(ctx, screen)
        if path is None:
            continue
        payload, digest = montage.encode_frame(read_image(path))
        hints = format_hints(_hints_for(ctx, [screen.representative_frame]))
        try:
            reading = client.read_frame(
                payload=payload,
                digest=digest,
                frame_id=screen.representative_frame,
                hints=hints,
            )
        except ModelRefusalError as exc:
            ctx.manifest.warn(
                "06",
                f"the full frame for {screen.id} at "
                f"{format_timecode(screen.t_ms_start)} was declined by policy "
                f"({exc.category}) — it stays unidentified",
            )
            continue
        except ModelError as exc:
            raise StageError(f"full frame for {screen.id}: {exc}") from exc

        for candidate in reading.screens:
            # The full-frame pass answers about one screen; the frame id it echoes
            # back is not trusted over the one that was actually sent.
            readings[screen.representative_frame] = candidate
            _set_identity(screen, candidate)


# --------------------------------------------------------------------------
# Recording and scoring
# --------------------------------------------------------------------------


def _apply(ctx: StageContext, readings: dict[str, ScreenReading]) -> None:
    for screen in ctx.manifest.screens:
        reading = readings.get(screen.representative_frame)
        screen.identity = None if reading is None else _identity_of(reading)


def _set_identity(screen: ScreenRecord, reading: ScreenReading) -> None:
    screen.identity = _identity_of(reading)


def _identity_of(reading: ScreenReading) -> IdentityRecord:
    return IdentityRecord(
        name=reading.name,
        record=reading.record,
        module=reading.module,
        tabs=list(reading.tabs),
        section=reading.section,
        dialog=reading.dialog,
        description=reading.structure,
    )


# --------------------------------------------------------------------------
# Pass 3 — corroboration
# --------------------------------------------------------------------------


def _corroborate(ctx: StageContext, client: IdentifyClient) -> dict[str, str | None]:
    """Read a second, different frame of each screen, for the cross-frame signal.

    The signal asks whether repeat sightings of one screen get the same name. The
    original implementation looked for repeats by matching band hashes exactly,
    which never fires on handheld footage — measured over 133 real screens, not
    one pair of hashes collided, and loosening to a distance threshold separates
    same-screen from different-screen pairs at a precision of about 0.5 (DEC-025).

    But stage 04 has already grouped the repeats: every screen record holds the
    frames that were folded into it. Those are genuinely different images of the
    same screen — different moment, different shake, different glare — and the
    grouping comes from dedupe rather than from the names being compared, so
    nothing here is circular.

    The frame chosen is the one furthest in time from the representative, because
    two adjacent frames are nearly the same photograph and agreeing about them
    would corroborate very little.
    """
    frames = ctx.manifest.frames_by_id()
    frame_for: dict[str, tuple[str, Path]] = {}
    for screen in ctx.manifest.screens:
        others = [fid for fid in screen.frame_ids if fid != screen.representative_frame]
        for frame_id in reversed(others):
            record = frames.get(frame_id)
            if record is None:
                continue
            path = sibling_frame(ctx.absolute(record.path), "clean")
            if path.exists():
                frame_for[screen.id] = (frame_id, path)
                break

    if not frame_for:
        return {}

    sheets = _build_sheets(ctx, frame_for)
    ctx.say(f"  corroborating {len(frame_for)} screen(s) on {len(sheets)} extra sheet(s)")
    readings = _read_sheets(ctx, client, sheets)

    by_screen = {frame_id: screen_id for screen_id, (frame_id, _) in frame_for.items()}
    return {
        by_screen[frame_id]: reading.name
        for frame_id, reading in readings.items()
        if frame_id in by_screen
    }


def _score(
    ctx: StageContext, corroborations: Mapping[str, str | None]
) -> None:
    """Compute confidence for every screen and escalate the ones that fail."""
    manifest = ctx.manifest
    weights = ctx.pipeline.confidence.weights
    threshold = ctx.pipeline.confidence.accept_threshold
    band_rect = _band_rect(ctx)


    for screen in manifest.screens:
        path = _kept_path(ctx, screen)
        legibility = None
        if path is not None:
            legibility = band_legibility(crop(read_image(path), band_rect))

        signals: dict[str, float | None] = {
            "ocr_agreement": scoring.ocr_agreement(
                screen.identity.name if screen.identity else None,
                screen.ocr.title_raw if screen.ocr else None,
            ),
            "cross_frame": scoring.cross_frame_agreement(
                [
                    screen.identity.name if screen.identity else None,
                    corroborations.get(screen.id),
                ]
            ),
            "framing": scoring.framing_quality(_framing_records(ctx, screen)),
            "legibility": legibility,
        }
        result = scoring.combine(
            signals,
            weights,
            accept_threshold=threshold,
            unreadable=_unreadable_reason(screen),
        )
        screen.confidence = ConfidenceRecord(
            score=result.score, signals=result.signals, verdict=result.verdict
        )
        if result.verdict == "review":
            manifest.escalate(
                "06",
                t_ms_start=screen.t_ms_start,
                t_ms_end=screen.t_ms_end,
                reason="low-confidence",
                detail=(
                    f"{screen.identity.name!r}" if screen.identity and screen.identity.name
                    else "unidentified"
                )
                + f" — {result.reason}",
                frame_ids=[screen.representative_frame],
            )


def _unreadable_reason(screen: ScreenRecord) -> str | None:
    if screen.identity is None:
        return "no reading was returned for this screen"
    if screen.identity.name is None:
        return "the title band could not be read"
    return None


def _framing_records(
    ctx: StageContext, screen: ScreenRecord
) -> list[tuple[RectifyMethod, Framing]]:
    frames = ctx.manifest.frames_by_id()
    records: list[tuple[RectifyMethod, Framing]] = []
    for frame_id in screen.frame_ids or [screen.representative_frame]:
        record = frames.get(frame_id)
        if record is not None and record.rectify is not None:
            records.append((record.rectify.method, record.rectify.framing))
    return records


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _band_rect(ctx: StageContext) -> tuple[int, int, int, int]:
    rect = ctx.pipeline.dedupe.band_rect
    return rect[0], rect[1], rect[2], rect[3]


def _kept_path(ctx: StageContext, screen: ScreenRecord) -> Path | None:
    frame = ctx.manifest.frames_by_id().get(screen.representative_frame)
    if frame is None:
        return None
    path = sibling_frame(ctx.absolute(frame.path), "kept")
    return path if path.exists() else None


def _hints_for(
    ctx: StageContext, frame_ids: list[str]
) -> list[tuple[str, str | None, list[str]]]:
    by_frame = {screen.representative_frame: screen for screen in ctx.manifest.screens}
    hints: list[tuple[str, str | None, list[str]]] = []
    for frame_id in frame_ids:
        screen = by_frame.get(frame_id)
        if screen is None or screen.ocr is None:
            hints.append((frame_id, None, []))
            continue
        hints.append((frame_id, screen.ocr.title_raw, list(screen.ocr.tabs_raw)))
    return hints


def _report(ctx: StageContext) -> None:
    screens = ctx.manifest.screens
    named = sum(1 for s in screens if s.identity is not None and s.identity.name)
    accepted = sum(
        1 for s in screens if s.confidence is not None and s.confidence.verdict == "accepted"
    )
    ctx.say(
        f"  {named} of {len(screens)} named · {accepted} accepted · "
        f"{len(screens) - accepted} to review"
    )
    for screen in screens:
        if screen.confidence is None or screen.confidence.verdict != "review":
            continue
        label = screen.identity.name if screen.identity and screen.identity.name else "?"
        ctx.say(
            f"    [cyan]?[/cyan] {format_timecode(screen.t_ms_start)}  {label}  "
            f"({screen.confidence.score:.2f})"
        )
