"""Lock P1 headline numbers: vacuum range vs analytic, drag range regression."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects" / "p1_projectile_drag"))

from simulate import simulate_trajectory, vacuum_range  # noqa: E402

MASS = 0.145      # kg
V0 = 40.0         # m/s
DRAG_C = 0.0015   # kg/m
ANGLE = 45.0      # deg

def test_vacuum_range_matches_analytic():
    _, _, r = simulate_trajectory(ANGLE, V0, MASS, drag_c=0.0)
    assert abs(r - vacuum_range(ANGLE, V0)) < 2e-6

def test_drag_range_regression():
    _, _, r = simulate_trajectory(ANGLE, V0, MASS, drag_c=DRAG_C)
    assert abs(r - 76.912) < 0.01