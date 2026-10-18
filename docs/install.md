# Installation

## WorkBuddy: project-installed kit (recommended)

For teachers, download the matching release package from GitHub Releases,
unzip it, and run the installer before opening the folder in WorkBuddy:

```bash
# macOS
unzip alevel-physics-animations-offline-<version>-darwin-<arch>.zip
cd alevel-physics-animations-offline-<version>-darwin-<arch>
bash install.sh
```

```powershell
# Windows PowerShell
Expand-Archive alevel-physics-animations-offline-<version>-windows-x64.zip
cd alevel-physics-animations-offline-<version>-windows-x64
.\install.ps1
```

The release package includes platform wheels, ffmpeg, pre-rendered MP4s and
PPT decks, so the teacher does not install Manim, cairo or ffmpeg. The
installer prefers WorkBuddy-managed Python, then falls back to a Python 3.10+
interpreter on `PATH`.
The app then picks up the `physics-animation` skill, the `new-topic` and
`memory-review` commands, the auto-injected `.workbuddy/memory/MEMORY.md`
index, and the memory hooks declared by `.workbuddy-plugin/plugin.json`.
Nothing is installed outside the project.

The hooks try `${CODEBUDDY_PLUGIN_ROOT}/.physics-anim-venv` first and then
fall back to `python3`/`python`. This covers an installed release package as
well as a source checkout on macOS, Linux and Windows.

## Codex / other harnesses

The same repository ships a Codex plugin and marketplace:

```bash
codex plugin marketplace add <repo>/.agents/plugins
codex plugin install alevel-physics-animations
```

## Python and rendering

- First run: `python plugins/alevel-physics-animations/scripts/anim.py setup`.
  It creates the project-local `.physics-anim-venv` (base interpreter is the
  WorkBuddy-managed Python when present), installs the pinned dependencies,
  and tolerates a missing Manim on macOS (cairo needed there). Offline:
  `anim setup --offline` installs from the vendored wheels in the offline
  package.
- Afterwards the CLI prefers that project venv, then the interpreter that
  launched it. Override with `PHYSICS_ANIM_PYTHON`.
- The CLI prefers the WorkBuddy-managed Python as the setup base on macOS,
  Linux and Windows (`bin/python3` and `python.exe` layouts).
- Manim needs pycairo: wheels exist for Linux and Windows; on macOS install
  cairo first (`brew install cairo pkg-config`) and re-run `anim setup`.
  PPT decks, memory and tests run everywhere without Manim.
- `python -m pip install -r requirements.txt` installs the exact pinned
  dependency set (resolved for Python 3.12 by `uv pip compile`; regenerate
  with `uv pip compile requirements.in -o requirements.txt`).

## Local development

```bash
python -m pip install -r requirements-dev.txt
make verify
```

`make verify` prefers `work/.venv/bin/python` when present. `make
dist-local` builds the current platform package and refuses to create a
misleading `offline` zip when required wheels, ffmpeg or videos are missing.
CI produces full offline packages for Linux, Apple Silicon macOS and Windows,
then publishes them to a GitHub Release when you push a `v*` tag.
