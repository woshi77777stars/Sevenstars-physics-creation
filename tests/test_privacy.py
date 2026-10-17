from privacy import PrivacyViolation, load_denylist, require_clean, scan, scrub_path


def test_secret_categories_are_detected():
    cases = {
        "api-key": "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ123456",
        "credential": "password=hunter2secret",
        "private-ip": "server is at 192.168.1.10",
        "absolute-path": "file lives in /Users/teacher/Desktop/lesson.pptx",
        "email": "contact student@school.example.org",
        "phone-number": "call 13800138000",
    }
    for category, text in cases.items():
        found = [v.category for v in scan(text)]
        assert category in found, (category, text)


def test_violations_never_leak_the_value():
    secret = "sk-abcdefghijklmnopqrstuvwxyz0123456789"
    try:
        require_clean(secret)
        raise AssertionError("should have raised")
    except PrivacyViolation as exc:
        message = str(exc)
        assert "SUPER-SECRET" not in message
        assert "api-key" in message


def test_clean_text_passes():
    require_clean("The pendulum period is T = 2 pi sqrt(L/g).")
    require_clean("Use the PhET sim: https://phet.colorado.edu/en/simulations/projectile-motion")
    require_clean("The equation is v = s / t, nothing else.")


def test_urls_and_division_are_not_absolute_paths():
    url = "https://phet.colorado.edu/en/simulations/projectile-motion"
    assert "absolute-path" not in [v.category for v in scan(url)]
    assert "absolute-path" not in [v.category for v in scan("a = v² / r")]
    assert "absolute-path" in [v.category for v in scan("file lives in /Users/teacher/Desktop/lesson.pptx")]
    assert "absolute-path" in [v.category for v in scan(r"open C:\Users\teacher\lesson.pptx")]


def test_denylist_words_are_detected():
    words = load_denylist()
    assert words  # default seeds exist
    assert any("passport" in w for w in words)
    assert [v.category for v in scan("the passport number is 12345")] == ["denylist"]


def test_scrub_path_reports_files(tmp_path):
    (tmp_path / "ok.md").write_text("physics is fun", encoding="utf-8")
    (tmp_path / "bad.txt").write_text("login with password=abc123", encoding="utf-8")
    report = scrub_path(tmp_path)
    assert str(tmp_path / "ok.md") not in report
    assert "credential" in report[str(tmp_path / "bad.txt")]
