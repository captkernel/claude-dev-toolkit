# Claude Code Starter Kit (CLAUDE.md + memory files)

> **Value:** High &nbsp;|&nbsp; **Implementability:** Easy

## What this is
A reusable project-context kit — CLAUDE.md, MEMORY.md, ERRORS.md, anti-style.md — you drop into any repo so Claude stops guessing and re-explaining.

## Why it's worth building
Foundational and genuinely effective: a good CLAUDE.md is the single highest-leverage thing for Claude Code quality, and the advice here (ask-don't-assume, simplest-first, don't-touch-unrelated-code, flag-uncertainty, decision/error logs, stack lock) is sound. You already run a memory system, so this formalises it.

## What to build (the gist)
- Four rules to bake in: ask don't assume, simplest solution first, don't touch unrelated code, flag uncertainty.
- Add MEMORY.md (decision log) + ERRORS.md (what failed & the fix) read at session start.
- anti-style.md banning filler phrases; lock language/framework/package-manager.
- Ignore the viral '65%->94% accuracy / $975-a-week' stats — invented; the practice stands on its own.

## What's in here (built)
```
claude-code-starter-kit/
  templates/
    CLAUDE.md       # project context + the 4 working rules + stack lock + hard stops
    MEMORY.md       # decision log (read at session start)
    ERRORS.md       # failure log (checked before similar tasks)
    anti-style.md   # banned phrases / tone
  install.py        # drops the templates into any repo (skips existing files)
  test_install.py   # tests for the installer
```

## Usage
From a target repo (or anywhere), run:
```
python /path/to/projects/claude-code-starter-kit/install.py .            # into current dir
python .../install.py /path/to/other-repo                                # into another repo
python .../install.py . --force                                          # overwrite existing
```
It copies the four files in, **skipping any that already exist** (so it won't
clobber a CLAUDE.md you've already written) unless you pass `--force`. Then open
`CLAUDE.md` and fill in the `<angle-bracket>` placeholders.

## Why these files
- **CLAUDE.md** — the four rules (ask don't assume · simplest first · don't touch
  unrelated code · flag uncertainty), a locked tech stack, run/test/build commands,
  and hard-stops. This is the highest-leverage file for Claude Code quality.
- **MEMORY.md / ERRORS.md** — lightweight decision + failure logs Claude reads each
  session, so choices and dead-ends persist across `/clear`.
- **anti-style.md** — kills the generic-AI tone.

(The viral "65%→94% accuracy / $975-a-week" numbers from the source posts are
invented — ignored here. The practice stands on its own.)

## Next steps / ideas
- Add a `--stack <preset>` flag that pre-fills CLAUDE.md for common stacks.
- Optionally generate from an interview (ask a few questions, fill placeholders).

## Source posts
DYm0Y9EktzS (@aitickerdaily), DX9TVLojYTa (@evolving.ai), DYMtxScjF2m (@therajeshchityal), DXs9fU9Fmw1 (@tenfoldmarc), DYkI_VZiYAg (@artificialintelligence.co), DXUfs86kjjy (@artificialintelligenceupdater), DYRNJWYk1Ar (@zeeeljain)

_Built by instacomp from forwarded Instagram posts (May 2026), hype filtered out._
