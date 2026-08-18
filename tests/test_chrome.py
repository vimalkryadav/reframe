"""Unit tests for chrome-band detection.

Synthesised frames rather than fixtures: each test states one property of the
detector — where it looks, what it refuses, how it slices — and a painted
rectangle says that more plainly than a photograph of a real application does.
"""

from __future__ import annotations

import numpy as np

from reframe.vision.chrome import ChromeExtent, band_rects, find_chrome_extent

WIDTH, HEIGHT = 1600, 1000
SETTINGS = {
    "saturation_threshold": 40.0,
    "min_row_coverage": 0.5,
    "min_height": 20,
    "search_fraction": 0.35,
    "margin_fraction": 0.06,
    "max_start_fraction": 0.03,
}


def frame(bands: list[tuple[int, int]]) -> np.ndarray:
    """A near-white frame with saturated bands painted at the given row ranges."""
    image = np.full((HEIGHT, WIDTH, 3), 235, dtype=np.uint8)
    for top, bottom in bands:
        image[top:bottom, :] = (40, 40, 200)  # BGR: saturated, high max-min
    return image


class TestFindChromeExtent:
    def test_finds_a_band_at_the_top(self) -> None:
        extent = find_chrome_extent(frame([(0, 110)]), **SETTINGS)  # type: ignore[arg-type]
        assert extent is not None
        assert (extent.top, extent.bottom) == (0, 110)

    def test_tolerates_a_bezel_sliver_above_the_chrome(self) -> None:
        """Rectification includes a few rows above the display; the chrome is
        still the chrome. This case alone accounted for 21 of 133 screens."""
        extent = find_chrome_extent(frame([(14, 120)]), **SETTINGS)  # type: ignore[arg-type]
        assert extent is not None
        assert (extent.top, extent.bottom) == (14, 120)

    def test_no_chrome_returns_none(self) -> None:
        """A full-screen dialog covers the chrome. Missing is a valid answer."""
        assert find_chrome_extent(frame([]), **SETTINGS) is None  # type: ignore[arg-type]

    def test_a_band_too_short_is_not_chrome(self) -> None:
        assert find_chrome_extent(frame([(0, 8)]), **SETTINGS) is None  # type: ignore[arg-type]

    def test_a_saturated_band_in_the_content_is_ignored(self) -> None:
        """A coloured banner halfway down the page is not chrome, and anchoring
        OCR to it would read content as though it were chrome."""
        assert find_chrome_extent(frame([(500, 640)]), **SETTINGS) is None  # type: ignore[arg-type]

    def test_the_topmost_band_wins_over_a_longer_one_below(self) -> None:
        extent = find_chrome_extent(frame([(0, 60), (200, 340)]), **SETTINGS)  # type: ignore[arg-type]
        assert extent is not None
        assert extent.bottom == 60


class TestBandRects:
    def test_slices_by_fraction_of_the_chrome(self) -> None:
        rects = band_rects(
            ChromeExtent(top=0, bottom=100),
            width=1600,
            bands={"title": (0.0, 0.4, 0.0, 0.5)},
        )
        assert rects["title"] == (0, 0, 800, 40)

    def test_fractions_are_relative_to_the_chrome_not_the_frame(self) -> None:
        """The same fractions must follow the chrome when it sits lower."""
        rects = band_rects(
            ChromeExtent(top=20, bottom=120),
            width=1600,
            bands={"title": (0.0, 0.4, 0.0, 0.5)},
        )
        assert rects["title"] == (0, 20, 800, 40)

    def test_a_fraction_above_one_reaches_below_the_chrome(self) -> None:
        """The strip under the chrome is addressable in the same coordinates."""
        rects = band_rects(
            ChromeExtent(top=0, bottom=100),
            width=1600,
            bands={"activity": (1.0, 1.4, 0.0, 0.5)},
        )
        assert rects["activity"] == (0, 100, 800, 40)

    def test_an_empty_band_is_dropped_not_returned_as_zero_height(self) -> None:
        """A zero-height crop would OCR to nothing and be recorded as an
        unreadable screen, which is a different and misleading claim."""
        rects = band_rects(
            ChromeExtent(top=0, bottom=100),
            width=1600,
            bands={"nothing": (0.5, 0.5, 0.0, 0.5), "sliver": (0.0, 0.4, 0.2, 0.2)},
        )
        assert rects == {}
