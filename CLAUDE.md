# DevNook — Claude Session Log (Dev Workspace)

> Always read this file first at the start of a new session. Updated at end of every session.
> **Content pipeline lives in `../devnook_content_workspace/`** — no pipeline code or registry in this repo.

## Session start — do NOT auto-read these files

Unless explicitly asked, do not open:

- `archives/decisions-archive.md` (on demand only)
- Prior chat transcripts or session history

Start each session from this file + MEMORY.md only.

---

## Project Overview

**DevNook** (devnook.dev) — developer resource site, 1,000+ programmatic posts + 18 client-side browser tools, monetized via AdSense (deferred until 50k visitors/month).

**Stack:** Astro + Cloudflare Pages. Content is published by `../devnook_content_workspace/` via PAT.
**Repo:** `main` branch, Cloudflare Pages auto-deploy on every push.

---

## Stage Progress

| Stage | Status | Completed |
|-------|--------|-----------|
| 1 — Skills | ✅ | 2026-04-10 |
| 2 — Dev Team | ✅ | 2026-04-10 |
| 3 — Tools Team | ✅ | 2026-04-11 |
| 4 — Content Pipeline Core | ✅ | 2026-04-12 |
| 5 — Content Pipeline Write | ✅ | 2026-04-12 |
| 6 — Publishing | ✅ | 2026-04-13 |
| 7 — Launch | ✅ Live | 2026-04-15 |
| 8 — Subagent Architecture | ✅ | 2026-04-17 |
| 9 — Workspace Split | ✅ | 2026-04-25 |
| 10 — Cross-repo CI + Cleanup | ✅ | 2026-04-25 |

---

## Last Session (2026-05-16, #45)

**Status:** ✅ Language article rewrite system fully set up. Infrastructure committed, session 1 manually completed (1 article), test Claude Routine created for tonight.

### What was done

- **Created `New_ContentStrategy/` rewrite infrastructure** — committed in `4b30e89`:
  - `REWRITE-WORKFLOW.md` — master self-contained instruction set for the Claude Routine
  - `SELECTION-GUIDE.md` — 9-step section selection algorithm in Claude-readable natural language (replaces deleted `select_sections.py`)
  - `rewrite-queue.json` — 47 articles ordered by `published_date` asc, all `"status": "pending"` except order 1
  - `rewrite-tracker.json` — per-language section history for diversity enforcement (seeds typescript from session 1)
  - Deleted: `migration.sql`, `INSTALL.md`, `select_sections.py` (Python/SQLite pipeline incompatible with remote Claude Routines)
- **Session 1 manual rewrite complete** — `src/content/languages/typescript/async-await-typescript.md` rewritten:
  - Voice: `thoughtful-explainer`, Sections: `[open-problem, core-design-decision, code-side-by-side, comp-cross-language, prac-gotchas, close-one-thing]`, ~1,680 words
  - Queue updated: `sessions_completed: 1`, `done_count: 1`, `pending_count: 46`
- **Test Claude Routine created** — fires tonight at 2026-05-17T01:00:00Z (3:00 AM Malta):
  - Routine ID: `trig_01FZHoRx5tsnS6WCyrCk7DfV`
  - URL: `https://claude.ai/code/routines/trig_01FZHoRx5tsnS6WCyrCk7DfV`
  - Rewrites orders 2, 3, 4: `php/json-decode`, `python/file-handling`, `rust/async-await`
  - Commits + pushes to `main` — fires once then auto-disables
- **GitHub App installed** on `syedjawad11/devnook` — required for remote routines to push code.

### Previous session (#44) summary

FAQPage JSON-LD added to all 14 tool pages that have visible FAQs. Commits: `4907a22` (infrastructure), `f74f21f` (14 markdown files).

### Next session priorities (#46)

1. **Morning review (do first)** — check the 3 articles rewritten by the test routine:
   - `src/content/languages/php/php-json-decode.md`
   - `src/content/languages/python/python-file-handling-tutorial.md`
   - `src/content/languages/rust/rust-async-await.md`
   - Verify: fresh body prose, frontmatter preserved, no `# H1`, `template_id: modular-v1`, word counts in range, `rewrite-queue.json` shows orders 2/3/4 `"done"`, `pending_count: 43`.
2. **If test passes — set up two recurring routines** (4 articles each, 8/day, ~6 days to finish):
   - Routine A: `0 23 * * *` UTC (= 1:00 AM Malta CEST)
   - Routine B: `0 5 * * *` UTC (= 7:00 AM Malta CEST)
