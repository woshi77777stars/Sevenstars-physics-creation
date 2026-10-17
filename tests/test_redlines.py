import math

import pytest

from redlines import (
    RED_LINES,
    TOPICS,
    apparent_brightness,
    capacitance_energy,
    circular_state,
    conductor_force,
    constructive_path_difference,
    coulomb_force,
    divider_voltage,
    doppler_frequency,
    double_slit_spacing,
    elastic_energy,
    equal_time_gaps,
    first_law,
    free_fall_distance,
    hubble_velocity,
    hydrostatic_pressure,
    ideal_transformer,
    inverse_square,
    kepler_period,
    kinetic_energy,
    lorentz_force,
    mass_energy,
    moments_balance,
    ohms_law,
    pendulum_period,
    photoelectric_emits,
    photon_energy,
    projectile_positions,
    pv_over_t,
    radioactive_decay,
    rc_discharge,
    rms,
    shm_state,
    spring_period,
    stationary_node_spacing,
    terminal_pd,
    ultrasound_wavelength,
    upthrust,
    wave_speed,
    work_done,
    xray_attenuation,
)


def test_registry_covers_all_25_topics():
    assert len(TOPICS) == 25
    assert [t.number for t in TOPICS] == list(range(1, 26))
    for topic in TOPICS:
        assert topic.red_lines, topic.id
    for rl in RED_LINES.values():
        assert rl.id in {r.id for t in TOPICS for r in t.red_lines}


def test_projectile_horizontal_red_lines():
    points = projectile_positions(u=12.0, angle_deg=0.0, dt=0.5, n=7)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    gaps_x = equal_time_gaps(xs)
    gaps_y = equal_time_gaps(ys)
    assert all(abs(g - gaps_x[0]) < 1e-12 for g in gaps_x)  # horizontal constant
    ratio = [g / gaps_y[0] for g in gaps_y]
    assert ratio == pytest.approx([1.0, 3.0, 5.0, 7.0, 9.0, 11.0])


def test_projectile_fall_time_independent_of_horizontal_speed():
    slow = projectile_positions(u=5.0, angle_deg=0.0, dt=0.5, n=9)
    fast = projectile_positions(u=20.0, angle_deg=0.0, dt=0.5, n=9)
    assert slow[-1][1] == pytest.approx(fast[-1][1])


def test_free_fall_t_squared():
    assert free_fall_distance(1.0) == pytest.approx(4.905)
    assert free_fall_distance(2.0) == pytest.approx(4 * free_fall_distance(1.0))


def test_circular_motion_acceleration_inward_and_perpendicular():
    for t in (0.0, 0.3, 1.1, 2.5):
        pos, vel, acc = circular_state(r=2.0, omega=0.9, t=t)
        v_mag = math.hypot(*vel)
        a_mag = math.hypot(*acc)
        assert v_mag == pytest.approx(0.9 * 2.0)
        assert a_mag == pytest.approx(0.9**2 * 2.0)  # v^2/r = omega^2 r
        dot = vel[0] * acc[0] + vel[1] * acc[1]
        assert dot == pytest.approx(0.0, abs=1e-12)  # perpendicular
        radial = pos[0] * acc[0] + pos[1] * acc[1]
        assert radial < 0  # points inward


def test_shm_acceleration_proportional_to_displacement():
    for t in (0.0, 0.2, 0.7):
        x, _v, a = shm_state(a=0.5, omega=2.0, t=t)
        assert a == pytest.approx(-(2.0**2) * x)


def test_pendulum_and_spring_periods():
    assert pendulum_period(1.0) == pytest.approx(2.006, abs=0.001)
    assert spring_period(1.0, 4.0) == pytest.approx(math.pi, abs=1e-9)
    # amplitude and (pendulum) mass do not enter either formula


def test_rc_and_nuclear_decay():
    assert rc_discharge(5.0, 1.0, 1.0) == pytest.approx(5.0 / math.e)
    assert rc_discharge(5.0, 2.0, 1.0) == pytest.approx(5.0 / math.e**2)
    assert radioactive_decay(8.0, 2.0, 1.0) == pytest.approx(2.0)
    assert radioactive_decay(8.0, 1.0, 1.0) == pytest.approx(4.0)


