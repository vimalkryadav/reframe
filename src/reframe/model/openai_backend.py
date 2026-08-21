"""The OpenAI backend for stage 06.

Uses the Responses API with ``text_format``, which constrains the reply to the
Pydantic schema in ``schema.py`` the same way the Anthropic backend's
``output_format`` does — so both providers are held to the identical shape and
neither can answer with prose where a null was wanted.

**Refusals arrive differently here and that difference is load-bearing.**
Anthropic reports one on ``stop_reason``; OpenAI returns a ``refusal`` content
part inside the output. Ported naively, the Anthropic check finds no
``stop_reason`` attribute, silently never fires, and a decline is reported as an
unreadable screen — a policy outcome recorded as a fact about the pixels. The
check below therefore reads the output parts, and treats "no parsed output and no
recognisable refusal" as an error rather than an empty reading.
"""

from __future__ import annotations

import base64
from typing import Any, Final

from reframe.model.backend import ModelError, ModelRefusalError
from reframe.model.schema import FrameReading, MontageReading

_PROVIDER: Final = "openai"


class OpenAIBackend:
    """Stage 06 against OpenAI. Constructed lazily so other stages never import
    the SDK, and so a missing key is reported when the model is first needed
    rather than at CLI startup."""

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
        encoded = base64.standard_b64encode(payload).decode("ascii")
        try:
            response = client.responses.parse(
                model=self._model,
                instructions=system,
                max_output_tokens=max_tokens,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": f"data:{media_type};base64,{encoded}",
                                "detail": "high",
                            },
                            {"type": "input_text", "text": user_prompt},
                        ],
                    }
                ],
                text_format=output_format,
            )
        except Exception as exc:
            # A response cut off by the token ceiling surfaces from the SDK as a
            # JSON parse failure, which reads as "the model returned nonsense"
            # when it means "the model ran out of room". Say which, because the
            # two have different fixes and only one of them is a config change.
            if "EOF while parsing" in str(exc):
                raise ModelError(
                    f"the response was cut off mid-JSON — identify.max_output_tokens "
                    f"({max_tokens}) was not enough for this screen. On a reasoning "
                    f"model that budget covers the reasoning too. ({type(exc).__name__})"
                ) from exc
            raise ModelError(f"{type(exc).__name__}: {exc}") from exc

        # Refusal before content: on a decline the parsed output is absent, and
        # reporting that as "the screen could not be read" would attribute a
        # policy decision to the footage.
        refusal = _refusal_text(response)
        if refusal is not None:
            raise ModelRefusalError(refusal)

        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            # `incomplete` means the token budget ran out mid-structure. Naming
            # it separately matters: it is the one failure here that is fixed by
            # a config change rather than by a human looking at the frame.
            status = getattr(response, "status", None)
            detail = getattr(response, "incomplete_details", None)
            raise ModelError(
                "the model returned no structured output — "
                f"status {status!r}"
                + (f", {detail}" if detail is not None else "")
            )
        if not isinstance(parsed, output_format):
            raise ModelError(f"expected {output_format.__name__}, got {type(parsed).__name__}")
        return parsed

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - declared dependency
            raise ModelError("the openai package is not installed") from exc
        try:
            self._client = OpenAI()
        except Exception as exc:
            raise ModelError(
                "could not construct an OpenAI client — set OPENAI_API_KEY.\n"
                f"  {type(exc).__name__}: {exc}"
            ) from exc
        return self._client


def _refusal_text(response: object) -> str | None:
    """The refusal string, if the model declined.

    Walks the output parts rather than trusting a single field: the Responses API
    nests content inside output items, and a refusal is a part type alongside
    text rather than a flag on the response.
    """
    for item in getattr(response, "output", None) or []:
        for part in getattr(item, "content", None) or []:
            if getattr(part, "type", None) == "refusal":
                text = getattr(part, "refusal", None)
                return str(text) if text else "unspecified"
    return None
