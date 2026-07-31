# Computational physics

I'm teaching myself physics by building small systems and forcing the numerics to be honest - every claim gets checked against an analytic limit, a conservation law, or a convergence test.

**Stack:** Python, NumPy, Matplotlib

## Projects

| # | Project | Status | Folder |
|---|---------|--------|--------|
| 1 | Projectile motion with quadratic air drag (RK4) | done | [`projects/p1_projectile_drag`](projects/p1_projectile_drag) |
| 2 | Damped / driven oscillator - resonance curve, Q factor | done | [`projects/p2_driven_oscillator`](projects/p2_driven_oscillator) |
| 3 | Quantum tunneling in 1D (eigenstates + wave-packet evolution) | planned | TBD |

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate   # Python >= 3.11 (built on 3.12)
pip install -r requirements.txt
python projects/p1_projectile_drag/simulate.py
```

Figures land in each project's `figures/` folder. Checks:

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Conventions

- Start from the equations; implement the numerics transparently (RK4 by hand, not a black box)
- Plots + an honest limitations section beat long prose
- Small systems understood deeply, over big ones understood shallowly

License: [MIT](LICENSE)
