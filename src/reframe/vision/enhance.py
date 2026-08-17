"""Alignment, contrast normalisation, glare suppression, moiré reduction.

Applied to a copy. ``frames/rect/`` stays untouched because every step here trades
away some of the fine detail that makes a small label readable, and which trade is
worth making differs per video — which is why each step is separately switchable
in config.

The bounded-correction rule matters most in ``suppress_glare``: a blown-out
highlight has no recoverable detail, and a filter that appears to recover some is
inventing pixels. Every correction here is multiplicative and clamped.
"""

from __future__ import annotations

from typing import Final

import cv2
import numpy as np

from reframe.vision import Field, Gray, Image

# Implementation constants. The illumination estimate has to be much coarser than
# any real screen content, or flat-fielding starts flattening the UI itself; a
# fraction of the frame width is the scale-free way to say that.
_ILLUMINATION_SIGMA_RATIO: Final = 0.08
# Below this phase-correlation response the estimated shift is noise, and applying
# it would add jitter rather than remove it.
_MIN_ALIGN_RESPONSE: Final = 0.05
# A residual shift larger than this fraction of the frame is not jitter — it is a
# scene change or a detection error, and shifting to match it would be wrong.
_MAX_ALIGN_SHIFT_RATIO: Final = 0.02


def to_gray(image: Image) -> Gray:
    gray: Gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray


def estimate_shift(image: Image, reference: Image) -> tuple[float, float, float]:
    """Sub-pixel translation from ``reference`` to ``image``, with its response.

    Phase correlation, on a Hann window to stop the frame edges dominating. The
    response is returned so the caller can decline a shift it does not believe.
    """
    if image.shape != reference.shape:
        return 0.0, 0.0, 0.0
    current: Field = to_gray(image).astype(np.float32)
    previous: Field = to_gray(reference).astype(np.float32)
    window = cv2.createHanningWindow((current.shape[1], current.shape[0]), cv2.CV_32F)
    (dx, dy), response = cv2.phaseCorrelate(previous, current, window)
    return float(dx), float(dy), float(response)


def align_to(image: Image, reference: Image) -> tuple[Image, tuple[float, float]]:
    """Cancel residual sub-pixel jitter against the previous frame.

    Rectification removes most apparent movement, but corner noise leaves a
    fraction of a pixel of wobble that dedupe would otherwise read as change.

    Each frame is shifted by its own measured offset against its predecessor and
    the offsets are never composed, so a bad estimate on one frame cannot drift
    the rest of the video. A shift that is too large or too weakly supported is
    declined outright and reported as (0, 0).
    """
    dx, dy, response = estimate_shift(image, reference)
    height, width = image.shape[:2]
    limit = _MAX_ALIGN_SHIFT_RATIO * max(width, height)
    if response < _MIN_ALIGN_RESPONSE or abs(dx) > limit or abs(dy) > limit:
        return image, (0.0, 0.0)
    matrix = np.array([[1.0, 0.0, -dx], [0.0, 1.0, -dy]], dtype=np.float32)
    shifted: Image = cv2.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return shifted, (dx, dy)


