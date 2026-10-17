"""Single CLI entry point for the A-Level Physics Animations plugin.

Commands:
  anim topics                                  List all CIE 9702 topics.
  anim render TOPIC [--scene NAME] [--1080p30] [--out DIR]
  anim render-all [--out DIR]
  anim ppt TOPIC [--out DIR]
  anim ppt-all [--out DIR]
  anim template [--out FILE]
  anim memory report [--out FILE]
  anim memory init
  anim memory where
  anim memory session-check --transcript PATH [--session-id ID]
  anim setup [--offline]
  anim scrub PATH
  anim install-check
  anim verify [--smoke]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import _runtime
import memory_file
from privacy import scrub_path
from redlines import TOPICS_BY_ID, assert_topic


SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = _runtime.repo_root()


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="anim", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("topics", help="List all topics.")

    render = sub.add_parser("render", help="Render one Manim scene.")
    render.add_argument("topic")
    render.add_argument("--scene")
    render.add_argument("--1080p30", action="store_true")
    render.add_argument("--out", default="outputs/videos")

    render_all = sub.add_parser("render-all", help="Render every scene.")
    render_all.add_argument("--out", default="outputs/videos")

    ppt = sub.add_parser("ppt", help="Build one PowerPoint deck.")
    ppt.add_argument("topic")
    ppt.add_argument("--out", default="outputs/pptx")

    ppt_all = sub.add_parser("ppt-all", help="Build every PowerPoint deck.")
    ppt_all.add_argument("--out", default="outputs/pptx")

    template = sub.add_parser("template", help="Emit the reusable ppt-master.pptx.")
    template.add_argument("--out")

    memory = sub.add_parser("memory")
    mem_sub = memory.add_subparsers(dest="memory_command", required=True)
    report = mem_sub.add_parser("report")
    report.add_argument("--out")
    mem_sub.add_parser("init")
    mem_sub.add_parser("where")
    check = mem_sub.add_parser("session-check")
    check.add_argument("--transcript", required=True)
    check.add_argument("--session-id", default="")

    setup = sub.add_parser("setup", help="Create the project venv and install pinned dependencies.")
    setup.add_argument("--offline", action="store_true", help="Install from vendored wheels only.")

    scrub = sub.add_parser("scrub", help="Scan text files for private data (categories only).")
    scrub.add_argument("path")

    sub.add_parser("install-check", help="Report Python/Manim/ffmpeg readiness.")

    verify = sub.add_parser("verify", help="Run tests and smoke checks.")
    verify.add_argument("--smoke", action="store_true")

    return parser.parse_args(argv)


def _find_ffmpeg() -> str | None:
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _ffmpeg_alias_dir(exe: str, cache_dir: Path, windows: bool) -> str:
    """Directory whose PATH entry exposes an executable named `ffmpeg`.

    imageio-ffmpeg bundles a platform-named binary (e.g. ffmpeg-macos-arm64),
    which `shutil.which("ffmpeg")` cannot find. Copy it once to a cached
    `ffmpeg`/`ffmpeg.exe` alias and return that directory."""
    exe_path = Path(exe)
    if exe_path.stem == "ffmpeg":
        return str(exe_path.parent)
    alias = cache_dir / ("ffmpeg.exe" if windows else "ffmpeg")
    if not alias.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(exe_path, alias)
    return str(cache_dir)


def _ffmpeg_dir() -> str | None:
    exe = _find_ffmpeg()
    if exe is None:
        return None
    return _ffmpeg_alias_dir(exe, REPO_ROOT / "work" / ".ffmpeg-bin", os.name == "nt")


def _python() -> str:
    return sys.executable


def _run(cmd: list[str], env: dict | None = None) -> int:
    proc_env = dict(os.environ)
    if env:
        proc_env.update(env)
    return subprocess.call(cmd, cwd=str(REPO_ROOT), env=proc_env)


def _scene_files() -> list[Path]:
    return sorted((SCRIPTS_DIR / "scenes").rglob("*.py"))


def _scene_files_for(topic: str) -> list[Path]:
    """Every scene file whose SCENE_META topic matches (a topic may span
    several files, e.g. kinematics has three)."""
    matches = []
    for path in _scene_files():
        if path.name == "__init__.py" or path.name == "_common.py":
            continue
        meta = _peek_meta(path)
        if meta and meta.get("topic") == topic:
            matches.append(path)
    return matches


def _peek_meta(path: Path) -> dict:
    """Extract SCENE_META without importing (avoids a Manim dependency)."""
    namespace: dict = {}
    try:
        exec(  # noqa: S102
            compile(path.read_text(encoding="utf-8"), str(path), "exec"),
            {"__name__": "__peek__", "__file__": str(path)},
            namespace,
        )
    except Exception:
        pass  # SCENE_META is set before the manim import, so it survives failures
    return namespace.get("SCENE_META", {})


def cmd_topics(args: argparse.Namespace) -> int:
    for topic in sorted(TOPICS_BY_ID.values(), key=lambda t: t.number):
        print(f"{topic.number:>2}  {topic.id:<28} {topic.name}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    assert_topic(args.topic)
    modules = _scene_files_for(args.topic)
    if not modules:
        print(f"No scene implemented for topic {args.topic!r}.", file=sys.stderr)
        return 1
    import importlib.util

    if importlib.util.find_spec("manim") is None:
        print("Manim is not installed. Run `pip install -r requirements.txt`.", file=sys.stderr)
        return 1
    pairs: list[tuple[Path, type]] = []
    for module in modules:
        try:
            classes = _scene_classes(module)
        except ImportError as exc:
            print(f"Manim could not be loaded: {exc}", file=sys.stderr)
            return 1
        if args.scene:
            pairs.extend((module, cls) for cls in classes if cls.__name__ == args.scene)
        else:
            pairs.extend((module, cls) for cls in classes)
    if args.scene and not pairs:
        available = sorted(
            {cls.__name__ for module in modules for cls in _scene_classes(module)}
        )
        print(f"Scene {args.scene!r} not found; available for {args.topic}: {available}", file=sys.stderr)
        return 1

    ffmpeg_dir = _ffmpeg_dir()
    if ffmpeg_dir is None:
        print("ffmpeg not found. Install it or `pip install imageio-ffmpeg`.", file=sys.stderr)
        return 1
    env = {"PATH": ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")}

    out_base = Path(args.out)
    out_base.mkdir(parents=True, exist_ok=True)
    quality = ["-r", "1920,1080", "--fps", "30"] if args.__dict__.get("1080p30") else ["-ql"]
    python_exe = _runtime.python_for_render()
    probe = subprocess.run(
        [python_exe, "-c", "import manim"],
        capture_output=True,
    )
    if probe.returncode != 0:
        print(
            f"Manim is not available in the selected Python ({python_exe}). "
            "Run `anim setup` (needs network, or `anim setup --offline` with vendored wheels).",
            file=sys.stderr,
        )
        return 1
    failed = 0
    for module, cls in pairs:
        cmd = [
            python_exe, "-m", "manim", "render",
            *quality, "--format", "mp4", "--media_dir", str(out_base),
            str(module), cls.__name__,
        ]
        rc = _run(cmd, env)
        if rc == 0:
            _copy_render(out_base, module, cls.__name__, args.topic)
        else:
            failed += 1
    return 1 if failed else 0


def _copy_render(out_base: Path, module: Path, class_name: str, topic: str) -> None:
    """Locate the freshly rendered mp4 and copy it to <out>/<topic>/<scene>.mp4."""
    module_stem = module.stem
    matches = list(out_base.rglob(f"**/{class_name}.mp4"))
    matches = [p for p in matches if f"/{module_stem}/" in str(p) or module_stem in p.parts]
    if not matches:
        return
    dest_dir = out_base / topic
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(matches[-1], dest_dir / f"{class_name}.mp4")


def _scene_classes(module: Path) -> list[type]:
    import importlib.util

    spec = importlib.util.spec_from_file_location(f"anim_scenes_{module.stem}", module)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from manim import Scene

    return [
        obj
        for name, obj in vars(mod).items()
        if isinstance(obj, type)
        and issubclass(obj, Scene)
        and obj.__module__ == mod.__name__
        and name != "Scene"
    ]


def cmd_render_all(args: argparse.Namespace) -> int:
    failed = []
    for topic in sorted(TOPICS_BY_ID):
        rc = cmd_render(argparse.Namespace(topic=topic, scene=None, out=args.out, **{"1080p30": True}))
        if rc:
            failed.append(topic)
    if failed:
        print("Failed topics:", ", ".join(failed), file=sys.stderr)
    return 1 if failed else 0


def cmd_ppt(args: argparse.Namespace) -> int:
    if _reexec_if_missing_module("pptx"):
        return 0
    try:
        from ppt_builder import build_deck
    except ImportError as exc:
        print(
            f"python-pptx is not available in the resolved Python ({_runtime.resolve_python()}). "
            f"Run `anim setup` first. ({exc})",
            file=sys.stderr,
        )
        return 1

    assert_topic(args.topic)
    out = build_deck(args.topic, Path(args.out))
    print(out)
    return 0


def cmd_ppt_all(args: argparse.Namespace) -> int:
    if _reexec_if_missing_module("pptx"):
        return 0
    try:
        from ppt_builder import available_topics, build_deck
    except ImportError as exc:
        print(
            f"python-pptx is not available in the resolved Python ({_runtime.resolve_python()}). "
            f"Run `anim setup` first. ({exc})",
            file=sys.stderr,
        )
        return 1

    failed = []
    for topic in available_topics():
        try:
            build_deck(topic, Path(args.out))
        except Exception as exc:  # keep going, report at the end
            print(f"{topic}: {exc}", file=sys.stderr)
            failed.append(topic)
    return 1 if failed else 0


def cmd_template(args: argparse.Namespace) -> int:
    if _reexec_if_missing_module("pptx"):
        return 0
    try:
        from ppt_builder import build_template
    except ImportError as exc:
        print(
            f"python-pptx is not available in the resolved Python ({_runtime.resolve_python()}). "
            f"Run `anim setup` first. ({exc})",
            file=sys.stderr,
        )
        return 1

    print(build_template(Path(args.out) if args.out else None))
    return 0


def _reexec_if_missing_module(module: str) -> bool:
    """Run this CLI again with a capable interpreter when the current one
    lacks `module`. Returns True only when the process was replaced."""
    try:
        __import__(module)
        return False
    except ImportError:
        pass
    target = _runtime.resolve_python()
    if Path(target).resolve() == Path(sys.executable).resolve():
        return False
    os.execv(target, [target, *sys.argv])
    return True  # unreachable


def cmd_setup(args: argparse.Namespace) -> int:
    """Create `<project>/.physics-anim-venv` and install pinned deps."""
    base = _runtime.setup_base_python()
    venv_dir = _runtime.project_root() / ".physics-anim-venv"
    venv_python = venv_dir / "bin" / "python3"
    if not venv_python.exists():
        venv_python = venv_dir / "Scripts" / "python.exe"
    if not venv_python.exists():
        print(f"Creating {venv_dir} with {base} ...")
        rc = subprocess.call([base, "-m", "venv", str(venv_dir)])
        if rc:
            print("venv creation failed.", file=sys.stderr)
            return rc
        venv_python = venv_dir / "bin" / "python3"
        if not venv_python.exists():
            venv_python = venv_dir / "Scripts" / "python.exe"

    # The plugin's own slim requirements (5 top-level pinned packages) are
    # the setup source. The repository root file is the full uv lock
    # including manim transitive deps (pycairo, av, moderngl...), which must
    # never leak into the base install on machines without cairo.
    reqs = SCRIPTS_DIR.parent / "requirements.txt"
    if not reqs.exists():
        reqs = REPO_ROOT / "requirements.txt"
    if not reqs.exists():
        print("requirements.txt not found.", file=sys.stderr)
        return 1

    print("Installing pinned dependencies (may take several minutes) ...")
    base_deps, manim_deps = _setup_groups(reqs)
    wheels_args = []
    if args.offline:
        wheels = REPO_ROOT / "vendor" / "wheels"
        if not wheels.exists():
            wheels = REPO_ROOT / "work" / "wheels"
        if not wheels.exists():
            print("No vendored wheels found for offline install.", file=sys.stderr)
            return 1
        wheels_args = ["--no-index", "--find-links", str(wheels)]
    rc = subprocess.call([str(venv_python), "-m", "pip", "install", *wheels_args, *base_deps])
    if rc:
        print("Base dependency install failed; see pip output above.", file=sys.stderr)
        return rc
    if manim_deps:
        manim_rc = subprocess.call([str(venv_python), "-m", "pip", "install", *wheels_args, *manim_deps])
        if manim_rc:
            print(
                "PPT, memory and privacy tools are ready. Manim could not be installed "
                "(on macOS it needs a system cairo: brew install cairo pkg-config). "
                "Re-run `anim setup` after installing cairo to enable video rendering.",
                file=sys.stderr,
            )
    print(f"Setup complete: {venv_python}")
    return 0


def _setup_groups(requirements_path: Path) -> tuple[list[str], list[str]]:
    """Split the slim requirements into base (no Manim) and manim groups."""
    lines = [
        line.strip()
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    base = [line for line in lines if not line.startswith("manim")]
    manim = [line for line in lines if line.startswith("manim")]
    return base, manim


def cmd_memory(args: argparse.Namespace) -> int:
    if args.memory_command == "report":
        text = memory_file.read()
        if not text:
            print("No PHYSICS-MEMORY.md yet. Run `anim memory init`.", file=sys.stderr)
            return 1
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print(args.out)
        else:
            print(text)
        return 0
    if args.memory_command == "init":
        print(memory_file.ensure_exists())
        return 0
    if args.memory_command == "where":
        print(memory_file.memory_path())
        return 0
    if args.memory_command == "session-check":
        from memory_gate import session_check

        return session_check(args.transcript, args.session_id)
    return 2


def cmd_scrub(args: argparse.Namespace) -> int:
    report = scrub_path(Path(args.path))
    if not report:
        print("No privacy violations found.")
        return 0
    for file, categories in sorted(report.items()):
        print(f"{file}: {', '.join(categories)}")
    return 1


def cmd_install_check(args: argparse.Namespace) -> int:
    resolved = _runtime.resolve_python()
    version_probe = subprocess.run(
        [resolved, "-c", "import sys; print(sys.version.split()[0])"],
        capture_output=True,
        text=True,
    )
    checks = {
        "resolved_python": resolved,
        "python": version_probe.stdout.strip() or "MISSING",
        "ffmpeg": _find_ffmpeg() or "MISSING",
        "manim": _module_version(resolved, "manim"),
        "python-pptx": _module_version(resolved, "pptx"),
    }
    if Path(resolved).resolve() != Path(sys.executable).resolve():
        checks["launched_with"] = sys.executable
    if checks["python-pptx"] == "MISSING" or checks["manim"] == "MISSING":
        checks["hint"] = "Run `anim setup` (or `anim setup --offline`) to create the project venv."
    print(json.dumps(checks, indent=2))
    return 0 if checks["ffmpeg"] != "MISSING" and checks["manim"] != "MISSING" else 1


def _module_version(python_exe: str, module: str) -> str:
    probe = subprocess.run(
        [
            python_exe,
            "-c",
            f"import {module}; print(getattr({module}, '__version__', 'installed'))",
        ],
        capture_output=True,
        text=True,
    )
    return probe.stdout.strip() if probe.returncode == 0 else "MISSING"


def cmd_verify(args: argparse.Namespace) -> int:
    tests = REPO_ROOT / "tests"
    rc = _run([_python(), "-m", "pytest", str(tests), "-q"])
    if rc:
        return rc

    # PPT smoke check: build every deck and validate the animation XML.
    try:
        from ppt_builder import available_topics, build_deck, validate_deck
    except ImportError as exc:
        print(f"python-pptx missing for the smoke check. Run `anim setup`. ({exc})", file=sys.stderr)
        return 1

    smoke_dir = Path("work") / "ppt-smoke"
    for topic in available_topics():
        deck = build_deck(topic, smoke_dir)
        summary = validate_deck(deck)
        content = next(s for s in summary["slides_checked"] if s.get("present"))
        if content["click_effects"] != content["body_paragraphs"]:
            print(f"{topic}: animation mismatch {content}", file=sys.stderr)
            return 1
    print(f"PPT smoke: {len(available_topics())} decks OK")

    if args.smoke:
        first = sorted(TOPICS_BY_ID)[0]
        rc = cmd_render(argparse.Namespace(topic=first, scene=None, out="work/smoke", **{"1080p30": False}))
        if rc:
            return rc
        print(f"Render smoke: {first} OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    handlers = {
        "topics": cmd_topics,
        "render": cmd_render,
        "render-all": cmd_render_all,
        "ppt": cmd_ppt,
        "ppt-all": cmd_ppt_all,
        "template": cmd_template,
        "memory": cmd_memory,
        "setup": cmd_setup,
        "scrub": cmd_scrub,
        "install-check": cmd_install_check,
        "verify": cmd_verify,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
