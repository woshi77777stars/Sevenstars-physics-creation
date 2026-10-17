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

BASE_PACKAGES = (
    "python-pptx",
    "pillow",
    "numpy",
    "imageio-ffmpeg",
)
MANIM_PACKAGE = "manim"


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


def wheel_files() -> list[Path]:
    wheels = REPO / "work" / "wheels"
    if not wheels.exists():
        return []
    return sorted(wheels.glob("*.whl"))


def wheel_distribution(path: Path) -> str:
    """Normalize a wheel filename to its PyPI distribution name."""
    return path.name.split("-", 1)[0].lower().replace("_", "-")


def has_package(package: str) -> bool:
    return any(wheel_distribution(path) == package for path in wheel_files())


def missing_packages(packages: tuple[str, ...]) -> list[str]:
    return [package for package in packages if not has_package(package)]


def vendor_ffmpeg(stage: Path) -> bool:
    try:
        import imageio_ffmpeg

        exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        print("imageio-ffmpeg not installed; skipping vendored ffmpeg", file=sys.stderr)
        return False
    dest = stage / "vendor" / "ffmpeg"
    dest.mkdir(parents=True, exist_ok=True)
    canonical = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    shutil.copy2(exe, dest / canonical)
    print(f"Vendored ffmpeg: {exe.name} -> {canonical}")
    return True


def vendor_wheels(stage: Path) -> int:
    files = wheel_files()
    if not files:
        print(
            "work/wheels is empty. Download wheels first, for example:\n"
            "  python -m pip download -d work/wheels python-pptx pillow numpy imageio-ffmpeg\n"
            "  # for the full package add: manim==0.22.0",
            file=sys.stderr,
        )
        return 0
    dest = stage / "vendor" / "wheels"
    dest.mkdir(parents=True, exist_ok=True)
    for path in files:
        shutil.copy2(path, dest / path.name)
    print(f"Vendored {len(files)} wheels from work/wheels")
    return len(files)


def build_pptx(stage: Path) -> None:
    out = stage / "examples" / "pptx"
    rc = subprocess.call([sys.executable, str(ANIM), "ppt-all", "--out", str(out)])
    if rc:
        raise SystemExit("ppt-all failed")


def copy_videos(stage: Path) -> int:
    videos = REPO / "outputs" / "videos"
    if videos.exists():
        shutil.copytree(videos, stage / "examples" / "videos", dirs_exist_ok=True)
        count = sum(1 for path in (stage / "examples" / "videos").rglob("*.mp4"))
        print(f"Vendored {count} rendered videos from outputs/videos")
        return count
    print("outputs/videos not present; skipping rendered videos", file=sys.stderr)
    return 0


INSTALL_SH_FULL = """#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
find_python() {
  for p in \\
    "$HOME/.workbuddy/binaries/python/envs/manim/bin/python3" \\
    "$HOME/.workbuddy/binaries/python/envs/manim/bin/python" \\
    "$HOME/.workbuddy/binaries/python/envs/default/bin/python3" \\
    "$HOME/.workbuddy/binaries/python/envs/default/bin/python"; do
    if [ -x "$p" ]; then
      printf '%s' "$p"
      return 0
    fi
  done
  for p in python3 python; do
    if command -v "$p" >/dev/null 2>&1; then
      printf '%s' "$p"
      return 0
    fi
  done
  return 1
}
PY="${PYTHON:-$(find_python || true)}"
if [ -z "$PY" ]; then
  echo "No Python 3 interpreter found. Install Python 3.10+ or run inside WorkBuddy." >&2
  exit 1
fi
"$PY" -m venv "$DIR/.physics-anim-venv"
"$DIR/.physics-anim-venv/bin/pip" install --no-index --find-links "$DIR/vendor/wheels" \\
  python-pptx pillow numpy imageio-ffmpeg
"$DIR/.physics-anim-venv/bin/pip" install --no-index --find-links "$DIR/vendor/wheels" manim \\
  || echo "manim is not bundled for this platform; PPT decks and memory work, video rendering needs a system cairo install on macOS."
if [ -d "$DIR/vendor/ffmpeg" ]; then
  echo "export PATH=\\"$DIR/vendor/ffmpeg:\\$PATH\\"" >> "$DIR/.physics-anim-venv/bin/activate"
fi
echo "Done. Activate with: source $DIR/.physics-anim-venv/bin/activate"
"""


