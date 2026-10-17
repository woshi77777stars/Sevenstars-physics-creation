import sys
from pathlib import Path

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "alevel-physics-animations"
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture()
def memory_env(tmp_path):
    """Redirect the project memory file and the gate marker into tmp_path."""
    import os

    os.environ["PHYSICS_ANIM_MEMORY_FILE"] = str(tmp_path / "PHYSICS-MEMORY.md")
    os.environ["PHYSICS_ANIM_GATE_DIR"] = str(tmp_path / "gate")
    yield tmp_path
    os.environ.pop("PHYSICS_ANIM_MEMORY_FILE", None)
    os.environ.pop("PHYSICS_ANIM_GATE_DIR", None)
