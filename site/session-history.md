# DevNook — Historical Session Summaries

> Sessions 4–10 moved here from [CLAUDE.md](CLAUDE.md) to keep the main file lean.  
> For the current session state, always check CLAUDE.md first.

---

## Session 20 Summary

**Session Date:** 2026-04-18 (session 20)
**Session Goal:** Stage and schedule 7 QA-passed antigravity articles for Apr 19–20 drip publish.
**Status:** ✅ Complete — 7 articles staged, schedule committed and pushed.

### What was done

1. **Verified QA** — all 7 antigravity drafts already had `qa_status='passed'` in registry; spot-checked content looks clean.

2. **Staged 7 articles** — moved from `agents/content-team/drafts/` to `content-staging/languages/{lang}/` via Python; registry updated to `status='staged'`.
   - how-to-implement-singleton-design-pattern-in-javascript (javascript)
   - how-to-parse-json-in-javascript (javascript)
   - how-to-send-http-request-in-cpp (cpp)
   - how-to-set-environment-variables-in-java (java)
   - how-to-set-environment-variables-in-php (php)
   - how-to-use-data-class-in-kotlin (kotlin)
   - how-to-write-closure-in-swift (swift)

3. **Updated `.github/workflows/drip-publish.yml`**:
   - Added `workflow_dispatch` count input (default: 3) for flexible manual triggering
   - Added extra cron `0 10 20 4 *` (Apr 20 at 10:00 UTC, count=1) so 4 articles publish on Apr 20
   - Publish count logic: workflow_dispatch uses input; `0 10 20 4 *` uses count=1; all other crons use count=3

4. **Drip schedule for the 7 new articles** (FIFO order, Apr 17 mtimes are oldest in queue):
   - Apr 19 08:00 UTC (daily): singleton-js, parse-json-js, http-request-cpp
   - Apr 20 08:00 UTC (daily): set-env-java, set-env-php, data-class-kotlin
   - Apr 20 10:00 UTC (extra): write-closure-swift
   - Apr 21 08:00 UTC (daily): lambda-java, dict-python, patterns-python (prior batch)

---

## Session 10 Summary

**Session Date:** 2026-04-15 (session 10)
**Session Goal:** Complete Phase 2 of the light-theme reskin.
**Status:** ✅ PHASE 2 COMPLETE — RESKIN FULLY SHIPPED. Both commits on `origin/main`. Cloudflare auto-deploys.
**Commits:** `a2e61d0` — feat(ui): rebuild page layouts to match template

---

## Session 9 Summary

**Session Date:** 2026-04-14 (session 9)
**Session Goal:** Execute the user's 3-stage fix plan for devnook.dev. Stages 1 + 2 (empty language tabs, broken post URLs) were finished in the compacted early portion of the session. Stage 3 is a full light-theme frontend reskin to match the user's attached HTML template (`devtoolkit-template.html`), excluding the search bar.

### Status at end of session: 🚧 PHASE 1 OF RESKIN SHIPPED — PHASE 2 HALF-DONE

### What was completed

**Stages 1 + 2** (already in git as `cdb4aea` + `82a0384`):
- `cdb4aea` fix(ui): render language names on homepage and /languages index
- `82a0384` fix(ui): build language post hrefs from data.concept, not filename stem

**Stage 3 Phase 1 — Foundation reskin, committed as `d57f46c`:**
- Rewrote `public/styles/tokens.css` for light theme. Palette: `--color-bg: #fafaf8`, `--color-surface: #fff`, `--color-accent: #2563eb`.
- Dropped broken `@font-face` blocks — moved to Google Fonts `<link>` tags in BaseLayout.astro (Outfit + JetBrains Mono).
- Rewrote NavBar.astro, Footer.astro, PostCard.astro, ToolCard.astro, LanguageCard.astro, TagBadge.astro.
- New file: `src/lib/language-colors.ts` — GitHub Linguist `LANGUAGE_COLORS` + `LANGUAGE_NAMES` map.
- Tool widget color sweep (9 files): replaced hardcoded dark-theme rgba with CSS custom properties.
- Fixed latent bug in `src/pages/tools/index.astro`: was passing whole object to ToolCard instead of destructured props. Phase 1 build passed: 43 pages in 24.37s.

**Stage 3 Phase 2 — 4 of 10 files rewritten (on disk only at end of session 9):**
- `src/pages/index.astro`, `src/pages/languages/[lang]/index.astro`, `src/pages/languages/index.astro`, `src/pages/blog/index.astro`

### Commits pushed
- `d57f46c` — feat(ui): light theme reskin — tokens, chrome, cards, tool widget colors

---

## Session 8 Summary

**Session Date:** 2026-04-13 (session 8)
**Session Goal:** Nuclear reset — delete the broken Cloudflare Pages project, recreate fresh from GitHub, and get a styled site up.

### Status: ✅ SITE LIVE WITH DARK THEME

