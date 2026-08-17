"""The Anthropic client, the response cache, and nothing else.

Stage 06 is the only stage allowed to call a model, and this is the only module
that does (DEC-008).

**Responses are cached, and the key covers the whole request.** The design named
``(montage_hash, prompt_version, model)``; this implementation hashes the rendered
prompt text as well, because OCR hints are part of the request and change when
stage 05 is re-tuned. A key that ignores them would replay an answer produced from
different inputs — the same silent-staleness failure the versioned prompt table
exists to prevent.

**A refusal is never cached.** It is not a reading of the screen, and caching one
would make a transient policy outcome permanent for that montage.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from reframe.model import prompts
from reframe.model.schema import FrameReading, MontageReading, ScreenReading

# Enough for a full sheet of structured entries without streaming. The SDK refuses
# non-streaming requests it expects to outlive the HTTP timeout, and 16k sits well
# inside that; a sheet of 20 short records needs a fraction of it.
_MAX_TOKENS: Final = 16000
_MEDIA_TYPE: Final = "image/jpeg"


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


@dataclass(frozen=True)
class ModelSettings:
    model: str
    prompt_version: int


@dataclass(frozen=True)
class Reading:
    """A response, and whether it came from the cache."""

    screens: list[ScreenReading]
    cached: bool


class IdentifyClient:
    """Reads montages and full frames. Caches by rendered request."""

    def __init__(self, settings: ModelSettings, cache_dir: Path) -> None:
        self._settings = settings
        self._cache_dir = cache_dir / "identify"
        self._client: object | None = None

    # ---- public API -----------------------------------------------------
    def read_montage(self, *, payload: bytes, digest: str, strip_count: int, hints: str) -> Reading:
        user_prompt = prompts.montage_prompt(
            self._settings.prompt_version, strip_count=strip_count, hints=hints
        )
        cached = self._load(digest, user_prompt)
        if cached is not None:
            return Reading(screens=MontageReading.model_validate(cached).screens, cached=True)

        reading = self._request(payload, user_prompt, MontageReading)
        self._store(digest, user_prompt, reading.model_dump(mode="json"))
        return Reading(screens=reading.screens, cached=False)

    def read_frame(self, *, payload: bytes, digest: str, frame_id: str, hints: str) -> Reading:
        user_prompt = prompts.frame_prompt(
            self._settings.prompt_version, frame_id=frame_id, hints=hints
        )
        cached = self._load(digest, user_prompt)
        if cached is not None:
            return Reading(screens=[FrameReading.model_validate(cached).screen], cached=True)

        reading = self._request(payload, user_prompt, FrameReading)
        self._store(digest, user_prompt, reading.model_dump(mode="json"))
        return Reading(screens=[reading.screen], cached=False)

    # ---- the call -------------------------------------------------------
    def _request[T: MontageReading | FrameReading](
        self, payload: bytes, user_prompt: str, output_format: type[T]
    ) -> T:
        client = self._ensure_client()
        try:
            response = client.messages.parse(  # type: ignore[attr-defined]
                model=self._settings.model,
                max_tokens=_MAX_TOKENS,
                system=prompts.system_prompt(self._settings.prompt_version),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": _MEDIA_TYPE,
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

        # Check the stop reason before the content: on a refusal the content is
        # empty or partial, and indexing into it would report a policy outcome as
        # an unreadable screen.
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

    def _ensure_client(self) -> object:
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

    # ---- cache ----------------------------------------------------------
    def cache_key(self, digest: str, user_prompt: str) -> str:
        """``(image, prompt text, prompt version, model)`` — everything that was sent."""
        material = "\n".join(
            [
                digest,
                str(self._settings.prompt_version),
                self._settings.model,
                prompts.system_prompt(self._settings.prompt_version),
                user_prompt,
            ]
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def _path(self, digest: str, user_prompt: str) -> Path:
        return self._cache_dir / f"{self.cache_key(digest, user_prompt)}.json"

    def _load(self, digest: str, user_prompt: str) -> dict[str, object] | None:
        path = self._path(digest, user_prompt)
        if not path.exists():
            return None
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # A corrupt cache entry is not worth failing a run over; re-asking the
            # model is always safe, and the bad file gets overwritten.
            return None
        return loaded if isinstance(loaded, dict) else None

    def _store(self, digest: str, user_prompt: str, payload: dict[str, object]) -> None:
        path = self._path(digest, user_prompt)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
