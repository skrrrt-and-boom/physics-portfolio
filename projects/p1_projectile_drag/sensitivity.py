#!/usr/bin/env python3
"""P1: sensitivity to drag coefficient - range(c) and optimal angle(c).

Sweeps c from 0 (vacuum limit - must recover the analytic results) to
0.01 kg/m. Both endpoints are self-checking:
  - c = 0 range at 45° must match v0^2 sin(2θ)/g
  - c = 0 optimal angle on the grid must be exactly 45°
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from simulate import simulate_trajectory, vacuum_range

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

MASS = 0.145  # kg
V0 = 40.0  # m/s
# dt=2e-3: the P1 verification block showed the drag range converged to
# 4 decimals already at dt=1e-2, so 2e-3 is ~10x finer than needed and
# keeps the ~500-simulation sweep quick.
DT = 2e-3


def optimal_angle(drag_c: float, angles: np.ndarray):
    """Argmax of range over the angle grid for a given drag coefficient."""
    ranges = [simulate_trajectory(th, V0, MASS, drag_c, dt=DT)[2] for th in angles]
    i = int(np.argmax(ranges))
    return float(angles[i]), float(ranges[i])


def main():
    cs = np.linspace(0.0, 0.01, 15)

    # --- range(c) at fixed 45° launch ---
    ranges45 = [simulate_trajectory(45.0, V0, MASS, c, dt=DT)[2] for c in cs]
    vac = vacuum_range(45.0, V0)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(cs, ranges45, "o-", ms=3.5, label="range at θ=45° (RK4)")
    ax.axhline(vac, ls="--", color="gray", label=f"vacuum limit {vac:.1f} m")
    ax.set_xlabel("drag coefficient c (kg/m)")
    ax.set_ylabel("range (m)")
    ax.set_title(f"Range vs drag coefficient (v0={V0} m/s, m={MASS} kg)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "range_vs_c.png", dpi=160)
    plt.close(fig)

    # --- optimal angle(c) ---
    angles = np.linspace(20.0, 50.0, 31)  # 1° grid, includes 45.0 exactly
    opts = [optimal_angle(c, angles) for c in cs]
    opt_ang = [o[0] for o in opts]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(cs, opt_ang, "s-", ms=3.5, color="C1", label="optimal angle (1° grid)")
    ax.axhline(45.0, ls="--", color="gray", label="vacuum optimum 45°")
    ax.set_xlabel("drag coefficient c (kg/m)")
    ax.set_ylabel("optimal launch angle (deg)")
    ax.set_title(f"Optimal angle vs drag coefficient (v0={V0} m/s, m={MASS} kg)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "optimal_angle_vs_c.png", dpi=160)
    plt.close(fig)

    print(f"Wrote figures -> {FIG}")

    # --- VERIFICATION: both ends of the sweep are known physics ---
    print("\n=== VERIFICATION ===")
    r0 = ranges45[0]
    print(f"(a) c=0 range = {r0:.3f} m vs analytic {vac:.3f} m "
          f"(|diff| = {abs(r0 - vac):.2e} m)")
    a0 = opt_ang[0]
    print(f"(b) c=0 optimal angle = {a0:.1f}° (vacuum theory: 45.0°)")
    mono = all(r2 <= r1 + 1e-9 for r1, r2 in zip(ranges45, ranges45[1:]))
    print(f"(c) range monotonically non-increasing with c: {mono}")
    print(f"(d) endpoints: c=0 -> θ*={opt_ang[0]:.0f}°, "
          f"c={cs[-1]:.3f} -> θ*={opt_ang[-1]:.0f}°, "
          f"range {ranges45[-1]:.1f} m ({ranges45[-1] / vac:.1%} of vacuum)")


if __name__ == "__main__":
    main()
