#!/usr/bin/env python3
"""Drop the starter-kit files (CLAUDE.md, MEMORY.md, ERRORS.md, anti-style.md)
into a target repo. Existing files are kept unless --force is passed.

Usage:
    python install.py <target_dir> [--force]
"""
from __future__ import annotations
import argparse
import os
import shutil

FILES = ["CLAUDE.md", "MEMORY.md", "ERRORS.md", "anti-style.md"]


def install(templates_dir: str, target_dir: str, force: bool = False) -> dict:
    """Copy each template into target_dir. Skip files that already exist unless
    force=True. Returns {"created": [...], "skipped": [...]}"""
    os.makedirs(target_dir, exist_ok=True)
    created, skipped = [], []
    for name in FILES:
        dst = os.path.join(target_dir, name)
        if os.path.exists(dst) and not force:
            skipped.append(name)
            continue
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
