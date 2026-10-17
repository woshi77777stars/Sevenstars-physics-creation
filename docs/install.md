# Installation

## For the teacher (installed plugin)

After `codex plugin install alevel-physics-animations`, ask in a new
conversation for an animation. The skills route the request and run the CLI.
On first video render the CLI needs Python 3.10+, Manim CE, and ffmpeg:

```bash
python -m pip install -r plugins/alevel-physics-animations/requirements.txt
python plugins/alevel-physics-animations/scripts/anim.py install-check
```

`imageio-ffmpeg` supplies a static ffmpeg binary, so no system ffmpeg or
LaTeX installation is required.

Platform note for local video rendering: Manim depends on pycairo, which
provides wheels for Linux and Windows but not macOS. On Linux/Windows
`pip install manim` is enough. On macOS install cairo first via Homebrew
(`brew install cairo pkg-config`) before `pip install manim`; PPT decks,
memory and tests run everywhere without it.

For local runs, `make verify` prefers the project virtualenv
(`work/.venv/bin/python`) when it exists and falls back to `python3`; pass
`PYTHON=<path>` to override.

## From the repository

```bash
python -m pip install -r requirements-dev.txt
make verify
```

`make verify` runs pytest, validates the plugin manifest, and smoke-builds
all 25 PPT decks. `make render-all` renders all scenes (slow; needs ffmpeg).
The Linux CI job also renders a scene end-to-end on every push, so video
rendering is verified even on machines without a local cairo install.

## Offline teacher package

`make dist-local` builds
`dist/alevel-physics-animations-offline-<version>-<os>-<arch>.zip` containing
the plugin, all pre-rendered MP4s, all pre-built PPT decks, vendored wheels
and ffmpeg, plus `install.sh` / `install.ps1` that work without a network.
Run the installer, open the examples, and the plugin is ready.
