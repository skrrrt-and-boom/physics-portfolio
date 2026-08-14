# P3 - Quantum tunneling in 1D (in progress)

A classical particle bounces off a wall it can't climb; a quantum one leaks through. I want the numbers: how the transmission probability depends on barrier height and width, whether a time-dependent simulation reproduces the analytic rectangular-barrier coefficients, and how far the cheap WKB estimate drifts from the exact answer.

Working in dimensionless units ($\hbar = m = 1$).

## Model

Time-independent Schrödinger equation and its time-dependent evolution:

$$
-\frac{1}{2}\frac{d^2\psi}{dx^2} + V(x)\psi = E\psi,
\qquad
i\frac{\partial\psi}{\partial t} = \left(-\frac{1}{2}\frac{\partial^2}{\partial x^2} + V(x)\right)\psi
$$

Analytic transmission coefficient for a rectangular barrier of height $V_0$ and width $a$, with wave number $k=\sqrt{2E}$ and $\kappa=\sqrt{2|V_0-E|}$:

$$
T(E) = \left[1 + \frac{V_0^2\,\sinh^2(\kappa a)}{4E\,(V_0-E)}\right]^{-1} \quad (E<V_0),
\qquad
T(E) = \left[1 + \frac{V_0^2\,\sin^2(k' a)}{4E\,(E-V_0)}\right]^{-1} \quad (E>V_0)
$$

## Plan / TODO

- [x] Potential builders: rectangular barrier, finite square well
- [ ] Bound-state solver for the finite well (finite-difference Hamiltonian, sparse eigensolver)
- [ ] Time-dependent Gaussian wave-packet evolution - Crank-Nicolson or split-operator, norm conservation printed
- [ ] Transmission: integrate $|\psi|^2$ past the barrier after scattering; sweep $E$ vs analytic curve
- [ ] WKB tunneling estimate vs exact - quantify the error across $\kappa a$
- [ ] pytest suite + figures + results table with tolerances
