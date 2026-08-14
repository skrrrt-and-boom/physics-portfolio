"""Shape checks for the P3 potential builders."""

import numpy as np

from projects.p3_quantum_tunneling.potentials import finite_well, square_barrier


def test_barrier_height_and_extent():
    x = np.linspace(-5, 5, 2001)
    V = square_barrier(x, V0=4.0, a=2.0)
    assert V.max() == 4.0
    # nonzero only inside |x| < 1
    assert np.all(V[np.abs(x) > 1.0] == 0.0)
    inside = x[np.abs(x) < 1.0]
    assert np.allclose(square_barrier(inside, 4.0, 2.0), 4.0)


def test_barrier_off_center():
    x = np.linspace(0, 10, 1001)
    V = square_barrier(x, V0=3.0, a=1.0, x0=5.0)
    assert V.max() == 3.0
    assert np.all(V[x < 4.5] == 0.0)
    assert np.all(V[x > 5.5] == 0.0)


def test_well_is_negative_barrier_shape():
    x = np.linspace(-5, 5, 2001)
    V = finite_well(x, V0=4.0, a=2.0)
    assert V.min() == -4.0
    assert np.all(V[np.abs(x) > 1.0] == 0.0)
    # well = -barrier for the same geometry
    assert np.allclose(V, -square_barrier(x, 4.0, 2.0))


def test_zero_height_is_flat():
    x = np.linspace(-3, 3, 101)
    assert np.all(square_barrier(x, 0.0, 1.0) == 0.0)
    assert np.all(finite_well(x, 0.0, 1.0) == 0.0)
