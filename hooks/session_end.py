#!/usr/bin/env python3
"""WorkBuddy Stop hook: block the turn if a teacher modification request was
not written to PHYSICS-MEMORY.md. Privacy: only counts/instructions print."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def engine_scripts_dir() -> Path:
    root = os.environ.get("CODEBUDDY_PLUGIN_ROOT") or os.environ.get("WORKBUDDY_PLUGIN_ROOT")
    candidates = []
    if root:
        base = Path(root)
        candidates += [base / "scripts", base / "plugins" / "alevel-physics-animations" / "scripts"]
    here = Path(__file__).resolve().parents[1]
    candidates.append(here / "plugins" / "alevel-physics-animations" / "scripts")
    for candidate in candidates:
        if (candidate / "memory_gate.py").exists():
            return candidate
    return here / "plugins" / "alevel-physics-animations" / "scripts"


sys.path.insert(0, str(engine_scripts_dir()))

import memory_gate  # noqa: E402


def read_payload() -> dict:
    if sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    try:
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def main() -> int:
    payload = read_payload()
    transcript = payload.get("transcript_path") or os.environ.get("WORKBUDDY_TRANSCRIPT_PATH") or ""
    session_id = payload.get("session_id") or ""
    return memory_gate.session_check(transcript, session_id)


if __name__ == "__main__":
    raise SystemExit(main())
