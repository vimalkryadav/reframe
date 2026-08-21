"""Provider selection and cache-key behaviour for stage 06.

No network: a stub backend stands in for a provider, because what these tests
are about is the seam — that the caching layer is provider-agnostic, and that a
cache entry can never be served to a different provider than produced it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from reframe.model.backend import ModelError
from reframe.model.client import IdentifyClient, ModelSettings, build_backend
from reframe.model.schema import FrameReading, MontageReading, ScreenReading


class StubBackend:
    """Counts calls so a cache hit is distinguishable from a second request."""

    def __init__(self, label: str = "stub/model-1") -> None:
        self._label = label
        self.calls = 0

    @property
    def label(self) -> str:
        return self._label

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
        self.calls += 1
        screen = ScreenReading(
            frame_id="f_000001",
            name="Some Screen",
            record=None,
            module=None,
            tabs=[],
            section=None,
            dialog=None,
            structure=None,
            unreadable=None,
        )
        if output_format is MontageReading:
            return MontageReading(screens=[screen])  # type: ignore[return-value]
        return FrameReading(screen=screen)  # type: ignore[return-value]


def settings(provider: str = "openai", model: str = "m") -> ModelSettings:
    return ModelSettings(
        provider=provider, model=model, prompt_version=1, max_output_tokens=48000
    )


class TestBuildBackend:
    @pytest.mark.parametrize(
        ("provider", "expected"), [("anthropic", "anthropic/"), ("openai", "openai/")]
    )
    def test_known_providers_resolve(self, provider: str, expected: str) -> None:
        backend = build_backend(settings(provider=provider, model="some-model"))
        assert backend.label.startswith(expected)

    def test_unknown_provider_names_the_valid_ones(self) -> None:
        with pytest.raises(ModelError, match=r"anthropic.*openai"):
            build_backend(settings(provider="nope"))

    def test_the_label_carries_provider_and_model(self) -> None:
        """The manifest and the cache key both read this, so it must identify
        the provider and not just the model name."""
        assert build_backend(settings("openai", "gpt-4o")).label == "openai/gpt-4o"


class TestCache:
    def test_a_second_identical_read_is_served_from_cache(self, tmp_path: Path) -> None:
        backend = StubBackend()
        client = IdentifyClient(settings(), tmp_path, backend)

        first = client.read_montage(payload=b"x", digest="d1", strip_count=2, hints="")
        second = client.read_montage(payload=b"x", digest="d1", strip_count=2, hints="")

        assert (first.cached, second.cached) == (False, True)
        assert backend.calls == 1

    def test_changed_hints_are_not_a_cache_hit(self, tmp_path: Path) -> None:
        """OCR hints are part of the request, so re-tuning stage 05 must not
        replay an answer produced from the old hints."""
        backend = StubBackend()
        client = IdentifyClient(settings(), tmp_path, backend)

        client.read_montage(payload=b"x", digest="d1", strip_count=2, hints="a")
        client.read_montage(payload=b"x", digest="d1", strip_count=2, hints="b")

        assert backend.calls == 2

    def test_a_different_provider_cannot_read_the_cache(self, tmp_path: Path) -> None:
        """The whole point of putting the provider in the key: switching vendors
        must re-ask, not serve the previous vendor's reading under a new label."""
        first = StubBackend("openai/gpt-4o")
        second = StubBackend("anthropic/claude-opus-5")

        IdentifyClient(settings(), tmp_path, first).read_montage(
            payload=b"x", digest="d1", strip_count=2, hints=""
        )
        reading = IdentifyClient(settings(), tmp_path, second).read_montage(
            payload=b"x", digest="d1", strip_count=2, hints=""
        )

        assert reading.cached is False
        assert second.calls == 1
