"""Single CLI entry point for the A-Level Physics Animations plugin.

Commands:
  anim topics                                  List all CIE 9702 topics.
  anim render TOPIC [--scene NAME] [--1080p30] [--out DIR]
  anim render-all [--out DIR]
  anim ppt TOPIC [--out DIR]
  anim ppt-all [--out DIR]
  anim template [--out FILE]
  anim memory add habit --kind K --content TEXT [--topic T]...
  anim memory add error --topic T --description TEXT --correct TEXT
  anim memory forget (--id ID | --match TEXT)
  anim memory show [--kind habit|error]
  anim memory report [--out FILE]
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

from memory import MemoryStore
from privacy import scrub_path
from redlines import TOPICS_BY_ID, assert_topic


SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parents[2]


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
    add = mem_sub.add_parser("add")
    add_sub = add.add_subparsers(dest="record_type", required=True)
    habit = add_sub.add_parser("habit")
    habit.add_argument("--kind", default="presentation", choices=["presentation", "communication", "defaults"])
    habit.add_argument("--content", required=True)
    habit.add_argument("--topic", action="append", default=[])
    error = add_sub.add_parser("error")
    error.add_argument("--topic", required=True)
    error.add_argument("--description", required=True)
    error.add_argument("--correct", required=True)
    modification = add_sub.add_parser("modification")
    modification.add_argument("--topic", required=True)
    modification.add_argument("--request", required=True)
    modification.add_argument("--change", required=True)
    forget = mem_sub.add_parser("forget")
    forget_group = forget.add_mutually_exclusive_group(required=True)
    forget_group.add_argument("--id")
    forget_group.add_argument("--match")
    show = mem_sub.add_parser("show")
    show.add_argument("--kind", choices=["habit", "error"])
    report = mem_sub.add_parser("report")
    report.add_argument("--out")

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

    ffmpeg = _find_ffmpeg()
    if ffmpeg is None:
        print("ffmpeg not found. Install it or `pip install imageio-ffmpeg`.", file=sys.stderr)
        return 1
    env = {"PATH": str(Path(ffmpeg).parent) + os.pathsep + os.environ.get("PATH", "")}

    out_base = Path(args.out)
    out_base.mkdir(parents=True, exist_ok=True)
    quality = ["-r", "1920,1080", "--fps", "30"] if args.__dict__.get("1080p30") else ["-ql"]
    failed = 0
    for module, cls in pairs:
        cmd = [
            _python(), "-m", "manim", "render",
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
    from ppt_builder import build_deck

    assert_topic(args.topic)
    out = build_deck(args.topic, Path(args.out))
    print(out)
    return 0


def cmd_ppt_all(args: argparse.Namespace) -> int:
    from ppt_builder import build_deck, available_topics

    failed = []
    for topic in available_topics():
        try:
            build_deck(topic, Path(args.out))
        except Exception as exc:  # keep going, report at the end
            print(f"{topic}: {exc}", file=sys.stderr)
            failed.append(topic)
    return 1 if failed else 0


def cmd_template(args: argparse.Namespace) -> int:
    from ppt_builder import build_template

    print(build_template(Path(args.out) if args.out else None))
    return 0


def cmd_memory(args: argparse.Namespace) -> int:
    store = MemoryStore()
    if args.memory_command == "add":
        if args.record_type == "habit":
            result = store.add_habit(args.content, getattr(args, "kind", "presentation"), args.topic)
        elif args.record_type == "modification":
            result = store.add_modification(args.topic, args.request, args.change)
        else:
            result = store.add_error(args.topic, args.description, args.correct)
        print(json.dumps({"action": result.action, "id": result.record.get("id")}))
        return 0
    if args.memory_command == "forget":
        if args.match is not None and not args.match.strip():
            print("forget --match requires a non-empty keyword.", file=sys.stderr)
            return 2
        removed = store.forget(match=args.match, record_id=args.id)
        print(json.dumps({"removed": removed}))
        return 0
    if args.memory_command == "show":
        if args.kind == "habit":
            records = store.habits()
        elif args.kind == "error":
            records = store.errors()
        else:
            records = store.habits() + store.errors() + store.modifications()
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0
    if args.memory_command == "report":
        target = Path(args.out) if args.out else None
        path = store.write_report(target)
        print(path)
        return 0
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
    checks = {
        "python": sys.version.split()[0],
        "ffmpeg": _find_ffmpeg() or "MISSING",
    }
    try:
        import manim  # noqa: F401

        checks["manim"] = getattr(manim, "__version__", "installed")
    except Exception:
        checks["manim"] = "MISSING"
    try:
        import pptx  # noqa: F401

        checks["python-pptx"] = pptx.__version__
    except Exception:
        checks["python-pptx"] = "MISSING"
    print(json.dumps(checks, indent=2))
    return 0 if checks["ffmpeg"] != "MISSING" and checks["manim"] != "MISSING" else 1


def cmd_verify(args: argparse.Namespace) -> int:
    tests = REPO_ROOT / "tests"
    rc = _run([_python(), "-m", "pytest", str(tests), "-q"])
    if rc:
        return rc

    # PPT smoke check: build every deck and validate the animation XML.
    from ppt_builder import available_topics, build_deck, validate_deck

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
        "scrub": cmd_scrub,
        "install-check": cmd_install_check,
        "verify": cmd_verify,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
