import json
import sys
from pathlib import Path

import pytest


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "alevel-physics-animations"
sys.path.insert(0, str(PLUGIN_ROOT / "hooks"))

import session_end  # noqa: E402
import session_start  # noqa: E402


def _transcript(tmp_path, *messages):
    path = tmp_path / "session.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for msg in messages:
            fh.write(
                json.dumps(
                    {"type": "event_msg", "payload": {"type": "user_message", "message": msg}},
                    ensure_ascii=False,
                )
                + "\n"
            )
    return str(path)


def test_hook_manifest_declares_session_start_and_stop():
    manifest = json.loads((PLUGIN_ROOT / "hooks" / "codex-hooks.json").read_text(encoding="utf-8"))
    assert set(manifest["hooks"]) == {"SessionStart", "Stop"}


def test_session_start_writes_baseline(memory_root):
    assert session_start.run(payload={"session_id": "s1"}) == 0
    sessions = memory_root / "sessions"
    latest = json.loads((sessions / "_latest.json").read_text(encoding="utf-8"))
    named = json.loads((sessions / "s1.json").read_text(encoding="utf-8"))
    assert latest["modifications"] == 0
    assert named["session_id"] == "s1"


def test_stop_blocks_when_request_was_not_recorded(memory_root, tmp_path, capsys):
    session_start.run(payload={"session_id": "s1"})
    transcript = _transcript(tmp_path, "把球的颜色改成蓝色")
    assert session_end.run(payload={"session_id": "s1", "transcript_path": transcript}) == 2
    err = capsys.readouterr().err
    assert "Memory gate" in err
    assert "颜色" not in err  # never leak transcript content


def test_stop_passes_after_modification_recorded(memory_root, tmp_path, capsys):
    session_start.run(payload={"session_id": "s2"})
    transcript = _transcript(tmp_path, "Make the ball blue instead")
    from memory import MemoryStore

    MemoryStore().add_modification("kinematics", "Make the ball blue", "Dot colour changed to blue")
    assert session_end.run(payload={"session_id": "s2", "transcript_path": transcript}) == 0
    assert "touched this session" in capsys.readouterr().out


def test_stop_passes_when_no_request_detected(memory_root, tmp_path):
    session_start.run(payload={"session_id": "s3"})
    transcript = _transcript(tmp_path, "Please draw a projectile animation.")
    assert session_end.run(payload={"session_id": "s3", "transcript_path": transcript}) == 0


def test_stop_passes_gracefully_without_baseline_or_transcript(memory_root):
    assert session_end.run(payload={}) == 0


def test_repeated_request_counts_as_touched_via_dedupe(memory_root, tmp_path):
    session_start.run(payload={"session_id": "s4"})
    from memory import MemoryStore

    store = MemoryStore()
    store.add_modification("kinematics", "Use a bigger font", "Font 32pt")
    store.add_modification("kinematics", "Use a bigger font", "Font 32pt")
    transcript = _transcript(tmp_path, "字体大一点")
    assert session_end.run(payload={"session_id": "s4", "transcript_path": transcript}) == 0
