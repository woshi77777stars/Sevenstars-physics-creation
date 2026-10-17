# Memory store format

See the plugin reference `plugins/alevel-physics-animations/skills/alevel-physics-animations/references/memory-format.md`
for the canonical description. Summary:

- Location `<home>/.physics-anim/memory/`, override with
  `PHYSICS_ANIM_MEMORY_DIR` (used by tests).
- `habits.jsonl` — written only on explicit "remember"; duplicates noop.
- `errors.jsonl` — automatic on fixed mistakes; same signature increments
  `recurrences`.
- `modifications.jsonl` — automatic on every applied teacher modification;
  the same request increments `recurrences` instead of duplicating.
- `deleted/*.jsonl` — tombstones from every "forget".
- `index.md` — generated human-readable report.
- Privacy filter rejects credentials, PII, intranet addresses and absolute
  paths; it reports categories only, never values.
