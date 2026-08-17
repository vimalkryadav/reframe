"""Label normalisation and similarity, shared by confidence scoring and matching.

One implementation, because a screen name has to compare the same way in stage 06
(does the model agree with OCR?) and stage 07 (does it match the inventory?). Two
normalisers that drift apart would put a screen above the fuzzy threshold in one
stage and below it in the other, and the manifest would contain both answers.
"""

from __future__ import annotations

import re
import unicodedata

from rapidfuzz import fuzz

_PUNCTUATION = re.compile(r"[^\w\s]+", re.UNICODE)
_WHITESPACE = re.compile(r"\s+")


def normalise_label(value: str) -> str:
    """Case-fold, strip accents and punctuation, collapse whitespace.

    Punctuation goes because OCR invents and drops it freely on this footage —
    an em dash read as two hyphens should not make two readings of the same title
    look like different screens. Word content is left alone: dropping a word would
    conflate genuinely different screens.
    """
    decomposed = unicodedata.normalize("NFKD", value)
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    without_punctuation = _PUNCTUATION.sub(" ", stripped)
    return _WHITESPACE.sub(" ", without_punctuation).strip().casefold()


def similarity(left: str, right: str) -> float:
    """Normalised similarity in [0, 1]; 0.0 if either side is empty.

    ``token_set_ratio`` rather than plain edit distance: OCR on chrome bands adds
    and drops whole words — a session name bleeding into the title, a tab label
    clipped off — and token-set comparison survives that while still punishing a
    genuinely different name.
    """
    a = normalise_label(left)
    b = normalise_label(right)
    if not a or not b:
        return 0.0
    return round(float(fuzz.token_set_ratio(a, b)) / 100.0, 4)