3. **After all 47 rewrites done** — re-enable drip-publish cron manually (do NOT auto-enable — the rewrite routine's stop condition does not re-enable it).
4. **Deferred from #45** — Re-run Ahrefs crawler, validate FAQPage schema in Google Rich Results Test, add FAQs to 3 skipped tools (`meta-tag-generator`, `readme-generator`, `sitemap-generator-from-url`), content expansion for WARN posts.

### Deferred (do not do)

- **AdSense integration** — revisit only at 50k visitors/month
- **GSC ping** — `GOOGLE_SERVICE_ACCOUNT_JSON` secret never set in content workspace repo; every cron run prints "Skipping GSC ping". Non-blocking config gap — defer to a dedicated session.
- Blog filter chips wiring (decorative only)
- Search bar wiring (`SearchBar.astro` parked)

---

## Key Paths

- Astro site: `src/`
- Layouts: `src/layouts/`
- Content: `src/content/` (written by content workspace publisher)
- Components: `src/components/`
- Global styles: `public/styles/` (NOT src/styles/)
- Tools: `src/pages/tools/[slug].astro` + `public/tools/*.html`
- Auto-internal-links plugin: `src/plugins/auto-internal-links/index.mjs`
- Related callouts plugin: `src/plugins/related-callouts/index.mjs`
- Dev subagent: `agents/subagent-prompts/builder.md`
- Dev skills: `agents/skills/astro-conventions.md`, `agents/skills/tool-build-patterns.md`
- SEO audit script: `scripts/seo_audit.py` — run with `D:\miniconda3\python.exe scripts/seo_audit.py`
- Trailing slash fixer: `scripts/fix_trailing_slashes.py` — run with `D:\miniconda3\python.exe scripts/fix_trailing_slashes.py`
- SEO audit log: `auditlog.md` — issues, verdicts, session fix plan (read before #37+)

---

## Dev Subagent

```
ORCHESTRATOR (Sonnet main session)
  └── Builder (Sonnet) — agents/subagent-prompts/builder.md
      Handles: Astro edits, new tools, npm run build verification
```

Spawn with: `Agent(prompt=open('agents/subagent-prompts/builder.md').read(), ...)`

**Workflow B** — new tool: Orchestrator → Builder → review + commit
**Workflow C** — bug fix: Orchestrator → Builder → review + commit

---

## Important Decisions Log

> Live guardrails — if you forget these, you will break something.

| Decision | Impact |
|----------|--------|
| No Tailwind | All styles in `tokens.css` custom properties |
| All tools client-side only | 18 tools, no Workers, no AI-powered tools |
| Static output (not hybrid) | `output: 'static'`, no adapter — satori crashes Workers runtime |
| Global CSS in `public/styles/` not `src/styles/` | Astro only copies `public/` to `dist/`; absolute `/styles/*` refs need public/ |
| PostCard prop is `href` not `slug` | All 5 call sites use `href`; never rename to slug/url/path |
| `tools/[slug].astro` uses `import.meta.glob` | Dynamic `await import()` crashes Vite static analysis |
| Never call `build-tool.py build_tool()` for existing tools | Writes page that collides with dynamic route — use `generate_seo_explainer()` + `write_file()` |
| Auto internal links plugin (rehype, build-time) | `src/plugins/auto-internal-links/index.mjs`; `autoAnchors: true`; `devnookUrlBuilder` required — language concept URLs use `frontmatter.language`+`frontmatter.concept`, NOT filename |
| Use `@astrojs/sitemap@3.2.1` not custom | Custom sitemap was broken; v3.7+ incompatible with Astro 4.x. Current version generates `sitemap-0.xml` (0-indexed) — do not expect `sitemap-1.xml` |
| Related posts auto-derived at render time (session 27) | `src/layouts/PostLayout.astro` builds the related list from `getCollection()` using a language/category/tags score — never from a hand-written `## Related` markdown section. `frontmatter.related_posts` is unused; leave as `[]`. |
| Linker retired (session 25) | Replaced by `src/plugins/auto-internal-links/index.mjs` (build-time rehype plugin). `link_utility.py` kept dormant in devnook root — delete after stable operation. |
| Content pipeline is external | No registry, no staging, no publish scripts in this repo. `src/content/` is written by `../devnook_content_workspace/agents/publish/publish.py` via cross-repo git push. |
| Language post URLs must use `concept`, not filename | Content pipeline agents historically guessed `/languages/{lang}/{filename-slug}` in body prose. Correct path is always `/languages/{lang}/{concept}` from registry. `publish.py` now has `validate_language_links()` guard that skips files with filename-based links at publish time. `link_utility.py._url_for_row()` is already correct — the bug is agents bypassing it. |
| Auto-internal-links plugin covers all categories | `src/plugins/auto-internal-links/index.mjs` scans the full `contentDir` via `fast-glob` — all of `guides`, `blog`, `cheatsheets`, `languages`. Not language-only. `devnookUrlBuilder` note only describes URL *generation* for language posts. |
| Related callouts plugin (session 32) | `src/plugins/related-callouts/index.mjs` — build-time rehype plugin injects up to 3 `<aside class="related-callout">` nodes at interior H2 boundaries. Scoring mirrors PostLayout.astro. CSS in `public/styles/global.css` (not scoped). Per-post opt-out: `excludeRelatedCallouts: true` in frontmatter. |
| No H1 in markdown body (session 42) | `PostLayout.astro` renders `frontmatter.title` as the page `<h1>`. Any `# Title` line in the body creates a second `<h1>` — Ahrefs flags as "Multiple H1 tags". Content pipeline files patched: `writer.md`, `antigravity-qa.md`, `seo-writing-rules.md`. Never write or instruct agents to write a body H1. |
| Never use `[skip ci]` in devnook commit messages (session 43) | Cloudflare Pages honors `[skip ci]` and skips the build — so drip-publish commits would never deploy. The `[skip ci]` in `drip-publish.yml` line 78 is intentional (content-workspace side, prevents workflow retriggering itself). The devnook-side commit in `publish.py` must NOT include it. |

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...       # Builder subagent (if needed for tool work)
```

---

## How to Run

```bash
# Dev server
npm run dev

# Production build (always verify before committing)
npm run build

# Preview production build
npm run preview
```
