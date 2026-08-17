"""Pure image functions. No pipeline awareness.

Nothing in this package reads a manifest, a config object or a path — every
function takes arrays and numbers and returns arrays and numbers. That is what
lets these be exercised against a folder of fixture frames with no video, no
manifest and no stage anywhere in the picture.

The three aliases below are **documentation, not enforcement**. OpenCV's stubs
describe every return as an array of some numeric dtype, so a stricter alias like
``NDArray[np.uint8]`` could only be sustained by casting at every call — asserting
a fact mypy still could not check. The alias says what a function expects; the
docstring says what happens if it gets something else.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

import cv2
import numpy as np

_Array = np.ndarray[Any, np.dtype[Any]]

# A BGR image as OpenCV hands it over: (h, w, 3), uint8.
Image = _Array
# A single-channel image: (h, w), uint8.
Gray = _Array
# Floating-point working copy, for anything that would clip in uint8.
Field = _Array

Point = tuple[float, float]


class ImageReadError(OSError):
    """A frame on disk could not be decoded.

    Raised rather than skipped. A frame that silently fails to load is a hole in
    the catalogue that nothing downstream can see.
    """


def read_image(path: Path) -> Image:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ImageReadError(f"could not decode {path}")
    loaded: Image = image
    return loaded


# JPEG quality for derived frames. Not a tunable and deliberately not in config:
# these frames feed OCR and a model, and nobody tuning this pipeline ever wants
# them worse. Storage is not a constraint — every set except frames/kept/ is
# gitignored and regenerable.
DERIVED_JPEG_QUALITY: Final = 95


def write_image(path: Path, image: Image, *, quality: int = DERIVED_JPEG_QUALITY) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image, [int(cv2.IMWRITE_JPEG_QUALITY), quality]):
        raise ImageReadError(f"could not write {path}")


__all__ = [
    "DERIVED_JPEG_QUALITY",
    "Field",
    "Gray",
    "Image",
    "ImageReadError",
    "Point",
    "read_image",
    "write_image",
]
