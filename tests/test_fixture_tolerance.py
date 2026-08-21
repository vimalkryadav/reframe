"""Matching a fixture across a change of sample rate.

A screen occupies a span; the pipeline records one instant inside it. Re-sampling
moves that instant, so the comparison has to tolerate the move — and the amount
it must tolerate is set by the *coarser* of the two rates, not the run's.
"""

from __future__ import annotations

from reframe.fixtures import Fixture, FixtureScreen, compare
from reframe.manifest import IdentityRecord, Manifest, ScreenRecord, VideoInfo


def video() -> VideoInfo:
    return VideoInfo(
        slug="t", source_path="/x.mp4", sha256="d", duration_s=10.0,
        width=1920, height=1080, fps=30.0, rotation=0, codec="h264",
    )


def manifest_at(t_ms: int, name: str) -> Manifest:
    m = Manifest(config_hash="h", video=video())
    m.screens = [
        ScreenRecord(
            id="s_000", representative_frame="f_000000", frame_ids=["f_000000"],
            t_ms_start=t_ms, t_ms_end=t_ms,
            identity=IdentityRecord(name=name),
        )
    ]
    return m


def fixture_at(t: str, name: str, sample_fps: float | None) -> Fixture:
    return Fixture(
        slug="t", inventory_commit=None, sample_fps=sample_fps,
        screens=[FixtureScreen(t=t, name=name)],
    )


def regressions(findings: list) -> list:
    return [f for f in findings if f.status == "regression"]


class TestToleranceAcrossSampleRates:
    def test_a_one_second_shift_matches_when_the_fixture_was_slower(self) -> None:
        """The case that motivated this: a 1 fps fixture against a 2 fps run.

        Re-sampling moved the representative instant by a second. The screen is
        the same screen, and at the coarser rate's interval it is within
        tolerance.
        """
        findings = compare(
            fixture_at("00:12", "Project Dashboard", sample_fps=1.0),
            manifest_at(11_000, "Project Dashboard"),
            fps=2.0,
        )
        assert regressions(findings) == []

    def test_the_same_shift_fails_without_the_recorded_rate(self) -> None:
        """Documents why `sample_fps` had to be carried.

        With no rate on the fixture the run's own is assumed, the tolerance
        halves, and a screen that merely moved reads as a regression.
        """
        findings = compare(
            fixture_at("00:14", "Project Dashboard", sample_fps=None),
            manifest_at(11_000, "Project Dashboard"),
            fps=2.0,
        )
        assert regressions(findings), "expected the narrow tolerance to reject it"

    def test_a_genuine_rename_is_still_caught(self) -> None:
        """Widening the tolerance must not blunt the thing the gate is for."""
        findings = compare(
            fixture_at("00:12", "Task Admin", sample_fps=1.0),
            manifest_at(11_000, "Task"),
            fps=2.0,
        )
        assert [f.message for f in regressions(findings)], "a renamed screen must regress"

    def test_a_distant_screen_is_not_swept_into_a_match(self) -> None:
        """Tolerance is two intervals, not open-ended."""
        findings = compare(
            fixture_at("00:12", "Project Dashboard", sample_fps=1.0),
            manifest_at(30_000, "Project Dashboard"),
            fps=2.0,
        )
        assert regressions(findings), "12s away is a different sighting"

    def test_same_rate_behaviour_is_unchanged(self) -> None:
        """The common case — fixture and run at one rate — must not shift."""
        findings = compare(
            fixture_at("00:12", "Project Dashboard", sample_fps=1.0),
            manifest_at(13_000, "Project Dashboard"),
            fps=1.0,
        )
        assert regressions(findings) == []
