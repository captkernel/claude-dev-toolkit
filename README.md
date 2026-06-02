# claude-dev-toolkit

Set up Claude Code well and build with it.

- **starter-kit/** — drop-in `CLAUDE.md` + `MEMORY.md` + `ERRORS.md` + `anti-style.md` with an `install.py` (skips existing files) and tests. The highest-leverage thing for Claude Code quality.
- **secrets-manager/** — keep API keys out of Claude Code's on-disk JSONL transcripts: a setup guide + a stdlib `secret_env.py` helper (with tests).
- **frontend-polish/** — a screenshot → self-review → refine loop that composes the official `frontend-design` skill instead of reinventing aesthetics.
- **a2a-agent-tutorial/** — a minimal, dependency-light Agent2Agent (A2A) demo in Python (pluggable LLM, runs offline, tested).
- **commands-reference.md** — which "Claude commands" are real native features vs. just renamed prompts.

Run any project's tests with `python -m pytest <subfolder>`.

## Use in Claude chat (claude.ai)

These are **Claude Code / runtime** tools (installers, a secrets helper, a Playwright screenshot loop, runnable agent code) — they need a local environment, so they aren't claude.ai chat skills. The *chat-usable* skills live in the sibling repos **claude-thinking-tools**, **claude-writing-tools**, and **claude-everyday-tools** (see their `skills/`).


---

_Curated/built from techniques shared by creators on Instagram (May 2026); marketing hype and inflated stats stripped out. Prompt text is rewritten, not copied; source handles are credited in the pack files._
