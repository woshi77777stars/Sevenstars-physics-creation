# A-Level Physics Animations (CIE 9702)

A native WorkBuddy plugin for A-Level Physics teachers. Two pipelines, one
memory, strict privacy:

- **Continuous motion -> Manim MP4.** 25 CIE 9702 topics, ~28 scenes. Every
  scene is built from tested physics helpers so it cannot violate its "red
  lines" (projectile 1:3:5 vertical spacing, a = v²/r inward, exponential RC
  discharge, threshold photoelectric behaviour, and so on).
- **Sequential text -> native PowerPoint animation.** 25 editable `.pptx`
  decks; each step appears on click through real PowerPoint `<p:timing>`
  entrance effects.
- **Memory.** Every teacher-requested modification is recorded automatically
  (repeats just count up), fixed mistakes are recorded automatically, habits
  are remembered on request, and "forget" always leaves a tombstone. New
  conversations load this memory first and apply it.
- **Privacy.** Credentials, student data, intranet addresses and absolute
  paths are filtered out of memory and courseware.

Everything is pure skills + scripts: no MCP servers, no extra frameworks.

Before publishing the repo, replace the placeholder `author`, `homepage` and
`repository` values in `plugins/alevel-physics-animations/.codex-plugin/plugin.json`.

## Install (WorkBuddy / Codex)

```bash
codex plugin marketplace add <path-to-this-repo>/.agents/plugins
codex plugin install alevel-physics-animations
```

Or install straight from the checked-out repo's marketplace entry. The plugin
adds three skills: `alevel-physics-animations` (router + memory + privacy),
`render-video`, and `build-ppt`.

## Quick start

```bash
python scripts/anim.py install-check     # from plugins/alevel-physics-animations/
python scripts/anim.py topics
python scripts/anim.py render kinematics --1080p30
python scripts/anim.py ppt capacitance
python scripts/anim.py memory add habit --kind presentation --content "Use a 16:9 layout"
python scripts/anim.py verify
```

See [docs/install.md](docs/install.md) for Python/Manim/ffmpeg setup and
[docs/verification.md](docs/verification.md) for what each command proves.

## Repository layout

```text
plugins/alevel-physics-animations/   the installable plugin (self-contained)
  skills/                            routing + video + ppt + memory reference
  scripts/anim.py                    single CLI
  scripts/redlines.py                single source of physics truth
  scripts/scenes/*.py                ~28 Manim scenes with SCENE_META
  scripts/content/*.deck.json        25 data-driven PPT decks
  scripts/{memory,privacy}.py        memory store + privacy filter
tests/                               red-line, memory, privacy, ppt, registry tests
docs/                                red lines, install, verification
.github/workflows/ci.yml             full verification + offline dist matrix
```

## Verification and release

`make verify` runs the full suite; `make dist-local` builds the offline
teacher package for the current platform; CI builds all platforms on tags.
See [docs/verification.md](docs/verification.md).

## License

MIT. Content and code are provided for teaching; verify against the current
official CIE 9702 syllabus before classroom use.
