---
name: frontend-screenshot-review
description: Self-review loop for UI work. After building or changing any non-trivial frontend (component, page, or app), render it, screenshot it with Playwright, critique the screenshot against design heuristics, and refine in code BEFORE showing the user. Use whenever you have just generated or edited visual UI, when asked to "polish"/"make it look better"/"review the design", or before presenting any frontend you have not yet seen rendered.
---

# Frontend screenshot self-review loop

You wrote UI code, but you have not *seen* it. Text generation reliably misses overflow, clipped
text, broken alignment, weak contrast, cramped spacing, and layouts that match the spec yet still
look generic. Close that gap: look at your own output and fix it before the user ever sees it.

This skill **composes** the official `frontend-design` skill — that skill defines what good looks
like (typography, color, motion, composition, anti-AI-slop). This skill verifies that *this render*
actually achieved it. Do not restate aesthetic rules here; apply `frontend-design`'s.

## When to use
- Immediately after generating or substantially editing any visual UI.
- When the user says "polish it", "make it look less AI", "review the design", "why does this look off".
- Before presenting any frontend you have not yet rendered and viewed.

## Prerequisites (set up once)
```bash
npm i -D playwright
npx playwright install chromium
```
If a browser/Playwright MCP tool is configured, you may use it to navigate + screenshot instead of
the script below.

## The loop

Run up to **3 passes**. Stop early when no high-severity issues remain.

### 1. Render
Start the app or open the file:
- Dev server: `npm run dev` (or the project's start command) and note the URL.
- Static HTML: use a local server or open the file directly.
Wait for it to be reachable before capturing.

### 2. Screenshot (Playwright)
Capture full-page at **desktop (1440px)** and **mobile (390px)** widths.
```js
// screenshot.mjs — node screenshot.mjs <url> <out.png> [width]
import { chromium } from 'playwright';
const [url, out = 'screenshot.png', width = '1440'] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: +width, height: 900 } });
await p.goto(url, { waitUntil: 'networkidle' });
await p.screenshot({ path: out, fullPage: true });
await b.close();
```
```bash
node screenshot.mjs http://localhost:3000 desktop.png 1440
node screenshot.mjs http://localhost:3000 mobile.png 390
```
Then **read the image files** (view them) — actually look. Do not skip this step or critique from
memory of the code.

### 3. Self-review against heuristics
Inspect each screenshot and write a short, honest critique. Score each area Pass / Minor / Major:

- **Layout & alignment** — overflow, clipping, overlap, misaligned edges, inconsistent gutters, broken grid.
- **Spacing & rhythm** — cramped or arbitrary padding/margins; consistent vertical rhythm.
- **Typographic hierarchy** — clear H1 > H2 > body scale; line length 45-75ch; line-height comfortable; the font is distinctive (per `frontend-design`), not Inter/Arial default.
- **Color & contrast** — WCAG AA text contrast; cohesive palette; *not* the purple-gradient-on-white AI cliché.
- **"AI-slop" smell test** — does it look like a generic template (centered hero, three feature cards, vague gradient, stock layout)? If yes, that is a Major.
- **Motion** — does the page-load / interaction read as intentional, or absent/janky? (Note: animation may not show in a still — reason about it and, if needed, capture mid-animation or describe expected behavior.)
- **Responsive** — at 390px: no horizontal scroll, nothing clipped, tap targets >= 44px, text reflows.
- **Accessibility (visual)** — focus states visible; images have alt; sufficient contrast; not conveying meaning by color alone.
- **Spec fidelity** — does it actually do what the user asked for?

For each **Major** and **Minor**, state the exact element and the fix.

### 4. Refine
Apply the fixes in code, highest severity first. Keep changes targeted.

### 5. Re-capture and repeat
Re-run steps 2-3. Stop when there are **no Major issues** (Minor remaining is acceptable), or after
3 passes — whichever comes first.

## Output to the user
Only after the loop, present the result. Include a one-line note such as:
> Self-reviewed across N passes (desktop + mobile). Fixed: <top items>. Remaining minor: <if any>.

Attach or reference the final screenshots if useful. Do **not** show the user intermediate broken
states unless they asked to see the process.

## Guardrails
- If you cannot render (no runnable target, missing deps you may not install), say so explicitly
  and review the code statically instead — do not claim a visual review you did not perform.
- Never fabricate that something "looks good" without having viewed a screenshot.
- Cap at 3 passes to avoid thrashing; diminishing returns after that — hand remaining minors to the user.
