# Memory hooks (WorkBuddy native)

Registered from `hooks/hooks.json`, declared by `.workbuddy-plugin/plugin.json`.
Commands use `${CODEBUDDY_PLUGIN_ROOT}`, the same placeholder as WorkBuddy's
built-in plugins.

- `SessionStart` -> `session_start.py`: prints the memory summary and records
  the gate baseline (memory mtime + transcript offset) in
  `.workbuddy/memory/.memory-gate.json` (gitignored).
- `Stop` -> `session_end.py`: scans only the user messages since the previous
  check. If any looks like a modification request and `PHYSICS-MEMORY.md` was
  not updated, it exits `2`, blocking the turn until the change is written.
  The marker advances after every check, so each turn is gated separately.

Detection is verb/imperative based ("改成/换成/调整/去掉/调大/调小/change…to/
make the…/instead"). Bare nouns like 颜色/字体/标题 do not fire, and "不要"
only fires with a concrete target ("不要用虚线", "不要连播"), not generic
prohibitions like "不要修改文件" or "不要超出目录". Output only ever contains
counts and instructions, never transcript content.

## Evidence for the chosen events

- WorkBuddy's own built-in plugin (sheetagent) ships `hooks/hooks.json` with
  `SessionStart`, `UserPromptSubmit` and `SubagentStop`, so those event names
  are real. WorkBuddy's session transcripts are Claude Code-format JSONL
  (`{"type":"message","role":"user","content":[{"type":"input_text",...}]}`),
  and hook commands receive `session_id`, `transcript_path`, `cwd` and
  `model` via stdin — the parser supports that exact format (plus the older
  Codex `event_msg` shape for compatibility).
- `Stop` follows the Claude Code hook semantics: exit `2` sends stderr back
  to the model, which keeps working until the gate passes. This is the
  enforcement point. It must be confirmed once on a real machine with the
  negative test in `docs/acceptance-checklist.md`.

## Cross-platform notes

- The hook commands use `python3 "…" || python "…"`, which works in both
  POSIX shells and `cmd.exe`, so no manual edit is needed on Windows.
- Entries deliberately omit `matcher` (like WorkBuddy's own sheetagent
  plugin); both events apply to every session.
- The gate transcripts are read in binary mode with true byte offsets, so
  CRLF line endings on Windows and process restarts cannot corrupt the
  per-turn marker.
- If the app does not auto-load plugin hooks, register the same two commands
  in the project's hook configuration.
