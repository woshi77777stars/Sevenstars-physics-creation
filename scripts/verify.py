"""Repository-level verification: manifest, marketplace, coverage, scaffolds."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "alevel-physics-animations"
MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"


def _fail(message: str) -> None:
    print(f"VERIFY FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_manifest() -> None:
    manifest_path = PLUGIN / ".codex-plugin" / "plugin.json"
    if not manifest_path.exists():
        _fail("plugin.json missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("name") != "alevel-physics-animations":
        _fail("plugin name mismatch")
    if not manifest.get("skills"):
        _fail("manifest must declare skills")
    if "[TODO" in manifest_path.read_text(encoding="utf-8"):
        _fail("manifest contains TODO placeholders")
    for asset in ("composerIcon", "logo"):
        rel = manifest.get("interface", {}).get(asset)
        if rel and not (PLUGIN / rel.lstrip("./")).exists():
            _fail(f"missing manifest asset {rel}")
    # Prefer the bundled plugin-creator validator when discoverable.
    for base in (
        Path(__import__("os").environ.get("CODEX_HOME", "~/.codex")).expanduser(),
        Path.home() / ".codex",
    ):
        validator = base / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"
        if validator.exists():
            rc = subprocess.call([sys.executable, str(validator), str(PLUGIN)])
            if rc:
                _fail("plugin-creator validator rejected the plugin")
            return


def check_marketplace() -> None:
    if not MARKETPLACE.exists():
        _fail("repo marketplace.json missing")
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    entry = next((p for p in data.get("plugins", []) if p.get("name") == "alevel-physics-animations"), None)
    if entry is None:
        _fail("marketplace has no entry for the plugin")
    if entry.get("source", {}).get("path") != "./plugins/alevel-physics-animations":
        _fail("marketplace source path mismatch")


def check_scaffold() -> None:
    for rel in (
        "skills/alevel-physics-animations/SKILL.md",
        "skills/render-video/SKILL.md",
        "skills/build-ppt/SKILL.md",
        "scripts/anim.py",
        "scripts/redlines.py",
        "scripts/ppt_builder.py",
        "scripts/ppt_anim.py",
        "scripts/memory.py",
        "scripts/privacy.py",
        "hooks/codex-hooks.json",
        "hooks/session_start.py",
        "hooks/session_end.py",
    ):
        if not (PLUGIN / rel).exists():
            _fail(f"missing {rel}")
    scenes = list((PLUGIN / "scripts" / "scenes").glob("*.py"))
    if len([p for p in scenes if p.stem not in {"__init__", "_common"}]) < 28:
        _fail(f"expected >=28 scene files, found {len(scenes)}")


def main() -> None:
    check_manifest()
    check_marketplace()
    check_scaffold()
    print("Plugin manifest, marketplace entry and scaffold OK.")


if __name__ == "__main__":
    main()
