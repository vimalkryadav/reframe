"""Screen-corner detection and temporal smoothing.

The screen is a bright, high-contrast quadrilateral against a darker room, and
that assumption is the whole detector. So confidence is measured *as* that
assumption: how solidly the contour fills its own quad, and how much brighter the
inside is than the outside. When the room is bright, the screen is dark, or the
"screen" found is actually the whole frame, both terms collapse and the detection
is correctly reported as weak rather than confidently wrong (DEC-006).

Nothing here decides what to do about a weak detection — that is stage 02's job.
This module reports.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise
from typing import Final

import cv2
import numpy as np

from reframe.vision import Gray, Image, Point

# Implementation constants, not tunables. These describe how the measurement is
# taken, not what counts as good enough — that threshold is
# rectify.min_quad_confidence in config (DEC-014).
_SUBPIX_WINDOW: Final = (11, 11)
_SUBPIX_ZERO_ZONE: Final = (-1, -1)
_SUBPIX_CRITERIA: Final = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.01)
# A contour point this close to the image edge means the screen runs off frame.
_BORDER_TOLERANCE_PX: Final = 2
# Polygon approximation tolerance, as a fraction of the contour's perimeter.
_APPROX_EPSILON_RATIO: Final = 0.02


@dataclass(frozen=True)
class Quad:
    """Four corners, clockwise from top-left, in source-frame pixels."""

    corners: tuple[Point, Point, Point, Point]
    confidence: float
    # True when the quad reaches the edge of the frame, which means the screen is
    # cut off and any crop of it is missing content.
    touches_border: bool = False

    def as_array(self) -> np.ndarray:
        return np.array(self.corners, dtype=np.float32)

    def centre(self) -> Point:
        xs = [x for x, _ in self.corners]
        ys = [y for _, y in self.corners]
        return sum(xs) / 4.0, sum(ys) / 4.0

    def aspect(self) -> float:
        top = _distance(self.corners[0], self.corners[1])
        bottom = _distance(self.corners[3], self.corners[2])
        left = _distance(self.corners[0], self.corners[3])
        right = _distance(self.corners[1], self.corners[2])
        height = (left + right) / 2.0
        if height <= 0:
            return 0.0
        return ((top + bottom) / 2.0) / height

    def area(self) -> float:
        return float(abs(cv2.contourArea(self.as_array())))


def _distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def order_corners(points: np.ndarray) -> tuple[Point, Point, Point, Point]:
    """Order four points clockwise from top-left.

    By angle about the centroid rather than by coordinate sums: a strongly
    keystoned quad can put two corners on the same side of a sum-based split,
    which silently swaps two corners and warps the screen inside out.
    """
    flat = points.reshape(-1, 2).astype(np.float64)
    centre_x = float(flat[:, 0].mean())
    centre_y = float(flat[:, 1].mean())
    ordered = sorted(
        (float(x), float(y)) for x, y in flat
    )  # deterministic starting order for ties
    by_angle = sorted(ordered, key=lambda p: math.atan2(p[1] - centre_y, p[0] - centre_x))
    # atan2 is measured with y growing downwards, so increasing angle already
    # runs clockwise on screen. Rotate so the top-left-most point comes first.
    start = min(range(4), key=lambda i: by_angle[i][0] + by_angle[i][1])
    rotated = by_angle[start:] + by_angle[:start]
    return rotated[0], rotated[1], rotated[2], rotated[3]


def to_gray(image: Image) -> Gray:
    gray: Gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray


def detect_screen_quad(image: Image, *, aspect_bounds: tuple[float, float]) -> Quad | None:
    """Find the screen. Returns None when no plausible quadrilateral exists.

    Otsu's threshold rather than a fixed luminance cutoff, so the detector adapts
    to how bright the room was without a per-video knob for it. ``aspect_bounds``
    is the one thing config decides here: it rejects contours that are plainly
    not a display — a window, a desk edge, a reflection.
    """
    gray = to_gray(image)
    blurred: Gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Close small gaps: glare and cursor artefacts otherwise split the screen
    # region into pieces and the largest contour becomes half a screen.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    closed: Gray = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    height, width = gray.shape[:2]
    best: Quad | None = None
    # Largest first: the screen is the dominant bright region, and a smaller
    # candidate only wins if every larger one is implausible.
    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        quad = _quad_from_contour(contour, gray, aspect_bounds=aspect_bounds)
        if quad is None:
            continue
        if best is None or quad.confidence > best.confidence:
            best = quad
        # A confident, plausible, large candidate is not improved on by anything
        # smaller, and scoring every contour on a 900-frame video is not free.
        if best.confidence > 0.0 and quad.area() > 0.5 * float(width * height):
            break
    return best


def _quad_from_contour(
    contour: np.ndarray, gray: Gray, *, aspect_bounds: tuple[float, float]
) -> Quad | None:
    perimeter = float(cv2.arcLength(contour, True))
    if perimeter <= 0:
        return None
    approx = cv2.approxPolyDP(contour, _APPROX_EPSILON_RATIO * perimeter, True)
    if len(approx) != 4 or not cv2.isContourConvex(approx):
        return None

    corners = order_corners(_refine(approx, gray))
    candidate = Quad(corners=corners, confidence=0.0)
    quad_area = candidate.area()
    if quad_area <= 0:
        return None

    low, high = aspect_bounds
    if not low <= candidate.aspect() <= high:
        return None

    solidity = min(float(cv2.contourArea(contour)) / quad_area, 1.0)
    confidence = solidity * _inside_outside_contrast(gray, candidate)
    return Quad(
        corners=corners,
        confidence=round(confidence, 4),
        touches_border=_touches_border(corners, gray.shape[1], gray.shape[0]),
    )


def _refine(approx: np.ndarray, gray: Gray) -> np.ndarray:
    """Sub-pixel corner refinement. Falls back to the integer corners if OpenCV
    declines — a slightly coarse quad is fine, a crash on one frame is not."""
    points = approx.reshape(-1, 2).astype(np.float32)
    try:
        cv2.cornerSubPix(gray, points, _SUBPIX_WINDOW, _SUBPIX_ZERO_ZONE, _SUBPIX_CRITERIA)
    except cv2.error:
        return approx.reshape(-1, 2).astype(np.float32)
    return points


def _inside_outside_contrast(gray: Gray, quad: Quad) -> float:
    """How much brighter the quad is than everything around it, in [0, 1].

    This is the detector's own assumption, measured. A quad that swallowed the
    whole frame has no outside to be brighter than, so it scores ~0 — which is
    exactly the outcome wanted, since such a "detection" is a thresholding
    failure rather than a screen.
    """
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.fillConvexPoly(mask, quad.as_array().astype(np.int32), 255)
    inside_count = int(np.count_nonzero(mask))
    outside_count = gray.size - inside_count
    if inside_count == 0 or outside_count == 0:
        return 0.0
    inside_mean = float(gray[mask == 255].mean())
    outside_mean = float(gray[mask == 0].mean())
    return max(0.0, min((inside_mean - outside_mean) / 255.0, 1.0))


def _touches_border(corners: tuple[Point, ...], width: int, height: int) -> bool:
    return any(
        x <= _BORDER_TOLERANCE_PX
        or y <= _BORDER_TOLERANCE_PX
        or x >= width - 1 - _BORDER_TOLERANCE_PX
        or y >= height - 1 - _BORDER_TOLERANCE_PX
        for x, y in corners
    )


def is_plausible_successor(
    previous: Quad, current: Quad, *, frame_diagonal: float, max_jump_fraction: float
) -> bool:
    """Whether a screen could have moved from ``previous`` to ``current``.

    A screen cannot jump. A detection that lands somewhere else entirely found
    something else — a reflection, a second monitor, a bright wall — and trusting
    it produces a confidently rectified crop of the wrong thing.

    The allowed movement is a fraction of the frame diagonal rather than a
    configured pixel count, so it holds at any capture resolution.

    This answers "could the screen have moved there in one sample", not "is the
    screen still where it was". A camera that is genuinely re-aimed fails this
    check and should — see :func:`has_settled` for how re-acquisition happens.
    """
    if frame_diagonal <= 0:
        return True
    moved = _distance(previous.centre(), current.centre())
    return moved <= max_jump_fraction * frame_diagonal


def has_settled(
    candidates: Sequence[Quad], *, frame_diagonal: float, max_jump_fraction: float
) -> bool:
    """Whether a run of rejected detections agrees on a new stable position.

    :func:`is_plausible_successor` compares against the last *accepted* quad, so a
    camera that is genuinely re-aimed desyncs it permanently: every later frame is
    measured against a position the screen has left, and rejection cascades to the
    end of the video however steady the new framing is.

    A screen cannot jump — but a camera can be moved, and the footage after that
    move is as real as the footage before it. Agreement among consecutive rejected
    detections is what separates the two cases: a reflection or a second bright
    object wanders, while a re-aimed camera settles. Requiring the run to be
    mutually consistent means re-acquisition needs evidence, not just persistence.
    """
    if len(candidates) < 2:
        return False
    if frame_diagonal <= 0:
        return True
    budget = max_jump_fraction * frame_diagonal
    return all(
        _distance(a.centre(), b.centre()) <= budget for a, b in pairwise(candidates)
    )


def median_smooth(
    sequence: list[Quad | None], window: int, *, pinned: list[bool] | None = None
) -> list[Quad | None]:
    """Median-filter corner positions across a window of neighbouring frames.

    Per-frame detection alone produces visible wobble; solving once per video
    fails when the framing drifts. The median is the middle path, and it is why
    ``interpolated`` exists as a distinct method in the manifest.

    ``pinned`` frames are returned untouched — manually supplied corners are a
    human's answer and smoothing them towards a bad neighbour would discard it.
    """
    if window <= 1:
        return list(sequence)
    half = window // 2
    smoothed: list[Quad | None] = []
    for index, quad in enumerate(sequence):
        if quad is None or (pinned is not None and pinned[index]):
            smoothed.append(quad)
            continue
        neighbours = [
            other
            for offset in range(-half, half + 1)
            if 0 <= index + offset < len(sequence)
            and (other := sequence[index + offset]) is not None
        ]
        if len(neighbours) < 2:
            smoothed.append(quad)
            continue
        stacked = np.stack([n.as_array() for n in neighbours])
        median = np.median(stacked, axis=0)
        smoothed.append(
            Quad(
                corners=order_corners(median),
                confidence=quad.confidence,
                touches_border=quad.touches_border,
            )
        )
    return smoothed


def interpolate_gaps(
    sequence: list[Quad | None], *, max_span: int
) -> tuple[list[Quad | None], list[bool]]:
    """Fill short runs of missing quads by interpolating between their neighbours.

    Returns the filled sequence and a flag per frame saying whether that frame was
    interpolated, because the manifest has to distinguish a measurement from an
    inference.

    Gaps longer than ``max_span`` are left empty. Interpolating across a long gap
    would invent a screen position for footage nobody looked at — a gap is
    escalated to a human instead.
    """
    filled: list[Quad | None] = list(sequence)
    interpolated = [False] * len(sequence)
    index = 0
    while index < len(sequence):
        if sequence[index] is not None:
            index += 1
            continue
        start = index
        while index < len(sequence) and sequence[index] is None:
            index += 1
        end = index  # first present frame after the gap
        before = filled[start - 1] if start > 0 else None
        after = sequence[end] if end < len(sequence) else None
        gap = end - start
        if before is None or after is None or gap > max_span:
            continue
        for offset in range(gap):
            weight = (offset + 1) / (gap + 1)
            blended = (1.0 - weight) * before.as_array() + weight * after.as_array()
            filled[start + offset] = Quad(
                corners=order_corners(blended),
                # Confidence follows the weaker neighbour: an inference is never
                # better evidence than the measurement it was drawn from.
                confidence=round(min(before.confidence, after.confidence), 4),
                touches_border=before.touches_border or after.touches_border,
            )
            interpolated[start + offset] = True
    return filled, interpolated
