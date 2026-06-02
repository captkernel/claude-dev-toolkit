"""Tests for scripts/secret_env.py (TDD).

Run from the repo root with:

    .venv\\Scripts\\python.exe -m pytest projects\\claude-code-secrets-manager
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).parent
_MODULE_PATH = _HERE / "scripts" / "secret_env.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("secret_env", _MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["secret_env"] = mod  # required so @dataclass can resolve annotations
    spec.loader.exec_module(mod)
    return mod


secret_env = _load_module()


# --------------------------------------------------------------------------
# Manifest parsing
# --------------------------------------------------------------------------

def test_parse_manifest_extracts_names(tmp_path):
    manifest = tmp_path / "secrets.example.txt"
    manifest.write_text(
        "# a comment\n"
        "\n"
        "OPENAI_API_KEY = the key\n"
        "DATABASE_URL\n"
        "   STRIPE_SECRET_KEY   = inline desc # trailing comment\n",
        encoding="utf-8",
    )
    names = secret_env.parse_manifest(manifest)
    assert names == ["OPENAI_API_KEY", "DATABASE_URL", "STRIPE_SECRET_KEY"]


def test_parse_manifest_ignores_blank_and_comment_lines(tmp_path):
    manifest = tmp_path / "m.txt"
    manifest.write_text("\n\n# only comments\n   # indented comment\n", encoding="utf-8")
    assert secret_env.parse_manifest(manifest) == []


def test_parse_manifest_rejects_value_like_lines(tmp_path):
    """A line that looks like it carries a real value must be refused, so the
    manifest can never accidentally store secrets. 'NAME = description' is fine
    (descriptions are short words); but a long opaque token triggers a guard."""
    manifest = tmp_path / "m.txt"
    manifest.write_text(
        "OPENAI_API_KEY = sk-proj-abcdef 0123456789ABCDEFghijklmnop\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        secret_env.parse_manifest(manifest)


# --------------------------------------------------------------------------
# Resolution
# --------------------------------------------------------------------------

def test_resolve_from_environment():
    env = {"FOO": "supersecretvalue"}
    res = secret_env.resolve(["FOO", "BAR"], env=env, vault_get=None)
    assert res["FOO"].present is True
    assert res["FOO"].source == "env"
    assert res["FOO"].value == "supersecretvalue"
    assert res["BAR"].present is False
    assert res["BAR"].source == "missing"
    assert res["BAR"].value is None


def test_resolve_falls_back_to_vault():
    env = {}
    calls = []

    def fake_vault_get(name):
        calls.append(name)
        return "vaultvalue" if name == "FOO" else None

    res = secret_env.resolve(["FOO", "BAR"], env=env, vault_get=fake_vault_get)
    assert res["FOO"].present is True
    assert res["FOO"].source == "vault"
    assert res["FOO"].value == "vaultvalue"
    assert res["BAR"].present is False
    assert calls == ["FOO", "BAR"]


def test_env_takes_precedence_over_vault():
    env = {"FOO": "fromenv"}

    def fake_vault_get(name):
        return "fromvault"

    res = secret_env.resolve(["FOO"], env=env, vault_get=fake_vault_get)
    assert res["FOO"].source == "env"
    assert res["FOO"].value == "fromenv"


# --------------------------------------------------------------------------
# Redaction
# --------------------------------------------------------------------------

def test_redact_masks_value():
    assert secret_env.redact("supersecretvalue") == "su************ue"
    # short values are fully masked
    assert secret_env.redact("abc") == "***"
    assert secret_env.redact("") == "<empty>"
    assert secret_env.redact(None) == "<missing>"


def test_summary_never_contains_raw_value():
    env = {"FOO": "supersecretvalue", "TOK": "1234567890abcdef"}
    res = secret_env.resolve(["FOO", "TOK", "BAR"], env=env, vault_get=None)
    summary = secret_env.format_summary(res)
    assert "supersecretvalue" not in summary
    assert "1234567890abcdef" not in summary
    assert "FOO" in summary
    assert "BAR" in summary
    # status words present
    assert "env" in summary
    assert "missing" in summary


def test_summary_reports_counts():
    env = {"FOO": "x" * 20}
    res = secret_env.resolve(["FOO", "BAR"], env=env, vault_get=None)
    summary = secret_env.format_summary(res)
    assert "1/2" in summary  # 1 of 2 resolved


# --------------------------------------------------------------------------
# Export / CLI behaviour
# --------------------------------------------------------------------------

def test_export_env_lines_are_shell_safe():
    env = {"FOO": "val ue", "BAR": "plain"}
    res = secret_env.resolve(["FOO", "BAR"], env=env, vault_get=None)
    lines = secret_env.export_lines(res)
    assert 'export FOO=' in lines[0]
    # value is quoted
    assert "'val ue'" in lines[0]
    assert "export BAR='plain'" in lines[1]


def test_export_skips_missing():
    env = {"FOO": "v"}
    res = secret_env.resolve(["FOO", "BAR"], env=env, vault_get=None)
    lines = secret_env.export_lines(res)
    assert len(lines) == 1
    assert "BAR" not in "".join(lines)


def test_main_prints_redacted_summary(tmp_path, monkeypatch, capsys):
    manifest = tmp_path / "secrets.example.txt"
    manifest.write_text("FOO\nBAR\n", encoding="utf-8")
    monkeypatch.setenv("FOO", "supersecretvalue")
    monkeypatch.delenv("BAR", raising=False)
    # no vault configured
    monkeypatch.delenv("SECRET_ENV_VAULT_CMD", raising=False)

    rc = secret_env.main(["--manifest", str(manifest)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "supersecretvalue" not in out
    assert "FOO" in out
    assert "BAR" in out


def test_main_export_mode(tmp_path, monkeypatch, capsys):
    manifest = tmp_path / "secrets.example.txt"
    manifest.write_text("FOO\n", encoding="utf-8")
    monkeypatch.setenv("FOO", "secretvalue123")
    rc = secret_env.main(["--manifest", str(manifest), "--export"])
    out = capsys.readouterr().out
    assert rc == 0
    # export mode DOES emit the real value (it's meant to be eval'd), but only
    # on stdout export lines, and the human summary goes to stderr.
    assert "export FOO=" in out
