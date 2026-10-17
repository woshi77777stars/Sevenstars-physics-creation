#!/usr/bin/env python3
"""Stop hook: the hard memory gate.

If the session transcript contains a teacher modification request but no
modification record was touched this session, exit 2 so the session cannot
finish until the missed change is recorded. Privacy: the hook only ever
prints counts and instructions, never transcript content.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from memory import MemoryStore, memory_dir  # noqa: E402


_REQUEST_PATTERN = re.compile(
    "|".join(
        [
            r"改成", r"换成", r"改为", r"改一?下", r"调整", r"删掉", r"删除", r"去掉",
            r"不要", r"加一个", r"加上", r"添加", r"调大", r"调小", r"大一点", r"小一点",
            r"颜色", r"字号", r"字体", r"背景", r"标题", r"虚线", r"实线", r"换成",
            r"用.{0,12}(?:代替|替代)", r"换个",
            r"\bchange\b", r"\breplace\b", r"\bremove\b", r"\bdelete\b", r"\bswitch\b",
            r"\bmake it\b", r"\buse .{1,20} instead\b", r"\binstead\b",
            r"\bmake (?:the|it) \w+ \w+\b", r"\bturn (?:the|it) \w+ \w+\b",
            r"\bbigger\b", r"\bsmaller\b",
            r"\bcolou?r\b", r"\bfont\b", r"\btitle\b", r"\bdashed\b", r"\bsolid\b",
        ]
    ),
    re.IGNORECASE,
)


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


def baseline_for(payload: dict) -> dict | None:
    sessions_dir = memory_dir() / "sessions"
    session_id = payload.get("session_id") or os.environ.get("CODEX_SESSION_ID") or ""
    if session_id:
        path = sessions_dir / f"{session_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    latest = sessions_dir / "_latest.json"
    if latest.exists():
        return json.loads(latest.read_text(encoding="utf-8"))
    return None


def user_requests(transcript_path: str) -> list[str]:
    if not transcript_path:
        return []
    path = Path(transcript_path)
    if not path.exists():
        return []
    found: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = event.get("payload") or {}
        if event.get("type") == "event_msg" and isinstance(payload, dict) and payload.get("type") == "user_message":
            message = payload.get("message") or ""
            if _REQUEST_PATTERN.search(message):
                found.append(message)
    return found


def modifications_touched_since(started_at: str) -> int:
    store = MemoryStore()
    touched = 0
    for record in store.modifications():
        if (record.get("last_seen") or "") >= started_at:
            touched += 1
    return touched


def run(payload: dict | None = None) -> int:
    payload = payload if payload is not None else read_payload()
    baseline = baseline_for(payload)
    requests = user_requests(payload.get("transcript_path") or "")
    if baseline is None or not requests:
        sys.stdout.write("memory gate: nothing to check\n")
        return 0
    touched = modifications_touched_since(baseline.get("started_at", ""))
    if touched:
        sys.stdout.write(f"memory gate: {touched} modification record(s) touched this session\n")
        return 0
    sys.stderr.write(
        "Memory gate (blocking): a teacher modification request was detected this session but no "
        "modification was recorded. Record every applied change with:\n"
        "python scripts/anim.py memory add modification --topic <topic-id> "
        '--request "what the teacher asked" --change "what you changed"\n'
        "Then finish the turn again.\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(run())
