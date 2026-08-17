"""OCR of chrome bands. Text and per-word confidence, nothing interpreted.

**On this footage OCR is a hint, not a source of truth.** It feeds the model in
stage 06 and cross-checks the model's answer in ``confidence.py``; it never decides
a screen's identity alone. The consuming project's existing catalogue already marks
phone-of-monitor reads with ``(?)`` for exactly this reason.

Data grids are never read here (DEC-011). An OCR error and a fabrication are
indistinguishable downstream, and a wrong cell value in a build queue is worse than
an empty one because nobody goes back to check it.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Final

import cv2
import numpy as np
import pytesseract

from reframe.vision import Gray, Image

# Implementation constants. Tesseract wants text roughly this tall; a canonical
# title band is half that, and upscaling before recognition is worth more than any
# amount of threshold tuning after it.
_TARGET_LINE_HEIGHT_PX: Final = 96
_MAX_UPSCALE: Final = 4.0
# Tesseract reports confidence 0–100, and -1 for boxes holding no word at all.
_NO_WORD_CONFIDENCE: Final = -1.0


class OcrUnavailableError(RuntimeError):
    """The tesseract binary is missing or unusable."""


@dataclass(frozen=True)
class Word:
    """One recognised word, with where it was and how sure tesseract was."""

    text: str
    confidence: float  # 0.0–1.0
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width


def prepare_for_ocr(region: Image) -> Gray:
    """Upscale and binarise a chrome band.

    Two steps, both about the same problem: at canonical size a title is around 30
    pixels tall and tesseract is trained on text roughly three times that. Cubic
    upscaling recovers the difference, and Otsu binarisation removes the soft
    edges that a camera and two resamplings leave behind.

    Nothing here is bounded by a configured threshold because nothing here makes a
    decision — a badly prepared band produces low-confidence words, which the
    caller can see.
    """
    gray: Gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if region.ndim == 3 else region
    height = gray.shape[0]
    if height <= 0:
        return gray
    scale = min(max(_TARGET_LINE_HEIGHT_PX / height, 1.0), _MAX_UPSCALE)
    if scale > 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    result: Gray = binary
    return result


def read_words(region: Image, *, psm: int) -> list[Word]:
    """Recognise a band and return every word tesseract found.

    Every word, including ones below any confidence bar. Filtering is the caller's
    decision and the manifest records the unfiltered result, so that a screen that
    went to review can be explained by what was actually read.
    """
    if region.size == 0:
        return []
    prepared = prepare_for_ocr(region)
    try:
        data = pytesseract.image_to_data(
            prepared,
            config=f"--psm {psm}",
            output_type=pytesseract.Output.DICT,
        )
    except pytesseract.TesseractNotFoundError as exc:
        raise OcrUnavailableError(
            "tesseract is not installed or not on PATH — stage 05 cannot read chrome bands.\n"
            "  macOS:  brew install tesseract\n"
            "  linux:  apt install tesseract-ocr"
        ) from exc

    words: list[Word] = []
    for index, raw_text in enumerate(data.get("text", [])):
        text = str(raw_text).strip()
        if not text:
            continue
        confidence = float(data["conf"][index])
        if confidence == _NO_WORD_CONFIDENCE:
            continue
        words.append(
            Word(
                text=text,
                confidence=round(max(confidence, 0.0) / 100.0, 4),
                left=int(data["left"][index]),
                top=int(data["top"][index]),
                width=int(data["width"][index]),
                height=int(data["height"][index]),
            )
        )
    return words


def join_text(words: list[Word], *, min_confidence: float) -> tuple[str | None, float | None]:
    """Join confident words into one string, with their mean confidence.

    Returns ``(None, None)`` when nothing cleared the bar. That is the point:
    missing is a valid state and is always more useful than a plausible guess
    assembled from words the pixels do not support.
    """
    confident = [word for word in words if word.confidence >= min_confidence]
    if not confident:
        return None, None
    confident.sort(key=lambda word: word.left)
    text = " ".join(word.text for word in confident)
    mean = statistics.fmean(word.confidence for word in confident)
    return text, round(mean, 4)


def group_by_gaps(words: list[Word], *, min_confidence: float) -> list[str]:
    """Split a line of words into labels, using the gaps between them.

    A tab strip reads as one line but is several labels, and one of them may well
    be three words long. The split is on gaps wider than the text is tall: a space
    inside a label is a fraction of the line height, whereas the padding between
    two tabs is at least as wide as the text. That rule needs no threshold in
    config and holds at any resolution, because it is expressed in units of the
    text itself.
    """
    confident = sorted(
        (word for word in words if word.confidence >= min_confidence),
        key=lambda word: word.left,
    )
    if not confident:
        return []

    line_height = statistics.median(word.height for word in confident)
    groups: list[list[Word]] = [[confident[0]]]
    for word in confident[1:]:
        gap = word.left - groups[-1][-1].right
        if gap > line_height:
            groups.append([word])
        else:
            groups[-1].append(word)
    return [" ".join(word.text for word in group) for group in groups]


def region_contrast(region: Image) -> float:
    """Normalised spread of a band, in [0, 1]. Diagnostic for the review list."""
    if region.size == 0:
        return 0.0
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY) if region.ndim == 3 else region
    return round(min(float(np.asarray(gray, dtype=np.float32).std()) / 64.0, 1.0), 4)
