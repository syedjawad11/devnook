# DevNook — Claude Session Log

> This file is updated at the end of every session. It is the primary reference for resuming work.  
> Always read this file first at the start of a new session.

---

## Project Overview

**DevNook** (devnook.dev) is a developer resource site targeting 1,000+ programmatic content pieces + 18 free browser-based client-side tools, monetized via Google AdSense.

**Domain:** devnook.dev (registered Cloudflare, April 2026)  
**Tech stack:** Astro + Cloudflare Pages + Python agents + Gemini API + Anthropic API  
**Content model:** "Concentric Rings" — tools → web fundamentals → language concepts  
**Agent model:** Plain Python scripts (no framework), local execution, GitHub Actions publishing

---

## Stage Progress

| Stage | File | Status | Session Completed |
|-------|------|--------|-------------------|
| 1 | [STAGE-1-skills.md](STAGE-1-skills.md) | ✅ Complete | 2026-04-10 |
| 2 | [STAGE-2-dev-team.md](STAGE-2-dev-team.md) | ✅ Complete | 2026-04-10 |
| 3 | [STAGE-3-tools-team.md](STAGE-3-tools-team.md) | ✅ Complete | 2026-04-11 |
| 4 | [STAGE-4-content-pipeline-core.md](STAGE-4-content-pipeline-core.md) | ✅ Complete | 2026-04-12 |
| 5 | [STAGE-5-content-pipeline-write.md](STAGE-5-content-pipeline-write.md) | ✅ Complete | 2026-04-12 |
| 6 | [STAGE-6-publishing.md](STAGE-6-publishing.md) | ✅ Complete | 2026-04-13 |
| 7 | [STAGE-7-launch.md](STAGE-7-launch.md) | ✅ Live — light-theme reskin complete (session 10) | 2026-04-15 |

---

## Last Session Summary

**Session Date:** 2026-04-15 (session 10)
**Session Goal:** Complete Phase 2 of the light-theme reskin. Phase 1 was committed as `d57f46c` in session 9. Phase 2 had 4 of 10 files on disk but unbuilt/uncommitted. This session finished the remaining 6 files, ran a clean build, smoke-tested all routes, and pushed.

### Status at end of session: ✅ PHASE 2 COMPLETE — RESKIN FULLY SHIPPED

Both Phase 1 and Phase 2 commits are on `origin/main`. Cloudflare auto-deploys from push. Light-theme reskin is complete.

### What was completed this session

**Already on disk from session 9 (4 files, finished in prior session):**
- [src/pages/index.astro](src/pages/index.astro) — hero + HERO_TAGS chips + featured tools grid + 12-language grid + cheatsheets strip + recent posts grid
- [src/pages/languages/[lang]/index.astro](src/pages/languages/[lang]/index.astro) — breadcrumb, langColor dot, stats row, numbered concept grid, related tools
- [src/pages/languages/index.astro](src/pages/languages/index.astro) — 12-card grid from LANGUAGE_NAMES, auto-fill layout
- [src/pages/blog/index.astro](src/pages/blog/index.astro) — static filter chips (decorative), featured card, 3-col PostCard grid

**Completed this session (6 files):**
- [src/pages/tools/[slug].astro](src/pages/tools/[slug].astro) — 2-column workspace: left `.tool-main` (ToolComponent + markdown prose), right `.tool-sidebar` (info box always + related tools if any + cheatsheet link if any related_content starts with `/cheatsheets/`). `import.meta.glob` eager pattern preserved. Collapses to 1-col at 900px.
- [src/pages/guides/index.astro](src/pages/guides/index.astro) — left-aligned header, auto-fill `minmax(340px,1fr)` grid, PostCard with `href`+`date`.
- [src/pages/cheatsheets/index.astro](src/pages/cheatsheets/index.astro) — same pattern as guides. PostCard props verified correct (`href={/cheatsheets/${sheet.slug}}`, no `url=` regression).
- [src/pages/404.astro](src/pages/404.astro) — `.home-link:hover` box-shadow fixed from dark-green rgba to accent-blue rgba. Structure was already light-theme compliant.
- [src/layouts/PostLayout.astro](src/layouts/PostLayout.astro) — h1 normalized to `2.75rem`, `.prose max-width: 760px`, removed `--color-accent-2` hover ref.
- [src/layouts/ToolLayout.astro](src/layouts/ToolLayout.astro) — stripped to minimal wrapper (~35 lines). Dropped Breadcrumb import + breadcrumbs prop + all inner layout styles. Tool page handles its own layout now.

**Inline-style audit (Step 7):**
- [src/components/SearchBar.astro](src/components/SearchBar.astro) — fixed `.search-result-item` active/hover background from `rgba(110,231,183,0.05)` to `var(--color-surface)`. SearchBar remains parked on disk (unmounted from NavBar).
- `cron-parser.astro`, `regex-tester.astro`: `style="display:none"` are JS visibility toggles — correct, left unchanged.
- Tool components using `--color-accent-2`: covered by back-compat alias in tokens.css — left unchanged.

**Build + deploy:**
- `npm run build` — 49 pages, zero warnings, zero errors.
- `npm run dev` smoke test — all routes 200, /nonexistent 404.
- Committed as `a2e61d0` with 11 files staged by explicit path (no `git add .`).
- Pushed to `origin/main`. Cloudflare auto-deploys.

### Commits pushed this session
- `a2e61d0` — feat(ui): rebuild page layouts to match template — hero, concept grid, featured card, tool workspace

### Full reskin commit history
- `d57f46c` — Phase 1: tokens, chrome, cards, tool widget colors (session 9)
- `a2e61d0` — Phase 2: all page/layout rewrites (session 10)

### Next session priorities

The reskin is done. The site is live at `devnook.dev` with the full light theme. Remaining work is content pipeline and monetization:

1. **Content pipeline** — run `python agents/content-team/run-pipeline.py --steps all` to generate and stage posts. Target: fill the 4 content rings (tools guides ~80, web fundamentals ~200, language concepts ~600+, AI/editorial ~200).
2. **GitHub Actions drip-publish** — wire up `agents/publish/publish.py` into a daily GitHub Actions workflow (2–3 posts/day from `content-staging/` → `src/content/` → push → Cloudflare deploy).
3. **Google AdSense** — apply once site has meaningful content. Also set up privacy/terms/about pages.
4. **Google Search Console** — submit sitemap once content is live.
5. **Search bar** — SearchBar.astro is parked and functional (Fuse.js, `/api/search-index.json`). Wire it back into NavBar when ready.
6. **Formal Stage 7 review** — check [STAGE-7-launch.md](STAGE-7-launch.md) for anything still outstanding.

### Deferred (unchanged)
- AdSense, GSC, gsc_ping.py
- GitHub Actions drip-publish automation
- Blog filter chips functional wiring (decorative only)
- Search bar wiring (SearchBar.astro parked on disk)
- Orphan `sitemap-generator-from-url.md` cleanup
- Remaining tool content `.md` files beyond the 10 seeded

