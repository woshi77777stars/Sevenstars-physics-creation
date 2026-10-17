#!/usr/bin/env python3
"""WorkBuddy SessionStart hook: load memory, record the gate baseline."""

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


_engine_dir = engine_scripts_dir()
_plugin_root = os.environ.get("CODEBUDDY_PLUGIN_ROOT") or os.environ.get("WORKBUDDY_PLUGIN_ROOT")
if _plugin_root:
    os.environ.setdefault("PHYSICS_ANIM_PROJECT_ROOT", _plugin_root)
sys.path.insert(0, str(_engine_dir))

import _runtime  # noqa: E402
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
    session_id = payload.get("session_id") or ""
    memory_gate.init_baseline(session_id)
    summary = memory_gate.summary()
    if _runtime.project_venv_python() is None:
        summary += (
            "\nFirst run: run `python plugins/alevel-physics-animations/scripts/anim.py setup` "
            "(network) or `anim setup --offline` from a release package before using PPT/video.\n"
        )
    sys.stdout.write(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
