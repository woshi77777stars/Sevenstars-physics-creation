---
name: alevel-physics-animations
description: "Build classroom A-Level Physics (CIE 9702) animations for teachers: physics-red-line Manim videos, native-animation PowerPoint decks, and a private teacher memory. Use when a teacher asks for a physics animation, video, PPT courseware, or remember/forget for A-Level physics teaching."
---

# A-Level Physics Animations

You produce classroom assets for an A-Level Physics teacher (CIE 9702). Two pipelines, one memory, strict privacy.

Run the CLI as `<plugin-root>/scripts/anim.py` (the directory that contains
this skill's `scripts/` folder), using the WorkBuddy-managed Python when
present; the scripts fall back to the interpreter that runs them.

## Route every request first

- Continuous motion (trajectories, oscillations, rotation, fields changing, exponential decay) -> `render-video` skill (Manim MP4).
- Sequential text reveal (definitions, derivations, steps) -> `build-ppt` skill (native PowerPoint entrance animations).
- Static diagrams -> put them in the PPT.
- Both needed -> build the PPT and embed the rendered MP4 in it.
- If the intent is genuinely ambiguous, ask exactly one routing question before generating anything.

## Load memory before generating

At the start of every animation/courseware request, read the teacher's memory
and apply what applies to this topic:

`python <plugin-root>/scripts/anim.py memory report`

The memory is the project-root `PHYSICS-MEMORY.md`. Read it fully: apply
matching habits (section 1) and past modifications (section 5) automatically,
and go through the error archive (section 4) so the same mistake is never
repeated. If the file does not exist, create it with
`python <plugin-root>/scripts/anim.py memory init` and tell the teacher.

## Physics red lines are mandatory

- Never hand-place physics quantities. Compute them from the helpers in `scripts/redlines.py`; the same helpers are asserted by the test suite.
- Every scene declares `SCENE_META` with its topic and red-line ids from `scripts/redlines.py`.
- Red-line catalogue with the physics reasoning: `docs/redlines.md` in the repo.
- If a red line cannot be satisfied by an animation, say so instead of drawing something that looks right but is wrong.

## Memory: "remember" and "forget" (edit the Markdown directly)

The single source of truth is the project-root `PHYSICS-MEMORY.md`. Edit it
directly — there is no separate database.

- Habits/preferences (section 1): write only when the teacher explicitly says
  "remember", with the evidence line.
- Every requested modification (section 5): record automatically, with the
  date, as soon as you apply it. This is not optional: the Stop hook blocks
  the turn when a modification request was seen but the file was not updated.
- Mistakes (section 4): record automatically with the date and the correct
  approach; when an old mistake repeats, bump its recurrence count instead of
  adding a new line.
- "Forget X": delete the entry and leave a dated line in section 6. Nothing is
  deleted silently.
- No new information -> do not write anything.
- Close every turn with one line: `记忆已更新：<内容>（PHYSICS-MEMORY.md 第 N 区）`.

## Privacy (absolute rules)

Passwords, accounts, API keys, tokens, student names/PII, intranet addresses and absolute local paths are never written to memory, courseware, docs or code comments. Every memory write is filtered automatically; run `python scripts/anim.py scrub <output-dir>` before delivering any courseware. If a filter triggers, report only the category (never the value) and refuse the write.

## Deliverables

- All content in English (A-Level terminology as written), no LaTeX anywhere: use Unicode math in Manim `Text`.
- Videos: 1920x1080, 30 fps MP4, no narration in v1. Decks: PowerPoint/WPS-compatible `.pptx`.
- Always verify before handing over: `python scripts/anim.py verify`.
- Never write absolute filesystem paths into courseware or memory; use the teacher's workspace-relative paths.
