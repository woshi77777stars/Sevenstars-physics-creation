# Memory hooks (SessionStart + Stop)

The model instructions in `skills/` already say to record every teacher
modification. These hooks make that a *hard* guarantee:

- `SessionStart` runs `session_start.py`: it prints the teacher's memory
  report into session context and writes a baseline marker under
  `<home>/.physics-anim/memory/sessions/`.
- `Stop` runs `session_end.py`: it scans the session transcript for
  modification requests (Chinese/English change verbs, colour/font/title
  keywords). If any were seen but no modification record was touched this
  session, it exits `2`, which blocks the session from finishing until the
  missed change is recorded with `anim memory add modification`.

## Event support (verified against the installed Codex binary)

The local Codex build registers these hook events: `SessionStart`,
`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Notification`, `Stop`,
`SubagentStop`. This plugin uses the two it needs.

## Platform notes

- Commands assume `python3` on PATH. On Windows, change the two commands in
  `codex-hooks.json` to `python`.
- If the app does not auto-discover plugin hooks, register the same two
  commands manually in the project's `.codex/config.toml` hooks section.
- Exit code `2` = block (Claude-compatible convention). The gate is a
  conservative keyword scan: it never prints transcript content, only counts
  and instructions.
