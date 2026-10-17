from memory import MemoryStore
from privacy import PrivacyViolation

import pytest


def test_habit_add_then_duplicate_is_noop(memory_root):
    store = MemoryStore()
    first = store.add_habit("Use a 16:9 layout", kind="presentation", topics=["kinematics"])
    assert first.action == "added"
    second = store.add_habit("Use a 16:9 layout", kind="presentation", topics=["kinematics"])
    assert second.action == "noop"
    assert len(store.habits()) == 1
    assert (memory_root / "habits.jsonl").read_text().count("\n") == 1


def test_habit_kind_change_updates_in_place(memory_root):
    store = MemoryStore()
    store.add_habit("Keep slides uncluttered", kind="presentation")
    changed = store.add_habit("Keep slides uncluttered", kind="communication")
    assert changed.action == "updated"
    assert len(store.habits()) == 1
    assert store.habits()[0]["kind"] == "communication"


def test_error_recurrence_counts(memory_root):
    store = MemoryStore()
    a = store.add_error("kinematics", "Drew vertical fall as equal spacing", "Use 1:3:5 gaps")
    b = store.add_error("kinematics", "Drew vertical fall as equal spacing", "Use 1:3:5 gaps")
    assert a.action == "added"
    assert b.action == "updated"
    errors = store.errors()
    assert len(errors) == 1
    assert errors[0]["recurrences"] == 2


def test_same_wording_different_topic_stays_separate(memory_root):
    store = MemoryStore()
    store.add_error("kinematics", "Forgot the factor of one half", "Check 1/2 g t^2")
    store.add_error("capacitance", "Forgot the factor of one half", "Check 1/2 C V^2")
    assert len(store.errors()) == 2


def test_forget_writes_tombstone_and_removes(memory_root):
    store = MemoryStore()
    rec = store.add_habit("Prefer blue axes", kind="defaults").record
    removed = store.forget(record_id=rec["id"])
    assert removed == 1
    assert store.habits() == []
    tombstones = list((memory_root / "deleted").glob("*.jsonl"))
    assert len(tombstones) == 1
    assert rec["id"] in tombstones[0].read_text()


def test_privacy_violation_refuses_write(memory_root):
    store = MemoryStore()
    try:
        store.add_habit("My password=hunter2secret", kind="defaults")
        raise AssertionError("should have raised")
    except PrivacyViolation as exc:
        assert "hunter2secret" not in str(exc)
    assert store.habits() == []


def test_report_generation(memory_root):
    store = MemoryStore()
    store.add_habit("Use large fonts", kind="presentation")
    store.add_error("waves", "Mixed up node and antinode spacing", "Nodes are lambda/2 apart")
    store.add_modification("waves", "Make the wave blue", "Changed wave colour to blue")
    report = store.report()
    assert "Use large fonts" in report
    assert "lambda/2 apart" in report
    assert "Make the wave blue" in report


def test_modification_auto_record_and_repeat_counts(memory_root):
    store = MemoryStore()
    first = store.add_modification("kinematics", "Make the ball blue", "Changed dot colour to blue")
    second = store.add_modification("kinematics", "Make the ball blue", "Changed dot colour to blue")
    assert first.action == "added"
    assert second.action == "updated"
    records = store.modifications()
    assert len(records) == 1
    assert records[0]["recurrences"] == 2


def test_modification_same_request_different_topic_stays_separate(memory_root):
    store = MemoryStore()
    store.add_modification("kinematics", "Use a bigger font", "Font 32pt")
    store.add_modification("capacitance", "Use a bigger font", "Font 32pt")
    assert len(store.modifications()) == 2


def test_forget_covers_modifications_with_tombstone(memory_root):
    store = MemoryStore()
    rec = store.add_modification("waves", "No dashed lines", "Solid lines only").record
    assert store.forget(record_id=rec["id"]) == 1
    assert store.modifications() == []
    tombstone = next((memory_root / "deleted").glob("*.jsonl")).read_text()
    assert "modification" in tombstone


def test_modification_privacy_filter_applies(memory_root):
    store = MemoryStore()
    try:
        store.add_modification("waves", "Put my password=abc123 on the slide", "Added text")
        raise AssertionError("should have raised")
    except PrivacyViolation:
        pass
    assert store.modifications() == []


def test_forget_rejects_blank_match(memory_root):
    store = MemoryStore()
    store.add_habit("Use large fonts", kind="presentation")
    with pytest.raises(ValueError):
        store.forget(match="   ")
    assert len(store.habits()) == 1
