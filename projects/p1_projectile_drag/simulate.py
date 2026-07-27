#!/usr/bin/env python3
"""P1: projectile with quadratic drag - trajectories + range vs angle."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from rk4 import integrate

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

G = 9.81  # m/s^2


def make_rhs(mass: float, drag_c: float):
    """Return f(t, state) for state = [x, y, vx, vy]."""
    k = drag_c / mass  # constant for the whole integration - hoist out of f

    def f(_t: float, s: np.ndarray) -> np.ndarray:
        vx, vy = s[2], s[3]  # x, y do not enter the RHS
        speed = np.hypot(vx, vy)
        # avoid 0/0 at rest
        if speed < 1e-12:
            ax = 0.0
            ay = -G
        else:
            ax = -k * speed * vx
            ay = -G - k * speed * vy
        return np.array([vx, vy, ax, ay], dtype=float)

    return f


def simulate_trajectory(
    theta_deg: float,
    v0: float,
    mass: float,
    drag_c: float,
    dt: float = 1e-3,
):
    theta = np.deg2rad(theta_deg)
    y0 = np.array([0.0, 0.0, v0 * np.cos(theta), v0 * np.sin(theta)], dtype=float)
    f = make_rhs(mass, drag_c)

    def stop(_t, s):
        # landed (after leaving ground)
        return s[1] < 0.0 and s[0] > 1e-6

    ts, ys = integrate(f, y0, 0.0, dt, stop)
    # linear interpolate last segment to y=0 for cleaner range;
    # interpolate the WHOLE state so the final row stays internally
    # consistent (x, y, vx, vy all at the same landing instant).
    # Note: this row is only O(dt^2) accurate, so energy checks below
    # use the last genuine RK4 state instead (see VERIFICATION block).
    if len(ys) >= 2 and ys[-1, 1] < 0:
        y_a, y_b = ys[-2, 1], ys[-1, 1]
        frac = y_a / (y_a - y_b) if (y_b != y_a) else 1.0
        ys[-1] = ys[-2] + frac * (ys[-1] - ys[-2])
        ys[-1, 1] = 0.0
        range_x = float(ys[-1, 0])
    else:
        range_x = float(ys[-1, 0])
    return ts, ys, range_x


def vacuum_range(theta_deg: float, v0: float) -> float:
    theta = np.deg2rad(theta_deg)
    return (v0**2) * np.sin(2 * theta) / G


def mechanical_energy(states: np.ndarray, mass: float) -> np.ndarray:
    """E = KE + PE per row of states [x, y, vx, vy]."""
    vx, vy = states[:, 2], states[:, 3]
    return 0.5 * mass * (vx**2 + vy**2) + mass * G * states[:, 1]


def max_energy_drift(states: np.ndarray, mass: float) -> float:
    """Max |E - E0| / |E0| over the genuine RK4 states.

    The last row of `states` is the linear-interpolated landing point
    (only O(dt^2) accurate), so it is excluded from the metric.
    """
    genuine = states[:-1] if len(states) >= 2 else states
    e = mechanical_energy(genuine, mass)
    return float(np.max(np.abs(e - e[0])) / abs(e[0]))


def main():
    mass = 0.145
    v0 = 40.0
    drag_c = 0.0015
    theta_demo = 45.0

    _, vac_ys, vac_r = simulate_trajectory(theta_demo, v0, mass, drag_c=0.0)
    _, drag_ys, drag_r = simulate_trajectory(theta_demo, v0, mass, drag_c=drag_c)
    analytic = vacuum_range(theta_demo, v0)

    print(f"Vacuum range (RK4)     = {vac_r:.3f} m")
    print(f"Vacuum range (analytic)= {analytic:.3f} m")
    print(f"Drag range (c={drag_c})  = {drag_r:.3f} m")
    print(f"Terminal speed sqrt(mg/c) = {np.sqrt(mass * G / drag_c):.1f} m/s")

    # --- trajectories ---
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(vac_ys[:, 0], vac_ys[:, 1], label=f"vacuum (R≈{vac_r:.1f} m)")
    ax.plot(drag_ys[:, 0], drag_ys[:, 1], label=f"quadratic drag (R≈{drag_r:.1f} m)")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(
        f"Projectile trajectories (θ={theta_demo}°, v0={v0} m/s)\n"
        f"m={mass} kg, c={drag_c} kg/m"
    )
    ax.legend()
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "trajectories.png", dpi=160)
    plt.close(fig)

    # --- range vs angle ---
    angles = np.linspace(15, 75, 25)
    r_vac = []
    r_drag = []
    for th in angles:
        _, _, rv = simulate_trajectory(th, v0, mass, 0.0)
        _, _, rd = simulate_trajectory(th, v0, mass, drag_c)
        r_vac.append(rv)
        r_drag.append(rd)
    r_vac = np.asarray(r_vac)
    r_drag = np.asarray(r_drag)
    i_v = int(np.argmax(r_vac))
    i_d = int(np.argmax(r_drag))
    print(f"Optimal angle vacuum ≈ {angles[i_v]:.1f}° (R={r_vac[i_v]:.1f} m)")
    print(f"Optimal angle drag   ≈ {angles[i_d]:.1f}° (R={r_drag[i_d]:.1f} m)")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(angles, r_vac, label="vacuum")
    ax.plot(angles, r_drag, label="quadratic drag")
    ax.axvline(angles[i_v], color="C0", ls="--", alpha=0.5)
    ax.axvline(angles[i_d], color="C1", ls="--", alpha=0.5)
    ax.set_xlabel("launch angle (deg)")
    ax.set_ylabel("range (m)")
    ax.set_title(f"Range vs launch angle (v0={v0} m/s, m={mass} kg, c={drag_c} kg/m)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "range_vs_angle.png", dpi=160)
    plt.close(fig)

    print(f"Wrote figures -> {FIG}")

    # --- VERIFICATION: prove the numerics, don't just plot them ---
    print("\n=== VERIFICATION ===")
    # (a) vacuum energy conservation: with c=0, E = KE + PE is exact physics,
    #     so any drift is pure integrator error. Uses genuine RK4 states only
    #     (interpolated landing row excluded - see max_energy_drift).
    drift = max_energy_drift(vac_ys, mass)
    print(f"(a) vacuum energy drift max|E-E0|/|E0| = {drift:.3e}  (expect ~1e-16..1e-12)")
    # (b) vacuum RK4 range vs analytic v0^2 sin(2θ)/g
    range_err = abs(vac_r - analytic)
    print(f"(b) vacuum range |RK4 - analytic|      = {range_err:.3e} m  (expect ~1e-6..1e-11)")
    # (c) dt-convergence of the DRAG range: no analytic solution exists,
    #     so show the value stops moving as dt shrinks.
    print("(c) drag-case dt-convergence (range in m):")
    for dt in (1e-1, 1e-2, 1e-3, 1e-4):
        _, _, r_dt = simulate_trajectory(theta_demo, v0, mass, drag_c, dt=dt)
        print(f"    dt={dt:.0e}   range = {r_dt:.4f} m")


if __name__ == "__main__":
    main()
