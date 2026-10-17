# Verification: every claim maps to a command

Run `make verify` for the complete suite, or target one check:

| Claim | Command |
|-------|---------|
| All 25 topics have scenes, decks and red lines | `python -m pytest tests/test_registry.py -q` |
| Projectile vertical gaps are 1:3:5:7… | `python -m pytest tests/test_redlines.py::test_projectile_horizontal_red_lines -q` |
| a = v²/r points inward, perpendicular to v | `python -m pytest tests/test_redlines.py::test_circular_motion_acceleration_inward_and_perpendicular -q` |
| Pendulum/spring periods match T = 2π√(...) | `python -m pytest tests/test_redlines.py::test_pendulum_and_spring_periods -q` |
| RC decay falls by e each τ; half-life invariant | `python -m pytest tests/test_redlines.py::test_rc_and_nuclear_decay -q` |
| Transformer, RMS, divider, terminal p.d. | `python -m pytest tests/test_redlines.py::test_circuits_and_power tests/test_redlines.py::test_ac_and_transformer -q` |
| Photoelectric threshold and E = hf | `python -m pytest tests/test_redlines.py::test_quantum_red_lines -q` |
| Hubble v = H₀d; brightness ∝ 1/d² | `python -m pytest tests/test_redlines.py::test_hubble_brightness_mass_energy_xray -q` |
| Memory seed has all 7 sections; init is idempotent | `python -m pytest tests/test_memory_file.py -q` |
| Secrets rejected and never echoed | `python -m pytest tests/test_privacy.py -q` |
| Gate blocks an unwritten modification and passes after the write | `python -m pytest tests/test_hooks.py::test_gate_blocks_when_request_not_written tests/test_hooks.py::test_gate_passes_after_memory_updated -q` |
| Gate checks each turn separately; bare nouns don't fire | `python -m pytest tests/test_hooks.py::test_gate_checks_each_turn_separately tests/test_hooks.py::test_bare_nouns_do_not_trigger -q` |
| Gate parses the real WorkBuddy transcript shape (input_text) | `python -m pytest tests/test_hooks.py -q -k workbuddy` |
| Python resolution: override > project venv > current | `python -m pytest tests/test_runtime.py -q` |
| WorkBuddy hook/plugin/skill manifests are native format | `python -m pytest tests/test_hooks.py -q -k manifest` |
| Every PPT step has a native click animation | `python -m pytest tests/test_ppt.py -q` |
| Plugin manifest is installable | `python3 scripts/verify.py` (also runs the bundled plugin-creator validator when available) |
| One scene actually renders | `python plugins/alevel-physics-animations/scripts/anim.py render physical-quantities --scene UnitsAndVectors --1080p30` |

`scripts/verify.py` checks the manifest, the repo marketplace entry and the
scaffold, and delegates to the bundled `plugin-creator` validator when it is
discoverable on the machine.
