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
- [ ] Sensitivity study over c (range + optimal angle)
