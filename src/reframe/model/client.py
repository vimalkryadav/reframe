"""Prompt selection, the response cache, and provider choice. No provider code.

Stage 06 is the only stage allowed to call a model (DEC-008); the call itself
lives in a backend behind :class:`~reframe.model.backend.ModelBackend`, so
everything here is true whichever provider is configured.

**Responses are cached, and the key covers the whole request.** The design named
``(montage_hash, prompt_version, model)``; this implementation hashes the rendered
prompt text as well, because OCR hints are part of the request and change when
stage 05 is re-tuned. A key that ignores them would replay an answer produced from
different inputs — the same silent-staleness failure the versioned prompt table
exists to prevent. The key also carries the **provider**, not just the model name,
so switching providers cannot serve the other one's answers under a new label.

**A refusal is never cached.** It is not a reading of the screen, and caching one
would make a transient policy outcome permanent for that montage.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from reframe.model import prompts
from reframe.model.backend import ModelBackend, ModelError
from reframe.model.schema import FrameReading, MontageReading, ScreenReading

# Enough for a full sheet of structured entries without streaming. The SDKs refuse
# non-streaming requests they expect to outlive the HTTP timeout, and 16k sits well
# inside that; a sheet of 20 short records needs a fraction of it.
_MAX_TOKENS: Final = 16000
_MEDIA_TYPE: Final = "image/jpeg"

Provider = str


@dataclass(frozen=True)
class ModelSettings:
    provider: Provider
    model: str
    prompt_version: int


@dataclass(frozen=True)
class Reading:
    """A response, and whether it came from the cache."""

    screens: list[ScreenReading]
    cached: bool


def build_backend(settings: ModelSettings) -> ModelBackend:
    """The backend named by config.

    Imported inside the branch so a run against one provider never imports the
    other's SDK, and an unknown name fails here with the list of valid ones
    rather than as an attribute error inside a stage.
    """
    if settings.provider == "anthropic":
        from reframe.model.anthropic_backend import AnthropicBackend

        return AnthropicBackend(settings.model)
    if settings.provider == "openai":
        from reframe.model.openai_backend import OpenAIBackend

        return OpenAIBackend(settings.model)
    raise ModelError(
        f"unknown identify.provider {settings.provider!r} — expected 'anthropic' or 'openai'"
    )


class IdentifyClient:
    """Reads montages and full frames. Caches by rendered request."""

    def __init__(
        self,
        settings: ModelSettings,
        cache_dir: Path,
        backend: ModelBackend | None = None,
    ) -> None:
        self._settings = settings
        self._cache_dir = cache_dir / "identify"
        self._backend = backend if backend is not None else build_backend(settings)

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
        return self._backend.request(
            payload=payload,
            media_type=_MEDIA_TYPE,
            system=prompts.system_prompt(self._settings.prompt_version),
            user_prompt=user_prompt,
            output_format=output_format,
            max_tokens=_MAX_TOKENS,
        )

    # ---- cache ----------------------------------------------------------
    def cache_key(self, digest: str, user_prompt: str) -> str:
        """``(image, prompt text, prompt version, provider/model)`` — everything sent."""
        material = "\n".join(
            [
                digest,
                str(self._settings.prompt_version),
                self._backend.label,
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
