#!/usr/bin/env python3
"""SessionStart hook: load teacher memory and write a session baseline.

Stdout is the generated memory report, which the harness can surface as
session context. The baseline marker lets the Stop hook know how many
modifications existed when this session began.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from memory import MemoryStore, memory_dir  # noqa: E402


def read_payload() -> dict:
    if sys.stdin.isatty():
        return {}
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def run(payload: dict | None = None) -> int:
    payload = payload if payload is not None else read_payload()
    session_id = payload.get("session_id") or os.environ.get("CODEX_SESSION_ID") or ""
    store = MemoryStore()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    baseline = {
        "session_id": session_id,
        "started_at": started_at,
        "modifications": len(store.modifications()),
        "habits": len(store.habits()),
        "errors": len(store.errors()),
    }
    sessions_dir = memory_dir() / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    (sessions_dir / "_latest.json").write_text(json.dumps(baseline), encoding="utf-8")
    if session_id:
        (sessions_dir / f"{session_id}.json").write_text(json.dumps(baseline), encoding="utf-8")
    sys.stdout.write(store.report())
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
