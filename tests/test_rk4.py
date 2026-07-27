"""Checks for the RK4 integrator and the P1 projectile-drag physics."""

import sys
from pathlib import Path

import numpy as np

# make projects/p1_projectile_drag importable without packaging it
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects" / "p1_projectile_drag"))

from rk4 import integrate  # noqa: E402
from simulate import simulate_trajectory, vacuum_range  # noqa: E402

MASS = 0.145  # kg
V0 = 40.0  # m/s
DRAG_C = 0.0015  # kg/m


def _exp_decay_error(dt: float, T: float = 1.0) -> float:
    """Error of RK4 on y' = -y, y(0)=1 at time T (exact: y = e^-t)."""
    _, ys = integrate(lambda _t, y: -y, np.array([1.0]), 0.0, dt, lambda t, _y: t >= T)
    return abs(ys[-1, 0] - np.exp(-T))


def test_rk4_is_fourth_order():
    # dts are powers of two so t lands on T=1 exactly
    e1 = _exp_decay_error(0.25)
    e2 = _exp_decay_error(0.125)
    order = np.log2(e1 / e2)
    assert order >= 3.9, f"measured convergence order {order:.2f} < 3.9"


def test_vacuum_range_matches_analytic():
    _, _, r = simulate_trajectory(45.0, V0, MASS, drag_c=0.0)
    assert abs(r - vacuum_range(45.0, V0)) < 1e-4


def test_drag_shortens_range():
    _, _, r_vac = simulate_trajectory(45.0, V0, MASS, drag_c=0.0)
    _, _, r_drag = simulate_trajectory(45.0, V0, MASS, drag_c=DRAG_C)
    assert r_drag < r_vac


def test_optimal_angle_with_drag_below_45_deg():
    angles = np.linspace(30.0, 45.0, 16)
    ranges = [simulate_trajectory(th, V0, MASS, DRAG_C)[2] for th in angles]
    assert angles[int(np.argmax(ranges))] < 45.0
