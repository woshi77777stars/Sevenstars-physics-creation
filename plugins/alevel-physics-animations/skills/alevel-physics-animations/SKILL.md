---
name: alevel-physics-animations
description: "Build classroom A-Level Physics (CIE 9702) animations for teachers: physics-red-line Manim videos, native-animation PowerPoint decks, and a private teacher memory. Use when a teacher asks for a physics animation, video, PPT courseware, or remember/forget for A-Level physics teaching."
---

# A-Level Physics Animations

You produce classroom assets for an A-Level Physics teacher (CIE 9702). Two pipelines, one memory, strict privacy.

## Route every request first

- Continuous motion (trajectories, oscillations, rotation, fields changing, exponential decay) -> `render-video` skill (Manim MP4).
- Sequential text reveal (definitions, derivations, steps) -> `build-ppt` skill (native PowerPoint entrance animations).
- Static diagrams -> put them in the PPT.
- Both needed -> build the PPT and embed the rendered MP4 in it.
- If the intent is genuinely ambiguous, ask exactly one routing question before generating anything.

## Load memory before generating

At the start of every animation/courseware request, read the teacher's memory
and apply what applies to this topic:

`python scripts/anim.py memory show` (and `memory report` for the summary).

- Apply matching remembered habits and past modifications automatically
  (e.g. colour, font size, layout, level of detail) before rendering.
- Check the topic's recorded mistakes so the same error is not repeated.

## Physics red lines are mandatory

- Never hand-place physics quantities. Compute them from the helpers in `scripts/redlines.py`; the same helpers are asserted by the test suite.
- Every scene declares `SCENE_META` with its topic and red-line ids from `scripts/redlines.py`.
- Red-line catalogue with the physics reasoning: `docs/redlines.md` in the repo.
- If a red line cannot be satisfied by an animation, say so instead of drawing something that looks right but is wrong.

## Memory: "remember" and "forget"

- Teacher habits/preferences: write only when the teacher explicitly says "remember".
  `python scripts/anim.py memory add habit --kind presentation|communication|defaults --content "..." [--topic kinematics]`
- Every requested modification is recorded automatically as soon as you apply it:
  `python scripts/anim.py memory add modification --topic <topic-id> --request "what the teacher asked" --change "what you changed"`
  Repeats of the same request just increment the count; no duplicate entries.
- Mistakes: when you discover and fix a physics or workflow mistake, record it automatically. Recurrences increment automatically.
  `python scripts/anim.py memory add error --topic <topic-id> --description "..." --correct "..."`
- "Forget X": `python scripts/anim.py memory forget --match "X"` — the record is moved to a tombstone, never silently deleted.
- No new information -> do not write anything (a duplicate habit returns "noop").
- Show state: `memory show`; human-readable summary: `memory report`.
- Details and file schemas: [references/memory-format.md](references/memory-format.md).

## Privacy (absolute rules)

Passwords, accounts, API keys, tokens, student names/PII, intranet addresses and absolute local paths are never written to memory, courseware, docs or code comments. Every memory write is filtered automatically; run `python scripts/anim.py scrub <output-dir>` before delivering any courseware. If a filter triggers, report only the category (never the value) and refuse the write.

## Deliverables

- All content in English (A-Level terminology as written), no LaTeX anywhere: use Unicode math in Manim `Text`.
- Videos: 1920x1080, 30 fps MP4, no narration in v1. Decks: PowerPoint/WPS-compatible `.pptx`.
- Always verify before handing over: `python scripts/anim.py verify`.
- Never write absolute filesystem paths into courseware or memory; use the teacher's workspace-relative paths.
