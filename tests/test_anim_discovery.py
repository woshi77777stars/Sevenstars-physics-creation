from anim import _scene_files_for
from redlines import TOPICS


def test_kinematics_has_three_scene_files():
    files = [p.stem for p in _scene_files_for("kinematics")]
    assert set(files) == {"free_fall", "projectile_horizontal", "projectile_oblique"}


def test_oscillations_has_two_scene_files():
    files = [p.stem for p in _scene_files_for("oscillations")]
    assert set(files) == {"oscillations_pendulum", "oscillations_spring"}


def test_every_topic_resolves_and_total_scene_files_are_28():
    seen = set()
    for topic in TOPICS:
        files = _scene_files_for(topic.id)
        assert files, f"no scene file for {topic.id}"
        seen.update(p for p in files)
    assert len(seen) == 28
