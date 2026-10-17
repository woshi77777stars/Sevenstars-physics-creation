"""The memory gate: per-turn accounting of teacher modification requests.

SessionStart records a baseline (memory mtime + transcript offset). Stop
scans only the *new* user messages since the last check; if any look like a
modification request and PHYSICS-MEMORY.md has not been modified since the
baseline, the gate blocks (exit 2) until the model writes the change into
memory. Because Stop runs at the end of every turn and advances the offset,
each turn's requests are checked separately — not "at least one per session".
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import _runtime
import memory_file


MARKER_NAME = ".memory-gate.json"

_REQUEST_PATTERN = re.compile(
    "|".join(
        [
            # Chinese: verbs/imperatives, no bare nouns (颜色/字体 alone do not fire).
            r"改成", r"换成", r"改为", r"改一?下", r"调整", r"删掉", r"删除", r"去掉",
            r"不要", r"加一个", r"加上", r"调大", r"调小", r"大一点", r"小一点",
            r"把.{0,16}(?:改|换)", r"用.{0,12}(?:代替|替代)",
            # English: change/remove with a target, or explicit "instead".
            r"\bchange .{1,40}\b(?:to|with|colou?r|font|size|title|line|dot|arrow|blue|red|green|black|white|bigger|smaller|bold|dashed|solid)\b",
            r"\breplace .{1,40}\b(?:with|colou?r|font|size|title)\b",
            r"\bswap .{1,40}\b(?:with|for)\b",
            r"\bremove .{1,30}\b", r"\bdelete .{1,30}\b",
            r"\buse .{1,30} instead\b", r"\binstead\b",
            r"\bmake (?:the|it) \w+ \w+\b", r"\bbigger\b", r"\bsmaller\b",
        ]
    ),
    re.IGNORECASE,
)


def marker_path() -> Path:
    override = os.environ.get("PHYSICS_ANIM_GATE_DIR")
    if override:
        return Path(override) / MARKER_NAME
    root = _runtime.project_root()
    return root / ".workbuddy" / "memory" / MARKER_NAME


def load_marker() -> dict | None:
    path = marker_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_marker(marker: dict) -> None:
    path = marker_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(marker), encoding="utf-8")


def init_baseline(session_id: str = "") -> dict:
    """SessionStart: reset the per-project gate baseline."""
    marker = {
        "session_id": session_id,
        "memory_mtime": memory_file.mtime(),
        "transcript_offset": 0,
    }
    save_marker(marker)
    return marker


def _extract_user_text(event: dict) -> str:
    """User text from either transcript dialect.

    WorkBuddy (Claude Code) format:
      {"type": "message", "role": "user",
       "content": [{"type": "text", "text": "..."}, ...]}
    Codex format:
      {"type": "event_msg",
       "payload": {"type": "user_message", "message": "..."}}
    """
    if event.get("type") == "message" and event.get("role") == "user":
        content = event.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("type") in {"text", "input_text"}
            ]
            return " ".join(parts)
        return ""
    payload = event.get("payload")
    if (
        event.get("type") == "event_msg"
        and isinstance(payload, dict)
        and payload.get("type") == "user_message"
    ):
        message = payload.get("message") or ""
        if isinstance(message, str):
            return message
        if isinstance(message, list):
            return " ".join(
                item.get("text", "") for item in message if isinstance(item, dict)
            )
        return ""
    return ""


def user_messages_after(transcript_path: str, offset: int) -> list[tuple[int, str]]:
    """(next_offset, text) for user messages starting at byte `offset`.

    Reads in binary mode so offsets are true byte offsets across processes
    and platforms (Windows CRLF translation can corrupt text-mode cookies),
    and strips a UTF-8 BOM when resuming from the start."""
    path = Path(transcript_path)
    if not transcript_path or not path.exists():
        return []
    try:
        with path.open("rb") as fh:
            fh.seek(offset)
            messages: list[tuple[int, str]] = []
            while True:
                line = fh.readline()
                if not line:
                    break
                end = fh.tell()
                try:
                    event = json.loads(line.decode("utf-8", errors="ignore").lstrip("\ufeff"))
                except json.JSONDecodeError:
                    continue
                text = _extract_user_text(event)
                if text:
                    messages.append((end, text))
            return messages
    except OSError:
        return []


def session_check(transcript_path: str, session_id: str = "") -> int:
    """Stop gate. Returns 0 to allow, 2 to block finishing the turn."""
    marker = load_marker()
    if marker is None:
        marker = init_baseline(session_id)
    offset = int(marker.get("transcript_offset", 0))
    messages = user_messages_after(transcript_path, offset)
    requests = [text for _, text in messages if _REQUEST_PATTERN.search(text)]
    next_offset = max([offset, *(end for end, _ in messages)])
    memory_touched = memory_file.mtime() > float(marker.get("memory_mtime", 0.0))

    if requests and not memory_touched:
        sys.stderr.write(
            "Memory gate (blocking): teacher modification request(s) detected since the last check, "
            "but PHYSICS-MEMORY.md was not updated. Write the change into the right section "
            "(section 1 for habits, 4 for mistakes, 5 for modifications) before finishing this turn.\n"
        )
        return 2

    save_marker(
        {
            "session_id": session_id or marker.get("session_id", ""),
            "memory_mtime": memory_file.mtime(),
            "transcript_offset": next_offset,
        }
    )
    return 0


def summary(max_lines: int = 60) -> str:
    """A short, privacy-safe excerpt of the memory for SessionStart output."""
    text = memory_file.read()
    if not text:
        return "PHYSICS-MEMORY.md not found yet; the skill will create it.\n"
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + "\n… (truncated; read the full file)\n"
