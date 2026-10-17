"""Portable location of the project root, engine dir and Python interpreter.

The kit can live in a WorkBuddy plugin package (hooks set
CODEBUDDY_PLUGIN_ROOT), as a project-installed checkout (PHYSICS-MEMORY.md
marks the project root), or inside this repository's plugins/ folder.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


ENGINE_DIR = Path(__file__).resolve().parent


def project_root(start: str | os.PathLike | None = None) -> Path:
    """Walk up from `start` (default: cwd) to the project root."""
    start = Path(start or os.getcwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".workbuddy-plugin" / "plugin.json").exists():
            return candidate
        if (candidate / "PHYSICS-MEMORY.md").exists() and (candidate / "skills").exists():
            return candidate
    # Fallback: this repository checkout (engine under plugins/<name>/scripts).
    for candidate in (start, *start.parents):
        if (candidate / "plugins" / "alevel-physics-animations" / "scripts" / "anim.py").exists():
            return candidate
    return start


def repo_root() -> Path:
    """Repository/plugin package root that contains tests, docs and dist."""
    env = os.environ.get("CODEBUDDY_PLUGIN_ROOT") or os.environ.get("WORKBUDDY_PLUGIN_ROOT") or os.environ.get("PLUGIN_ROOT")
    if env:
        return Path(env)
    # Engine checkout: scripts/ -> <name>/ -> plugins/ -> repo
    if ENGINE_DIR.parent.name == "alevel-physics-animations" and ENGINE_DIR.parent.parent.name == "plugins":
        return ENGINE_DIR.parents[2]
    return project_root()


def python_for_render() -> str:
    """Best Python for rendering: explicit override, then WorkBuddy-managed
    environments, then the interpreter running us."""
    override = os.environ.get("PHYSICS_ANIM_PYTHON")
    if override:
        return override
    home = Path.home()
    candidates = (
        home / ".workbuddy" / "binaries" / "python" / "envs" / "manim" / "bin" / "python3",
        home / ".workbuddy" / "binaries" / "python" / "envs" / "default" / "bin" / "python3",
    )
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable
