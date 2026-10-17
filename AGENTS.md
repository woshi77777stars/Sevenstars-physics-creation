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

- One memory: `PHYSICS-MEMORY.md` at the project root (sections 1 habits,
  2 red lines, 3 pipelines, 4 error archive, 5 modifications, 6
  delete-with-trace, 7 open questions). Habits only on an explicit
  "remember"; mistakes and applied modifications are written automatically;
  "forget" moves the entry to section 6; no new info -> no write. This repo
  ships the empty seed; a teacher's personal entries live in their own copy.
- Credentials, student data, intranet addresses and absolute paths must never
  appear in memory, courseware, docs or comments. Run
  `python plugins/alevel-physics-animations/scripts/anim.py scrub <dir>`
  before delivering.

## Verification before finishing

- `make verify` must pass: pytest (red lines, memory, privacy, PPT animation
  XML, coverage registry), plugin manifest validation, PPT smoke build.
- Do not commit, push, or open PRs unless the user asks.
- **Mandatory memory close-out (cannot be skipped):** after applying any
  teacher change, write it into the right `PHYSICS-MEMORY.md` section in the
  same turn and report `记忆已更新：<内容>（第 N 区）`. The Stop hook
  (`hooks/session_end.py`) blocks the turn end when a modification request
  was detected but the memory file was not updated. Even without the hook,
  this step is mandatory before finishing any turn.

## Layout conventions

- Scratch work in `work/`, generated assets in `outputs/` and `dist/`
  (all gitignored). Deliverables land in the committed tree only on request.
