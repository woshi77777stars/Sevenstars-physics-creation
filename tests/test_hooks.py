import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "alevel-physics-animations" / "scripts"))

import memory_file  # noqa: E402
import memory_gate  # noqa: E402


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


def _transcript_wb(tmp_path, *messages):
    """WorkBuddy (Claude Code) transcript format."""
    path = tmp_path / "session-wb.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for msg in messages:
            fh.write(
                json.dumps(
                    {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "text", "text": msg}],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    return str(path)


def _reminder(user_query: str) -> str:
    return (
        "<system-reminder data-role=\"user-context\">\n"
        "请改成/换成/调整/去掉/不要…这是注入的记忆协议文字，不是老师的话。\n"
        "</system-reminder>\n"
        f"<user_query>{user_query}</user_query>"
    )


def _transcript_wb_reminder(tmp_path, user_query):
    path = tmp_path / "session-wb-reminder.jsonl"
    path.write_text(
        json.dumps(
            {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": _reminder(user_query)}],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return str(path)


def _touch_memory():
    path = memory_file.ensure_exists()
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n- 2026-10-17 ｜ 老师要求：改色 ｜ 已改为：蓝色\n")


def test_workbuddy_hook_manifest_is_native_format():
    manifest = json.loads((REPO_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    assert set(manifest["hooks"]) == {"SessionStart", "Stop"}
    start_cmd = manifest["hooks"]["SessionStart"][0]["hooks"][0]["command"]
    stop_cmd = manifest["hooks"]["Stop"][0]["hooks"][0]["command"]
    assert "${CODEBUDDY_PLUGIN_ROOT}/hooks/session_start.py" in start_cmd
    assert "${CODEBUDDY_PLUGIN_ROOT}/hooks/session_end.py" in stop_cmd
    assert "|| python" in start_cmd and "|| python" in stop_cmd  # Windows fallback


def test_workbuddy_plugin_manifest_points_at_kit():
    manifest = json.loads((REPO_ROOT / ".workbuddy-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["commands"] == "./commands"
    assert manifest["skills"] == "./skills"
    assert manifest["hooks"] == "./hooks/hooks.json"


def test_skill_manifest_declares_workbuddy_compat():
    manifest = json.loads((REPO_ROOT / "skills" / "physics-animation" / "manifest.json").read_text(encoding="utf-8"))
    assert "workbuddy" in manifest["compat"]
    assert manifest["name"] == "physics-animation"


def test_gate_blocks_when_request_not_written(memory_env, tmp_path, capsys):
    memory_file.ensure_exists()
    memory_gate.init_baseline("s1")
    transcript = _transcript(tmp_path, "把球的颜色改成蓝色")
    assert memory_gate.session_check(transcript, "s1") == 2
    err = capsys.readouterr().err
    assert "Memory gate" in err
    assert "蓝色" not in err  # never leak transcript content


def test_gate_passes_after_memory_updated(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("s2")
    transcript = _transcript(tmp_path, "Make the ball blue instead")
    _touch_memory()
    assert memory_gate.session_check(transcript, "s2") == 0


def test_gate_checks_each_turn_separately(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("s3")
    transcript = _transcript(tmp_path, "画一个平抛")
    # First check: only the first message (no request) -> pass, offset advances.
    assert memory_gate.session_check(transcript, "s3") == 0
    # The teacher's modification request arrives in the next turn.
    with open(transcript, "a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(
                {"type": "event_msg", "payload": {"type": "user_message", "message": "把字体调大"}},
                ensure_ascii=False,
            )
            + "\n"
        )
    # Second check: the new request exists and memory is untouched -> block.
    assert memory_gate.session_check(transcript, "s3") == 2


def test_bare_nouns_do_not_trigger(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("s4")
    transcript = _transcript(tmp_path, "这页颜色很漂亮，谢谢")
    assert memory_gate.session_check(transcript, "s4") == 0


def test_no_request_advances_marker(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("s5")
    transcript = _transcript(tmp_path, "画一个平抛动画")
    assert memory_gate.session_check(transcript, "s5") == 0
    marker = memory_gate.load_marker()
    assert marker["transcript_offset"] > 0


def test_workbuddy_transcript_format_is_parsed(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("wb1")
    transcript = _transcript_wb(tmp_path, "画一个平抛", "把标题字号调大")
    # Both messages are present at the first check, so it blocks immediately.
    assert memory_gate.session_check(transcript, "wb1") == 2


def test_workbuddy_format_passes_after_write(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("wb2")
    transcript = _transcript_wb(tmp_path, "change the colour to blue")
    _touch_memory()
    assert memory_gate.session_check(transcript, "wb2") == 0


def test_extract_user_text_variants():
    wb = {"type": "message", "role": "user", "content": [{"type": "text", "text": "把球改蓝"}]}
    wb_input = {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "把球改蓝"}]}
    wb_str = {"type": "message", "role": "user", "content": "把球改蓝"}
    codex = {"type": "event_msg", "payload": {"type": "user_message", "message": "把球改蓝"}}
    assistant = {"type": "message", "role": "assistant", "content": [{"type": "text", "text": "好的"}]}
    tool_result = {"type": "message", "role": "user", "content": [{"type": "tool_result", "content": "x"}]}
    assert memory_gate._extract_user_text(wb) == "把球改蓝"
    assert memory_gate._extract_user_text(wb_input) == "把球改蓝"
    assert memory_gate._extract_user_text(wb_str) == "把球改蓝"
    assert memory_gate._extract_user_text(codex) == "把球改蓝"
    assert memory_gate._extract_user_text(assistant) == ""
    assert memory_gate._extract_user_text(tool_result) == ""


def test_system_reminder_extracts_only_the_user_query():
    reminder = _reminder("画一个平抛")
    assert memory_gate._content_to_user_text([{"type": "input_text", "text": reminder}]) == "画一个平抛"
    assert "改成" not in memory_gate._content_to_user_text([{"type": "input_text", "text": reminder}])


def test_system_reminder_protocol_words_do_not_trigger(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("rem1")
    transcript = _transcript_wb_reminder(tmp_path, "画一个平抛")
    assert memory_gate.session_check(transcript, "rem1") == 0


def test_system_reminder_real_modification_request_triggers(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("rem2")
    transcript = _transcript_wb_reminder(tmp_path, "把标题字号调大")
    assert memory_gate.session_check(transcript, "rem2") == 2


def test_system_reminder_without_query_is_dropped(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("rem3")
    path = tmp_path / "no-query.jsonl"
    path.write_text(
        json.dumps(
            {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "<system-reminder>改成/不要/去掉</system-reminder>"}
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    assert memory_gate.session_check(str(path), "rem3") == 0


def test_bom_prefixed_transcript_is_parsed(memory_env, tmp_path):
    memory_file.ensure_exists()
    memory_gate.init_baseline("bom1")
    path = tmp_path / "bom.jsonl"
    path.write_bytes(
        b"\xef\xbb\xbf"
        + json.dumps(
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "把标题改成蓝色"}]},
            ensure_ascii=False,
        ).encode("utf-8")
        + b"\n"
    )
    assert memory_gate.session_check(str(path), "bom1") == 2
