"""Minimal fixed-step RK4 for dy/dt = f(t, y)."""

from __future__ import annotations

import numpy as np


def rk4_step(f, t: float, y: np.ndarray, dt: float) -> np.ndarray:
    """Advance one step with classical 4th-order Runge-Kutta."""
    k1 = f(t, y)
    k2 = f(t + 0.5 * dt, y + 0.5 * dt * k1)
    k3 = f(t + 0.5 * dt, y + 0.5 * dt * k2)
    k4 = f(t + dt, y + dt * k3)
    return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate(f, y0: np.ndarray, t0: float, dt: float, stop_fn, max_steps: int = 200_000):
    """Integrate until stop_fn(t, y) is True. Returns times, states."""
    t = float(t0)
    y = np.asarray(y0, dtype=float).copy()
    ts = [t]
    ys = [y.copy()]
    for _ in range(max_steps):
        if stop_fn(t, y):
            break
        y = rk4_step(f, t, y, dt)
        t += dt
        ts.append(t)
        ys.append(y.copy())
    return np.asarray(ts), np.asarray(ys)
