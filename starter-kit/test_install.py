import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from install import install, FILES  # noqa: E402

TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def test_install_creates_all_files(tmp_path):
    res = install(TEMPLATES, str(tmp_path))
    assert set(res["created"]) == set(FILES)
    assert res["skipped"] == []
    for f in FILES:
        assert (tmp_path / f).exists() and (tmp_path / f).read_text(encoding="utf-8")


def test_install_skips_existing_by_default(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("keep me", encoding="utf-8")
    res = install(TEMPLATES, str(tmp_path))
    assert "CLAUDE.md" in res["skipped"]
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") == "keep me"
    assert "MEMORY.md" in res["created"]


def test_force_overwrites(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("old", encoding="utf-8")
    res = install(TEMPLATES, str(tmp_path), force=True)
    assert "CLAUDE.md" in res["created"]
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8") != "old"


def test_templates_carry_the_four_rules():
    txt = open(os.path.join(TEMPLATES, "CLAUDE.md"), encoding="utf-8").read()
    for rule in ["Ask, don't assume", "Simplest solution first",
                 "Don't touch unrelated code", "Flag uncertainty"]:
        assert rule in txt


def test_install_creates_nested_claude_config(tmp_path):
    install(TEMPLATES, str(tmp_path))
    for rel in [".claude/settings.json", ".claude/commands/loop.md",
                ".claude/commands/goal.md", ".claude/agents/orchestrator.md"]:
        assert (tmp_path / rel).exists(), rel


def test_settings_json_is_valid_with_permissions(tmp_path):
    install(TEMPLATES, str(tmp_path))
    data = json.loads((tmp_path / ".claude/settings.json").read_text(encoding="utf-8"))
    perms = data["permissions"]
    # Read-only/test commands auto-allowed; destructive and secret reads denied.
    assert "Bash(pytest:*)" in perms["allow"]
    assert "Bash(rm -rf:*)" in perms["deny"]
    assert any(d.startswith("Read(./.env") for d in perms["deny"])


def test_skips_nested_existing_file(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text("keep me", encoding="utf-8")
    res = install(TEMPLATES, str(tmp_path))
    assert ".claude/settings.json" in res["skipped"]
    assert (tmp_path / ".claude/settings.json").read_text(encoding="utf-8") == "keep me"
