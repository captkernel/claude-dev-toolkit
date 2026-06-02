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

## Hard stops — ask before doing
Deletes/overwrites, schema changes, migrations, deploys, external API calls, or
anything irreversible.

## Memory & errors
- Read `MEMORY.md` (decisions) and `ERRORS.md` (known failures) at session start.
- Append to `MEMORY.md` when we make a non-obvious decision.
- Append to `ERRORS.md` when something fails twice and you find the fix.

## Voice
See `anti-style.md` for banned phrases and tone.
