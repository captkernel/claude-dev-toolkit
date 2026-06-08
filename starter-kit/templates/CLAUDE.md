# CLAUDE.md — <PROJECT NAME>

> Project context and working rules for Claude Code. Claude reads this every
> session — keep it short, current, and true. Delete the angle-bracket prompts
> as you fill them in.

## What this is
<One to three sentences: what this project does and who it's for.>

## Tech stack (locked — do not silently swap)
- Language: <e.g. Python 3.12>
- Framework: <e.g. FastAPI / Next.js / none>
- Package manager: <e.g. uv / pnpm / pip>
- Tests: <e.g. pytest>
- Lint / format: <e.g. ruff>

## How to run, test, build
- Run: `<command>`
- Test: `<command>`
- Build: `<command>`

## Working rules (the four that matter)
1. **Ask, don't assume.** If intent, architecture, or requirements are unclear,
   ask before writing a line. No silent guesses.
2. **Simplest solution first.** Implement the simplest thing that works. No
   abstractions or flexibility I didn't ask for.
3. **Don't touch unrelated code.** Change only what the task needs — no drive-by
   refactors, renames, or reformatting outside scope.
4. **Flag uncertainty.** If you're not confident about an approach or a fact,
   say so before proceeding.

## Conventions
- Follow the existing patterns in the codebase over any default.
- <Code style, naming, file-layout notes specific to this project.>

## Long-running / autonomous work
When given a big task, work to a *verified* finish, not a plausible one:
- **Define done first.** Restate the goal and a checkable definition of done before
  coding — use `/goal`.
- **Keep going.** Don't pause between steps to ask permission for routine, in-scope
  work; loop until done or truly blocked — use `/loop`. (Safe read-only and test
  commands are pre-approved in `.claude/settings.json` so the loop isn't interrupted.)
- **Self-verify end to end.** Prove it works: run the tests/linters/build, or
  exercise the change for real (start the server and hit it, run the CLI, screenshot
  the UI). If there's no way to verify, build one before claiming success.
- **Delegate breadth.** For large multi-part work, split into independent subtasks and
  run them in parallel via subagents — see the `orchestrator` agent in `.claude/agents/`.

## Hard stops — ask before doing
Deletes/overwrites, schema changes, migrations, deploys, external API calls, or
anything irreversible. These hold even during `/loop` — autonomy is not a license
for irreversible actions.

## Memory & errors
- Read `MEMORY.md` (decisions) and `ERRORS.md` (known failures) at session start.
- Append to `MEMORY.md` when we make a non-obvious decision.
- Append to `ERRORS.md` when something fails twice and you find the fix.

## Voice
See `anti-style.md` for banned phrases and tone.