INSTALL_SH_PPT = """#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
find_python() {
  for p in \\
    "$HOME/.workbuddy/binaries/python/envs/manim/bin/python3" \\
    "$HOME/.workbuddy/binaries/python/envs/manim/bin/python" \\
    "$HOME/.workbuddy/binaries/python/envs/default/bin/python3" \\
    "$HOME/.workbuddy/binaries/python/envs/default/bin/python"; do
    if [ -x "$p" ]; then
      printf '%s' "$p"
      return 0
    fi
  done
  for p in python3 python; do
    if command -v "$p" >/dev/null 2>&1; then
      printf '%s' "$p"
      return 0
    fi
  done
  return 1
}
PY="${PYTHON:-$(find_python || true)}"
if [ -z "$PY" ]; then
  echo "No Python 3 interpreter found. Install Python 3.10+ or run inside WorkBuddy." >&2
  exit 1
fi
"$PY" -m venv "$DIR/.physics-anim-venv"
"$DIR/.physics-anim-venv/bin/pip" install --no-index --find-links "$DIR/vendor/wheels" \\
  python-pptx pillow numpy imageio-ffmpeg
echo "Done. Activate with: source $DIR/.physics-anim-venv/bin/activate"
echo "Note: this package contains the PPT and memory kit only; Manim and rendered videos are not bundled."
"""


INSTALL_PS1_FULL = """$ErrorActionPreference = "Stop"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$managed = @(
  "$env:USERPROFILE\\.workbuddy\\binaries\\python\\envs\\manim\\python.exe",
  "$env:USERPROFILE\\.workbuddy\\binaries\\python\\envs\\default\\python.exe",
  "python"
)
$python = $null
foreach ($p in $managed) {
  if ($p -like "*\\python.exe") {
    if (Test-Path $p) { $python = $p; break }
  } else {
    $cmd = Get-Command $p -ErrorAction SilentlyContinue
    if ($cmd) { $python = $p; break }
  }
}
if (-not $python) {
  Write-Error "No Python 3 interpreter found. Install Python 3.10+ or run inside WorkBuddy."
  exit 1
}
& $python -m venv "$dir\\.physics-anim-venv"
& "$dir\\.physics-anim-venv\\Scripts\\pip.exe" install --no-index --find-links "$dir\\vendor\\wheels" `
  python-pptx pillow numpy imageio-ffmpeg
$manimOk = $true
try {
  & "$dir\\.physics-anim-venv\\Scripts\\pip.exe" install --no-index --find-links "$dir\\vendor\\wheels" manim *>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) { $manimOk = $false }
} catch {
  $manimOk = $false
}
if (-not $manimOk) {
  Write-Host "manim is not bundled for this platform; PPT decks and memory work, video rendering needs a system install."
}
if (Test-Path "$dir\\vendor\\ffmpeg") {
  Add-Content "$dir\\.physics-anim-venv\\Scripts\\Activate.ps1" "`n`$env:PATH = `"$dir\\vendor\\ffmpeg;$env:PATH`""
}
Write-Host "Done. Activate with: $dir\\.physics-anim-venv\\Scripts\\Activate.ps1"
"""


INSTALL_PS1_PPT = """$ErrorActionPreference = "Stop"
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$managed = @(
  "$env:USERPROFILE\\.workbuddy\\binaries\\python\\envs\\manim\\python.exe",
  "$env:USERPROFILE\\.workbuddy\\binaries\\python\\envs\\default\\python.exe",
  "python"
)
$python = $null
foreach ($p in $managed) {
  if ($p -like "*\\python.exe") {
    if (Test-Path $p) { $python = $p; break }
  } else {
    $cmd = Get-Command $p -ErrorAction SilentlyContinue
    if ($cmd) { $python = $p; break }
  }
}
if (-not $python) {
  Write-Error "No Python 3 interpreter found. Install Python 3.10+ or run inside WorkBuddy."
  exit 1
}
& $python -m venv "$dir\\.physics-anim-venv"
& "$dir\\.physics-anim-venv\\Scripts\\pip.exe" install --no-index --find-links "$dir\\vendor\\wheels" `
  python-pptx pillow numpy imageio-ffmpeg
Write-Host "Done. Activate with: $dir\\.physics-anim-venv\\Scripts\\Activate.ps1"
Write-Host "Note: this package contains the PPT and memory kit only; Manim and rendered videos are not bundled."
"""