---

## Previous Session Summary (session 9)

**Session Date:** 2026-04-14 (session 9)
**Session Goal:** Execute the user's 3-stage fix plan for devnook.dev. Stages 1 + 2 (empty language tabs, broken post URLs) were finished in the compacted early portion of the session. Stage 3 is a full light-theme frontend reskin to match the user's attached HTML template (`devtoolkit-template.html`), excluding the search bar.

### Status at end of session: 🚧 PHASE 1 OF RESKIN SHIPPED — PHASE 2 HALF-DONE, NOT BUILT, NOT COMMITTED, NOT PUSHED

**Do NOT push or run a build at the start of session 10 without reading the "What's on disk but uncommitted" block below.** Four Phase-2 page files are rewritten on disk but never went through `npm run build`. Session 10 must either finish the remaining Phase-2 files first *or* verify/roll-forward the partial state deliberately. Pushing a half-rewrote tree would likely break the live site.

### The plan being executed

Approved plan lives at `C:\Users\Syed Jawad Hassan\.claude\plans\eager-toasting-moon.md` (this path is on the user's machine — treat it as reference, not source of truth). Structure: **2 commits**.

- **Commit 1 (Phase 1 — Foundation):** tokens.css rewrite, global.css sweep, BaseLayout font links, NavBar/Footer rewrite, PostCard/ToolCard/LanguageCard/TagBadge rewrite, new `src/lib/language-colors.ts`, tool widget color sweep (9 files). **SHIPPED as `d57f46c` this session.**
- **Commit 2 (Phase 2 — Page structure rewrites):** index.astro, languages/[lang]/index.astro, languages/index.astro, blog/index.astro, tools/[slug].astro, guides/index.astro, cheatsheets/index.astro, 404.astro, PostLayout.astro, ToolLayout.astro + inline-style audit. **NOT YET COMMITTED. Only 4 of 10 files rewritten.**

### What was completed this session

**Stages 1 + 2** (before compaction, already in git as `cdb4aea` + `82a0384`):
- `cdb4aea` fix(ui): render language names on homepage and /languages index
- `82a0384` fix(ui): build language post hrefs from data.concept, not filename stem

**Stage 3 Phase 1 — Foundation reskin, committed as `d57f46c`:**
- Rewrote [public/styles/tokens.css](public/styles/tokens.css) for light theme. Palette: `--color-bg: #fafaf8`, `--color-surface: #fff`, `--color-accent: #2563eb`, plus extended `--color-purple/green/amber/coral` with matching `-light` variants. Added back-compat aliases (`--color-accent-2`, `--color-error`, `--color-success`) so existing component-scoped styles don't break.
- Dropped the broken `@font-face` blocks from tokens.css — Google Fonts CSS2 URLs return CSS text, not font binaries, so `@font-face src: url(...css2...)` never worked. Moved to Google Fonts `<link>` tags in [src/layouts/BaseLayout.astro](src/layouts/BaseLayout.astro) (Outfit + JetBrains Mono). Added `<meta name="theme-color" content="#fafaf8">`.
- Updated [public/styles/global.css](public/styles/global.css) for light theme: scrollbar, selection, prose `code` on `--color-elevated`, prose `pre` on `#0c0c0b` (dark code blocks on light page — intentional, matches template), table thead background.
- Rewrote [src/components/NavBar.astro](src/components/NavBar.astro): logo with blue square "D" mark, nav order Home/Languages/Guides/Cheatsheets/Tools/Blog, **no search button** (per user scope), active-link bottom border, mobile hamburger preserved. SearchBar.astro **left on disk**, just unmounted.
- Rewrote [src/components/Footer.astro](src/components/Footer.astro): 4-column grid (Brand 2fr + Tools + Languages + Resources), collapses to 2-col at 900px, 1-col at 520px.
- Rewrote [src/components/PostCard.astro](src/components/PostCard.astro): new structure with `deriveCategory()` helper that regex-matches tags/title for `comparison|tutorial|ai|how-to|cheatsheet` and a `CATEGORY_STYLES` color map. Handles `isNaN(d.getTime())` safely for the Invalid-Date fallout.
- Rewrote [src/components/ToolCard.astro](src/components/ToolCard.astro): 36x36 colored icon box + tier badge. Deterministic hash-to-palette (`hashSlug(slug) % 5`) so each tool gets stable icon colors across builds.
- Rewrote [src/components/LanguageCard.astro](src/components/LanguageCard.astro): simplified to dot + name + count (removed the featured-topics grid that used to live here).
- Updated [src/components/TagBadge.astro](src/components/TagBadge.astro): neutral bg + muted text, accent only on hover.
- **New file:** [src/lib/language-colors.ts](src/lib/language-colors.ts) — GitHub Linguist `LANGUAGE_COLORS` + `LANGUAGE_NAMES` map + `langColor()` + `langName()` helpers.
- **Tool widget color sweep (9 files via sed):** `src/components/tools/{base64-encoder,csv-to-json,hash-generator,json-formatter,jwt-decoder,markdown-to-html,sitemap-generator,url-encoder,uuid-generator}.astro`. Replaced hardcoded dark-theme rgba (`rgba(110, 231, 183, 0.1)` → `var(--color-green-light)`, `rgba(239, 68, 68, 0.1)` → `var(--color-coral-light)`, `#fca5a5` / `#ef4444` → `var(--color-coral)`, purple rgba → `var(--color-purple-light)`).
- **Latent bug caught during Phase 1 build:** [src/pages/tools/index.astro](src/pages/tools/index.astro) was calling `<ToolCard tool={tool} />` — passing the whole object — instead of destructured props. ToolCard's old loose TypeScript interface masked it; once tightened, `hashSlug(undefined)` crashed the build. Fixed call site to pass `slug={tool.data.tool_slug ?? tool.slug}` + explicit name/description/tier/icon. Also fixed two hardcoded rgba colors in the same file. **Phase 1 build passed locally: 43 pages in 24.37s, no warnings.**

**Stage 3 Phase 2 — Page structure rewrites, 4 of 10 files done (ON DISK ONLY):**
- [src/pages/index.astro](src/pages/index.astro) — new hero with gradient span + `HERO_TAGS` chips, featured-tools grid (`FEATURED_TOOL_SLUGS = ['json-formatter', 'base64-encoder', 'regex-tester', 'jwt-decoder']`), 12-language grid pulling from `LANGUAGE_NAMES`, cheatsheets strip (hide-if-empty), recent-posts grid from combined collections.
- [src/pages/languages/[lang]/index.astro](src/pages/languages/[lang]/index.astro) — breadcrumb row, header with `langColor()` dot, stats row (Tutorials / Cheat sheets / Related tools), **numbered concept grid** (posts sorted alphabetically by `concept`, `NN` zero-padded). Related tools section uses `FEATURED_TOOL_SLUGS` (`json-formatter|regex-tester|base64-encoder`) as a simple placeholder. Also extends `getStaticPaths` to emit a page for every `LANGUAGE_NAMES` entry (even zero-post languages) so empty-state doesn't 404.
- [src/pages/languages/index.astro](src/pages/languages/index.astro) — simplified to a 12-card grid driven by `LANGUAGE_NAMES`, responsive auto-fill `minmax(200px, 1fr)` → 2-col on narrow.
- [src/pages/blog/index.astro](src/pages/blog/index.astro) — decorative static filter chips (non-functional — `disabled` + comment noting they're visual only), featured card (first/most-recent post) with gradient thumb + "Featured" pill, remaining posts in 3-col grid via PostCard.

### Commits pushed this session
- `d57f46c` — feat(ui): light theme reskin — tokens, chrome, cards, tool widget colors **(already on origin/main)**
- Stages 1 + 2 fix commits `cdb4aea` + `82a0384` were pushed in a prior session slice.

### What's on disk but uncommitted (⚠️ CRITICAL for session 10)

`git status` at end of session:
```
 M CLAUDE.md                                    ← this update
 M src/pages/blog/index.astro                    ← Phase 2, done
 M src/pages/index.astro                         ← Phase 2, done
 M src/pages/languages/[lang]/index.astro        ← Phase 2, done
 M src/pages/languages/index.astro               ← Phase 2, done
 D STAGE-1..7-*.md                              ← pre-existing, not part of this session
 D devnook.8fc0dbf5-...log                      ← pre-existing, not part of this session
?? .claude/                                      ← untracked, not part of this session
?? development_stages/                           ← untracked, not part of this session
```

**These 4 Phase-2 files have never been through `npm run build`.** The last successful local build was after Phase 1 commit `d57f46c`, which had these files in their *pre-rewrite* state.

### Phase 2 remaining work (6 files + verification)

From the approved plan, in order:
1. **[src/pages/tools/[slug].astro](src/pages/tools/[slug].astro)** — rewrite to 2-column workspace: left `.tool-main` card with `<ToolComponent />` + markdown `<Content />`, right `.tool-sidebar` with (a) info box always, (b) related tools list if `tool.data.related_tools.length > 0`, (c) cheat-sheet link if any `related_content` entry starts with `/cheatsheets/`. Drop the outer breadcrumb from ToolLayout in favor of page-local breadcrumb. Collapses to 1-col on mobile. **Must preserve the existing `import.meta.glob` pattern** for tool component loading — do not switch to dynamic import, that was fixed in session 5.
2. **[src/pages/guides/index.astro](src/pages/guides/index.astro)** — restyle header + 3-col PostCard grid (no featured card, no filter chips). Mostly wrapper/padding tweaks — cards already come from new PostCard.
3. **[src/pages/cheatsheets/index.astro](src/pages/cheatsheets/index.astro)** — same treatment as guides. Check for the old `url=` prop mismatch at call site (session 8 fixed it but verify after rewrite).
4. **[src/pages/404.astro](src/pages/404.astro)** — big "404" in `--color-accent`, centered, return-home CTA button. Light theme.
5. **[src/layouts/PostLayout.astro](src/layouts/PostLayout.astro)** — breadcrumb + h1 + meta-bar styling tweaks for light theme. Prose already handled by global.css.
6. **[src/layouts/ToolLayout.astro](src/layouts/ToolLayout.astro)** — drop the outer breadcrumb (tool page handles its own after rewrite #1). Container max-width only.
7. **Inline-style audit:** `grep -rn 'style=' src/pages src/components` to catch hardcoded greens/darks that survived. Any `rgba(110, 231, 183` or `rgba(239, 68, 68` hits → replace.
8. **`npm run build`** must pass cleanly (target: ~43 pages, no warnings). Then **`npm run dev`** spot-check the walkthrough in the "Verification" block of the plan file.
9. **Commit** as `feat(ui): rebuild page layouts to match template — hero, concept grid, featured card, tool workspace`.
10. **Push** (this pushes both `d57f46c` and the Phase 2 commit to origin/main in one go so Cloudflare rebuilds one coherent state).

### Known gotchas carried into session 10

- **Do not delete the pre-existing `D STAGE-*.md` + `D devnook.*.log` entries or the untracked `.claude/` + `development_stages/` directories as part of the Phase 2 commit.** Those are pre-existing dirty-tree state from before session 9 and are outside the reskin scope. Stage the 4 page files explicitly by path when committing Phase 2.
- **Cheatsheets schema:** the `[lang]/index.astro` rewrite filters `allCheatsheets` by `(cs.data as any).language === lang`. If the cheatsheets Zod schema doesn't actually have a `language` field, that count will always be 0. Not worth fixing in Phase 2 — verify after build and note it.
- **PostCard `category` prop:** Phase 2 sometimes passes `category="blog"`. That's fine (it's optional, falls through to CATEGORY_STYLES.blog), but if you see TS errors it's because the rewritten PostCard typed it narrowly. Keep it optional.
- **Plan file path** `C:\Users\Syed Jawad Hassan\.claude\plans\eager-toasting-moon.md` is user-machine-local — it exists but is not in the repo. Treat the checklist above as source of truth; refer to the plan file only if more detail is needed.

### Deferred / out of scope (unchanged from session 8)
- AdSense, Google Search Console, GSC pinging
- GitHub Actions drip-publish workflow
- Blog filter chips functional wiring (decorative only in this reskin pass)
- Search bar functional wiring (SearchBar.astro parked on disk)
- Orphan content file `sitemap-generator-from-url.md` cleanup
- Formal Stage 7 review against [STAGE-7-launch.md](STAGE-7-launch.md)

---

## Previous Session Summary (session 8)

**Session Date:** 2026-04-13 (session 8)
**Session Goal:** Nuclear reset — delete the broken Cloudflare Pages project, recreate fresh from GitHub, and finally get a styled site up.

### Status at end of session 8: ✅ SITE LIVE WITH DARK THEME — USER HAS A FIX LIST FOR SESSION 9

User confirmed `devnook.dev` is live and rendering with the correct dark theme after commit `b61fd73`. User is tired and stopping for the night. They flagged that there are "a few things we need to fix" and will share the specific list at the start of session 9. **Do not assume the site is done** — treat session 9 as a polish/bug-fix session driven by whatever the user reports.

### What was completed this session

**Phase 1 — Nuclear Cloudflare Pages reset:**
- User deleted the old `devnook` Pages project entirely from the Cloudflare dashboard (Workers & Pages → devnook → Settings → Delete project). This wiped all lingering Functions-mode state from the hybrid-adapter era that sessions 6–7 couldn't clear.
- DNS zone was already clean (no stale `devnook.dev` or `www` records) — Cloudflare's "recommended steps" banner was still prompting the user to add them, which confirmed the nuclear option was safe.
- User created a fresh Pages project via **Workers & Pages → Create application → Pages tab → Connect to Git**:
  - Repo: `syedjawad11/DevNook-`, branch `main`
  - Project name: `devnook` (lowercase — gave a clean `devnook.pages.dev` subdomain)
  - Framework preset: Astro (auto-filled `npm run build` and `dist`)
  - Env var: `NODE_VERSION=20`
  - **Gotcha**: on first attempt the user accidentally entered the new "Create a Worker" wizard (which has "Deploy command" and no framework preset). Had to back out and specifically click the **Pages** tab. Document this for future resets.
- First build deployed cleanly, custom domain `devnook.dev` bound without issue.

**Phase 2 — Diagnosing the "styled HTTP 200" regression:**
- Site was reachable (200 everywhere, both `devnook.pages.dev` and `devnook.dev`) but **completely unstyled** — default browser serif, blue underlined links, no dark theme. User screenshots also showed every post card displaying **"Invalid Date NaN"**.
- This looked identical to session 7's symptom but was a different root cause — sessions 6–7 were chasing a 500 that was masking these two latent bugs the whole time.

**Phase 3 — Root cause #1: CSS never shipped in the build.**
- [src/layouts/BaseLayout.astro:52-53](src/layouts/BaseLayout.astro#L52-L53) references `/styles/tokens.css` and `/styles/global.css` with **absolute paths**. Absolute paths resolve against the deployed root, which means those files needed to live in `public/styles/` (Astro copies `public/` verbatim into `dist/`).
- But the files lived in `src/styles/`. Astro does not scan `src/styles/` for static copy — that directory is only useful when CSS is imported by a component. Nothing imported them, so they never made it into `dist/` at all. Every page shipped HTML pointing at non-existent CSS URLs → unstyled render.
- This bug was latent since day one. The HTTP 500 in sessions 6–7 masked it completely — we never got far enough to see an unstyled 200.
- **Fix:** `mv src/styles public/styles`. No code changes, just a directory move. Verified locally: `dist/styles/tokens.css` and `dist/styles/global.css` are now present after build.

**Phase 4 — Root cause #2: Systemic PostCard prop mismatch.**
- [src/components/PostCard.astro](src/components/PostCard.astro) defined `Props` as `{ title, description, slug, tags, date, category }` and used `slug` as the `<a href>`.
- All 5 call sites were passing garbage prop names: [src/pages/index.astro](src/pages/index.astro) passed `url` + `publishedDate`, [src/pages/guides/index.astro](src/pages/guides/index.astro) passed `url`, [src/pages/languages/[lang]/index.astro](src/pages/languages/[lang]/index.astro) passed `publishedDate`, [src/pages/cheatsheets/index.astro](src/pages/cheatsheets/index.astro) passed `url`, [src/pages/blog/index.astro](src/pages/blog/index.astro) was the only one already correct.
- Result: every card rendered with `href={undefined}` (dead links) and `date={undefined}` → `new Date(undefined)` → "Invalid Date NaN".
- **Fix:** renamed PostCard's `slug` prop → `href` (it was always used as a URL, never a slug), made `category` optional (it's declared but never rendered anywhere in the JSX — dead prop), then normalized all 5 call sites to pass `href={...}` + `date={...}`.

**Phase 5 — Commit + deploy:**
- Local `npm run build` → 43 pages built in ~34s, no warnings.
- Verified `dist/styles/{tokens,global}.css` exist and `dist/index.html` still references `/styles/tokens.css` + `/styles/global.css`.
- Committed as `b61fd73` and pushed. Cloudflare rebuilt automatically.
- User confirmed live site is now styled with dark theme.

### Commits pushed this session
- `b61fd73` — fix(ui): serve global CSS from public/ and fix PostCard prop mismatch

### Known still-broken / unverified at end of session
- **User has not shared their fix list yet.** They only said "few things we need to fix" before stopping. Wait for them in session 9 before touching anything.
- The network-tab check for `/_astro/*.css` status codes was not performed — user stopped before running DevTools. Likely fine since the homepage renders correctly, but nested tool pages haven't been verified.
- `/tools/json-formatter/` interactivity (does the formatter widget actually work in browser?) was not tested.
- The `formatLanguageName` fallback in [src/pages/languages/[lang]/index.astro](src/pages/languages/[lang]/index.astro) was not re-verified after the PostCard prop fix — local build passed so it's fine, but worth a smoke test.
- Orphan content file `sitemap-generator-from-url.md` still exists (deferred from session 6).

---

## Previous Session Summary (session 7)

**Session Date:** 2026-04-13 (session 7)
**Session Goal:** Diagnose and fix the persistent HTTP 500 on `devnook.dev` / `devnook.pages.dev` after session 6's static-output switch.

### What was completed
- Diagnosed that the 500 reproduced on per-deploy unique URLs (bypassing all edge layers), pointing at Pages-project-internal state.
- Hypothesized that `@astrojs/cloudflare` + `@astrojs/sitemap` were still in [package.json](package.json) despite being removed from [astro.config.mjs](astro.config.mjs), keeping the Pages project pinned to Functions mode via the presence of the adapter package on disk.
- Ran `npm uninstall @astrojs/cloudflare @astrojs/sitemap` (66 packages removed), verified local build was still clean static output, committed as **`e5dff68`** and pushed.
- Instructed user to clear Cloudflare build cache. User went on break before verifying.

### Outcome
The `e5dff68` fix was correct but insufficient — session 8 discovered that even after the adapter cleanup the Pages project still had poisoned state, and there were two unrelated latent bugs (missing CSS in `public/`, PostCard prop mismatch) that only surfaced once the 500 was cleared. Session 8 performed a nuclear Pages-project reset and fixed both latent bugs.

---

## Previous Session Summary (session 6)

**Session Date:** 2026-04-13 (session 6)
**Session Goal:** Revised Stage 7 — ship devnook.dev live on Cloudflare with ≤20 seed posts + 10 tools. Scope explicitly excludes AdSense, Google Search Console, and GitHub Actions drip automation (deferred).

### Status at end of session 6: ⚠️ SITE STILL RETURNING ERRORS — PAUSED FOR BREAK

User reported that Google Gemini Antigravity tool interfered with workflow this session. User is stopping Antigravity use for now and taking a break before continuing debug.

### What was completed in this session

**Phase 1 — Scope confirmation (via AskUserQuestion):**
- User confirmed recommended 10 tools: `json-formatter`, `base64-encoder`, `url-encoder`, `jwt-decoder`, `uuid-generator`, `hash-generator`, `regex-tester`, `sql-formatter`, `markdown-to-html`, `csv-to-json`.
- User approved custom domain setup for `devnook.dev`.
- User approved deleting orphan `regex-tester-online-java.md`.

**Phase 2 — Generated 10 tool content `.md` files safely:**
- Could NOT run `python agents/tools-team/build-tool.py --all` because `build_tool()` in [agents/tools-team/build-tool.py:211-219](agents/tools-team/build-tool.py#L211-L219) writes **three** files per slug: component, content, AND `src/pages/tools/{slug}.astro`. Running it would (a) overwrite working tool components with fresh LLM output and (b) create duplicate-route conflicts with the existing dynamic `[slug].astro` route.
- Worked around the gotcha with a temp Python script that imported `build-tool.py` as a module and called only `generate_seo_explainer()` + `write_file()` for each slug — bypassing `build_tool()` entirely. Temp script was deleted after use.
- All 10 new `.md` files in [src/content/tools/](src/content/tools/) are schema-compliant (deterministic Python-built frontmatter from the `ae88cbd` fix).

**Phase 3 — Orphan cleanup:**
- Deleted [src/content/tools/regex-tester-online-java.md](src/content/tools/regex-tester-online-java.md) (orphan with non-schema fields).
- Left `sitemap-generator-from-url.md` since it has a matching component and renders correctly.

**Phase 4 — CRITICAL astro.config.mjs rewrite to fix HTTP 500 errors:**
- After pushing Phase 2 + 3 commits, `devnook.pages.dev` started returning **HTTP 500 Internal Server Error** on every URL (different from session 5's 404).
- **Root cause identified:** [astro.config.mjs](astro.config.mjs) was set to `output: 'hybrid'` with `@astrojs/cloudflare` adapter. No route had `export const prerender = true`, so every route became an SSR Cloudflare Worker. The OG image endpoints in [src/pages/og/](src/pages/og/) import `satori` and `@resvg/resvg-js` at the top level — these native/large modules cannot load in the Cloudflare Workers runtime, crashing the worker on every request.
- **Fix:** Rewrote [astro.config.mjs](astro.config.mjs) to `output: 'static'`, removed `@astrojs/cloudflare` adapter, removed `vite.ssr.external` block, added `image.service` noop for Cloudflare compatibility. Verified zero Cloudflare runtime bindings used anywhere in codebase, so removing the adapter is safe.
- Local `npm run build` passed cleanly: 43 static HTML pages, 31 OG images, 11 tool pages rendered.

**Phase 5 — Committed + pushed as `e39ac16`.**

### ⚠️ OUTSTANDING PROBLEM — NOT YET RESOLVED

After pushing `e39ac16`:
- Polled `devnook.pages.dev` every 20 seconds for 3+ minutes.
- Main alias `https://devnook.pages.dev/` **still returned HTTP 500**.
- Commit-specific preview URL `https://e39ac16.devnook.pages.dev/` returned **HTTP 404**, suggesting the Cloudflare build for `e39ac16` either failed or had not yet deployed.
- Local `dist/` output is clean (no `_worker.js`, no `functions/` directory) confirming static build output is correct. Issue is entirely Cloudflare-side.

**Suspected Cloudflare-side causes (not yet verified):**
1. Cloudflare Pages project may still have "Build output directory" configured for the old hybrid setup — should be `dist` with build command `npm run build`.
2. Cloudflare may be caching stale worker deployment and not picking up the static switch.
3. Build may have failed due to a new error — user needs to check the build log.

**At the end of the session, user said Antigravity had been interfering and they want to stop using it for now, then take a short break before continuing debug.**

### Commits pushed this session
- `e39ac16` — fix(deploy): switch to static output + add 10 tool content pages

### Scope explicitly deferred (per user direction this session)
- Google AdSense setup / privacy / terms / about pages
- Google Search Console submission, `gsc_ping.py`
- GitHub Actions drip-publish workflow
- Remaining 7 tool content files (only the 10 user-selected tools were generated)

### Root cause discovered at end of session
**Stage 7 was never actually executed.** Previous session claimed Stage 7 complete, but `src/pages/` only contained API/OG/sitemap endpoints — zero HTML page routes. No `index.astro`, no `404.astro`, no collection routes. Cloudflare built cleanly but served 404 on every URL because there was nothing to serve. Stage 7 steps (scaffold pages, verify build, custom domain, GSC) were skipped. This session's work was primarily patching that gap to get the deploy working; Stage 7 still needs a formal review.

### What was completed in this session

**Part 1 — Schema error (build-tool.py frontmatter bug):**
- Diagnosed the pasted Cloudflare log as stale — it was from commit `799ea22` where both orphan tool `.md` files lacked `related_content`. At HEAD they already had `related_content: []` (fixed in `dfb8406`). The log would not recur.
- Found the latent root-cause bug in `agents/tools-team/build-tool.py`: the `generate_seo_explainer` prompt told Claude to emit frontmatter with camelCase field names (`publishedDate`, `relatedTools`, `template`) that did NOT match the Zod schema in `src/content/config.ts`. Any *new* tool built via this script would produce broken frontmatter.
- Fixed by rewriting `generate_seo_explainer` to build the frontmatter dict in Python deterministically (all fields pulled from spec JSON), ask the LLM only for the Markdown body, and assemble both with `frontmatter.Post` + `frontmatter.dumps`. Same pattern as `seo_optimizer.py:189`.
- Committed as `ae88cbd` and pushed.

**Part 2 — 404 on devnook.pages.dev (missing HTML pages):**
- After Cloudflare built `91e544d` successfully, `devnook.pages.dev/` returned 404. Investigation revealed `src/pages/` had never contained any HTML routes — only `api/`, `og/`, `sitemap-index.xml.ts`.
- Ran `agents/dev-team/scaffold.py` to generate the 13 missing pages. Before running, added two guardrails to the script:
  1. **`write_file` skip-if-exists check** — prevents re-runs from clobbering committed work (OG generator fixes, config.ts schema, etc.). The 24 existing files were correctly skipped; only the 13 missing page files were written.
  2. **`load_dotenv` import** — scaffold.py wasn't loading `.env`, so the first run crashed with `ANTHROPIC_API_KEY is not set`. Fixed by mirroring the pattern from `build-tool.py:23-27`.
- The 13 newly-scaffolded pages had 6 Claude-generated bugs that only surfaced during `npm run build`:
  1. `cheatsheets/index.astro` — wrong relative path (`../layouts/` instead of `../../layouts/`). Fixed.
  2. `blog/[slug].astro`, `guides/[slug].astro`, `cheatsheets/[subject].astro`, `languages/[lang]/[concept].astro` — passed scattered individual props (`title`, `description`, `publishedDate`) to `PostLayout`, but `PostLayout` expects a single `frontmatter` prop object. Fixed all 4 to pass `frontmatter={post.data}`.
  3. `PostLayout.astro` — passed `items={breadcrumbItems}` to `Breadcrumb`, but `Breadcrumb` component expects `crumbs`. Also rewrote the breadcrumb list construction since the old code assumed props that no longer exist. This was a pre-existing bug that was masked until the new dynamic routes actually tried to render with real content.
  4. `languages/[lang]/index.astro` — defined `formatLanguageName` at module top level and referenced it from inside `getStaticPaths`, but Astro extracts `getStaticPaths` into an isolated scope so the reference failed with `formatLanguageName is not defined`. Fixed by inlining the function + name map inside `getStaticPaths`.
  5. `tools/[slug].astro` — used `await import(\`../../components/tools/${tool.slug}.astro\`)` which Vite can't analyze statically, and crashed for the orphan `regex-tester-online-java.md` content file (no matching component). Fixed by switching to `import.meta.glob('../../components/tools/*.astro', { eager: true })` and filtering `getStaticPaths` to only emit paths where `tool.data.tool_slug` (or fallback `tool.slug`) has a matching component. Orphan `.md` files are silently skipped.
- Local build now passes cleanly: 20 static HTML pages, 22 OG images, 1 tool page (only `sitemap-generator` because its orphan `.md` happens to have a `tool_slug` that matches a real component — the other 16 real tool components have no content yet).
- Committed scaffold fixes + all 13 new pages + PostLayout fix as `04d042f`. Pushed to `origin/main`. Cloudflare rebuild triggered.

### Known orphan / cruft (NOT fixed this session)
- `src/content/tools/regex-tester-online-java.md` and `sitemap-generator-from-url.md` are orphans — they don't match any real tool spec slug and contain extra non-schema fields (`concept`, `difficulty`, `schema_org`, `tier`, `related_cheatsheet`, `related_guides`, `actual_word_count`). The content pipeline (`writer_agent.py` / `staging.py`) appears to be writing to `src/content/tools/` when it shouldn't. Worth investigating in a future session.
- 16 of 17 real tool components (`json-formatter`, `base64-encoder`, etc.) have no matching content markdown, so they don't render as pages. The `build-tool.py` fix from this session now produces schema-compliant content, so `python agents/tools-team/build-tool.py --all` should populate them.

### Commits pushed this session
- `ae88cbd` — fix(tools-team): build schema-compliant frontmatter deterministically
- `04d042f` — feat(pages): add missing HTML page routes + fix PostLayout props

### What's pending going into next session
- **Verify Cloudflare served `04d042f` successfully** and that devnook.pages.dev/ now returns the homepage (not 404).
- **Review Stage 7 formally** against [STAGE-7-launch.md](STAGE-7-launch.md) to list what was actually in scope vs what got done. User flagged this explicitly.
- Revisit the known cruft / orphan content files above.

---

## Previous Session Summary (session 5)

**Session Date:** 2026-04-13 (session 5)
**Session Goal:** Unblock Cloudflare Pages deploy (schema error + 404 on devnook.pages.dev) and discover why deploy was broken.

### Root cause discovered at end of session
**Stage 7 was never actually executed in prior sessions.** `src/pages/` only contained API/OG/sitemap endpoints — zero HTML page routes. Cloudflare built cleanly but served 404 on every URL because there was nothing to serve.

### What was completed in session 5

**Part 1 — Schema error (build-tool.py frontmatter bug):**
- Found latent bug in `agents/tools-team/build-tool.py`: the `generate_seo_explainer` prompt told Claude to emit frontmatter with camelCase field names (`publishedDate`, `relatedTools`, `template`) that did NOT match the Zod schema in `src/content/config.ts`.
- Fixed by rewriting `generate_seo_explainer` to build the frontmatter dict in Python deterministically, ask LLM only for Markdown body, and assemble both with `frontmatter.Post` + `frontmatter.dumps`. Committed as `ae88cbd`.

**Part 2 — 404 on devnook.pages.dev (missing HTML pages):**
- Ran `agents/dev-team/scaffold.py` to generate 13 missing pages. Added two guardrails first: `write_file` skip-if-exists check, and `load_dotenv` import.
- Fixed 6 Claude-generated bugs in the scaffolded pages (wrong relative path, wrong PostLayout props, Breadcrumb prop mismatch, `getStaticPaths` scope issue, dynamic import in tool route).
- Committed as `04d042f`.

## Session 4 Summary

**Session Date:** 2026-04-13 (session 4)
**Session Goal:** Fix Cloudflare Pages deployment build errors and deploy the site live.

**What was completed:**
- Gemini Flash generated 20 seed posts, pushed `799ea22`, connected Cloudflare Pages.
- Claude Opus fixed 3 OG image generator bugs (Google Fonts CSS parsing, Satori `inline-block` not supported, fragile regex with silent fallback). Committed as `dfb8406`.
- Pushed `91e544d` to force fresh Cloudflare build after it cached the wrong commit.
- **(Discovered session 5):** This session never actually generated the HTML page routes, so Cloudflare built cleanly but served 404 on everything.

---

## Next Session Priorities (session 10)

**START HERE:** Session 9 ended mid-Phase-2 of the light-theme reskin. Phase 1 is committed and pushed as `d57f46c`. Phase 2 has 4 of 10 files rewritten **on disk only** — not built, not committed, not pushed. The live site is still the Phase 1 state.

**Do not push anything or run a build before reading the "What's on disk but uncommitted" + "Phase 2 remaining work" blocks in the Last Session Summary above.** Pushing the current half-rewrote tree would ship a broken coherence (new homepage/language hub linking into old tool page layouts, etc.).

### Recommended order for session 10

1. **Verify current state:** `git status` should show the 4 Phase-2 files modified (plus pre-existing dirty state for CLAUDE.md, deleted STAGE files, untracked `.claude/` + `development_stages/`). The 4 Phase-2 files are: `src/pages/index.astro`, `src/pages/languages/[lang]/index.astro`, `src/pages/languages/index.astro`, `src/pages/blog/index.astro`.
2. **Finish the remaining 6 Phase-2 files** in the order listed under "Phase 2 remaining work" in the Last Session Summary. The plan file `C:\Users\Syed Jawad Hassan\.claude\plans\eager-toasting-moon.md` has the full design spec per file — especially section 2.5 for the tool-page 2-col workspace which is the biggest remaining piece.
3. **Run the inline-style audit** (`grep -rn 'style=' src/pages src/components`) to catch stragglers.
4. **`npm run build`** and fix any breakage. The Phase 1 build was 43 pages in ~24s with no warnings — that's your target.
5. **`npm run dev`** and walk the verification checklist from the plan file (homepage, `/languages/python/`, `/tools/json-formatter/` widget interactivity, mobile 375px viewport, DevTools network + console).
6. **Commit Phase 2** staging only the reskin files by explicit path (do NOT `git add .` — that would sweep up the pre-existing dirty tree state). Suggested message: `feat(ui): rebuild page layouts to match template — hero, concept grid, featured card, tool workspace`.
7. **Push `origin main`**. This ships both `d57f46c` and the new Phase 2 commit together so Cloudflare rebuilds one coherent state.
8. **Spot-check live `devnook.dev`** after Cloudflare finishes: homepage hero, language hub concept grid, a tool page, 404.

### Things NOT to touch in this session
- Pre-existing `D STAGE-1..7-*.md` + `D devnook.*.log` deletions in the working tree. They've been dirty since before session 9 and are outside the reskin scope. Stage Phase 2 files by explicit path.
- Untracked `.claude/` and `development_stages/` directories — same reason.
- The search bar (SearchBar.astro is parked on disk, unmounted from NavBar — user explicitly excluded it from scope).
- `build-tool.py` / content pipeline / tool content `.md` files — all out of scope for the reskin.

### Gotchas carried from session 9 (don't repeat)
1. **`tools/[slug].astro` uses `import.meta.glob` for tool component loading** — that pattern was fixed in session 5 to handle the orphan content file. Do not switch to dynamic `await import()`.
2. **When committing, stage by explicit path.** `git add -A` will sweep up the pre-existing dirty tree state and make the commit noisy.
3. **Cheatsheets schema may not have a `language` field** — the language-hub rewrite assumes it does for the stats count. Verify after build; acceptable if count shows 0.

### Deferred (unchanged)
- AdSense, Google Search Console, GSC pinging
- GitHub Actions drip-publish automation
- Remaining 7 tool content files beyond the user's 10
- Orphan `sitemap-generator-from-url.md` cleanup
- Formal Stage 7 review against [STAGE-7-launch.md](STAGE-7-launch.md)

### Important workflow note
**Antigravity remains disabled.** Claude Code is sole driver. The Antigravity Integration Notes section below is historical — ignore it until further notice.

### Gotchas from prior sessions (still apply)
1. **Cloudflare's "Create application" flow defaults to the Workers wizard**, not Pages. If the project ever needs recreating, click the **Pages** tab specifically.
2. **Astro only copies files from `public/` into the build output.** Absolute-path CSS (`/styles/foo.css`) must live in `public/styles/`.
3. **PostCard's prop is `href`, not `slug`.** All 5 call sites normalized in session 8.

---

## Key File Locations

### Source of Truth
- `project-summary.md` — Complete project blueprint (641 lines)
- `templates/templates/` — 22 content template files

### Stage Plans (in `/devnook/` root)
- `STAGE-1-skills.md` through `STAGE-7-launch.md`

### Files Created (All Stages)

**Agent skills** — all 6 `.md` files in `agents/skills/`  
**Dev team** — `agents/dev-team/scaffold.py` + `update.py`  
**Tools team** — `agents/tools-team/build-tool.py` + 17 spec JSON files  
**Utils** — `agents/utils/llm_router.py`, `gemini_client.py`, `registry.py`  
**Skills loader** — `agents/skills/__init__.py`  
**Pipeline** — `agents/content-team/run-pipeline.py`, `keyword_agent.py`, `planner_agent.py`  
**Content pipeline (Stage 5)** — `writer_agent.py`, `seo_optimizer.py`, `qa_agent.py`, `staging.py`  
**Registry** — `agents/content-team/registry.db` (schema initialized, 22 template counters, 323 keywords, `fetched_seeds` cache table)  
**Astro site** — `src/` fully generated and building cleanly  
**Tool content** — all 51 tool files across `src/components/tools/`, `src/pages/tools/` (dynamic only), `src/content/tools/`  
**Publishing** — `agents/publish/publish.py`  
**Launch scripts** — `finish-launch.ps1`  
**OG image generators** — `src/pages/og/{blog,guides,cheatsheets,languages,tools}/[slug].png.ts` (all fixed and working)  
**GitHub repo** — `https://github.com/syedjawad11/DevNook-.git` (main branch, connected to Cloudflare Pages)  

---

## Agent Architecture Quick Reference

```
3 Teams, 7 Python Scripts
├── Dev Team
│   ├── scaffold.py    → Generates entire Astro project (run once)
│   └── update.py      → Updates pages based on registry.db (run after pipeline)
├── Tools Team
│   └── build-tool.py  → Generates tool component + page + SEO content (per tool)
└── Content Team
    └── run-pipeline.py → Orchestrates 6 steps:
        1. keyword_agent.py    → Google Autocomplete → keywords table
        2. planner_agent.py    → Gemini Flash classify → posts table (status=queued)
        3. writer_agent.py     → Claude Sonnet 4.5 → drafts/{slug}.md (status=drafted)
        4. seo_optimizer.py    → Gemini Flash add links + schema → update draft (status=optimized)
        5. qa_agent.py         → Rule-based validate (no LLM) → approve/reject
        6. staging.py          → Move to /content-staging/ (status=staged)

Publishing (GitHub Actions daily):
    drip-publish.yml → publish.py → moves from content-staging → src/content → git push → Cloudflare auto-deploy → gsc_ping.py
```

**LLM Usage (routed via `agents/utils/llm_router.py`):**
- `keyword`, `planner`, `seo`, `analytics` → Gemini 2.5 Flash (free, direct API)
- `qa` → Claude Haiku 4.5 (`claude-haiku-4-5-20251001`, Anthropic direct)
- `writer`, `tool_builder`, `frontend_dev` → Claude Sonnet 4.5 (`claude-sonnet-4-5`, Anthropic direct)

---

## Important Decisions Log

| Decision | Reason | Impact |
|----------|--------|--------|
| No Tailwind | Cleaner diffs, no purge complexity | All styles in tokens.css custom properties |
| Plain Python scripts | No containers, no cloud scheduler | Local execution, simpler debugging |
| Gemini free tier as primary | $0 cost for content pipeline | Rate limiting requires retry logic |
| SQLite + markdown for memory | No external memory framework | DECISIONS.md + registry.db + PIPELINE_LOG.md |
| 22 templates, round-robin | Prevents spam signals | Template counters tracked in registry.db |
| Drip publish (not bulk) | Google Scaled Content Abuse mitigation | 2–3 posts/day via GitHub Actions |
| Content-staging buffer | Decouples generation from publishing | Pipeline runs weekly, publishes daily |
| All tools client-side only | API costs uncontrollable at scale; privacy; zero infra cost | 18 tools, no Workers, no AI-powered tools at launch |
| Dropped OpenRouter, direct Anthropic API | Simpler stack, no intermediary cost/latency | All Claude calls via `anthropic` SDK; llm_router.py is single routing point |
| Mixed model strategy | Right model for right task; cost control | Gemini free for structured tasks; Haiku for QA; Sonnet for writing/building |
| Removed @astrojs/sitemap plugin | Crashed on empty collections with hybrid output; custom sitemap-index.xml.ts already exists | No change to sitemap generation |
| Removed standalone tool pages | Conflicted with [slug].astro dynamic route; duplicate rendering | All tools now served by single dynamic route |
| Writer uses Claude Sonnet, not Gemini | Stage 5 spec suggested Gemini but llm_router routes "writer" to Sonnet 4.5; better quality for long-form content | Writer costs ~$1.10 per 20-post batch at $3/$15 per M tokens |
| QA agent is rule-based, no LLM | Deterministic, fast, zero cost; Haiku routing exists for future use | QA checks: frontmatter, word count, banned phrases, heading hierarchy, TF-IDF dedup |
| Async keyword fetching | Original sync approach took 5+ min (290 HTTP requests); asyncio+aiohttp batches of 10 with 1s delay | Under 1 min; `fetched_seeds` cache table skips repeat runs |
| Switched Gemini to Anthropic (Haiku) | Bypasses `limit 0` HTTP 429 quota exhaustion on Gemini free tier | Planner, Keyword, Analytics, and SEO now run seamlessly via `claude-haiku-4-5-20251001` |
| Stripped markdown wrappers | Claude Sonnet sometimes wraps the entire YAML output in ` ```markdown ` fences | Ensured `python-frontmatter` loads correctly |
| Max 2,000 words logic | User requested articles don't get too lengthy | Appended hard `STRICTLY no more than 2000 words` limit into writer prompt |
| OG font loading via CSS parsing | Google Fonts CSS2 API returns CSS text, not binary font data | All OG generators must: fetch CSS as text → extract `fonts.gstatic.com` URL → fetch binary |
| Satori CSS subset only | Satori only supports `flex`, `block`, `none`, `-webkit-box` for display | No `inline-block`, `inline-flex`, `grid`, `inline` in OG image templates |
| Cloudflare Pages webhook caching | Cloudflare sometimes builds stale commits after rapid pushes | Push a follow-up commit if Cloudflare grabs wrong SHA |
| Switched from hybrid to static output | `output: 'hybrid'` + no `prerender=true` made every route SSR. OG endpoints import `satori` + `@resvg/resvg-js` which can't load in Cloudflare Workers runtime → HTTP 500 on every request. Static build is simpler and has zero runtime dependencies. | Removed `@astrojs/cloudflare` adapter, all routes prerendered at build time, `dist/` is pure static HTML/JS. Applied in `e39ac16`. |
| Never call `build-tool.py build_tool()` for tools with existing components | `build_tool()` writes 3 files per slug (component + content + page). Page file collides with dynamic `[slug].astro` route, and component gets overwritten with fresh LLM output. | To regenerate only content `.md`, import `build-tool.py` as a module and call `generate_seo_explainer()` + `write_file()` directly. |
| Always uninstall an Astro adapter at the same time you remove it from config | Leaving `@astrojs/cloudflare` in package.json after removing the import kept the Cloudflare Pages project pinned to Functions mode even with `output: 'static'`. Confirmed contributor to sessions 6–7 HTTP 500 (applied in `e5dff68`). | If adapter is ever removed from config, run `npm uninstall` in the same commit. |
| Global CSS served via absolute path must live in `public/`, not `src/styles/` | Astro only copies `public/` verbatim into `dist/`. CSS in `src/styles/` is invisible to the build unless a component imports it. BaseLayout references `/styles/tokens.css` + `/styles/global.css` with absolute paths, so they must ship from `public/styles/`. Missing CSS caused the unstyled-200 regression confirmed in session 8 (fixed in `b61fd73`). | Any stylesheet referenced via absolute `/styles/*` path in a layout must live in `public/styles/`. |
| If Cloudflare Pages ever goes fully sideways, nuke the project rather than debug it | The session 6–7 HTTP 500 came from poisoned Pages-project state (Functions-mode flags) that no commit or cache-clear could fix. Deleting and recreating the project via Workers & Pages → Create application → **Pages tab** → Connect to Git was the first thing that actually worked. | Preserve the GitHub repo and DNS zone; only the Pages project gets deleted. Recreate with Framework=Astro, Build=`npm run build`, Output=`dist`, Env=`NODE_VERSION=20`. Then rebind custom domain. |

---

## Environment Variables Required

```bash
ANTHROPIC_API_KEY=sk-ant-...       # writer, qa agents + tools-team
GEMINI_API_KEY=AIza...             # keyword, planner, seo, analytics agents
GOOGLE_SERVICE_ACCOUNT_JSON=...    # GSC pinging (Stage 6+)
```

---

## Content Targets

| Ring | Content Type | Target Count | Status |
|------|-------------|--------------|--------|
| Ring 1 | Tool-adjacent guides | ~80 posts | 0 / 80 |
| Ring 2 | Web dev fundamentals | ~200 posts | 0 / 200 |
| Ring 3 | Language concepts | ~600+ posts | 0 / 600 |
| Bonus | AI/comparison/editorial | ~200 posts | 0 / 200 |
| Tools | Browser-based dev tools | 18 (client-side) | 0 / 18 |

**Publishing velocity target:** 1,000+ posts in 6 months

---

## How to Run Agents

### Prerequisites
```bash
pip install -r agents/requirements.txt
# Set ANTHROPIC_API_KEY and GEMINI_API_KEY before running pipeline
```

### Run Commands (execute from project root)
| What the user says | Command to run |
|--------------------|---------------|
| "run scaffold" | `python agents/dev-team/scaffold.py` |
| "run update" | `python agents/dev-team/update.py` |
| "build tool {slug}" | `python agents/tools-team/build-tool.py --spec {slug}` |
| "build all tools" | `python agents/tools-team/build-tool.py --all` |
| "run keyword agent" | `python agents/content-team/run-pipeline.py --steps keyword` |
| "run planner" | `python agents/content-team/run-pipeline.py --steps planner` |
| "run keyword + planner" | `python agents/content-team/run-pipeline.py --steps keyword,planner` |
| "run writer" | `python agents/content-team/run-pipeline.py --steps writer` |
| "run seo + qa + staging" | `python agents/content-team/run-pipeline.py --steps seo,qa,staging` |
| "run the content pipeline" | `python agents/content-team/run-pipeline.py --steps all` |
| "run write pipeline" | `python agents/content-team/run-pipeline.py --steps writer,seo,qa,staging` |
| "start dev server" | `npm run dev` |
| "build site" | `npm run build` |
| "check registry" | `python -c "import sqlite3; db=sqlite3.connect('agents/content-team/registry.db'); [print(r) for r in db.execute('SELECT status, COUNT(*) FROM posts GROUP BY status')]"` |

---

## Antigravity Integration Notes

> ⚠️ **PAUSED as of session 6 (2026-04-13).** User disabled Antigravity because it was interfering with the workflow. Claude Code is sole driver. Section kept for reference only.

This project uses Google Antigravity IDE with Claude Code extension.

**Role division:**
- Antigravity (Gemini agents): Planning, architecture review, pipeline monitoring, frontend scaffolding
- Claude Code: Implementation, debugging, agent code writing, CLAUDE.md updates

**Coordination rules:**
- Only Claude Code updates CLAUDE.md
- Antigravity skills file is at .gemini/antigravity/skills/devnook.md
- When Antigravity generates a plan, it should be saved to a temp file that Claude Code can read
- Pipeline runs can be started from either tool's terminal
