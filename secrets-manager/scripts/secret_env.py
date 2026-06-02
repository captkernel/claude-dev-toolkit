#!/usr/bin/env python3
"""secret_env.py — load secrets by NAME, never by value.

Reads a manifest of secret *names* (``secrets.example.txt``) and resolves each
name to a value from the process environment, falling back to a vault CLI
(e.g. Infisical) if one is configured. Prints a *redacted* summary by default so
you can confirm what is wired up without exposing values — and so prompts to
Claude Code reference ``${NAME}`` instead of pasting raw secrets.

Why this exists
---------------
Claude Code persists session transcripts as plaintext JSONL on disk. Anything
pasted into the chat (API keys, tokens, passwords) lands there in the clear.
Keep raw values out of the transcript: store them in a vault / your shell env,
reference them by NAME, and let an allowlisted CLI fetch them at runtime.

Usage
-----
    # Redacted status report (safe to show Claude / paste anywhere):
    python scripts/secret_env.py

    # Emit `export NAME='value'` lines for `eval` in your own shell
    # (NOT for the chat window — this prints real values to stdout):
    eval "$(python scripts/secret_env.py --export)"

Configure a vault CLI via the SECRET_ENV_VAULT_CMD env var. Use ``{name}`` as a
placeholder for the secret name, e.g.:

    SECRET_ENV_VAULT_CMD="infisical secrets get {name} --plain"

The module is dependency-free (standard library only).
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

# A valid secret NAME: shell-env-style identifier.
_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Heuristic guard: a manifest "description" token that looks like an opaque
# secret (long, high-entropy-ish run of base64/hex chars) is rejected, so the
# example file can never accidentally hold a real value.
_SECRET_LIKE_RE = re.compile(r"[A-Za-z0-9+/_\-]{20,}")

DEFAULT_MANIFEST = Path(__file__).with_name("secrets.example.txt")


# ---------------------------------------------------------------------------
# Manifest parsing
# ---------------------------------------------------------------------------

def parse_manifest(path: os.PathLike | str) -> List[str]:
    """Return the ordered list of secret NAMES declared in *path*.

    Format: one ``NAME`` per line, optionally ``NAME = short description``.
    ``#`` starts a comment. Blank lines are ignored. Raises ``ValueError`` if a
    line appears to embed a real value (so the file stays values-free).
    """
    names: List[str] = []
    text = Path(path).read_text(encoding="utf-8")
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if "=" in line:
            name, _, desc = line.partition("=")
            name = name.strip()
            desc = desc.strip()
            if _SECRET_LIKE_RE.search(desc):
                raise ValueError(
                    f"{path}:{lineno}: description looks like a real secret value; "
                    f"the manifest must contain NAMES and short descriptions only"
                )
        else:
            name = line
        if not _NAME_RE.match(name):
            raise ValueError(f"{path}:{lineno}: invalid secret name: {name!r}")
        names.append(name)
    return names


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

@dataclass
class Resolved:
    name: str
    value: Optional[str]
    source: str  # "env" | "vault" | "missing"

    @property
    def present(self) -> bool:
        return self.value is not None


def make_vault_getter(cmd_template: Optional[str]) -> Optional[Callable[[str], Optional[str]]]:
    """Build a vault getter from a command template containing ``{name}``.

    Returns None if no template is configured. The returned callable runs the
    CLI and returns the trimmed stdout, or None on any failure / empty output.
    """
    if not cmd_template:
        return None

    def getter(name: str) -> Optional[str]:
        # Substitute {name} safely (shell-quoted) then split into argv.
        filled = cmd_template.replace("{name}", shlex.quote(name))
        try:
            proc = subprocess.run(
                shlex.split(filled),
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if proc.returncode != 0:
            return None
        out = proc.stdout.strip()
        return out or None

    return getter


def resolve(
    names: List[str],
    env: Optional[Dict[str, str]] = None,
    vault_get: Optional[Callable[[str], Optional[str]]] = None,
) -> "Dict[str, Resolved]":
    """Resolve each NAME to a value. Environment wins; vault is the fallback."""
    if env is None:
        env = dict(os.environ)
    result: Dict[str, Resolved] = {}
    for name in names:
        if name in env and env[name] != "":
            result[name] = Resolved(name, env[name], "env")
            continue
        value = vault_get(name) if vault_get is not None else None
        if value is not None and value != "":
            result[name] = Resolved(name, value, "vault")
        else:
            result[name] = Resolved(name, None, "missing")
    return result


# ---------------------------------------------------------------------------
# Redaction / reporting
# ---------------------------------------------------------------------------

def redact(value: Optional[str]) -> str:
    """Mask a secret value for display. Never reveals the middle."""
    if value is None:
        return "<missing>"
    if value == "":
        return "<empty>"
    if len(value) <= 6:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"


def format_summary(resolved: "Dict[str, Resolved]") -> str:
    """A human-readable, fully redacted status table."""
    total = len(resolved)
    found = sum(1 for r in resolved.values() if r.present)
    width = max((len(n) for n in resolved), default=4)
    lines = [f"secrets resolved: {found}/{total}", ""]
    for r in resolved.values():
        lines.append(f"  {r.name.ljust(width)}  {r.source.ljust(8)}  {redact(r.value)}")
    return "\n".join(lines)


def _sq(value: str) -> str:
    """Single-quote a value for POSIX shell, always quoting for clarity."""
    # Close quote, insert an escaped single quote, reopen: foo'bar -> 'foo'\''bar'
    return "'" + value.replace("'", "'\\''") + "'"


def export_lines(resolved: "Dict[str, Resolved]") -> List[str]:
    """Shell ``export`` lines for present secrets (real values, for eval)."""
    lines: List[str] = []
    for r in resolved.values():
        if r.present:
            lines.append(f"export {r.name}={_sq(r.value)}")
    return lines


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve secrets by NAME from env or a vault CLI; print a redacted summary."
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST),
        help="path to secrets.example.txt (NAMES only). Default: alongside this script.",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="emit `export NAME='value'` lines on stdout (for `eval`); summary goes to stderr.",
    )
    parser.add_argument(
        "--vault-cmd",
        default=os.environ.get("SECRET_ENV_VAULT_CMD"),
        help="vault fetch command template using {name}, e.g. 'infisical secrets get {name} --plain'.",
    )
    args = parser.parse_args(argv)

    try:
        names = parse_manifest(args.manifest)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    vault_get = make_vault_getter(args.vault_cmd)
    resolved = resolve(names, env=dict(os.environ), vault_get=vault_get)
    summary = format_summary(resolved)

    if args.export:
        # Real values on stdout (for eval); redacted summary to stderr.
        for line in export_lines(resolved):
            print(line)
        print(summary, file=sys.stderr)
    else:
        print(summary)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
