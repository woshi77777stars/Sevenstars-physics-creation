import sys
from pathlib import Path

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "alevel-physics-animations"
SCRIPTS = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


@pytest.fixture()
def memory_root(tmp_path):
    import os

    root = tmp_path / "memory"
    os.environ["PHYSICS_ANIM_MEMORY_DIR"] = str(root)
    yield root
    os.environ.pop("PHYSICS_ANIM_MEMORY_DIR", None)
