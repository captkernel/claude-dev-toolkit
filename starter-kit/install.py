#!/usr/bin/env python3
"""Drop the starter-kit files into a target repo. Existing files are kept unless
--force is passed.

Copies the project-context files (CLAUDE.md, MEMORY.md, ERRORS.md, anti-style.md)
plus a `.claude/` config tree that sets up long-running/autonomous work:
a curated permission allowlist (settings.json), the `/loop` and `/goal` slash
commands, and an `orchestrator` subagent.

Usage:
    python install.py <target_dir> [--force]
"""
from __future__ import annotations
import argparse
import os
import shutil

# Relative paths copied from templates/ into the target, in order. Nested paths
# (under .claude/) have their parent directories created as needed.
FILES = [
    "CLAUDE.md",
    "MEMORY.md",
    "ERRORS.md",
    "anti-style.md",
    ".claude/settings.json",
    ".claude/commands/loop.md",
    ".claude/commands/goal.md",
    ".claude/agents/orchestrator.md",
]


def install(templates_dir: str, target_dir: str, force: bool = False) -> dict:
    """Copy each template into target_dir, preserving relative subpaths. Skip
    files that already exist unless force=True. Returns
    {"created": [...], "skipped": [...]}"""
    os.makedirs(target_dir, exist_ok=True)
    created, skipped = [], []
    for name in FILES:
        dst = os.path.join(target_dir, name)
        if os.path.exists(dst) and not force:
            skipped.append(name)
            continue
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        shutil.copyfile(os.path.join(templates_dir, name), dst)
        created.append(name)
    return {"created": created, "skipped": skipped}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Install the Claude Code starter kit.")
    ap.add_argument("target", help="directory to install the kit into")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing files")
    args = ap.parse_args(argv)
    here = os.path.dirname(os.path.abspath(__file__))
    res = install(os.path.join(here, "templates"), args.target, args.force)
    for f in res["created"]:
        print(f"  created  {f}")
    for f in res["skipped"]:
        print(f"  skipped  {f} (already exists - use --force to overwrite)")
    print(f"done: {len(res['created'])} created, {len(res['skipped'])} skipped "
          f"in {args.target}")


if __name__ == "__main__":
    main()