def write_installers(stage: Path, ver: str, tag: str, kind: str) -> None:
    install_sh = stage / "install.sh"
    install_sh.write_text(INSTALL_SH_FULL if kind in {"full", "renderer"} else INSTALL_SH_PPT, encoding="utf-8")
    install_sh.chmod(0o755)
    (stage / "install.ps1").write_text(INSTALL_PS1_FULL if kind in {"full", "renderer"} else INSTALL_PS1_PPT, encoding="utf-8")

    if kind == "full":
        readme = f"""# Offline package {ver} ({tag})

Everything works without a network connection.

1. Run the installer: `bash install.sh` (macOS/Linux) or `install.ps1`
   (Windows PowerShell).
2. Open `examples/videos/` for ready-made MP4s and `examples/pptx/` for
   editable decks with native click animations.
3. The plugin itself is under `plugins/alevel-physics-animations/`.

Requirements bundled: Python wheels, static ffmpeg, rendered videos. The
installers create a local `.physics-anim-venv` and never touch the system Python.
The installer prefers WorkBuddy-managed Python, then falls back to Python
3.10+ on `PATH`.
"""
    elif kind == "renderer":
        readme = f"""# Renderer package {ver} ({tag})

This package contains the Manim rendering environment and PPT/memory kit.

1. Run the installer: `bash install.sh` (macOS/Linux) or `install.ps1`
   (Windows PowerShell).
2. Open `examples/pptx/` for editable decks with native click animations.
3. Render videos locally with the bundled Python environment.

Manim wheels and static ffmpeg are bundled, but pre-rendered MP4 files are
not included. Use the CI-built `offline` package if you need ready-made
videos without rendering.
The installer prefers WorkBuddy-managed Python, then falls back to Python
3.10+ on `PATH`.
"""
    else:
        readme = f"""# PPT-only package {ver} ({tag})

This package contains the PPT and memory kit only.

1. Run the installer: `bash install.sh` (macOS/Linux) or `install.ps1`
   (Windows PowerShell).
2. Open `examples/pptx/` for editable decks with native click animations.
3. The plugin itself is under `plugins/alevel-physics-animations/`.

Manim and rendered videos are not bundled. To create video locally, install
the full package built by CI, or set up Manim on this machine.
The installer prefers WorkBuddy-managed Python, then falls back to Python
3.10+ on `PATH`.
"""
    (stage / "OFFLINE_README.md").write_text(readme, encoding="utf-8")


def build(local_only: bool = True) -> Path:
    ver = version()
    tag = platform_tag()
    stage = REPO / "work" / "dist-stage" / f"{ver}-{tag}"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    shutil.copytree(PLUGIN, stage / "plugins" / "alevel-physics-animations")
    for rel in KIT_FILES:
        src = REPO / rel
        if src.is_dir():
            shutil.copytree(src, stage / rel, dirs_exist_ok=True)
        elif src.exists():
            dst = stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    build_pptx(stage)
    video_count = copy_videos(stage)
    ffmpeg_ok = vendor_ffmpeg(stage)
    vendor_wheels(stage)

    missing_base = missing_packages(BASE_PACKAGES)
    has_base = not missing_base
    has_manim = has_package(MANIM_PACKAGE)

    if not has_base:
        print(
            "Cannot build an installable package: missing base wheels for "
            f"{', '.join(missing_base)}. Download them into work/wheels first.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    if has_base and has_manim and video_count > 0 and ffmpeg_ok:
        kind = "full"
    elif has_base and has_manim and video_count == 0 and ffmpeg_ok:
        kind = "renderer"
    elif has_base and not has_manim and video_count == 0:
        kind = "ppt"
    else:
        problems = []
        if not has_manim:
            problems.append("Manim wheels are missing")
        if video_count == 0:
            problems.append("rendered videos are missing")
        if not ffmpeg_ok:
            problems.append("vendored ffmpeg is missing")
        print(
            "Cannot build a complete offline package. Problems:\n  "
            + "\n  ".join(problems),
            file=sys.stderr,
        )
        raise SystemExit(1)

    write_installers(stage, ver, tag, kind)

    dist = REPO / "dist"
    dist.mkdir(exist_ok=True)
    prefix = {"full": "offline", "renderer": "renderer", "ppt": "ppt-only"}[kind]
    target = dist / f"alevel-physics-animations-{prefix}-{ver}-{tag}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(stage.rglob("*")):
            if path.is_file() and ".physics-anim-venv" not in path.parts:
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
