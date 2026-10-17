# AGENTS.md — A-Level Physics Animations

Project rules for every agent working in this repository. Section 1 of the
global AGENTS.md (secrets, privacy, machine information) always applies.

## Language

- All courseware, code, docs, commit messages and identifiers are English.
- Physics terms use standard CIE 9702 wording; formulas are Unicode, never LaTeX.

## Physics correctness (non-negotiable)

- Never hand-place physics quantities in an animation. Compute from
  `plugins/alevel-physics-animations/scripts/redlines.py`; tests assert the
  same helpers.
- Every scene declares `SCENE_META` with topic + red-line ids. Read
  `docs/redlines.md` before drawing anything.
- A red line that cannot be shown honestly must be reported, not faked.

## Pipelines

- Continuous motion -> Manim MP4 (`render-video` skill).
- Sequential text -> `.pptx` with native entrance animations (`build-ppt`).
- Static diagram -> PPT. Both -> PPT with embedded MP4.

## Memory and privacy

- Habits are written only on an explicit "remember"; mistakes are recorded
  automatically when fixed; every teacher-requested modification is recorded
  automatically when applied; "forget" writes a tombstone; no new info -> no
  write. Memory lives in `<home>/.physics-anim/memory/` and never in git.
- Credentials, student data, intranet addresses and absolute paths must never
  appear in memory, courseware, docs or comments. Run
  `python plugins/alevel-physics-animations/scripts/anim.py scrub <dir>`
  before delivering.

## Verification before finishing

- `make verify` must pass: pytest (red lines, memory, privacy, PPT animation
  XML, coverage registry), plugin manifest validation, PPT smoke build.
- Do not commit, push, or open PRs unless the user asks.

## Layout conventions

- Scratch work in `work/`, generated assets in `outputs/` and `dist/`
  (all gitignored). Deliverables land in the committed tree only on request.