def apply_clahe(image: Image, *, clip: float, grid: int) -> Image:
    """Local contrast normalisation on the luminance channel only.

    Local, not global: a screen photographed at an angle is unevenly lit across
    the frame, so a global stretch improves one side by making the other worse.

    Chroma is passed through untouched. Nothing in this pipeline reads colour and
    nothing may emit it (DEC-011) — but altering it would still change what a
    reviewer sees in a committed frame, which is not this function's business.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    operator = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid))
    equalised = operator.apply(lightness)
    merged: Image = cv2.cvtColor(cv2.merge((equalised, a_channel, b_channel)), cv2.COLOR_LAB2BGR)
    return merged


def suppress_glare(image: Image, *, max_correction: float) -> Image:
    """Flatten uneven illumination, by a bounded amount.

    Divides the luminance by a heavily blurred estimate of itself, which removes
    the broad bright patch a monitor reflection puts across the frame while
    leaving UI-scale detail alone. The correction factor is clamped to
    ``1 ± max_correction``.

    What this does not do is recover blown-out highlights. Where the sensor
    saturated there is no detail left, and scaling a flat white region only makes
    it a flat grey one — the pixels stay unreadable and the manifest, not this
    filter, is where that gets said.
    """
    if max_correction <= 0:
        return image
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lightness, a_channel, b_channel = cv2.split(lab)
    working: Field = lightness.astype(np.float32)

    sigma = max(_ILLUMINATION_SIGMA_RATIO * image.shape[1], 1.0)
    illumination: Field = cv2.GaussianBlur(working, (0, 0), sigma)
    mean = float(illumination.mean())
    if mean <= 0:
        return image

    factor: Field = np.clip(
        mean / np.maximum(illumination, 1.0), 1.0 - max_correction, 1.0 + max_correction
    ).astype(np.float32)
    corrected = np.clip(working * factor, 0, 255).astype(np.uint8)
    merged: Image = cv2.cvtColor(cv2.merge((corrected, a_channel, b_channel)), cv2.COLOR_LAB2BGR)
    return merged


def reduce_moire(image: Image, *, sigma: float) -> Image:
    """Mild low-pass against the interference pattern of photographing a screen.

    Off by default. It costs exactly the high-frequency detail that small labels
    are made of, so it is worth enabling only when the pattern is measurably
    harming OCR on a particular video.
    """
    if sigma <= 0:
        return image
    blurred: Image = cv2.GaussianBlur(image, (0, 0), sigma)
    return blurred


def band_legibility(band: Image) -> float:
    """How readable a title band is, in [0, 1]. A confidence signal, not a filter.

    Two measures, and the **worse** of the two decides:

    - **ink separation** — the gap between the mean of the ink and the mean of the
      paper, split by Otsu's threshold. This asks whether text stands off its
      background at all, and it is indifferent to how *little* of the band is ink,
      which is the trap both obvious alternatives fall into: a title band is ~4%
      text, so a standard deviation and a 5th-to-95th-percentile range both
      describe the background rather than the text. Measured on a clean band, the
      percentile range even *rose* under Gaussian blur (0.247 → 0.259) while the
      band became unreadable.
    - **sharpness** — variance of the Laplacian, the standard blur measure, and the
      strongest discriminator available here: 1.00 clean against 0.005 at blur
      sigma 3 on the same band.

    Taken as a minimum, not a product. Sub-scores multiplied together compound into
    a low number even when each is individually fine, and a signal reading 0.4 for
    a band OCR lifts at 0.95 confidence makes ``confidence.accept_threshold``
    uninterpretable.

    **Glare over part of a band is not detected, and cannot be.** A blown-out
    region and an empty background are the same pixels: flat and near-white. On the
    fixture, whiting out half a band *raised* ink separation (0.566 → 0.635),
    because pure white lifts the paper mean. Any saturation-counting term that
    caught it would also condemn every frame of a light-themed application. The
    backstops are stage 02's framing signal and the human reading
    ``NEEDS_REVIEW.md`` — not a number invented here.

    Both normalising constants are **provisional**, fitted to synthetic footage
    (clean ink separation 0.57, clean Laplacian variance 470–795). Re-check them
    against the first real video, together with ``confidence.weights``.
    """
    if band.size == 0:
        return 0.0
    gray = to_gray(band) if band.ndim == 3 else band
    working: Field = gray.astype(np.float32)

    threshold, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ink = working[gray <= threshold]
    paper = working[gray > threshold]
    if ink.size == 0 or paper.size == 0:
        # One class is empty: the band is uniform, so there is no text in it.
        return 0.0
    # 0.5 of full range is the separation a cleanly rendered band achieves; Otsu's
    # ink class includes anti-aliased edge pixels, so it never approaches 1.0.
    separation = min(((float(paper.mean()) - float(ink.mean())) / 255.0) / 0.5, 1.0)
    # 500 is the Laplacian variance of comfortably sharp small text.
    sharpness = min(float(cv2.Laplacian(gray, cv2.CV_64F).var()) / 500.0, 1.0)
    return round(max(min(separation, sharpness), 0.0), 4)
