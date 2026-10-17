"""Privacy filter: keep credentials, PII, intranet addresses and absolute
paths out of memory and courseware.

Safety rule: results only ever expose the *category* of a violation, never the
matched value itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Violation:
    category: str

    def __str__(self) -> str:
        return self.category


class PrivacyViolation(ValueError):
    def __init__(self, categories: list[str]):
        self.categories = categories
        super().__init__(
            "Content rejected by privacy filter (category only): " + ", ".join(categories)
        )


_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("api-key", re.compile(r"\b(sk|pk|rk)-[A-Za-z0-9]{20,}\b")),
    ("api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("api-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}")),
    ("token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{20,}", re.IGNORECASE)),
    ("token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("credential", re.compile(r"\b(password|passwd|pwd|secret)\s*[=:]\s*\S+", re.IGNORECASE)),
    ("private-ip", re.compile(r"\b(?:10|127)\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")),
    ("private-ip", re.compile(r"\b192\.168\.\d{1,3}\.\d{1,3}\b")),
    ("private-ip", re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b")),
    ("private-ip", re.compile(r"\bfe80::[0-9a-f:]+", re.IGNORECASE)),
    ("intranet-host", re.compile(r"\b[\w-]+\.(?:local|internal|lan|corp)\b", re.IGNORECASE)),
    # Absolute local paths: a "/" not preceded by a letter/digit, another "/"
    # (the "//" in URLs) or ":" (the "://" in URLs). Requiring at least one
    # "segment/" avoids flagging normal division like "s / t" or a URL path.
    ("absolute-path", re.compile(r"(?<![:/A-Za-z0-9])/(?:[A-Za-z0-9._~+%-]+/)+[A-Za-z0-9._~+%-]*")),
    ("absolute-path", re.compile(r"\b[A-Za-z]:\\(?:[^\\\s]+\\)+[^\\\s]*")),
    ("absolute-path", re.compile(r"\\\\[\w.-]+\\[^\\\s]+")),
    ("file-uri", re.compile(r"file:///\S+", re.IGNORECASE)),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("phone-number", re.compile(r"(?<!\d)(?:1[3-9]\d{9}|\+?86\d{11})(?!\d)")),
]

_DEFAULT_DENYLIST = (
    "passport\n"
    "passport number\n"
    "national id\n"
    "id number\n"
    "student id\n"
)


def load_denylist(path: Path | None = None) -> list[str]:
    if path is None:
        path = Path(__file__).resolve().parent / "privacy" / "denylist.txt"
    if not path.exists():
        return [line for line in _DEFAULT_DENYLIST.splitlines() if line.strip()]
    return [line.strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def scan(text: str, denylist: Path | None = None) -> list[Violation]:
    """Return category-only violations for text. Raises nothing."""
    found: list[Violation] = []
    lowered = text.lower()
    for category, pattern in _PATTERNS:
        if pattern.search(text) and category not in (v.category for v in found):
            found.append(Violation(category))
    for token in load_denylist(denylist):
        if token and token in lowered and Violation("denylist") not in found:
            found.append(Violation("denylist"))
    return found


def require_clean(text: str, denylist: Path | None = None) -> None:
    """Raise PrivacyViolation (categories only) if text contains sensitive data."""
    violations = scan(text, denylist)
    if violations:
        raise PrivacyViolation([v.category for v in violations])


def scrub_path(path: Path) -> dict[str, list[str]]:
    """Scan readable text files under `path`; report violations by file."""
    report: dict[str, list[str]] = {}
    suffixes = {".md", ".txt", ".json", ".jsonl", ".csv", ".yaml", ".yml"}
    for file in sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in suffixes):
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        categories = [v.category for v in scan(text)]
        if categories:
            report[str(file)] = categories
    return report
