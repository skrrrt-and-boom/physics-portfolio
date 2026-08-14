"""Potential-energy profiles for the 1D tunneling study (dimensionless units: hbar = m = 1)."""

from __future__ import annotations

import numpy as np


def square_barrier(x: np.ndarray, V0: float, a: float, x0: float = 0.0) -> np.ndarray:
    """Rectangular barrier of height V0 and width a, centered on x0.

    V(x) = V0 for |x - x0| < a/2, else 0.
    """
    x = np.asarray(x, dtype=float)
    return np.where(np.abs(x - x0) < a / 2, V0, 0.0)


def finite_well(x: np.ndarray, V0: float, a: float, x0: float = 0.0) -> np.ndarray:
    """Finite square well of depth V0 and width a, centered on x0.

    V(x) = -V0 for |x - x0| < a/2, else 0.
    """
    x = np.asarray(x, dtype=float)
    return np.where(np.abs(x - x0) < a / 2, -V0, 0.0)
