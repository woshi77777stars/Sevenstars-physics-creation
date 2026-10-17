# Physics red lines by topic (CIE 9702)

Each line below is asserted by `tests/test_redlines.py` or visible in a scene.
Scene ids live in `plugins/alevel-physics-animations/scripts/redlines.py`.

| # | Topic | Red lines |
|---|-------|-----------|
| 1 | Physical quantities and units | Equations are dimensionally homogeneous; vectors add tip-to-tail. |
| 2 | Kinematics | Horizontal equal-time gaps are equal; vertical gaps follow 1:3:5:7; time of flight ignores horizontal speed; the path is a parabola and free fall grows as t². |
| 3 | Dynamics | F = ma; total momentum conserved in collisions. |
| 4 | Forces, density and pressure | Moments balance about a pivot in equilibrium; upthrust = ρgV. |
| 5 | Work, energy and power | KE = ½mv²; W = Fs cosθ; mechanical energy conserved without dissipation. |
| 6 | Deformation of solids | F ∝ x only below the elastic limit; stored energy = area under F–x = ½kx². |
| 7 | Waves | v = fλ; particles vibrate in place while the wave travels; phase changes linearly with distance. |
| 8 | Superposition | Path difference nλ is constructive; nodes/antinodes are λ/2 apart; double-slit fringes are equally spaced. |
| 9 | Electricity | V = IR for ohmic conductors; P = VI = I²R; diode one-way, filament resistance rises. |
| 10 | D.C. circuits | Kirchhoff junction/loop laws; terminal p.d. = EMF − Ir; divider V_out = V_in R₂/(R₁+R₂). |
| 11 | Particle physics | Charge, baryon and lepton numbers conserved in every interaction. |
| 12 | Motion in a circle | a = v²/r inward and perpendicular to v; v = ωr. |
| 13 | Gravitational fields | g = GM/r² inverse square; Kepler T² ∝ r³. |
| 14 | Temperature | Temperature defined by thermal equilibrium; heat flows hot to cold. |
| 15 | Ideal gases | pV/T constant for a fixed amount; pressure from molecular collisions. |
| 16 | Thermodynamics | ΔU = q + W; adiabatic p–V curve steeper than isothermal. |
| 17 | Oscillations | a = −ω²x; pendulum T = 2π√(L/g) independent of mass/amplitude; spring T = 2π√(m/k). |
| 18 | Electric fields | E = F/q; lines + to −; Coulomb inverse square. |
| 19 | Capacitance | Q = CV; energy ½CV²; discharge exponential with τ = RC. |
| 20 | Magnetic fields | F = BIL sinθ / Bqv sinθ perpendicular to B and current/velocity; right-hand rule. |
| 21 | Alternating currents | V_rms = V₀/√2; transformer V_s/V_p = N_s/N_p. |
| 22 | Quantum physics | E = hf; no emission below threshold frequency at any intensity. |
| 23 | Nuclear physics | E = mc²; N = N₀e^(−λt); half-life independent of starting amount. |
| 24 | Medical physics | f = v/λ and reflection at interfaces; X-rays I = I₀e^(−μx). |
| 25 | Astronomy and cosmology | v = H₀d; apparent brightness ∝ 1/d². |

How a red line is honoured: the scene computes every displayed quantity from
the pure helpers in `redlines.py`, so the drawing inherits the correct
physics; the test suite then checks the helpers against hand-derived numbers
(for example projectile gaps at t = 0.5 s come out 1 : 3 : 5 : 7...).
