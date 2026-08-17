"""Perspective transform to a canonical size.

Everything downstream — dedupe, OCR, the model — assumes flat, aligned,
identically-sized frames. This is the module that makes that true, and the reason
``rectify.canonical_size`` is fixed per video: ``dedupe.band_rect`` and the OCR
regions are expressed in these coordinates, so they only mean anything if the
canvas never changes size mid-run.
"""

from __future__ import annotations

import cv2
import numpy as np

from reframe.vision import Image, Point


def canonical_corners(size: tuple[int, int]) -> np.ndarray:
    """Destination corners, clockwise from top-left, for a canvas of ``size``."""
    width, height = size
    return np.array(
        [(0.0, 0.0), (width - 1.0, 0.0), (width - 1.0, height - 1.0), (0.0, height - 1.0)],
        dtype=np.float32,
    )


def warp_to_canonical(
    image: Image, corners: tuple[Point, Point, Point, Point], size: tuple[int, int]
) -> Image:
    """Warp the quadrilateral ``corners`` onto a ``size`` canvas.

    Cubic interpolation: the labels this pipeline exists to read are a few pixels
    tall, and nearest/linear resampling of small text is the difference between an
    OCR hint and noise.
    """
    source = np.array(corners, dtype=np.float32)
    transform = cv2.getPerspectiveTransform(source, canonical_corners(size))
    warped: Image = cv2.warpPerspective(
        image,
        transform,
        size,
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return warped


def crop(image: Image, rect: tuple[int, int, int, int]) -> Image:
    """Crop ``[x, y, w, h]``, clamped to the image.

    Clamped rather than validated: a band_rect that overhangs the canvas by a few
    pixels should crop what exists, not abort a 900-frame run. A rect entirely
    outside the image returns an empty array, and callers treat that as no data
    rather than as a blank band.
    """
    x, y, width, height = rect
    top = max(y, 0)
    left = max(x, 0)
    bottom = min(y + height, image.shape[0])
    right = min(x + width, image.shape[1])
    if bottom <= top or right <= left:
        return image[0:0, 0:0]
    region: Image = image[top:bottom, left:right]
    return region
