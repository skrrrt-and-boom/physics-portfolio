"""Locks the physics of the drag-coefficient sensitivity sweep."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects" / "p1_projectile_drag"))

from simulate import simulate_trajectory  # noqa: E402

MASS = 0.145  # kg
V0 = 40.0  # m/s
DT = 2e-3  # converged far past 4 decimals per the P1 verification block


def test_range_decreases_with_drag_coefficient():
    cs = [0.0, 0.001, 0.005, 0.01]
    ranges = [simulate_trajectory(45.0, V0, MASS, c, dt=DT)[2] for c in cs]
    assert all(r2 < r1 for r1, r2 in zip(ranges, ranges[1:])), (
        f"range not strictly decreasing with c: {ranges}"
    )


def test_optimal_angle_vacuum_is_45_on_grid():
    angles = np.linspace(20.0, 50.0, 31)  # includes 45.0 exactly
    ranges = [simulate_trajectory(th, V0, MASS, 0.0, dt=DT)[2] for th in angles]
    assert angles[int(np.argmax(ranges))] == 45.0
