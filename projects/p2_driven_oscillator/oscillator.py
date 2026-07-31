"""Driven damped harmonic oscillator: simulation + resonance measurement.

    m x'' + b x' + k x = F0 cos(w t)

rewritten as  x'' + 2 g x' + w0^2 x = (F0/m) cos(w t)
with g = b/(2m), w0 = sqrt(k/m).

Every number the script reports is checked against the analytic steady state.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# reuse P1's hand-written RK4 without packaging the repo
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "p1_projectile_drag"))
from rk4 import rk4_step  # noqa: E402


def natural_frequency(m: float, k: float) -> float:
    return float(np.sqrt(k / m))


def damping_gamma(m: float, b: float) -> float:
    return b / (2.0 * m)


def q_factor(m: float, b: float, k: float) -> float:
    return natural_frequency(m, k) / (2.0 * damping_gamma(m, b))


def steady_amplitude(m: float, b: float, k: float, F0: float, w: float) -> float:
    """Analytic steady-state amplitude at drive frequency w."""
    w0 = natural_frequency(m, k)
    g = damping_gamma(m, b)
    return (F0 / m) / np.sqrt((w0**2 - w**2) ** 2 + (2.0 * g * w) ** 2)


def peak_frequency(m: float, b: float, k: float) -> float:
    """Drive frequency of maximum steady-state amplitude (analytic)."""
    w0 = natural_frequency(m, k)
    g = damping_gamma(m, b)
    if 2.0 * g**2 >= w0**2:
        return 0.0
    return float(np.sqrt(w0**2 - 2.0 * g**2))


def make_rhs(m, b, k, F0, w):
    def rhs(t, y):
        x, v = y
        return np.array([v, (F0 * np.cos(w * t) - b * v - k * x) / m])

    return rhs


def simulate(m, b, k, F0, w, dt, t_end, x0=0.0, v0=0.0):
    """Integrate with fixed-step RK4. Returns (ts, ys); ys[:, 0] = x, ys[:, 1] = v."""
    rhs = make_rhs(m, b, k, F0, w)
    t, y = 0.0, np.array([x0, v0])
    n = int(round(t_end / dt))
    ts = np.empty(n + 1)
    ys = np.empty((n + 1, 2))
    ts[0], ys[0] = t, y
    for i in range(1, n + 1):
        y = rk4_step(rhs, t, y, dt)
        t += dt
        ts[i], ys[i] = t, y
    return ts, ys


def measure_amplitude(m, b, k, F0, w, dt, t_settle, n_periods=8):
    """Steady-state amplitude from the tail of the trajectory.

    The transient dies like e^{-g t}, so everything before t_settle is
    dropped; amplitude = (max - min)/2 over an integer number of drive
    periods after that.
    """
    period = 2.0 * np.pi / w
    t_end = t_settle + n_periods * period
    ts, ys = simulate(m, b, k, F0, w, dt, t_end)
    tail = ys[ts >= t_settle, 0]
    return 0.5 * (tail.max() - tail.min())


def resonance_sweep(m, b, k, F0, ws, dt, t_settle, n_periods=8):
    return np.array(
        [measure_amplitude(m, b, k, F0, w, dt, t_settle, n_periods) for w in ws]
    )


def bandwidth(ws, amps):
    """Full width of the resonance peak at A_max / sqrt(2).

    For light damping Q = w_peak / dw. Returns None if either crossing
    falls outside the swept grid.
    """
    i = int(np.argmax(amps))
    level = amps[i] / np.sqrt(2.0)

    def crossing(w1, a1, w2, a2):
        return w1 + (level - a1) * (w2 - w1) / (a2 - a1)

    left = None
    for j in range(i, 0, -1):
        if amps[j - 1] < level <= amps[j]:
            left = crossing(ws[j - 1], amps[j - 1], ws[j], amps[j])
            break
    right = None
    for j in range(i, len(ws) - 1):
        if amps[j] >= level > amps[j + 1]:
            right = crossing(ws[j], amps[j], ws[j + 1], amps[j + 1])
            break
    if left is None or right is None:
        return None
    return right - left


def decay_gamma(m, b, k, dt, t_end, x0=1.0):
    """Extract the free-decay rate: successive maxima of x fall as e^{-g t}."""
    # F0 = 0 -> drive frequency is irrelevant
    ts, ys = simulate(m, b, k, F0=0.0, w=1.0, dt=dt, t_end=t_end, x0=x0)
    x, v = ys[:, 0], ys[:, 1]
    crossings = np.where((v[:-1] > 0) & (v[1:] <= 0))[0]
    slope, _ = np.polyfit(ts[crossings], np.log(x[crossings]), 1)
    return -slope


if __name__ == "__main__":
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    M = 1.0                    # kg
    K = (2.0 * np.pi) ** 2     # N/m  ->  w0 = 2 pi rad/s  (f0 = 1 Hz)
    F0 = 1.0                   # N
    DT = 2e-3                  # s
    QS = [2.0, 5.0, 10.0]

    w0 = natural_frequency(M, K)
    ws = np.linspace(0.3 * w0, 1.8 * w0, 36)
    fine = np.linspace(ws[0], ws[-1], 500)
    out = Path(__file__).resolve().parent / "figures"
    out.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    print("=== VERIFICATION ===")
    for Q in QS:
        b = M * w0 / Q
        g = damping_gamma(M, b)
        t_settle = 12.0 / g  # transient suppressed by e^-12 ~ 6e-6
        amps = resonance_sweep(M, b, K, F0, ws, DT, t_settle)

        i = int(np.argmax(amps))
        w_peak_num, a_peak_num = ws[i], amps[i]
        w_peak_th = peak_frequency(M, b, K)
        a_peak_th = steady_amplitude(M, b, K, F0, w_peak_th)
        dw = bandwidth(ws, amps)
        q_num = w_peak_num / dw if dw else float("nan")
        grid = ws[1] - ws[0]

        ax.plot(ws / w0, amps, "o", ms=3, color=f"C{QS.index(Q)}",
                label=f"sim, Q = {Q:g}")
        ax.plot(fine / w0, steady_amplitude(M, b, K, F0, fine), "-", lw=1,
                alpha=0.55, color=f"C{QS.index(Q)}", label=f"analytic, Q = {Q:g}")

        print(f"Q = {Q:g}  (b = {b:.4f} kg/s, gamma = {g:.4f} 1/s)")
        print(f"  peak freq:  sim {w_peak_num:.4f} vs theory {w_peak_th:.4f} rad/s"
              f"   (grid step {grid:.4f})")
        print(f"  peak amp:   sim {a_peak_num:.5f} vs theory {a_peak_th:.5f} m"
              f"   rel err {abs(a_peak_num - a_peak_th) / a_peak_th:.2e}")
        print(f"  bandwidth:  dw = {dw:.4f} -> Q_sim = {q_num:.2f}"
              f" vs Q_theory = {Q:g}")

    ax.set_xlabel("drive frequency / w0")
    ax.set_ylabel("steady-state amplitude [m]")
    ax.set_title("Resonance curves of the driven damped oscillator")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "resonance_curves.png", dpi=150)
    print(f"figure -> {out / 'resonance_curves.png'}")

    # free decay: envelope must follow x0 * e^{-g t}
    Q = QS[-1]
    b = M * w0 / Q
    g = damping_gamma(M, b)
    ts, ys = simulate(M, b, K, F0=0.0, w=1.0, dt=DT, t_end=6.0 / g, x0=1.0)
    g_fit = decay_gamma(M, b, K, DT, 6.0 / g)
    print(f"decay rate: fit {g_fit:.5f} vs theory {g:.5f} 1/s"
          f"   rel err {abs(g_fit - g) / g:.2e}")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ts, ys[:, 0], lw=1, label="sim x(t)")
    env = np.exp(-g * ts)
    ax.plot(ts, env, "--", lw=1, label=r"$x_0 e^{-\gamma t}$")
    ax.plot(ts, -env, "--", lw=1)
    ax.set_xlabel("t [s]")
    ax.set_ylabel("x [m]")
    ax.set_title(f"Free decay with exponential envelope (Q = {Q:g})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "decay_envelope.png", dpi=150)
    print(f"figure -> {out / 'decay_envelope.png'}")
