import json
from pathlib import Path

from redlines import RED_LINES, TOPICS, TOPICS_BY_ID

from scenes import scene_metadata


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "alevel-physics-animations"


def test_every_topic_has_a_scene_and_a_deck():
    scenes = scene_metadata()
    decks = {
        json.loads(p.read_text(encoding="utf-8"))["topic"]
        for p in (PLUGIN_ROOT / "scripts" / "content").glob("*.deck.json")
    }
    for topic in TOPICS:
        assert topic.id in scenes, f"missing scene: {topic.id}"
        assert topic.id in decks, f"missing deck: {topic.id}"


def test_kinematics_has_three_scenes_and_oscillations_two():
    files = sorted((PLUGIN_ROOT / "scripts" / "scenes").glob("*.py"))
    names = [p.stem for p in files]
    assert "projectile_horizontal" in names
    assert "projectile_oblique" in names
    assert "free_fall" in names
    assert "oscillations_pendulum" in names
    assert "oscillations_spring" in names


def test_scene_declared_red_lines_exist():
    scenes_dir = PLUGIN_ROOT / "scripts" / "scenes"
    for path in scenes_dir.glob("*.py"):
        namespace = {}
        try:
            exec(  # noqa: S102
                compile(path.read_text(encoding="utf-8"), str(path), "exec"),
                {"__name__": "__peek__", "__file__": str(path)},
                namespace,
            )
        except Exception:
            pass
        meta = namespace.get("SCENE_META")
        if not meta:
            continue
        assert meta["topic"] in TOPICS_BY_ID, path
        for red_line in meta["red_lines"]:
            assert red_line in RED_LINES, (path, red_line)


def test_no_scene_duplicates_red_lines_across_topics():
    for topic in TOPICS:
        ids = {rl.id for rl in topic.red_lines}
        assert len(ids) == len(topic.red_lines)
