---
description: Keep working autonomously until the goal is verified done or you're truly blocked
argument-hint: [task description]
---
Work on the following until it is fully done — verified, not just plausible:

$ARGUMENTS

Loop until done:
1. Restate the goal as a concrete, checkable definition of done.
2. Do the next smallest useful step.
3. Self-verify: run the tests / linters / build, or exercise the change end to end
   (start the server and hit it, run the CLI, screenshot the UI). If there is no
   way to verify, set one up first — don't skip this.
4. If verification fails, fix it and go back to step 2. Don't stop at "should work."
5. Stop only when (a) every definition-of-done item is verified green, or (b) you
   hit a real blocker that needs my input — then say exactly what you tried and
   what you need.

Don't pause to ask permission for routine, in-scope work between steps; keep going.
Still honor the hard-stops in CLAUDE.md (deletes, migrations, deploys, irreversible actions).
