---
name: render-video
description: Render a CIE 9702 physics scene to an MP4 with Manim CE for the alevel-physics-animations plugin. Use when a teacher asks for a continuous-motion animation, video, or an animated physics demonstration.
---

# Render a physics video (Manim)

Goal: a 1920x1080 / 30 fps MP4 that visibly satisfies the scene's physics red lines, computed (never hand-placed) from `scripts/redlines.py`.

## Standard flow

1. List topics: `python scripts/anim.py topics`. Confirm the topic id (e.g. `kinematics`, `circular-motion`).
2. Render: `python scripts/anim.py render <topic> [--scene ClassName] [--1080p30] [--out outputs/videos]`.
   Without the flag you get a fast low-resolution preview (480p15); pass
   `--1080p30` for the classroom-quality 1920x1080 @ 30 fps file. `render-all`
   always renders every scene of every topic at classroom quality. **Any
   delivery must use `--1080p30`; a preview is never a deliverable.**
3. If the environment lacks Manim or ffmpeg: run `python scripts/anim.py install-check` and install the pinned requirements (`pip install -r requirements.txt`, which includes `imageio-ffmpeg` for a bundled static ffmpeg).
4. Verify the result exists at `outputs/videos/<topic>/<Scene>.mp4` and scrub it before delivery.

## Correctness discipline

- Before animating, read the topic's red lines in `docs/redlines.md`.
- Use the pure helpers in `scripts/redlines.py` for every displayed number (positions, periods, gaps, decay constants).
- Declare `SCENE_META = {"topic": ..., "title": ..., "red_lines": [...]}` at the very top of a scene file, before importing manim, so tooling can index it without Manim installed.
- One scene class per demonstration; put shared visuals in `scripts/scenes/_common.py`.

## Add a new scene

1. Create `scripts/scenes/<topic_extra>.py` with `SCENE_META` and a `Scene` subclass that imports helpers from `redlines`.
2. Confirm the red-line ids exist in `scripts/redlines.py` (`RED_LINES`).
3. Add a pytest for any new physics helper in `tests/test_redlines.py`.
4. Smoke-render with `python scripts/anim.py render <topic> --scene <ClassName>` before claiming it works.

## Known constraints

- No LaTeX: formulas are Unicode inside Manim `Text` (π, ², √, ω, λ, τ, Δ).
- Keep scenes short (5-15 s). Prefer small standard-axes diagrams over elaborate visuals.
- Abstract topics (medical, astronomy) show only animatable models: wave echoes, attenuation curves, Hubble plots. Never fabricate imagery.
