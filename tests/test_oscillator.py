"""Checks for the P2 driven-damped oscillator physics."""

import sys
from pathlib import Path

import numpy as np

# make projects/p2_driven_oscillator importable without packaging it
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects" / "p2_driven_oscillator"))

from oscillator import (  # noqa: E402
    bandwidth,
    damping_gamma,
    decay_gamma,
    measure_amplitude,
    natural_frequency,
    peak_frequency,
    resonance_sweep,
    steady_amplitude,
)

M = 1.0                      # kg
K = (2.0 * np.pi) ** 2       # N/m  ->  w0 = 2 pi rad/s
F0 = 1.0                     # N
Q = 5.0
B = M * natural_frequency(M, K) / Q
GAMMA = damping_gamma(M, B)
W0 = natural_frequency(M, K)
DT = 5e-3                    # coarse is fine: checks are relative-error based
SETTLE = 8.0 / GAMMA         # transient suppressed by e^-8 ~ 3e-4


def test_steady_amplitude_matches_analytic_off_peak():
    w = 1.3 * W0
    a_num = measure_amplitude(M, B, K, F0, w, DT, SETTLE, n_periods=6)
    a_th = steady_amplitude(M, B, K, F0, w)
    assert abs(a_num - a_th) / a_th < 0.02


def test_peak_frequency_matches_theory():
    ws = np.linspace(0.8 * W0, 1.2 * W0, 17)
    amps = resonance_sweep(M, B, K, F0, ws, DT, SETTLE, n_periods=6)
    grid = ws[1] - ws[0]
    assert abs(ws[int(np.argmax(amps))] - peak_frequency(M, B, K)) < 1.5 * grid


def test_q_from_bandwidth():
    ws = np.linspace(0.85 * W0, 1.15 * W0, 31)
    amps = resonance_sweep(M, B, K, F0, ws, DT, SETTLE, n_periods=6)
    dw = bandwidth(ws, amps)
    assert dw is not None
    q_num = ws[int(np.argmax(amps))] / dw
    assert abs(q_num - Q) / Q < 0.10


def test_free_decay_rate():
    g_fit = decay_gamma(M, B, K, DT, 6.0 / GAMMA)
    assert abs(g_fit - GAMMA) / GAMMA < 0.02