def test_inverse_square_family():
    assert inverse_square(9.0, 2.0) == pytest.approx(9.0 / 4.0)
    assert apparent_brightness(32 * math.pi, 2.0) == pytest.approx(8.0 / 4.0)
    assert coulomb_force(1.0, 2.0, 2.0) == pytest.approx(coulomb_force(1.0, 2.0, 1.0) / 4.0)


def test_kepler_third_law():
    t1 = kepler_period(1.0, 4.0)
    t2 = kepler_period(2.0, 4.0)
    assert (t1**2 / 1.0**3) == pytest.approx(t2**2 / 2.0**3)


def test_circuits_and_power():
    assert ohms_law(12.0, 2.0, 6.0)
    assert divider_voltage(10.0, 100.0, 100.0) == pytest.approx(5.0)
    assert terminal_pd(12.0, 2.0, 0.5) == pytest.approx(11.0)
    assert terminal_pd(12.0, 2.0, 0.5) < 12.0


def test_energy_helpers():
    assert kinetic_energy(2.0, 3.0) == pytest.approx(9.0)
    assert elastic_energy(4.0, 0.5) == pytest.approx(0.5)
    assert capacitance_energy(2.0, 3.0) == pytest.approx(9.0)
    assert work_done(10.0, 2.0) == pytest.approx(20.0)
    assert first_law(100.0, 40.0) == pytest.approx(140.0)


def test_fluids_and_moments():
    assert hydrostatic_pressure(1000.0, 10.0) == pytest.approx(98100.0)
    assert upthrust(1000.0, 0.001) == pytest.approx(9.81)
    assert moments_balance(2.0, 3.0, 3.0, 2.0)
    assert not moments_balance(2.0, 3.0, 3.0, 1.0)


def test_waves_and_superposition():
    assert wave_speed(2.0, 3.0) == pytest.approx(6.0)
    assert constructive_path_difference(2, 1.5) == pytest.approx(3.0)
    assert double_slit_spacing(5.0e-7, 2.0, 1.0e-3) == pytest.approx(1.0e-3)
    assert stationary_node_spacing(3.0) == pytest.approx(1.5)
    assert doppler_frequency(1000.0, 10.0, 340.0) > 1000.0
    assert ultrasound_wavelength(5.0e6, 1500.0) == pytest.approx(3.0e-4)


def test_electromagnetism_helpers():
    assert lorentz_force(1.6e-19, 2.0, 0.5) == pytest.approx(1.6e-19)
    assert lorentz_force(1.6e-19, 2.0, 0.5, 30.0) == pytest.approx(0.8e-19)
    assert conductor_force(0.5, 2.0, 0.4) == pytest.approx(0.4)


def test_ac_and_transformer():
    assert rms(10.0) == pytest.approx(10.0 / math.sqrt(2.0))
    assert ideal_transformer(240.0, 1000.0, 100.0) == pytest.approx(24.0)


def test_quantum_red_lines():
    f0 = 5.0e14
    assert not photoelectric_emits(f0 - 1.0, f0)
    assert photoelectric_emits(f0, f0)
    assert photoelectric_emits(f0 + 1.0, f0)
    assert photon_energy(f0) == pytest.approx(6.63e-34 * f0)


def test_gas_and_thermo_red_lines():
    assert pv_over_t(1.0, 2.0, 300.0) == pytest.approx(pv_over_t(2.0, 1.0, 300.0))
    assert pv_over_t(1.0, 2.0, 300.0) != pytest.approx(pv_over_t(1.0, 2.0, 600.0))


def test_hubble_brightness_mass_energy_xray():
    h0 = 2.2e-18
    d = 3.086e22  # 1 Mpc
    v = hubble_velocity(d, h0)
    assert v == pytest.approx(h0 * d)
    assert v / 1000.0 == pytest.approx(67.89, abs=0.1)
    assert apparent_brightness(32 * math.pi, 1.0) == pytest.approx(8.0)
    assert apparent_brightness(32 * math.pi, 2.0) == pytest.approx(2.0)
    assert mass_energy(1.0e-3) == pytest.approx(9.0e13)
    assert xray_attenuation(5.0, 1.0, 1.0) == pytest.approx(5.0 / math.e)
