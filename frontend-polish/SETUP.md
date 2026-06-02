# Setting up frontend quality in Claude Code

Goal: get Claude to produce frontend that does **not** look like generic "AI slop" — and to
catch its own mistakes *before* it shows you. This is achieved by **composing** what already
exists, not by reinventing design rules.

There are three layers. Only the third one is new work; the first two already exist or are
optional add-ons.

---

## Layer 1 — Aesthetics: use the official `frontend-design` skill (already here)

An official **`frontend-design`** skill is already installed in this environment
(`~/.claude/plugins/.../plugins/frontend-design/skills/frontend-design/SKILL.md`). It is
Anthropic's own skill and Claude invokes it automatically whenever you ask it to build a
component, page, or app.

It already covers everything the Instagram post promised as the "look":

- **Typography** — pick distinctive display + body fonts; explicitly avoid Inter / Roboto / Arial / system fonts.
- **Color & theme** — commit to a cohesive palette; CSS variables; dominant color + sharp accents; *no* purple-gradient-on-white cliché.
- **Motion** — high-impact animation; CSS-only for plain HTML, the Motion library for React; one orchestrated page-load reveal over scattered micro-interactions.
- **Spatial composition** — asymmetry, overlap, grid-breaking, intentional negative space.
- **Backgrounds & texture** — gradient meshes, noise, grain, layered transparency, dramatic shadows.
- An explicit **anti-AI-slop** rule set.

**Do not rewrite these guidelines.** That skill is the source of truth for aesthetics. If you
want it to lean harder, just say so in your prompt (e.g. "commit to a bold editorial/magazine
direction, dark theme"). The skill is built to take that direction.

> Sanity check it's available: ask Claude "Which skill do you use for frontend design?" or look
> for `frontend-design` under your installed plugins/skills.

---

## Layer 2 — Optional external pieces (vet before trusting)

The source post (`exports/items/DX-2amujKLF.md`, @tenfoldmarc) claims **one** copy-paste command
installs "21st.dev + Framer Motion + a UI/UX skill" and fixes any site in 30 seconds. Treat that
framing with suspicion — the final carousel slide is literally *"comment below and I'll send it
to you, follow @tenfoldmarc."* It is a **comment-funnel / lead-magnet**, and "install this skill
from my GitHub" runs third-party instructions inside your agent. The underlying *tools* it name-drops
are real and sometimes useful; the *bundle* is the part to ignore.

Evaluate each piece on its own merits:

| Piece | What it actually is | Honest caveat |
|---|---|---|
| **21st.dev** | A registry/marketplace of React + Tailwind UI components ("npm for design"); some pieces have an MCP/"magic" install flow. | Useful as a **component source you cherry-pick**, not an auto-installer. Components still need your design direction or they re-introduce sameness. Read the code you pull in; pin versions. |
| **Framer Motion / Motion** | The mainstream React animation library (`motion` / `framer-motion` on npm). Genuinely good. | The official `frontend-design` skill **already** tells Claude to use Motion for React. You usually just need `npm i motion` — no special "skill" required. |
| **"UI/UX Pro Max" skill** | A third-party prompt skill bundled by the post's author. | Overlaps heavily with the official `frontend-design` skill you already have. Low marginal value; **highest** trust risk (it is the unvetted, author-hosted piece). Skip unless you read it line-by-line first. |
| **The single "install this skill" command** | A GitHub repo (`tenfoldmarc/website-builder-setup`) that wires the above together. | This is the lead-magnet. Don't run it blind. If curious, clone and read it; do not let an agent execute it unreviewed. |

**Rule of thumb:** add an external component library only when you have a concrete need
(e.g. you want a specific animated component fast), install it explicitly with `npm`, pin the
version, and read what it adds. Never adopt a "one command fixes everything" bundle on trust.

### If you do want components fast (the safe version)
```bash
npm i motion          # animation (the part the post is right about)
# then pull individual components you've read from 21st.dev / shadcn/ui as needed,
# and let the official frontend-design skill drive the overall aesthetic.
```

---

## Layer 3 — The one technique that actually matters: screenshot -> self-review -> refine

This is the reusable, high-value piece and the reason this folder exists. Aesthetic *guidelines*
(Layer 1) tell Claude what good looks like; they don't tell Claude whether **this specific render**
achieved it. A text model writing CSS is working blind. The fix: make Claude **look at its own
output** and critique it before showing you.

The loop:

1. **Render** — run the UI locally (dev server, or open the HTML).
2. **Screenshot** — capture it with Playwright (desktop width; ideally a mobile width too).
3. **Self-review** — Claude inspects the screenshot and critiques it against design heuristics
   (the same ones in `frontend-design`: typography, hierarchy, spacing/alignment, color/contrast,
   motion, "does this read as generic AI slop?", plus accessibility and responsive checks).
4. **Refine** — fix the top issues in code.
5. **Repeat** until no high-severity issues remain (cap at ~3 passes), **then** show the user.

This catches the things text generation reliably misses: overflow, clipped text, broken alignment,
unreadable contrast, cramped spacing, a layout that *technically* matches the spec but looks
amateur. It is model-, framework-, and library-agnostic.

The ready-to-use skill for this loop is **`screenshot-review.md`** in this folder
(skill name: `frontend-screenshot-review`). It is the actual deliverable — invoke it (or paste it)
after generating any non-trivial UI.

### One-time setup for the loop
```bash
npm i -D playwright
npx playwright install chromium
```
Minimal capture script (Node):
```js
// screenshot.mjs — usage: node screenshot.mjs http://localhost:3000 out.png
import { chromium } from 'playwright';
const [url, out = 'screenshot.png'] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.goto(url, { waitUntil: 'networkidle' });
await p.screenshot({ path: out, fullPage: true });
await b.close();
```
(Claude can also drive Playwright directly via an MCP/browser tool if you have one configured —
the script above is the dependency-light fallback.)

---

## TL;DR

- **Aesthetics:** lean entirely on the official `frontend-design` skill. Don't reinvent it.
- **External tools (21st.dev, Motion, "UI/UX" skills):** Motion is worth it and the official skill
  already uses it; 21st.dev is a fine *cherry-pick* source; the "one command" bundle is a
  comment-funnel — vet every third-party piece, run nothing unreviewed.
- **The real win:** the screenshot -> self-review -> refine loop in `screenshot-review.md`. Run it
  before showing the user. That is where measurable quality comes from.
