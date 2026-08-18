"""Unit tests for the screen-quad geometry helpers.

These run against synthesised corner sets rather than fixture frames: the
question here is whether the *rules* about movement are right, and a rule about
movement is best stated in coordinates. Detection itself is tested against
committed frames elsewhere.
"""

from __future__ import annotations

import numpy as np

from reframe.vision.quad import Quad, has_settled, is_plausible_successor, order_corners

# 1920x1080, the resolution the corpus is shot at.
DIAGONAL = float(np.hypot(1920, 1080))
JUMP_FRACTION = 0.10


def quad_at(cx: float, cy: float, *, width: float = 1200.0, height: float = 620.0) -> Quad:
    """An axis-aligned quad centred on ``(cx, cy)``."""
    half_w, half_h = width / 2, height / 2
    points = np.array(
        [
            [cx - half_w, cy - half_h],
            [cx + half_w, cy - half_h],
            [cx + half_w, cy + half_h],
            [cx - half_w, cy + half_h],
        ],
        dtype=np.float64,
    )
    return Quad(corners=order_corners(points), confidence=1.0)


class TestIsPlausibleSuccessor:
    def test_small_drift_is_accepted(self) -> None:
        assert is_plausible_successor(
            quad_at(900, 500),
            quad_at(908, 506),
            frame_diagonal=DIAGONAL,
            max_jump_fraction=JUMP_FRACTION,
        )

    def test_a_leap_across_the_frame_is_rejected(self) -> None:
        assert not is_plausible_successor(
            quad_at(400, 300),
            quad_at(1500, 800),
            frame_diagonal=DIAGONAL,
            max_jump_fraction=JUMP_FRACTION,
        )

    def test_the_budget_scales_with_the_fraction(self) -> None:
        """The same movement flips verdict when the fraction is widened."""
        previous, current = quad_at(900, 500), quad_at(1200, 500)
        assert not is_plausible_successor(
            previous, current, frame_diagonal=DIAGONAL, max_jump_fraction=0.10
        )
        assert is_plausible_successor(
            previous, current, frame_diagonal=DIAGONAL, max_jump_fraction=0.20
        )

    def test_unknown_diagonal_does_not_reject(self) -> None:
        """With no frame to measure against, the check abstains rather than guesses."""
        assert is_plausible_successor(
            quad_at(0, 0),
            quad_at(1900, 1000),
            frame_diagonal=0.0,
            max_jump_fraction=JUMP_FRACTION,
        )


class TestHasSettled:
    def test_a_steady_run_has_settled(self) -> None:
        """The v01 case: one big reposition, then the camera holds."""
        run = [quad_at(951, 421), quad_at(852, 403), quad_at(846, 430), quad_at(848, 436)]
        assert has_settled(run, frame_diagonal=DIAGONAL, max_jump_fraction=JUMP_FRACTION)

    def test_a_wandering_run_has_not_settled(self) -> None:
        """A reflection crossing the frame must never be re-acquired as a screen."""
        run = [quad_at(200, 200), quad_at(900, 600), quad_at(1600, 200), quad_at(500, 900)]
        assert not has_settled(run, frame_diagonal=DIAGONAL, max_jump_fraction=JUMP_FRACTION)

    def test_one_detection_is_never_enough(self) -> None:
        """Re-acquisition needs corroboration; a single frame is not evidence."""
        assert not has_settled(
            [quad_at(900, 500)], frame_diagonal=DIAGONAL, max_jump_fraction=JUMP_FRACTION
        )

    def test_empty_run_has_not_settled(self) -> None:
        assert not has_settled([], frame_diagonal=DIAGONAL, max_jump_fraction=JUMP_FRACTION)

    def test_a_run_that_breaks_at_the_end_has_not_settled(self) -> None:
        """Agreement must hold across the whole run, not just most of it."""
        run = [quad_at(900, 500), quad_at(905, 505), quad_at(1800, 200)]
        assert not has_settled(run, frame_diagonal=DIAGONAL, max_jump_fraction=JUMP_FRACTION)
