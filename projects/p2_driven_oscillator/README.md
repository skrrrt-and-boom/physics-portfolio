# P2 - Driven damped oscillator: resonance curve and Q factor

Push a swing in rhythm and it grows huge; push off-beat and nothing much happens. I wanted the actual curve - how the steady-state amplitude depends on drive frequency, and whether the simulator reproduces the analytic result instead of just looking plausible.

## Model

A mass on a spring with linear damping, driven sinusoidally:

$$
m\ddot{x} + b\dot{x} + kx = F_0\cos(\omega t)
\quad\Longleftrightarrow\quad
\ddot{x} + 2\gamma\dot{x} + \omega_0^2 x = \tfrac{F_0}{m}\cos(\omega t),
\qquad \gamma = \frac{b}{2m},\ \ \omega_0 = \sqrt{\tfrac{k}{m}}
$$

Analytic steady-state amplitude and its peak position:

$$
A(\omega) = \frac{F_0/m}{\sqrt{(\omega_0^2-\omega^2)^2 + (2\gamma\omega)^2}},
\qquad
\omega_{\text{peak}} = \sqrt{\omega_0^2 - 2\gamma^2},
\qquad
Q = \frac{\omega_0}{2\gamma}
$$

## Method

- Fixed-step **RK4** (the hand-written integrator from P1)
- Transient discarded at $t = 12/\gamma$ (suppressed by $e^{-12} \sim 6\times10^{-6}$); amplitude = (max - min)/2 over 8 drive periods after that
- Resonance curve by sweeping $\omega$; **Q measured** from the bandwidth at $A_{\max}/\sqrt{2}$
- Free decay: fit successive maxima to $x_0 e^{-\gamma t}$ and compare the rate to $b/2m$

## Run

```bash
# from repo root, venv on
python projects/p2_driven_oscillator/oscillator.py
```

## Outputs

- `figures/resonance_curves.png` - sim points vs analytic curves for Q = 2, 5, 10
- `figures/decay_envelope.png` - free decay inside the $e^{-\gamma t}$ envelope

## Results

(defaults: m = 1 kg, k = (2π)² N/m so ω₀ = 2π rad/s, F₀ = 1 N, dt = 2e-3 s)

- The peak sits **below** ω₀ and damping pulls it further left: ω_peak = **5.88 rad/s** at Q = 2 vs **6.27 rad/s** at Q = 10 (theory: $\sqrt{\omega_0^2 - 2\gamma^2}$) - sim peaks land within one grid step every time
- Peak amplitude: sim vs theory agrees to **4e-04** (Q = 2) and **9e-04** (Q = 5) relative error; the Q = 10 peak is **4.7× taller** than Q = 2 - lighter damping, sharper and higher resonance
- Q from bandwidth: **1.74 / 4.82 / 9.14** measured vs **2 / 5 / 10** true - see Limitations, this is the grid talking, not the physics
- Free decay: fitted γ = **0.31416** vs theory **0.31416** 1/s, rel err **1.7e-07** - the integrator is effectively exact here

Verification block printed by the script:

```
=== VERIFICATION ===
Q = 2  (b = 3.1416 kg/s, gamma = 1.5708 1/s)
  peak amp:   sim 0.05230 vs theory 0.05232 m   rel err 4.17e-04
Q = 5  (b = 1.2566 kg/s, gamma = 0.6283 1/s)
  peak amp:   sim 0.12718 vs theory 0.12729 m   rel err 8.83e-04
Q = 10  (b = 0.6283 kg/s, gamma = 0.3142 1/s)
  peak amp:   sim 0.24695 vs theory 0.25362 m   rel err 2.63e-02
decay rate: fit 0.31416 vs theory 0.31416 1/s   rel err 1.68e-07
```

## Limitations

- The bandwidth<->Q mapping assumes $\gamma \ll \omega_0$; at Q = 2 the peak is broad and slightly asymmetric, so the measured Q is worst exactly there
- Peak height/position resolution is set by the sweep grid - at Q = 10 the whole FWHM spans ~2 grid points, which is where the 2.6% peak-amplitude error comes from (the decay fit shows the integrator itself is good to 1e-7)
- Amplitude is measured from the tail extrema - no phase information, so the phase-lag curve is unchecked
- Fixed-step integrator with no adaptivity; fine at these frequencies, unproven for stiff cases

## TODO

- Phase-lag vs drive frequency, checked against $\arctan(2\gamma\omega / (\omega_0^2-\omega^2))$
- Parabolic peak interpolation (or an adaptive sweep) to break the grid limit on Q
- Add a cubic term (Duffing) and watch the resonance peak bend and hysterese
