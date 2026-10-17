from pathlib import Path

import _runtime


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
