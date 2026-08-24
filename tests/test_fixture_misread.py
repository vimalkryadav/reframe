"""A read the fixture already records as wrong is a standing defect, not a regression.

Without this, a fixture that carries a human correction reports a failure on every
run forever, and `reframe verify`'s gate can never be satisfied — which makes it
noise rather than a gate (DEC-030).
"""

from __future__ import annotations

from reframe.fixtures import Fixture, compare
from reframe.manifest import IdentityRecord, Manifest, ScreenRecord, VideoInfo


def _manifest(name: str | None) -> Manifest:
    video = VideoInfo(
        slug="v",
        source_path="/dev/null",
        sha256="0" * 64,
        duration_s=10.0,
        width=1920,
        height=1080,
        fps=30.0,
        rotation=0,
        codec="h264",
    )
    screen = ScreenRecord(
        id="s_000",
        t_ms_start=1000,
        t_ms_end=1000,
        representative_frame="f_000001",
        frame_ids=["f_000001"],
        identity=IdentityRecord(name=name),
    )
    return Manifest(config_hash="sha256:0", video=video, screens=[screen])


def _fixture(**screen: object) -> Fixture:
    return Fixture.model_validate({"slug": "v", "screens": [{"t": "00:01", **screen}]})


def test_recorded_misread_is_not_a_regression() -> None:
    fixture = _fixture(name="NDC Admin", known_misread="Package")
    findings = compare(fixture, _manifest("Package"), fps=1.0)
    statuses = {f.status for f in findings}
    assert "misread" in statuses
    assert "regression" not in statuses
    assert not any(f.is_failure for f in findings)


def test_misread_still_reports_the_truth() -> None:
    fixture = _fixture(name="NDC Admin", known_misread="Package")
    (finding,) = [f for f in compare(fixture, _manifest("Package"), fps=1.0) if f.status == "misread"]
    assert "Package" in finding.message and "NDC Admin" in finding.message


def test_a_different_wrong_name_is_still_a_regression() -> None:
    """The field excuses ONE known value, not any wrong value."""
    fixture = _fixture(name="NDC Admin", known_misread="Package")
    findings = compare(fixture, _manifest("Something Else"), fps=1.0)
    regressions = [f for f in findings if f.status == "regression"]
    assert regressions and "recorded misread was 'Package'" in regressions[0].message


def test_the_model_getting_it_right_is_not_reported_at_all() -> None:
    """A fixed defect should go quiet, not keep announcing itself."""
    fixture = _fixture(name="NDC Admin", known_misread="Package")
    findings = compare(fixture, _manifest("NDC Admin"), fps=1.0)
    assert not [f for f in findings if f.status in ("misread", "regression")]


def test_without_the_field_a_wrong_name_still_fails() -> None:
    fixture = _fixture(name="NDC Admin")
    findings = compare(fixture, _manifest("Package"), fps=1.0)
    assert any(f.status == "regression" and f.is_failure for f in findings)


def test_recorded_unread_is_not_a_regression() -> None:
    """`unread` is `known_misread`'s sibling: an ABSENT read rather than a wrong one."""
    fixture = _fixture(name="Launching Adjust Par Levels", unread=True)
    findings = compare(fixture, _manifest(None), fps=1.0)
    assert [f.status for f in findings if f.status in ("misread", "regression")] == ["misread"]
    assert not any(f.is_failure for f in findings)


def test_unread_reports_the_human_read_truth() -> None:
    fixture = _fixture(name="Launching Adjust Par Levels", unread=True)
    (f,) = [x for x in compare(fixture, _manifest(None), fps=1.0) if x.status == "misread"]
    assert "still unread" in f.message and "Launching Adjust Par Levels" in f.message


def test_unread_entry_that_starts_reading_a_WRONG_name_is_a_regression() -> None:
    """Progress, but not silent progress — a new wrong name must still surface."""
    fixture = _fixture(name="Launching Adjust Par Levels", unread=True)
    regs = [f for f in compare(fixture, _manifest("Something Else"), fps=1.0)
            if f.status == "regression"]
    assert regs and "recorded as unread" in regs[0].message


def test_unread_entry_that_starts_reading_correctly_goes_quiet() -> None:
    fixture = _fixture(name="Launching Adjust Par Levels", unread=True)
    findings = compare(fixture, _manifest("Launching Adjust Par Levels"), fps=1.0)
    assert not [f for f in findings if f.status in ("misread", "regression")]


def test_unread_without_a_name_says_nothing() -> None:
    """The flag alone must not excuse anything."""
    fixture = _fixture(unread=True)
    findings = compare(fixture, _manifest(None), fps=1.0)
    assert not [f for f in findings if f.status in ("misread", "regression")]
