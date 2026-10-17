"""Build the offline teacher package for the current platform."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "alevel-physics-animations"
ANIM = PLUGIN / "scripts" / "anim.py"
KIT_FILES = (
    ".workbuddy-plugin/plugin.json",
    "skills",
    "commands",
    "hooks",
    "PHYSICS-MEMORY.md",
    "USER.md",
    ".workbuddy/memory/MEMORY.md",
)


def version() -> str:
    manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    return manifest["version"]


def platform_tag() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if machine in {"arm64", "aarch64"}:
        arch = "arm64"
    elif machine in {"x86_64", "amd64"}:
        arch = "x64"
    else:
        arch = machine
    return f"{system}-{arch}"


def vendor_ffmpeg(stage: Path) -> None:
    try:
        import imageio_ffmpeg

        exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        print("imageio-ffmpeg not installed; skipping vendored ffmpeg", file=sys.stderr)
        return
    dest = stage / "vendor" / "ffmpeg"
    dest.mkdir(parents=True, exist_ok=True)
    canonical = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    shutil.copy2(exe, dest / canonical)
    print(f"Vendored ffmpeg: {exe.name} -> {canonical}")


def vendor_wheels(stage: Path) -> None:
    wheels = REPO / "work" / "wheels"
    if not wheels.exists():
        print("work/wheels not present; pip download first: "
              "python -m pip download -d work/wheels manim imageio-ffmpeg python-pptx pillow numpy",
              file=sys.stderr)
        return
    dest = stage / "vendor" / "wheels"
    shutil.copytree(wheels, dest, dirs_exist_ok=True)
    print("Vendored wheels from work/wheels")


def build_pptx(stage: Path) -> None:
    out = stage / "examples" / "pptx"
    rc = subprocess.call([sys.executable, str(ANIM), "ppt-all", "--out", str(out)])
    if rc:
        raise SystemExit("ppt-all failed")


def copy_videos(stage: Path) -> None:
    videos = REPO / "outputs" / "videos"
    if videos.exists():
        shutil.copytree(videos, stage / "examples" / "videos", dirs_exist_ok=True)


INSTALL_SH = """#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
"$PY" -m venv "$DIR/.venv"
"$DIR/.venv/bin/pip" install --no-index --find-links "$DIR/vendor/wheels" \\
  python-pptx pillow numpy imageio-ffmpeg
"$DIR/.venv/bin/pip" install --no-index --find-links "$DIR/vendor/wheels" manim \\
  || echo "manim is not bundled for this platform; PPT decks and memory work, video rendering needs a system cairo install on macOS."
if [ -d "$DIR/vendor/ffmpeg" ]; then
  echo "export PATH=\\"$DIR/vendor/ffmpeg:\\$PATH\\"" >> "$DIR/.venv/bin/activate"
fi
echo "Done. Activate with: source $DIR/.venv/bin/activate"
"""


INSTALL_PS1 = """$ErrorActionPreference = "Stop"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
python -m venv "$dir\\.venv"
& "$dir\\.venv\\Scripts\\pip.exe" install --no-index --find-links "$dir\\vendor\\wheels" `
  python-pptx pillow numpy imageio-ffmpeg
$manimOk = $true
try {
  & "$dir\\.venv\\Scripts\\pip.exe" install --no-index --find-links "$dir\\vendor\\wheels" manim *>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) { $manimOk = $false }
} catch {
  $manimOk = $false
}
if (-not $manimOk) {
  Write-Host "manim is not bundled for this platform; PPT decks and memory work, video rendering needs a system install."
}
if (Test-Path "$dir\\vendor\\ffmpeg") {
  Add-Content "$dir\\.venv\\Scripts\\Activate.ps1" "`n`$env:PATH = `"$dir\\vendor\\ffmpeg;$env:PATH`""
}
Write-Host "Done. Activate with: $dir\\.venv\\Scripts\\Activate.ps1"
"""


def write_installers(stage: Path, ver: str, tag: str) -> None:
    install_sh = stage / "install.sh"
    install_sh.write_text(INSTALL_SH, encoding="utf-8")
    install_sh.chmod(0o755)
    (stage / "install.ps1").write_text(INSTALL_PS1, encoding="utf-8")
    readme = f"""# Offline package {ver} ({tag})

Everything works without a network connection.

1. Run the installer: `bash install.sh` (macOS/Linux) or `install.ps1`
   (Windows PowerShell).
2. Open `examples/videos/` for ready-made MP4s and `examples/pptx/` for
   editable decks with native click animations.
3. The plugin itself is under `plugin/alevel-physics-animations/`.

Requirements bundled: Python wheels, static ffmpeg. The installers create a
local `.venv` and never touch the system Python.
"""
    (stage / "OFFLINE_README.md").write_text(readme, encoding="utf-8")


def build(local_only: bool = True) -> Path:
    ver = version()
    tag = platform_tag()
    stage = REPO / "work" / "dist-stage" / f"{ver}-{tag}"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    shutil.copytree(PLUGIN, stage / "plugin" / "alevel-physics-animations")
    for rel in KIT_FILES:
        src = REPO / rel
        if src.is_dir():
            shutil.copytree(src, stage / rel, dirs_exist_ok=True)
        elif src.exists():
            dst = stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    build_pptx(stage)
    copy_videos(stage)
    vendor_ffmpeg(stage)
    vendor_wheels(stage)
    write_installers(stage, ver, tag)

    dist = REPO / "dist"
    dist.mkdir(exist_ok=True)
    target = dist / f"alevel-physics-animations-offline-{ver}-{tag}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(stage.rglob("*")):
            if path.is_file() and ".venv" not in path.parts:
                zf.write(path, path.relative_to(stage))
    print(target)
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="build current platform only")
    args = parser.parse_args()
    build(local_only=args.local)


if __name__ == "__main__":
    main()
