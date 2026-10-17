import memory_file


def test_init_creates_structured_template(memory_env):
    path = memory_file.ensure_exists()
    assert path.name == "PHYSICS-MEMORY.md"
    text = path.read_text(encoding="utf-8")
    for section in range(1, 8):
        assert f"## {section}." in text
    assert "别写什么" in text  # privacy rule is part of the template


def test_ensure_exists_is_idempotent(memory_env):
    first = memory_file.ensure_exists()
    first.write_text("## 1. 课堂呈现习惯\n\n- 老师偏好 ｜ 证据：某次", encoding="utf-8")
    second = memory_file.ensure_exists()
    assert second.read_text(encoding="utf-8").startswith("## 1.")


def test_sections_parse(memory_env):
    memory_file.ensure_exists()
    sections = memory_file.sections()
    assert set(sections) == {1, 2, 3, 4, 5, 6, 7}
    assert "物理正确性红线" in memory_file.read()


def test_memory_path_env_override(memory_env, tmp_path):
    assert memory_file.memory_path() == tmp_path / "PHYSICS-MEMORY.md"
