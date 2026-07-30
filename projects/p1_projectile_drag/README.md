# P1 - Projectile motion with quadratic air drag

Everyone learns the optimal launch angle is 45°. That's the vacuum answer. I wanted to see what quadratic air drag actually does - to the trajectory, and to that angle.

## Model

2D motion under constant gravity, drag force opposite velocity:

- Gravity: $\mathbf{F}_g = (0, -mg)$
- Quadratic drag: $\mathbf{F}_d = -c\,|\mathbf{v}|\,\mathbf{v}$
- Net acceleration:

$$
a_x = -\frac{c}{m}|v|\,v_x, \qquad
a_y = -g -\frac{c}{m}|v|\,v_y
$$

State vector: $(x, y, v_x, v_y)$.

## Method

- Fixed-step **RK4** integrator, written by hand (`rk4.py`)
- Flight ends when the projectile returns to $y \le 0$ (with $x > 0$)
- Compare vacuum ($c = 0$) vs drag ($c > 0$), then sweep the launch angle

## Run

```bash
# from repo root, venv on
python projects/p1_projectile_drag/simulate.py
```

## Outputs

- `figures/trajectories.png` - vacuum vs drag paths  
- `figures/range_vs_angle.png` - range sweep  

## Results

(defaults: m = 0.145 kg, v0 = 40 m/s, c = 0.0015 kg/m, dt = 1e-3 s)

- Vacuum range: RK4 **163.099 m** vs analytic $v_0^2\sin(2\theta)/g$ **163.099 m** - abs. error **1.19e-06 m**
- Drag range at c = 0.0015 kg/m: **76.912 m** - drag more than halves the vacuum range
- Optimal angle: **45°** vacuum -> **≈ 40°** with drag (R = 78.0 m). Makes sense in hindsight: with drag you can't afford hang time, so you trade height for speed
- Terminal speed $v_t = \sqrt{mg/c}$ ≈ **30.8 m/s** - launch at 40 m/s is above $v_t$, so drag bites hard early

Verification block printed by the script:

```
=== VERIFICATION ===
(a) vacuum energy drift max|E-E0|/|E0| = 5.721e-14  (expect ~1e-16..1e-12)
(b) vacuum range |RK4 - analytic|      = 1.192e-06 m  (expect ~1e-6..1e-11)
(c) drag-case dt-convergence (range in m):
    dt=1e-01   range = 76.9049 m
    dt=1e-02   range = 76.9116 m
    dt=1e-03   range = 76.9116 m
    dt=1e-04   range = 76.9116 m
```

My read: (a) energy is conserved to ~1e-14 over the flight, so the integrator isn't the error source; (b) the vacuum range matches the closed form to ~1 µm - what's left is the linear landing interpolation, not RK4; (c) the drag range is converged to 4 decimals by dt = 1e-2, so I trust the dt = 1e-3 numbers. The suite in `tests/` locks these properties in.

## Sensitivity to drag coefficient

`python projects/p1_projectile_drag/sensitivity.py` sweeps c from 0 to 0.01 kg/m - range at fixed 45°, then an angle sweep per c for the optimal angle.

- `figures/range_vs_c.png` - range falls monotonically from the vacuum limit. The c = 0 endpoint recovers the analytic 163.099 m, so the sweep is self-checking where it starts
- `figures/optimal_angle_vs_c.png` - optimal angle starts at exactly 45° (c = 0) and slides to **32°** at c = 0.01 kg/m, where the 45° range is down to **23.9 m - 14.7% of vacuum**

Physical reading: larger c lowers the terminal speed v_t = sqrt(mg/c), so drag dominates earlier and hang time gets taxed harder - the optimum keeps trading height for a flatter path. Verification printed by the script: c = 0 reproduces both vacuum answers (range to 3.2e-06 m, angle exactly 45°), and range is non-increasing over the whole sweep. `tests/test_sensitivity.py` locks the monotonicity and the vacuum optimum.

## Parameters (defaults in `simulate.py`)

| Symbol | Meaning | Default |
|--------|---------|--------:|
| m | mass | 0.145 kg (baseball-ish) |
| g | gravity | 9.81 m/s² |
| v0 | launch speed | 40 m/s |
| c | drag coefficient | 0.0015 kg/m (tunable) |
| θ | launch angle | 45° (single path) + sweep |

## Limitations

- Drag coefficient is illustrative, not wind-tunnel data for a real object
- Flat Earth, no spin / Magnus force
- Fixed-step RK4 - converges only for small enough dt (hence the checks)

## TODO

- [ ] Match against a published drag example
- [x] Sensitivity study over c (range + optimal angle) - `sensitivity.py`, 2026-07-30
