"""Teacher memory: habits (on request) and fixed mistakes (automatic).

Stored in <home>/.physics-anim/memory/ as JSONL with a generated Markdown
index and a tombstone archive for "forget" operations. Every write passes the
privacy filter first. The store never records absolute filesystem paths.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from privacy import PrivacyViolation, require_clean


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def memory_dir() -> Path:
    override = os.environ.get("PHYSICS_ANIM_MEMORY_DIR")
    base = Path(override) if override else Path.home() / ".physics-anim" / "memory"
    return base


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _signature(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode("utf-8")).hexdigest()[:16]


@dataclass
class WriteResult:
    action: str  # "added" | "updated" | "noop"
    record: dict


class MemoryStore:
    def __init__(self, root: Path | None = None):
        self.root = root or memory_dir()
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "deleted").mkdir(exist_ok=True)

    # -- paths ---------------------------------------------------------------
    @property
    def habits_path(self) -> Path:
        return self.root / "habits.jsonl"

    @property
    def errors_path(self) -> Path:
        return self.root / "errors.jsonl"

    @property
    def modifications_path(self) -> Path:
        return self.root / "modifications.jsonl"

    # -- habits --------------------------------------------------------------
    def add_habit(self, content: str, kind: str = "presentation", topics: list[str] | None = None) -> WriteResult:
        require_clean(content)
        require_clean(kind)
        if kind not in {"presentation", "communication", "defaults"}:
            raise ValueError(f"Invalid habit kind {kind!r}")
        sig = _signature(content)
        records = self._read(self.habits_path)
        for rec in records:
            if rec.get("status") == "active" and _signature(rec.get("content", "")) == sig:
                if rec.get("topics") == (topics or []) and rec.get("kind") == kind:
                    return WriteResult("noop", rec)
                rec["kind"] = kind
                rec["topics"] = topics or []
                rec["updated"] = _now()
                self._rewrite(self.habits_path, records)
                return WriteResult("updated", rec)
        rec = {
            "id": "h_" + uuid.uuid4().hex[:12],
            "kind": kind,
            "content": content,
            "topics": topics or [],
            "created": _now(),
            "updated": _now(),
            "status": "active",
        }
        self._append(self.habits_path, rec)
        return WriteResult("added", rec)

    # -- errors ---------------------------------------------------------------
    def add_error(self, topic: str, description: str, correct_approach: str) -> WriteResult:
        require_clean(topic)
        require_clean(description)
        require_clean(correct_approach)
        sig = _signature(description)
        records = self._read(self.errors_path)
        for rec in records:
            if rec.get("signature") == sig and rec.get("topic") == topic:
                rec["recurrences"] = int(rec.get("recurrences", 1)) + 1
                rec["last_seen"] = _now()
                self._rewrite(self.errors_path, records)
                return WriteResult("updated", rec)
        rec = {
            "id": "e_" + uuid.uuid4().hex[:12],
            "topic": topic,
            "signature": sig,
            "description": description,
            "correct_approach": correct_approach,
            "recurrences": 1,
            "first_seen": _now(),
            "last_seen": _now(),
        }
        self._append(self.errors_path, rec)
        return WriteResult("added", rec)

    # -- modifications ---------------------------------------------------------
    def add_modification(self, topic: str, request: str, change_made: str) -> WriteResult:
        """Record a teacher-requested change. Called automatically every time
        the teacher asks for a modification and the change is applied."""
        require_clean(topic)
        require_clean(request)
        require_clean(change_made)
        sig = _signature(request)
        records = self._read(self.modifications_path)
        for rec in records:
            if rec.get("signature") == sig and rec.get("topic") == topic:
                rec["recurrences"] = int(rec.get("recurrences", 1)) + 1
                rec["last_seen"] = _now()
                self._rewrite(self.modifications_path, records)
                return WriteResult("updated", rec)
        rec = {
            "id": "m_" + uuid.uuid4().hex[:12],
            "topic": topic,
            "signature": sig,
            "request": request,
            "change_made": change_made,
            "recurrences": 1,
            "first_seen": _now(),
            "last_seen": _now(),
        }
        self._append(self.modifications_path, rec)
        return WriteResult("added", rec)

    # -- forget ---------------------------------------------------------------
    def forget(self, match: str | None = None, record_id: str | None = None) -> int:
        """Remove matching records, writing each to a tombstone file."""
        if match is not None and not match.strip():
            raise ValueError("forget match must be a non-empty keyword or id")
        removed = 0
        for path in (self.habits_path, self.errors_path, self.modifications_path):
            records = self._read(path)
            keep, drop = [], []
            needle = (match or "").lower()
            for rec in records:
                hit = bool(record_id and rec.get("id") == record_id)
                if not hit and needle:
                    blob = " ".join(str(v) for v in rec.values()).lower()
                    hit = needle in blob
                (drop if hit else keep).append(rec)
            for rec in drop:
                tombstone = {
                    "id": rec.get("id"),
                    "kind": (
                        "habit"
                        if path.name.startswith("habits")
                        else ("modification" if path.name.startswith("modifications") else "error")
                    ),
                    "removed_at": _now(),
                    "reason": "user requested",
                    "payload": rec,
                }
                stamp = _now().replace(":", "").replace("+00:00", "Z")
                self._append(
                    self.root / "deleted" / f"{stamp}-{rec.get('id')}.jsonl", tombstone
                )
                removed += 1
            if drop:
                self._rewrite(path, keep)
        return removed

    # -- reads -----------------------------------------------------------------
    def habits(self) -> list[dict]:
        return [r for r in self._read(self.habits_path) if r.get("status") == "active"]

    def errors(self) -> list[dict]:
        return self._read(self.errors_path)

    def modifications(self) -> list[dict]:
        return self._read(self.modifications_path)

    def report(self) -> str:
        lines = ["# Physics Animations Memory Report", ""]
        lines.append(f"Generated: {_now()}", )
        lines += ["", "## Habits", ""]
        habits = sorted(self.habits(), key=lambda r: r.get("updated", ""), reverse=True)
        if not habits:
            lines.append("_None remembered yet._")
        for r in habits:
            topic_tag = f" ({', '.join(r.get('topics', []))})" if r.get("topics") else ""
            lines.append(f"- **{r['kind']}**{topic_tag}: {r['content']}")
        lines += ["", "## Recurring mistakes", ""]
        errors = sorted(self.errors(), key=lambda r: -int(r.get("recurrences", 1)))
        if not errors:
            lines.append("_No mistakes recorded._")
        for r in errors:
            lines.append(
                f"- **{r['topic']}** (x{r['recurrences']}): {r['description']} -> {r['correct_approach']}"
            )
        lines += ["", "## Requested modifications", ""]
        modifications = sorted(self.modifications(), key=lambda r: -int(r.get("recurrences", 1)))
        if not modifications:
            lines.append("_No modifications recorded._")
        for r in modifications:
            lines.append(
                f"- **{r['topic']}** (x{r['recurrences']}): {r['request']} -> {r['change_made']}"
            )
        return "\n".join(lines) + "\n"

    def write_report(self, path: Path | None = None) -> Path:
        target = path or (self.root / "index.md")
        target.write_text(self.report(), encoding="utf-8")
        return target

    # -- io helpers -------------------------------------------------------------
    @staticmethod
    def _read(path: Path) -> list[dict]:
        if not path.exists():
            return []
        records = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records

    @staticmethod
    def _append(path: Path, record: dict) -> None:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    @staticmethod
    def _rewrite(path: Path, records: list[dict]) -> None:
        with path.open("w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
