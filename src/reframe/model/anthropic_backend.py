"""The Anthropic backend for stage 06.

Uses ``messages.parse`` with ``output_format``, which constrains the reply to the
Pydantic schema in ``schema.py``.

A refusal arrives as ``stop_reason == "refusal"`` with a category in
``stop_details``, and is checked before the content is read: on a decline the
content is empty or partial, and indexing into it would report a policy outcome
as an unreadable screen.
"""

from __future__ import annotations

import base64
from typing import Any, Final

from reframe.model.backend import ModelError, ModelRefusalError
from reframe.model.schema import FrameReading, MontageReading

_PROVIDER: Final = "anthropic"


class AnthropicBackend:
    """Stage 06 against Anthropic. Constructed lazily so other stages never
    import the SDK, and so a missing credential is reported when the model is
    first needed rather than at CLI startup."""

    def __init__(self, model: str) -> None:
        self._model = model
        self._client: Any | None = None

    @property
    def label(self) -> str:
        return f"{_PROVIDER}/{self._model}"

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
        client = self._ensure_client()
        try:
            response = client.messages.parse(
                model=self._model,
                max_tokens=max_tokens,
                system=system,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": base64.standard_b64encode(payload).decode("ascii"),
                                },
                            },
                            {"type": "text", "text": user_prompt},
                        ],
                    }
                ],
                output_format=output_format,
            )
        except Exception as exc:  # SDK raises a family of typed errors
            raise ModelError(f"{type(exc).__name__}: {exc}") from exc

        if getattr(response, "stop_reason", None) == "refusal":
            details = getattr(response, "stop_details", None)
            raise ModelRefusalError(getattr(details, "category", None))

        parsed = getattr(response, "parsed_output", None)
        if parsed is None:
            raise ModelError(
                "the model returned no structured output — "
                f"stop_reason was {getattr(response, 'stop_reason', 'unknown')!r}"
            )
        if not isinstance(parsed, output_format):
            raise ModelError(f"expected {output_format.__name__}, got {type(parsed).__name__}")
        return parsed

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover - declared dependency
            raise ModelError("the anthropic package is not installed") from exc
        try:
            self._client = Anthropic()
        except Exception as exc:
            raise ModelError(
                "could not construct an Anthropic client — set ANTHROPIC_API_KEY, or "
                "run `ant auth login` to store a credential profile.\n"
                f"  {type(exc).__name__}: {exc}"
            ) from exc
        return self._client
