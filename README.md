# A-Level Physics Animations (CIE 9702)

A classroom animation kit for A-Level Physics teachers, built **natively for
WorkBuddy** as a project-installed kit, with a Codex/Claude-compatible
package alongside.

- **Continuous motion → Manim MP4.** 25 CIE 9702 topics, 28 scenes. Every
  displayed quantity is computed from tested physics helpers in
  `plugins/alevel-physics-animations/scripts/redlines.py`, so the drawings
  cannot violate their red lines (projectile 1:3:5 vertical spacing,
  a = v²/r inward, τ = RC exponential decay, photoelectric threshold...).
- **Sequential text → native PowerPoint animation.** 25 editable `.pptx`
  decks, one click effect per step.
- **Memory that travels with the project.** A single structured
  `PHYSICS-MEMORY.md` at the project root: habits, physics red lines, an
  error archive, modification records and delete-with-trace. Session hooks
  (WorkBuddy `hooks/hooks.json`) load it at session start and **block the
  turn end** when a teacher modification request was seen but not written
  back.
- **Privacy.** Credentials, student data, intranet addresses and absolute
  paths are filtered out of memory and courseware (`anim scrub`).

## Install

### WorkBuddy (project-installed kit — recommended)

**Teachers:** download the matching release package from GitHub Releases,
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

The package includes the platform wheels, ffmpeg, pre-rendered MP4s and all
PPT decks, so the teacher does not install Manim, cairo or ffmpeg. The
installer prefers WorkBuddy-managed Python, then falls back to a Python 3.10+
interpreter on `PATH`.

The app discovers:

- the `physics-animation` skill (`skills/physics-animation/`);
- the commands `new-topic` and `memory-review` (`commands/`);
- the auto-injected memory index (`.workbuddy/memory/MEMORY.md`);
- the memory gates (`hooks/hooks.json`, declared by
  `.workbuddy-plugin/plugin.json`).

Everything lives inside the project; nothing is written outside it.

**Developers:** run from source:

```bash
python plugins/alevel-physics-animations/scripts/anim.py setup
```

This creates the project venv. On macOS, Manim additionally needs
`brew install cairo pkg-config`.

### Codex / other harnesses

`plugins/alevel-physics-animations/` is a Codex plugin
(`.codex-plugin/plugin.json`) with a repo marketplace at
`.agents/plugins/marketplace.json`:

```bash
codex plugin marketplace add <path-to-this-repo>/.agents/plugins
codex plugin install alevel-physics-animations
```

## Usage

Say "做一个平抛演示动画" or run the CLI directly:

```bash
python plugins/alevel-physics-animations/scripts/anim.py setup   # once: project venv + pinned deps
python plugins/alevel-physics-animations/scripts/anim.py topics
python plugins/alevel-physics-animations/scripts/anim.py render kinematics --1080p30
python plugins/alevel-physics-animations/scripts/anim.py ppt capacitance
python plugins/alevel-physics-animations/scripts/anim.py memory report
```

Deliveries always use `--1080p30` (1920×1080 @ 30 fps). The default without
the flag is a fast 480p15 preview. On teacher machines the CLI prefers the
WorkBuddy-managed Python (`.workbuddy/binaries/python/envs/manim`, falling
back to `envs/default`); override with `PHYSICS_ANIM_PYTHON`.

## Memory gate

- `SessionStart` prints the memory summary and records a baseline.
- `Stop` scans only the new user messages since the last check (per-turn
  accounting). If any looks like a modification request and
  `PHYSICS-MEMORY.md` was not modified, it exits `2` and blocks the turn
  until the change is written.
- Bare nouns ("颜色/字体/标题") do not trigger the gate; verbs and
  imperatives do ("把颜色改成蓝色", "change the color to red").

## Verify and release

`make verify` runs the physics, memory, privacy and PPT tests, validates both
manifests, and smoke-builds all decks. CI renders every scene and builds a
full offline package for Linux, Apple Silicon macOS and Windows.
A local build refuses to create an `offline` package when wheels, ffmpeg or
videos are missing; it can still emit an honest `ppt-only` or `renderer`
package when those pieces are present.

Before distributing, complete [docs/acceptance-checklist.md](docs/acceptance-checklist.md)
on at least two real machines (one Windows).

## Layout

```text
skills/physics-animation/   WorkBuddy skill + manifest (compat: workbuddy, ...)
commands/                   new-topic, memory-review
hooks/hooks.json            SessionStart + Stop memory gates
PHYSICS-MEMORY.md           the teacher memory (single source, travels with project)
USER.md                     per-project preferences
.workbuddy/memory/MEMORY.md auto-injected memory index
plugins/alevel-physics-animations/  engine: CLI, scenes, decks, red lines
tests/  docs/  .github/workflows/ci.yml
```

## License

MIT.
