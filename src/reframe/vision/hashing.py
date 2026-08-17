"""Perceptual hashing and band comparison.

The inherited method — greyscale, crop the taskbar, resize, blur, keep a frame
when more than 5.5% of pixels differ from the last kept one — *inverts* on
handheld footage. Hand shake alone displaces the whole image by more than that,
so nothing registers as a duplicate and every frame survives as a "distinct
screen" (DEC-007).

What replaces it is here: compare the **title and tab band** specifically, since
that band is what identifies a screen, with a full-frame comparison as a weaker
secondary signal to catch a dialog opening or the content scrolling within one
screen.

Two implementation choices matter, and both were forced by measurement rather
than chosen up front:

**The hash grid matches the region's aspect ratio.** A stock square dHash squashes
a 1600×190 band into a 9×8 grid, which averages the title text away entirely. A
wide region gets a wide grid.

**Cells that differ by less than the noise floor are recorded as flat, not as a
direction.** This is the change that made the band signal usable at all. A title
bar is mostly uniform: perhaps a quarter of its cell pairs contain text, and in
the rest the adjacent difference is smaller than the sensor noise, so a plain
``left > right`` test is a coin flip. Measured on static footage, that put two
frames of the *same* screen 8–13 bits apart while two *different* screens sat 10–18
apart — no separation at all, and no threshold could have recovered one. Each cell
pair therefore contributes two bits, "brighter" and "darker", and a flat pair sets
neither.

**Distances are reported on a fixed 64-bit scale** regardless of the grid actually
used, so ``dedupe.hash_distance`` keeps one meaning across regions of different
shapes and stays comparable between videos.
"""

from __future__ import annotations

import math
from typing import Final

import cv2
import numpy as np

from reframe.vision import Gray, Image

# Reporting scale. dedupe.hash_distance is expressed out of this many bits, so
# changing it would silently reinterpret every tuned config in the repo.
MAX_DISTANCE: Final = 64
# Cell pairs sampled per hash. Each contributes two bits, and distances are scaled
# back to MAX_DISTANCE before anyone sees them.
_TARGET_CELLS: Final = 128
# Pixels below this are too small a region to hash meaningfully.
_MIN_SIDE: Final = 4
# Dead zone, in grey levels. A noise floor, not a tunable: INTER_AREA averaging
# over cells tens of pixels across reduces per-pixel sensor noise to a small
# fraction of one level, while real text sits 50–200 levels above its background.
# Anything in between is nothing.
_FLAT_EPSILON: Final = 2


def _grid_for(shape: tuple[int, ...]) -> tuple[int, int]:
    """Columns and rows for ~``_TARGET_CELLS`` cells, matching the region's aspect.

    A 1600×190 band gets roughly 32×4 and a full frame roughly 14×9. Cells stay
    close to square in source pixels either way, which is what keeps the
    difference between neighbouring cells meaningful.
    """
    height, width = shape[0], shape[1]
    aspect = max(width / max(height, 1), 1e-6)
    rows = max(1, round(math.sqrt(_TARGET_CELLS / aspect)))
    cols = max(2, round(_TARGET_CELLS / rows))
    return cols, rows


def _to_gray(image: Image) -> Gray:
    if image.ndim == 3:
        gray: Gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray
    return image


def perceptual_hash(image: Image) -> str:
    """Difference hash of a region: ``"<cols>x<rows>:<hex>"``.

    Difference hashing rather than average hashing: it responds to *gradients*
    between adjacent cells, which is what distinguishes one row of chrome labels
    from another, and it is largely indifferent to the overall brightness shift
    that moving a camera introduces.

    ``INTER_AREA`` for the downscale, deliberately. It averages every source pixel
    in a cell, so per-pixel sensor noise falls by the square root of the cell area
    — which is the difference between a stable hash and one that flips bits on a
    static screen. Interpolating filters sample instead of average and ring on the
    extreme squash a title band needs.

    Each adjacent cell pair yields two bits — brighter, darker — so that a pair
    flatter than the noise floor sets neither and reads as flat on every frame
    instead of picking a direction at random.

    The grid is part of the string: two hashes taken at different shapes are not
    comparable, and a silent comparison between them would read as "different
    screen" for a reason that has nothing to do with the pixels.
    """
    if image.size == 0 or min(image.shape[0], image.shape[1]) < _MIN_SIDE:
        return ""
    gray = _to_gray(image)
    cols, rows = _grid_for(gray.shape)
    small = cv2.resize(gray, (cols + 1, rows), interpolation=cv2.INTER_AREA).astype(np.int16)
    delta = small[:, 1:] - small[:, :-1]
    bits = np.concatenate(
        [(delta > _FLAT_EPSILON).flatten(), (delta < -_FLAT_EPSILON).flatten()]
    )
    packed = np.packbits(bits)
    return f"{cols}x{rows}:{packed.tobytes().hex()}"


def hamming_distance(left: str, right: str) -> int:
    """Bit distance between two hashes, scaled to ``MAX_DISTANCE``.

    An empty or mismatched hash means a region that could not be measured. That is
    not zero distance — it is no measurement — so it returns the maximum, which
    reads downstream as "assume this is a different screen". Wrongly keeping a
    frame costs a duplicate row in the catalogue; wrongly dropping one loses a
    screen silently, and only one of those is recoverable by a reviewer.
    """
    if not left or not right:
        return MAX_DISTANCE
    left_grid, _, left_hex = left.partition(":")
    right_grid, _, right_hex = right.partition(":")
    if left_grid != right_grid or len(left_hex) != len(right_hex):
        return MAX_DISTANCE
    try:
        left_bytes = bytes.fromhex(left_hex)
        right_bytes = bytes.fromhex(right_hex)
    except ValueError:
        return MAX_DISTANCE

    differing = np.unpackbits(
        np.frombuffer(left_bytes, dtype=np.uint8) ^ np.frombuffer(right_bytes, dtype=np.uint8)
    )
    total_bits = _bit_count(left_grid, len(differing))
    if total_bits <= 0:
        return MAX_DISTANCE
    raw = int(differing[:total_bits].sum())
    return round(MAX_DISTANCE * raw / total_bits)


def _bit_count(grid: str, available: int) -> int:
    """Bits the grid actually carries, ignoring packbits' padding.

    Two per cell pair — one for brighter, one for darker.
    """
    cols_text, _, rows_text = grid.partition("x")
    try:
        return min(2 * int(cols_text) * int(rows_text), available)
    except ValueError:
        return 0


def combined_distance(*, band: int, full_frame: int, full_frame_weight: float) -> float:
    """Blend the band distance with the weaker full-frame signal.

    The band is primary because it is what names a screen. The full frame is
    secondary and weighted below 1 because on handheld footage it always carries
    some residual movement — at weight 1 it would dominate and every frame would
    look new, which is the inherited failure this stage exists to avoid.
    """
    return round(band + full_frame_weight * full_frame, 4)


def frame_difference_ratio(left: Image, right: Image) -> float:
    """Fraction of pixels that differ appreciably. Diagnostic, not a decision.

    Kept because it is the measure the inherited pipeline used, and having it
    available makes it possible to show *why* that measure fails on this footage
    rather than asserting it.
    """
    if left.shape != right.shape or left.size == 0:
        return 1.0
    a = _to_gray(left)
    b = _to_gray(right)
    delta = cv2.absdiff(a, b)
    changed = int(np.count_nonzero(delta > 16))
    return round(changed / float(delta.size), 4)
