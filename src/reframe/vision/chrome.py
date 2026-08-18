"""Locate the application's chrome band, so OCR rectangles can follow it.

Fixed rectangles in canonical coordinates assume the chrome sits at the same
height on every screen. Measured against real footage, it does not: an
application can put a modal over its own toolbar, add a context header on some
workspaces and not others, and hide the tab strip entirely. On the first real
video, three screens produced chrome bottoms of 15, 83 and 108 canonical pixels,
and a single rectangle read the title on one, the menu row on another and a data
row on the third.

So the rectangle is measured per frame rather than declared once. What config
supplies is *which fraction of the chrome* each band occupies — a statement about
the application's chrome layout — instead of absolute pixels, which are a
statement about one screenshot.

**When the chrome cannot be found, this returns None rather than a guess.** A
band read from a rectangle that was not located is worse than no band at all: it
is text, it looks like a reading, and nothing downstream can tell that the
geometry underneath it was invented.

Nothing here knows what application it is looking at. It knows that chrome is a
saturated horizontal band at the top of the screen, which is a statement about
desktop applications, not about any one of them.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from reframe.vision import Image

# Rect in canonical pixels: (x, y, w, h) — the shape `warp.crop` takes.
Rect = tuple[int, int, int, int]


@dataclass(frozen=True)
class ChromeExtent:
    """The vertical run of chrome at the top of a rectified screen."""

    top: int
    bottom: int

    @property
    def height(self) -> int:
        return self.bottom - self.top


def saturation_profile(image: Image) -> np.ndarray:
    """Per-row share of pixels that are strongly coloured rather than neutral.

    Application chrome is a saturated band; document content is near-neutral,
    whatever its brightness. Measuring *colourfulness* rather than a particular
    hue keeps this free of any one application's palette — and colour is only
    ever used here to locate a rectangle, never extracted or emitted, so DEC-011
    is untouched.
    """
    pixels = image.astype(np.int16)
    high = pixels.max(axis=2)
    low = pixels.min(axis=2)
    return (high - low).astype(np.float64)


def find_chrome_extent(
    image: Image,
    *,
    saturation_threshold: float,
    min_row_coverage: float,
    min_height: int,
    search_fraction: float,
    margin_fraction: float,
    max_start_fraction: float,
) -> ChromeExtent | None:
    """The contiguous chrome band near the top of the screen.

    Only the top ``search_fraction`` of the image is considered: a saturated band
    halfway down is a toolbar inside the content, or a photograph, and anchoring
    OCR to it would be worse than not reading at all.

    The band is allowed to begin up to ``max_start_fraction`` below the top edge
    rather than at row zero. Rectification warps to the *detected* screen quad,
    which routinely includes a few rows of bezel above the display — on the first
    real video that sliver alone hid the chrome on 21 of 133 screens, all of which
    had perfectly readable bands a dozen rows further down.

    Rows are measured across the middle of the frame — ``margin_fraction`` is
    trimmed from each side — because the rectified edges carry warp artefacts and
    a sliver of the surrounding room.
    """
    height, width = image.shape[:2]
    if height == 0 or width == 0:
        return None

    margin = int(width * margin_fraction)
    if width - 2 * margin <= 0:
        margin = 0
    profile = saturation_profile(image)[:, margin : width - margin]
    coloured = (profile > saturation_threshold).mean(axis=1)

    limit = max(1, int(height * search_fraction))
    latest_start = int(height * max_start_fraction)

    row = 0
    while row < limit:
        if coloured[row] < min_row_coverage:
            row += 1
            continue
        start = row
        while row < limit and coloured[row] >= min_row_coverage:
            row += 1
        # First qualifying run wins rather than the longest: chrome is the
        # topmost band, and a longer saturated run further down is content.
        if start <= latest_start and row - start >= min_height:
            return ChromeExtent(top=start, bottom=row)
    return None


def band_rects(
    extent: ChromeExtent,
    *,
    width: int,
    bands: Mapping[str, tuple[float, float, float, float]],
) -> dict[str, Rect]:
    """Slice the chrome into named rectangles.

    Each band is ``(y0, y1, x0, x1)`` as fractions — the y pair of the chrome's
    own height, the x pair of the frame width. Fractions rather than pixels
    because the chrome's height on a rectified frame depends on how much of the
    camera frame the screen filled, which changes shot to shot; the *proportions*
    of an application's own chrome do not.

    A band that would come out empty is dropped rather than returned as a
    zero-height rectangle, so a caller iterating the result never hands an empty
    crop to an OCR engine and records the blank answer as an unreadable screen.
    """
    rects: dict[str, Rect] = {}
    for name, (y0, y1, x0, x1) in bands.items():
        top = extent.top + round(extent.height * y0)
        bottom = extent.top + round(extent.height * y1)
        left = round(width * x0)
        right = round(width * x1)
        if bottom - top < 1 or right - left < 1:
            continue
        rects[name] = (left, top, right - left, bottom - top)
    return rects
