# Installation

## WorkBuddy: project-installed kit (recommended)

Copy the repository into the teacher's project folder and open the folder in
WorkBuddy. The app picks up the `physics-animation` skill, the `new-topic`
and `memory-review` commands, the auto-injected `.workbuddy/memory/MEMORY.md`
index, and the memory hooks declared by `.workbuddy-plugin/plugin.json`.
Nothing is installed outside the project.

The hooks call `python3` with the `${CODEBUDDY_PLUGIN_ROOT}` placeholder, the
same pattern WorkBuddy's own built-in plugins use. On Windows change
`python3` to `python` in `hooks/hooks.json`.

## Codex / other harnesses

The same repository ships a Codex plugin and marketplace:

```bash
codex plugin marketplace add <repo>/.agents/plugins
codex plugin install alevel-physics-animations
```

## Python and rendering

- The CLI prefers the WorkBuddy-managed Python
  (`~/.workbuddy/binaries/python/envs/manim`, then `envs/default`), then the
  interpreter that launched it. Override with `PHYSICS_ANIM_PYTHON`.
- Manim needs pycairo: wheels exist for Linux and Windows; on macOS install
  cairo first (`brew install cairo pkg-config`). PPT decks, memory and tests
  run everywhere without Manim.
- `python -m pip install -r requirements.txt` installs the exact pinned
  dependency set (resolved for Python 3.12 by `uv pip compile`; regenerate
  with `uv pip compile requirements.in -o requirements.txt`).

## Local development

```bash
python -m pip install -r requirements-dev.txt
make verify
```

`make verify` prefers `work/.venv/bin/python` when present. `make
dist-local` builds the offline package for the current platform; CI builds
all platforms with pre-rendered videos and vendored wheels.
