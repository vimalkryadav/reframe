"""Title-band contact sheets with burnt-in labels.

Reading nine montages beats reading 196 full frames — an economy already proven in
the workflow this tool serves, and it cuts model cost by an order of magnitude.

Two details make the sheets trustworthy:

**The label is burnt into the pixels.** The model is asked to report a frame id
per strip, and that id has to come from something it can actually see. A label
supplied only as text alongside the image invites the model to guess which strip
is which, and a mis-attributed screen name is indistinguishable from a correct one.

**The sheet is scaled here, not by the API.** Vision requests are downscaled to a
fixed long edge on arrival; doing it locally means the bytes that get hashed for
the response cache are the bytes the model actually read, and it makes the strip
height — the thing that decides whether the labels are legible at all —
measurable before the call rather than guessable after it.
"""

from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont

from reframe.timecode import format_timecode
from reframe.vision import DERIVED_JPEG_QUALITY, Image

# Vision requests are resampled to this long edge, so a sheet larger than this is
# downscaled by the API before the model sees it. Matching it locally keeps the
# cached bytes and the read bytes identical.
MAX_SHEET_EDGE: Final = 1568
# Below this, a strip's text is too small to read reliably after scaling. Not a
# quality bar — a legibility floor, surfaced so the operator can lower
# identify.montage_rows rather than wonder why the model is guessing.
MIN_LEGIBLE_STRIP_PX: Final = 44
# Left gutter for the burnt-in label. Wide enough for "f_000842 · 14:02" and
# placed beside the band rather than over it, so no screen content is covered.
_GUTTER_PX: Final = 250
_LABEL_SIZE_PX: Final = 26
_PADDING_PX: Final = 6
_BACKGROUND: Final = (24, 24, 28)
_LABEL_COLOUR: Final = (245, 245, 245)


@dataclass(frozen=True)
class Strip:
    """One screen's title band, waiting to be laid out."""

    screen_id: str
    frame_id: str
    t_ms: int
    band: Image

    @property
    def label(self) -> str:
        return f"{self.frame_id} · {format_timecode(self.t_ms)}"


@dataclass(frozen=True)
class SheetEntry:
    """What ended up on a sheet, in the order it was drawn."""

    screen_id: str
    frame_id: str
    t_ms: int
    label: str


@dataclass(frozen=True)
class Sheet:
    index: int
    path: Path
    entries: tuple[SheetEntry, ...]
    # sha256 of the encoded bytes — the montage half of the response cache key.
    digest: str
    strip_height_px: int
    width_px: int
    height_px: int

    @property
    def legible(self) -> bool:
        return self.strip_height_px >= MIN_LEGIBLE_STRIP_PX

    def read_bytes(self) -> bytes:
        return self.path.read_bytes()


def build_sheets(strips: list[Strip], out_dir: Path, *, rows_per_sheet: int) -> list[Sheet]:
    """Stack strips into labelled contact sheets, in order.

    Deterministic: same strips and same row count produce byte-identical sheets,
    which is what lets the response cache be keyed on the sheet's hash.
    """
    if rows_per_sheet <= 0:
        raise ValueError("identify.montage_rows must be positive")
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("titles-*.jpg"):
        stale.unlink()

    sheets: list[Sheet] = []
    for index, chunk in enumerate(_chunks(strips, rows_per_sheet)):
        path = out_dir / f"titles-{index:02d}.jpg"
        sheets.append(_render_sheet(index, chunk, path))
    return sheets


def _chunks(strips: list[Strip], size: int) -> list[list[Strip]]:
    return [strips[start : start + size] for start in range(0, len(strips), size)]


def _render_sheet(index: int, strips: list[Strip], path: Path) -> Sheet:
    band_width = max(strip.band.shape[1] for strip in strips)
    band_height = max(strip.band.shape[0] for strip in strips)
    row_height = band_height + _PADDING_PX
    canvas_width = _GUTTER_PX + band_width + _PADDING_PX
    canvas_height = row_height * len(strips) + _PADDING_PX

    sheet = PILImage.new("RGB", (canvas_width, canvas_height), _BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    font = _label_font()

    for row, strip in enumerate(strips):
        top = _PADDING_PX + row * row_height
        band = PILImage.fromarray(_to_rgb(strip.band))
        sheet.paste(band, (_GUTTER_PX, top))
        draw.text(
            (_PADDING_PX, top + max((band_height - _LABEL_SIZE_PX) // 2, 0)),
            strip.label,
            font=font,
            fill=_LABEL_COLOUR,
        )

    scale = min(MAX_SHEET_EDGE / max(canvas_width, canvas_height), 1.0)
    if scale < 1.0:
        sheet = sheet.resize(
            (max(int(canvas_width * scale), 1), max(int(canvas_height * scale), 1)),
            PILImage.Resampling.LANCZOS,
        )

    buffer = io.BytesIO()
    sheet.save(buffer, format="JPEG", quality=DERIVED_JPEG_QUALITY)
    payload = buffer.getvalue()
    path.write_bytes(payload)

    return Sheet(
        index=index,
        path=path,
        entries=tuple(
            SheetEntry(
                screen_id=strip.screen_id,
                frame_id=strip.frame_id,
                t_ms=strip.t_ms,
                label=strip.label,
            )
            for strip in strips
        ),
        digest=hashlib.sha256(payload).hexdigest(),
        strip_height_px=int(band_height * scale),
        width_px=sheet.width,
        height_px=sheet.height,
    )


def _label_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Pillow's bundled font, sized.

    Deliberately not a system font path: the sheets must render identically on
    whatever machine re-runs the pipeline, and a missing font file is a crash in
    the middle of a long run.
    """
    try:
        return ImageFont.load_default(size=_LABEL_SIZE_PX)
    except (AttributeError, TypeError):  # pragma: no cover - very old Pillow
        return ImageFont.load_default()


def _to_rgb(band: Image) -> np.ndarray:
    """OpenCV hands over BGR; PIL wants RGB."""
    if band.ndim == 2:
        return np.stack([band] * 3, axis=-1)
    return band[:, :, ::-1]


def encode_frame(image: Image) -> tuple[bytes, str]:
    """Encode a full frame for the fallback pass, scaled and hashed like a sheet."""
    picture = PILImage.fromarray(_to_rgb(image))
    scale = min(MAX_SHEET_EDGE / max(picture.width, picture.height), 1.0)
    if scale < 1.0:
        picture = picture.resize(
            (max(int(picture.width * scale), 1), max(int(picture.height * scale), 1)),
            PILImage.Resampling.LANCZOS,
        )
    buffer = io.BytesIO()
    picture.save(buffer, format="JPEG", quality=DERIVED_JPEG_QUALITY)
    payload = buffer.getvalue()
    return payload, hashlib.sha256(payload).hexdigest()