### What was completed

**Nuclear Cloudflare Pages reset:**
- Deleted old `devnook` Pages project (Workers & Pages → devnook → Settings → Delete project).
- Created fresh Pages project via Workers & Pages → Create application → **Pages tab** → Connect to Git.
  - Repo: `syedjawad11/DevNook-`, branch `main`, project name: `devnook`
  - Framework preset: Astro, Env: `NODE_VERSION=20`
  - Gotcha: first attempt accidentally entered the "Create a Worker" wizard — must click the **Pages** tab.

**Root cause #1: CSS never shipped in the build.**
- `BaseLayout.astro` referenced `/styles/tokens.css` + `/styles/global.css` with absolute paths.
- Files lived in `src/styles/` — Astro doesn't copy `src/styles/` to `dist/`. Fix: `mv src/styles public/styles`.

**Root cause #2: PostCard prop mismatch.**
- PostCard used `slug` prop as `<a href>`. All 5 call sites passed `url` / `publishedDate` instead.
- Fix: renamed `slug` → `href`, normalized all call sites. Also fixed "Invalid Date NaN" issue.

### Commits pushed
- `b61fd73` — fix(ui): serve global CSS from public/ and fix PostCard prop mismatch

---

## Session 7 Summary

**Session Date:** 2026-04-13 (session 7)
**Session Goal:** Diagnose and fix persistent HTTP 500 on `devnook.dev` after session 6's static-output switch.

### What was completed
- Diagnosed 500 reproduced on per-deploy unique URLs, pointing at Pages-project-internal state.
- Hypothesized `@astrojs/cloudflare` still in `package.json` kept Pages pinned to Functions mode.
- Ran `npm uninstall @astrojs/cloudflare @astrojs/sitemap`, committed as `e5dff68` and pushed.

### Outcome
Fix was correct but insufficient — session 8 discovered poisoned Pages-project state required a nuclear reset, plus two unrelated latent bugs (missing CSS in `public/`, PostCard prop mismatch) that only surfaced after the 500 cleared.

---

## Session 6 Summary

**Session Date:** 2026-04-13 (session 6)
**Session Goal:** Ship devnook.dev live on Cloudflare with ≤20 seed posts + 10 tools.

### Status at end: ⚠️ SITE STILL RETURNING ERRORS — PAUSED

User disabled Antigravity (was interfering) and took a break before continuing debug.

### What was completed

- User confirmed 10 tools: `json-formatter`, `base64-encoder`, `url-encoder`, `jwt-decoder`, `uuid-generator`, `hash-generator`, `regex-tester`, `sql-formatter`, `markdown-to-html`, `csv-to-json`.
- Generated 10 tool content `.md` files safely (avoiding `build_tool()` which would overwrite components).
- Deleted orphan `regex-tester-online-java.md`.
- Rewrote `astro.config.mjs` to `output: 'static'` — fixed HTTP 500 caused by `output: 'hybrid'` + OG image endpoints importing `satori`/`@resvg/resvg-js` which can't load in Cloudflare Workers.

### Commits pushed
- `e39ac16` — fix(deploy): switch to static output + add 10 tool content pages

---

## Session 5 Summary

**Session Date:** 2026-04-13 (session 5)
**Session Goal:** Unblock Cloudflare Pages deploy (schema error + 404 on devnook.pages.dev).

### Root cause discovered
Stage 7 was never actually executed — `src/pages/` only contained API/OG/sitemap endpoints, zero HTML page routes.

### What was completed

**Part 1 — build-tool.py frontmatter bug:**
- `generate_seo_explainer` told Claude to emit camelCase frontmatter (`publishedDate`, `relatedTools`) that didn't match Zod schema. Fixed: Python builds frontmatter deterministically, LLM writes only the body. Committed `ae88cbd`.

**Part 2 — 404: missing HTML pages:**
- Ran `scaffold.py` to generate 13 missing pages. Added `write_file` skip-if-exists guard + `load_dotenv`.
- Fixed 6 Claude-generated bugs: wrong relative path, wrong PostLayout props, Breadcrumb prop mismatch, `getStaticPaths` scope issue, dynamic import in tool route (`import.meta.glob` fix).
- Committed `04d042f`.

---

## Session 4 Summary

**Session Date:** 2026-04-13 (session 4)
**Session Goal:** Fix Cloudflare Pages deployment build errors and deploy the site live.

### What was completed
- Gemini Flash generated 20 seed posts, pushed `799ea22`, connected Cloudflare Pages.
- Claude Opus fixed 3 OG image generator bugs (Google Fonts CSS parsing, Satori `inline-block` not supported, fragile regex with silent fallback). Committed `dfb8406`.
- Pushed `91e544d` to force fresh Cloudflare build.
- **Discovered in session 5:** This session never generated HTML page routes — Cloudflare built cleanly but served 404 on everything.
