"""Manim scene registry. Imports happen lazily because they require Manim."""

from pathlib import Path


SCENES_DIR = Path(__file__).resolve().parent


def scene_metadata() -> dict[str, dict]:
    """topic -> metadata for every implemented scene, without importing Manim."""
    result: dict[str, dict] = {}
    for path in sorted(SCENES_DIR.rglob("*.py")):
        if path.name == "__init__.py" or path.name == "_common.py":
            continue
        namespace: dict = {}
        try:
            exec(  # noqa: S102
                compile(path.read_text(encoding="utf-8"), str(path), "exec"),
                {"__name__": "__peek__", "__file__": str(path)},
                namespace,
            )
        except Exception:
            pass
        meta = namespace.get("SCENE_META")
        if meta and isinstance(meta, dict) and meta.get("topic"):
            result.setdefault(meta["topic"], {"title": meta.get("title", ""), "scene_file": str(path)})
    return result
