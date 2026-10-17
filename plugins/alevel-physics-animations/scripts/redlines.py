"""Physics red lines for CIE 9702 (AS + A2).

This module is the single source of truth shared by the Manim scenes and the
test suite. It has zero dependencies (standard library only) so tests can run
without Manim installed. Scenes must compute their displayed quantities from
the helpers below; the tests assert the helpers reproduce the physics.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


G = 9.81  # m/s^2, free-fall acceleration


@dataclass(frozen=True)
class RedLine:
    id: str
    text: str


@dataclass(frozen=True)
class Topic:
    id: str
    number: int
    name: str
    red_lines: tuple[RedLine, ...]


def _rl(topic_id: str, n: int, text: str) -> RedLine:
    return RedLine(id=f"{topic_id}-{n}", text=text)


TOPICS: tuple[Topic, ...] = (
    Topic(
        "physical-quantities",
        1,
        "Physical quantities and units",
        (_rl("physical-quantities", "units-homogeneous", "Equations must be dimensionally homogeneous."),
         _rl("physical-quantities", "vector-addition", "Vectors add tip-to-tail (triangle/parallelogram), scalars add arithmetically.")),
    ),
    Topic(
        "kinematics",
        2,
        "Kinematics (projectiles and free fall)",
        (_rl("kinematics", "horizontal-constant", "Horizontal velocity is constant; equal-time horizontal gaps are equal."),
         _rl("kinematics", "vertical-1-3-5", "Vertical displacement gaps in equal time intervals follow 1:3:5:7..."),
         _rl("kinematics", "fall-time-independent", "Time of flight depends only on vertical motion, not horizontal speed."),
         _rl("kinematics", "parabola", "The projectile path is a parabola; free-fall distance grows as t^2.")),
    ),
    Topic(
        "dynamics",
        3,
        "Dynamics (Newton's laws and momentum)",
        (_rl("dynamics", "fma", "Net force equals mass times acceleration: F = ma."),
         _rl("dynamics", "momentum-conserved", "Total momentum is conserved in collisions when no external force acts.")),
    ),
    Topic(
        "forces-density-pressure",
        4,
        "Forces, density and pressure",
        (_rl("forces-density-pressure", "moments-balance", "Clockwise and anticlockwise moments balance about a pivot in equilibrium."),
         _rl("forces-density-pressure", "upthrust-displaced", "Upthrust equals the weight of displaced fluid: rho g V.")),
    ),
    Topic(
        "work-energy-power",
        5,
        "Work, energy and power",
        (_rl("work-energy-power", "kinetic-energy", "Kinetic energy = 1/2 m v^2; work done = F s cos(theta)."),
         _rl("work-energy-power", "conservation", "Mechanical energy is conserved in the absence of dissipative forces.")),
    ),
    Topic(
        "deformation",
        6,
        "Deformation of solids",
        (_rl("deformation", "hooke-limit", "F is proportional to x only up to the elastic limit."),
         _rl("deformation", "area-energy", "Elastic energy stored equals the area under the force-extension graph (1/2 k x^2).")),
    ),
    Topic(
        "waves",
        7,
        "Waves",
        (_rl("waves", "v-f-lambda", "Wave speed v = f * lambda."),
         _rl("waves", "particle-vs-wave", "Particles oscillate about fixed positions; only energy/phase travels at v."),
         _rl("waves", "phase-linear", "Phase changes linearly with distance along the wave.")),
    ),
    Topic(
        "superposition",
        8,
        "Superposition",
        (_rl("superposition", "constructive-n-lambda", "Constructive interference when path difference = n * lambda."),
         _rl("superposition", "node-lambda-2", "Adjacent nodes (and antinodes) of a stationary wave are lambda/2 apart."),
         _rl("superposition", "double-slit-equal", "Double-slit fringes are equally spaced, spacing = lambda D / s.")),
    ),
    Topic(
        "electricity",
        9,
        "Electricity",
        (_rl("electricity", "ohms-law", "For an ohmic conductor V = IR (straight I-V line through origin)."),
         _rl("electricity", "power", "P = VI = I^2 R = V^2 / R."),
         _rl("electricity", "iv-shapes", "Diode conducts in one direction only; filament resistance rises with temperature.")),
    ),
    Topic(
        "dc-circuits",
        10,
        "D.C. circuits",
        (_rl("dc-circuits", "kirchhoff", "Current in = current out at a junction; EMFs balance p.d.s around a loop."),
         _rl("dc-circuits", "terminal-pd", "Terminal p.d. = EMF - I r (internal resistance)."),
         _rl("dc-circuits", "divider", "Potential divider: V_out = V_in R2 / (R1 + R2).")),
    ),
    Topic(
        "particle-physics",
        11,
        "Particle physics",
        (_rl("particle-physics", "conservation", "Charge, baryon number and lepton number are conserved in every interaction."),),
    ),
    Topic(
        "circular-motion",
        12,
        "Motion in a circle",
        (_rl("circular-motion", "accel-inward", "Acceleration a = v^2/r points to the centre, always perpendicular to v."),
         _rl("circular-motion", "v-omega-r", "v = omega r; a = r omega^2.")),
    ),
    Topic(
        "gravitational-fields",
        13,
        "Gravitational fields",
        (_rl("gravitational-fields", "inverse-square", "g = GM/r^2: field strength follows an inverse-square law."),
         _rl("gravitational-fields", "kepler", "Kepler's third law: T^2 is proportional to r^3 for circular orbits.")),
    ),
    Topic(
        "temperature",
        14,
        "Temperature",
        (_rl("temperature", "zeroth-law", "Temperature is defined by thermal equilibrium; heat flows hot to cold, never the reverse."),),
    ),
    Topic(
        "ideal-gases",
        15,
        "Ideal gases",
        (_rl("ideal-gases", "pv-t", "For a fixed amount of gas pV/T is constant; pressure arises from molecular collisions."),),
    ),
    Topic(
        "thermodynamics",
        16,
        "Thermodynamics",
        (_rl("thermodynamics", "first-law", "First law: Delta U = q + W."),
         _rl("thermodynamics", "adiabatic-vs-isothermal", "An adiabatic p-V curve is steeper than an isothermal one through the same point.")),
    ),
    Topic(
        "oscillations",
        17,
        "Oscillations",
        (_rl("oscillations", "shm-accel", "SHM: a = -omega^2 x; energy swaps between KE and PE."),
         _rl("oscillations", "pendulum-period", "Small-angle pendulum: T = 2 pi sqrt(L/g), independent of amplitude and mass."),
         _rl("oscillations", "spring-period", "Mass-spring: T = 2 pi sqrt(m/k), independent of amplitude.")),
    ),
    Topic(
        "electric-fields",
        18,
        "Electric fields",
        (_rl("electric-fields", "field-f-q", "Electric field strength E = F/q; field lines run from + to -."),
         _rl("electric-fields", "coulomb", "Point-charge force follows Coulomb's inverse-square law.")),
    ),
    Topic(
        "capacitance",
        19,
        "Capacitance",
        (_rl("capacitance", "q-cv", "Charge stored Q = CV; energy stored = 1/2 C V^2."),
         _rl("capacitance", "tau-rc", "Discharge is exponential with time constant tau = RC; V falls by e every tau.")),
    ),
    Topic(
        "magnetic-fields",
        20,
        "Magnetic fields",
        (_rl("magnetic-fields", "perpendicular", "F = BIL sin(theta) / Bqv sin(theta) is perpendicular to both B and the current/velocity."),
         _rl("magnetic-fields", "right-hand-rule", "Field and force directions follow the right-hand rule consistently.")),
    ),
    Topic(
        "alternating-currents",
        21,
        "Alternating currents",
        (_rl("alternating-currents", "rms", "V_rms = V_0 / sqrt(2)."),
         _rl("alternating-currents", "transformer", "Ideal transformer: V_s / V_p = N_s / N_p.")),
    ),
    Topic(
        "quantum-physics",
        22,
        "Quantum physics",
        (_rl("quantum-physics", "photon-energy", "Photon energy E = h f."),
         _rl("quantum-physics", "threshold", "No photoelectrons are emitted below the threshold frequency, whatever the intensity.")),
    ),
    Topic(
        "nuclear-physics",
        23,
        "Nuclear physics",
        (_rl("nuclear-physics", "mass-energy", "Mass-energy equivalence E = m c^2."),
         _rl("nuclear-physics", "half-life", "N = N0 e^(-lambda t); half-life does not depend on the starting amount.")),
    ),
    Topic(
        "medical-physics",
        24,
        "Medical physics",
        (_rl("medical-physics", "ultrasound", "Ultrasound: f = v/lambda; strong reflection at tissue interfaces."),
         _rl("medical-physics", "xray-attenuation", "X-ray intensity falls exponentially: I = I0 e^(-mu x).")),
    ),
    Topic(
        "astronomy-cosmology",
        25,
        "Astronomy and cosmology",
        (_rl("astronomy-cosmology", "hubble", "Hubble's law: recessional velocity v = H0 d."),
         _rl("astronomy-cosmology", "brightness", "Apparent brightness is inversely proportional to distance squared.")),
    ),
)

TOPICS_BY_ID = {t.id: t for t in TOPICS}
RED_LINES = {rl.id: rl for t in TOPICS for rl in t.red_lines}


def assert_topic(topic_id: str) -> Topic:
    if topic_id not in TOPICS_BY_ID:
        raise KeyError(f"Unknown topic {topic_id!r}. Valid: {sorted(TOPICS_BY_ID)}")
    return TOPICS_BY_ID[topic_id]


# ---------------------------------------------------------------------------
# Pure physics helpers. Scenes and tests must both use these.
# ---------------------------------------------------------------------------


def projectile_positions(u: float, angle_deg: float, dt: float, n: int):
    """Return [(x, y), ...] for n samples at t = 0, dt, 2dt, ... with y measured up."""
    theta = math.radians(angle_deg)
    vx = u * math.cos(theta)
    vy = u * math.sin(theta)
    return [(vx * i * dt, vy * i * dt - 0.5 * G * (i * dt) ** 2) for i in range(n)]


def free_fall_distance(t: float, g: float = G) -> float:
    return 0.5 * g * t * t


def equal_time_gaps(values) -> list[float]:
    """Gaps between consecutive samples (used for the 1:3:5 check)."""
    return [values[i] - values[i - 1] for i in range(1, len(values))]


def circular_state(r: float, omega: float, t: float):
    """Position, velocity and acceleration of uniform circular motion."""
    theta = omega * t
    x, y = r * math.cos(theta), r * math.sin(theta)
    vx, vy = -omega * r * math.sin(theta), omega * r * math.cos(theta)
    ax, ay = -omega * omega * r * math.cos(theta), -omega * omega * r * math.sin(theta)
    return (x, y), (vx, vy), (ax, ay)


def shm_state(a: float, omega: float, t: float, phi: float = 0.0):
    """Displacement, velocity, acceleration for SHM."""
    phase = omega * t + phi
    x = a * math.cos(phase)
    v = -a * omega * math.sin(phase)
    acc = -a * omega * omega * math.cos(phase)
    return x, v, acc


def pendulum_period(length: float, g: float = G) -> float:
    return 2.0 * math.pi * math.sqrt(length / g)


def spring_period(mass: float, k: float) -> float:
    return 2.0 * math.pi * math.sqrt(mass / k)


def rc_discharge(v0: float, t: float, tau: float) -> float:
    return v0 * math.exp(-t / tau)


def radioactive_decay(n0: float, t: float, half_life: float) -> float:
    return n0 * 0.5 ** (t / half_life)


def inverse_square(scale: float, r: float) -> float:
    return scale / (r * r)


def kepler_period(r: float, gm: float) -> float:
    return 2.0 * math.pi * math.sqrt(r ** 3 / gm)


def rms(peak: float) -> float:
    return peak / math.sqrt(2.0)


def ideal_transformer(vp: float, np: float, ns: float) -> float:
    return vp * ns / np


def hubble_velocity(distance_m: float, h0: float = 2.2e-18) -> float:
    return h0 * distance_m


def apparent_brightness(luminosity: float, distance: float) -> float:
    return luminosity / (4.0 * math.pi * distance * distance)


def coulomb_force(q1: float, q2: float, r: float, k: float = 8.99e9) -> float:
    return k * q1 * q2 / (r * r)


def lorentz_force(q: float, v: float, b: float, theta_deg: float = 90.0) -> float:
    return q * v * b * math.sin(math.radians(theta_deg))


def conductor_force(b: float, i: float, length: float, theta_deg: float = 90.0) -> float:
    return b * i * length * math.sin(math.radians(theta_deg))


def doppler_frequency(f: float, v_source: float, v_wave: float) -> float:
    """Frequency received when a source moves toward the observer."""
    return f * v_wave / (v_wave - v_source)


def double_slit_spacing(wavelength: float, screen_distance: float, slit_separation: float) -> float:
    return wavelength * screen_distance / slit_separation


def stationary_node_spacing(wavelength: float) -> float:
    return wavelength / 2.0


def photoelectric_emits(frequency: float, threshold: float) -> bool:
    return frequency >= threshold


def photon_energy(frequency: float, h: float = 6.63e-34) -> float:
    return h * frequency


def pv_over_t(p: float, v: float, t: float) -> float:
    return p * v / t


def work_done(force: float, displacement: float, theta_deg: float = 0.0) -> float:
    return force * displacement * math.cos(math.radians(theta_deg))


def kinetic_energy(mass: float, velocity: float) -> float:
    return 0.5 * mass * velocity * velocity


def elastic_energy(k: float, x: float) -> float:
    return 0.5 * k * x * x


def divider_voltage(vin: float, r1: float, r2: float) -> float:
    return vin * r2 / (r1 + r2)


def terminal_pd(emf: float, current: float, internal_r: float) -> float:
    return emf - current * internal_r


def hydrostatic_pressure(density: float, height: float, g: float = G) -> float:
    return density * g * height


def upthrust(density: float, volume: float, g: float = G) -> float:
    return density * g * volume


def first_law(q: float, w: float) -> float:
    return q + w


def wave_speed(frequency: float, wavelength: float) -> float:
    return frequency * wavelength


def constructive_path_difference(n: int, wavelength: float) -> float:
    return n * wavelength


def xray_attenuation(i0: float, mu: float, x: float) -> float:
    return i0 * math.exp(-mu * x)


def ultrasound_wavelength(frequency: float, speed: float) -> float:
    return speed / frequency


def mass_energy(mass: float, c: float = 3.0e8) -> float:
    return mass * c * c


def moments_balance(force_l: float, arm_l: float, force_r: float, arm_r: float) -> bool:
    return math.isclose(force_l * arm_l, force_r * arm_r, rel_tol=1e-9, abs_tol=1e-12)


def capacitance_energy(c: float, v: float) -> float:
    return 0.5 * c * v * v


def ohms_law(v: float, i: float, r: float) -> bool:
    return math.isclose(v, i * r, rel_tol=1e-9)
