# Claude Commands Reference (trimmed & de-hyped)

Source: Instagram carousel `DYNIf1XHEBV` (@mrsocialgrowthstudio_), "50 Hidden Commands."
That post mixes **real Claude Code features** with **community prompts dressed up as
"/commands."** This file separates the two, verifies the native ones against actual
Claude Code behavior, and gives you the real prompt text for the rest so you can paste
them or save them as genuine slash-commands.

Verification legend:
- ✅ **Native / real** — actually built into Claude or Claude Code.
- ⚠️ **Partly true / nuance** — real concept but the post's framing is off.
- ❌ **Not native** — it's just a prompt someone named with a slash. Works only if YOU
  define it (custom instructions or a `.claude/commands/` file). Typing it raw does nothing special.

---

## A. Genuinely native commands

These work out of the box. In Claude Code, slash commands are typed at the start of a
message; `ultrathink` is a keyword you put inline.

| Command | Status | What it actually does |
|---|---|---|
| `ultrathink` | ✅ Native | A thinking-effort trigger word. Including "think" / "think hard" / "think harder" / "ultrathink" in your message raises the extended-thinking (reasoning) budget, `ultrathink` being the largest tier. It's a keyword, not a slash-command. |
| `/compact` | ✅ Native | Summarizes the current conversation to reclaim context window so the session can continue without hitting the limit. You can optionally pass focus instructions, e.g. `/compact keep the API design decisions`. |
| `/model` | ✅ Native | Switches the active model (Opus / Sonnet / Haiku) mid-session. |
| `/resume` | ✅ Native | Reopens a previous Claude Code session and continues it. (`claude --resume` / `claude --continue` from the shell do the same.) |
| `/context` | ✅ Native | Shows current context-window usage (what's filling the window). Not in the post, but real and useful — included because the brief asked about it. |
| `/init` | ✅ Native | Scaffolds a `CLAUDE.md` for the repo by analyzing the codebase, so Claude has standing project context. |

**Other real native ones worth knowing (not in the post):**
`/clear` (reset conversation), `/help`, `/config`, `/cost`, `/login` & `/logout`,
`/review` (PR review), `/agents`, `/mcp`, `/memory` (edit memory/CLAUDE.md), `/vim`,
`/terminal-setup`, `/doctor`, `/bug`.

### Native — but the post is wrong about it

| Command | Status | Reality |
|---|---|---|
| `/btw` | ⚠️ Not native | The post says it asks a "side question without polluting your main thread." There is **no** native `/btw` command that forks context. It's a made-up convenience name. If you want a real throwaway question, just open a new session (`/clear` or a new terminal). Treat as ❌ community. |
| `L99` | ❌ Not native | Presented as "add to end of any message for max reasoning." This is **not** a real Claude flag or token — there's no `L99` reasoning switch. To actually raise reasoning, use the `think`/`ultrathink` keywords (above). Ignore `L99`. |

---

## B. Community "commands" — really just prompts

None of these are built in. Typing `/ghost` to a fresh Claude does nothing on its own.
They work in one of two ways:

1. **Paste-as-prompt:** drop the instruction text below into your message.
2. **Make it a real slash-command:** save the text as a file in `.claude/commands/`
   (see Section C). Then `/ghost` actually exists *for you*.

Below is the actual instruction text for each, reconstructed from the post's one-line
descriptions. Tune to taste.

### Voice & writing

**`/ghost`** — de-AI a draft. *Useful.*
> Rewrite the following so it reads like a sharp, slightly tired human wrote it — not an
> AI. Rules: no em-dashes, no "In today's world" preamble, no "it's not just X, it's Y"
> constructions, no rule-of-three padding. Vary sentence length. Keep every concrete
> claim, number, and example. Don't add hype. Output only the rewrite.

**`/milliondollarversion`** — premium rewrite. *Useful, overlaps with /tighten.*
> Rewrite this as the premium version: cut ~30% of the words, sharpen the opening hook,
> and replace every vague claim with a specific, verifiable proof point (number, example,
> or mechanism). Keep my voice. Flag anything I claim that you can't make specific.

**`/tighten`** — compress. *Useful.*
> Cut this draft by 30–40% without losing a single claim, number, or example. Remove
> filler, hedging, and redundancy only. Return just the tightened version.

### Thinking & analysis

**`/brutal`** — honest advisor. *Useful (pair with `ultrathink`).*
> Drop all flattery and hedging. Give me your honest assessment of the following as a
> blunt advisor who wants me to win. List what's weak, what won't work, and why. End
> with the single hardest truth I'm avoiding.

**`/redteam`** — adversarial review. *Useful.*
> Act as a red team attacking this plan/argument from the outside. Find the assumptions
> that, if wrong, break everything. Give the 5 strongest attacks an informed critic would
> make, ranked by how much damage each does, plus the cheapest test for each.

**`/premortem`** — failure-back planning. *Useful.*
> Assume it's 12 months from now and this plan failed badly. Write the post-mortem: the
> 3–5 most likely causes of failure, the early warning signs we'd have ignored, and what
> we should change now to prevent each.

**`/steelman`** — strongest counter-case. *Useful.*
> Build the strongest possible case *against* my current position — the version a smart,
> fair opponent would make. No strawmen. Then tell me which parts I genuinely need to answer.

**`/shadow`** — blind spots. *Lower value — overlaps with /redteam and /devil.*
> Surface the blind spots in this plan: the things I'm not seeing because I'm too close to
> it. Focus on what I haven't mentioned at all, not what I've already weighed.

### Content creation

**`/hook`** — opening hooks. *Useful for creators.*
> Give me 10 opening hooks for the topic below, 2 each across these patterns: contrarian
> take, surprising stat, painful truth, before/after, curiosity gap. One line each. No
> explanations.

**`/thread`** — X thread. *Useful.*
> Turn the idea below into a 7-tweet X thread. Tweet 1 is a scroll-stopping hook. Each
> tweet stands alone, ~280 chars max, no hashtags. End with a soft CTA.

**`/carousel`** — IG carousel. *Useful.*
> Turn the idea below into a 7-slide carousel: slide 1 hook, 2 reframe of the problem,
> 3–5 proof/steps, 6 payoff, 7 CTA. Give each slide a short on-screen headline plus a
> one-line caption note.

**`/repurpose`** — multiply formats. *Useful.*
> Take this one piece of content and repurpose it into 5 formats: a Reel script, an email,
> an X thread, an IG carousel outline, and a short LinkedIn post. Keep the core message;
> adapt tone and length per format.

### Framework commands

**`/OODA`** — *Useful for decisions.*
> Apply the OODA loop to my situation: Observe (what's actually happening), Orient (what
> it means given context/biases), Decide (the call), Act (first concrete move). Be concrete.

**`/firstprinciples`** — *Useful.*
> Break this problem down to first principles. List the inherited assumptions I'm carrying,
> strip the ones that aren't fundamentally true, and rebuild a solution from only what's
> actually true.

**`/devil`** — devil's advocate. *Medium — overlaps with /redteam, /shadow.*
> Play devil's advocate on this: name 3 specific logic flaws, 1 cognitive bias I'm likely
> falling into, and 1 unintended consequence I haven't considered.

> Note: `/OODA`, `/firstprinciples`, `/devil`, `/shadow`, `/redteam`, `/steelman`, and
> `/premortem` are all "think harder from a named angle." You don't need all of them. Keep
> 2–3 (e.g. `/brutal`, `/premortem`, `/redteam`) and drop the rest as noise.

---

## C. How to make a real Claude Code slash-command

A community "command" becomes a real one when you save its prompt as a Markdown file.

1. Create the commands folder in your repo (project-scoped) or home dir (global):
   - Project: `.claude/commands/`
   - Personal/global: `~/.claude/commands/`
2. Add one file per command — the filename is the command name:
   `.claude/commands/ghost.md`
3. Put the instruction text in the file. Use `$ARGUMENTS` (or `$1`, `$2`…) for input:

   ```markdown
   ---
   description: De-AI a draft — human voice, no em-dashes, no preamble
   ---
   Rewrite the following so it reads like a sharp, tired human wrote it. No em-dashes,
   no preamble, varied sentence length, keep every claim and number.

   $ARGUMENTS
   ```

4. In Claude Code, type `/ghost <your draft>`. The file's body becomes the prompt,
   with your text dropped into `$ARGUMENTS`.

Notes:
- Subfolders namespace commands, e.g. `.claude/commands/writing/ghost.md` → `/writing:ghost`.
- This is also how to "promote the keepers" mentioned in the project README.
- The post's "paste one Master Block into Claude settings" is just putting these prompts
  into Custom Instructions / `CLAUDE.md` — same idea, less reliable than real command files.

---

## Bottom line

- **Real & worth knowing:** `ultrathink`, `/compact`, `/model`, `/resume`, `/context`,
  `/init` (plus `/clear`, `/review`, `/config`, `/cost`, `/memory`, `/agents`, `/mcp`).
- **Fake-native — ignore the post's claim:** `/btw` (no context-forking command),
  `L99` (not a real reasoning switch).
- **Useful prompts to save as real commands:** `/ghost`, `/tighten`, `/brutal`,
  `/premortem`, `/redteam`, `/hook`, `/thread`, `/carousel`, `/repurpose`.
- **Low-value / redundant:** `/shadow`, `/devil`, `/steelman`, `/OODA`,
  `/firstprinciples`, `/milliondollarversion` — keep at most one or two.
- The "50 commands" framing is marketing. The real list of things you'll use is ~15.
