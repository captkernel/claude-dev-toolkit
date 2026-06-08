# Long-Running Autonomy — running Claude for hours/days (de-hyped)

Source: a Threads post by **boris-cherny** (a Claude Code creator), May/June 2026,
on getting good results from Opus 4.8 on long-running, autonomous work. The post
lists five tips. They're sound, but most are *usage habits* or *runtime settings*,
not things you "install." This file separates what you actually wire into a project
from what you just do, and points at the files in `starter-kit/` that bake the
wireable parts in.

Legend:
- 🔧 **Wireable** — there's a concrete file/setting you can drop into every project (shipped in `starter-kit/`).
- 🪄 **Habit** — a way you drive Claude; nothing to install.

---

## The five tips, mapped to real mechanisms

### 1. Auto mode for permissions — so Claude doesn't stop to ask 🔧
Don't reach for `--dangerously-skip-permissions` (alias: "YOLO mode") as your
default — it approves *everything*, including destructive commands. The safer way
to keep an autonomous run from stalling is a **curated permission allowlist** in
`.claude/settings.json`: auto-allow the safe, repeatable stuff (read-only inspection,
tests, linters, type-checks, `git status/diff/log`) and let writes/deploys still
prompt. `--dangerously-skip-permissions` is real and useful in a throwaway sandbox,
but it's not what you want shipped to every repo.
→ Shipped: `starter-kit/templates/.claude/settings.json` (allow / ask / deny lists).

### 2. Dynamic workflows — orchestrate many subagents 🔧🪄
Claude Code can spawn **subagents** (the Task/Agent tool) and run independent
subtasks in parallel. The leverage is in *decomposition*: split a big task into
pieces with no shared files / no ordering between them, delegate each, then
integrate and verify the whole. The "hundreds/thousands of agents" framing is
aspirational — the real win is breadth over one long serial thread.
→ Shipped: an `orchestrator` subagent (`starter-kit/templates/.claude/agents/orchestrator.md`)
that does decompose → delegate in parallel → integrate → verify.

### 3. `/loop` or `/goal` — nudge Claude to keep going until done 🔧🪄
These are **not native** Claude Code commands — they're custom slash commands you
define (a `.claude/commands/<name>.md` file is just a saved prompt). The pattern
that makes them work: fix a *checkable definition of done* up front (`/goal`), then
loop — do a step, self-verify, fix, repeat — until it's green or genuinely blocked
(`/loop`). Without a definition of done, "keep going" just drifts.
(There's also a community `loop` skill in some setups that runs a prompt on an
interval; that's a different thing — a timer, not a finish-the-task loop.)
→ Shipped: `starter-kit/templates/.claude/commands/loop.md` and `goal.md`.

### 4. Claude Code in the cloud — close your laptop 🪄
Run sessions from the **desktop or mobile app**, or Claude Code on the web, so a
long job keeps going after you walk away. Nothing to put in a repo — it's where you
launch from. Docs: https://code.claude.com/docs/en/claude-code-on-the-web
(This very session is an example: a remote, ephemeral container. Anything worth
keeping has to be committed and pushed before the container is reclaimed.)

### 5. Self-verify end to end — give Claude a way to check its own work 🔧🪄
The highest-value tip, and the one people skip. Autonomy is only safe if Claude can
*prove* the work, not just assert it. Give it a real feedback loop:
- **Backend/CLI:** a way to start the server/service and exercise it; a test suite.
- **Web/UI:** a browser the model can drive (e.g. a Chrome extension / Playwright)
  so it can screenshot and review its own output — see `frontend-polish/`.
- **Mobile:** an iOS/Android **simulator MCP** so it can run the app.
If there's no verification path, the right first step of any long task is to *build
one*. "Should work" is not done.
→ Reinforced in the CLAUDE.md template's **Long-running / autonomous work** section,
and in `/loop` (step 3 is mandatory self-verification); composes with `frontend-polish/`.

---

## What "incorporate into all my projects" actually means

| Tip | What reaches every project | How |
|---|---|---|
| 1. Auto permissions | `.claude/settings.json` allowlist | `starter-kit/install.py` |
| 2. Subagent orchestration | `.claude/agents/orchestrator.md` | `starter-kit/install.py` |
| 3. `/loop`, `/goal` | `.claude/commands/{loop,goal}.md` | `starter-kit/install.py` |
| 4. Cloud | nothing — launch from desktop/mobile/web | habit |
| 5. Self-verify | CLAUDE.md guidance + per-project verify path | `starter-kit/install.py` + `frontend-polish/` |

Install into a repo:
```
python starter-kit/install.py /path/to/repo        # skips files that already exist
python starter-kit/install.py /path/to/repo --force # overwrite
```

To apply to **every** project at once, run the installer per repo (a shell loop over
your repos), or copy the `.claude/` tree into your user-level `~/.claude/` so the
settings, commands, and agent are available globally rather than per-repo.

---

_Curated from a public Threads post; the technique is paraphrased, not copied, and
the source author is credited above. Inflated framing ("thousands of agents",
"hours/days unattended") is flagged rather than repeated._
