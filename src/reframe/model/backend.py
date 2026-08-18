"""The contract every model provider satisfies, and the errors they share.

Stage 06 is the only stage allowed to call a model (DEC-008). *Which* model is a
config choice, so the call itself sits behind a protocol and the caching, prompt
selection and schema live once in ``client.py`` rather than once per provider.

**The two errors below are the whole point of the seam.** Providers disagree
about almost everything in their response shape, but the pipeline only needs to
distinguish three outcomes: a reading, "the model would not", and "the model
could not". A backend's job is to collapse its provider's vocabulary into those
three, and a backend that cannot tell a refusal apart from a failure must raise
:class:`ModelError` rather than guess — an unrecognised refusal reported as a
generic failure is recoverable, but a refusal parsed as an empty reading would
put "screen unreadable" into the catalogue for a screen that is perfectly legible.
"""

from __future__ import annotations

from typing import Protocol

from reframe.model.schema import FrameReading, MontageReading


class ModelError(RuntimeError):
    """The model could not be reached, or returned something unusable."""


class ModelRefusalError(ModelError):
    """The request was declined by policy.

    Surfaced rather than retried on another model: this pipeline's answer to "the
    model would not read this" is the same as its answer to "the model could not
    read this" — escalate the timestamp to a human. Quietly substituting a
    different model would put an unlabelled second opinion into the catalogue.
    """

    def __init__(self, category: str | None) -> None:
        self.category = category
        super().__init__(f"the model declined to answer (category: {category or 'unspecified'})")


class ModelBackend(Protocol):
    """One provider's call, reduced to: image plus prompts in, schema out."""

    @property
    def label(self) -> str:
        """``provider/model``. Recorded in the manifest and hashed into the cache
        key, so a run cannot silently replay another provider's answers."""
        ...

    def request[T: MontageReading | FrameReading](
        self,
        *,
        payload: bytes,
        media_type: str,
        system: str,
        user_prompt: str,
        output_format: type[T],
        max_tokens: int,
    ) -> T:
        """Send one image and return the parsed structure.

        Raises :class:`ModelRefusalError` on a policy decline and
        :class:`ModelError` on anything else, including a response that parsed to
        nothing. Never returns a partially-filled result.
        """
        ...
