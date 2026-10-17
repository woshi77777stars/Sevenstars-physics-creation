from pathlib import Path

import _runtime
from anim import _ffmpeg_alias_dir, _setup_groups


def test_project_root_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("PHYSICS_ANIM_PROJECT_ROOT", str(tmp_path))
    assert _runtime.project_root() == tmp_path


def test_resolve_python_prefers_override(monkeypatch, tmp_path):
    monkeypatch.setenv("PHYSICS_ANIM_PYTHON", "/custom/python3")
    assert _runtime.resolve_python() == "/custom/python3"


def test_resolve_python_prefers_project_venv(monkeypatch, tmp_path):
    venv_python = tmp_path / ".physics-anim-venv" / "bin" / "python3"
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()
    monkeypatch.setenv("PHYSICS_ANIM_PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv("PHYSICS_ANIM_PYTHON", raising=False)
    assert Path(_runtime.resolve_python()) == venv_python


def test_setup_base_python_prefers_workbuddy_managed(monkeypatch, tmp_path, tmp_home):
    monkeypatch.delenv("PHYSICS_ANIM_PYTHON", raising=False)
    managed = tmp_home / ".workbuddy" / "binaries" / "python" / "envs" / "default" / "bin" / "python3"
    managed.parent.mkdir(parents=True)
    managed.touch()
    # Path.home() is cached by pathlib at import time in some versions; our
    # module calls Path.home() at call time, so monkeypatching home is enough.
    monkeypatch.setattr(_runtime.Path, "home", lambda: tmp_home)
    assert _runtime.setup_base_python() == str(managed)


def test_setup_base_python_handles_windows_layout(monkeypatch, tmp_home):
    monkeypatch.delenv("PHYSICS_ANIM_PYTHON", raising=False)
    managed = (
        tmp_home
        / ".workbuddy" / "binaries" / "python" / "envs" / "default" / "python.exe"
    )
    managed.parent.mkdir(parents=True)
    managed.touch()
    monkeypatch.setattr(_runtime.Path, "home", lambda: tmp_home)
    assert _runtime.setup_base_python() == str(managed)


def test_ffmpeg_alias_for_platform_named_binary(tmp_path):
    fake_exe = tmp_path / "bin" / "ffmpeg-macos-arm64"
    fake_exe.parent.mkdir(parents=True)
    fake_exe.write_bytes(b"fake")
    cache = tmp_path / "cache"
    alias_dir = _ffmpeg_alias_dir(str(fake_exe), cache, windows=False)
    assert alias_dir == str(cache)
    assert (cache / "ffmpeg").exists()
    # Idempotent: an existing alias is not re-copied.
    before = (cache / "ffmpeg").stat().st_mtime_ns
    assert _ffmpeg_alias_dir(str(fake_exe), cache, windows=False) == str(cache)
    assert (cache / "ffmpeg").stat().st_mtime_ns == before


def test_ffmpeg_alias_keeps_real_ffmpeg_dir(tmp_path):
    real = tmp_path / "bin" / "ffmpeg"
    real.parent.mkdir(parents=True)
    real.touch()
    assert _ffmpeg_alias_dir(str(real), tmp_path / "cache", windows=False) == str(real.parent)


def test_setup_groups_use_the_slim_plugin_requirements():
    slim = (
        Path(__file__).resolve().parents[1]
        / "plugins"
        / "alevel-physics-animations"
        / "requirements.txt"
    )
    base, manim = _setup_groups(slim)
    joined = "\n".join(base)
    assert "pycairo" not in joined  # never leak manim transitives into base
    assert "av" not in joined and "moderngl" not in joined
    names = {line.split("==")[0] for line in base}
    assert {"python-pptx", "pillow", "numpy", "imageio-ffmpeg"} <= names
    assert [line.split("==")[0] for line in manim] == ["manim"]
