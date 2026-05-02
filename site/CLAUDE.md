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

## Last Session (2026-05-02, #33)

**Status:** ✅ Inline cross-links added to all 17 tool pages — 51 new links, committed `7c8072c` and live on Cloudflare Pages.

### What was done

- **Added ≥3 inline body cross-links to all 17 tool pages** in `src/content/tools/`. Links point to related tools, guides, cheatsheets, and blog posts. Added inline within existing prose — no new sections, no frontmatter changes.
- **51 total new links** across: `base64-encoder`, `colour-converter`, `cron-parser`, `csv-to-json`, `diff-viewer`, `hash-generator`, `html-formatter`, `json-formatter`, `jwt-decoder`, `markdown-to-html`, `meta-tag-generator`, `readme-generator`, `regex-tester`, `sitemap-generator-from-url`, `sql-formatter`, `url-encoder`, `uuid-generator`.
- **Auto-internal-links plugin does NOT cover tool-to-tool links** — all tool page cross-links must be manually maintained in markdown prose (plugin handles guides/blog/cheatsheets/languages only).
- **Build verified**: 88 pages, no errors. Committed and pushed to `main`.

### Previous session (#32) summary

- Related callouts plugin (`src/plugins/related-callouts/index.mjs`) shipped — injects `<aside class="related-callout">` at H2 boundaries for non-tool content pages.

### Next session priorities (#34)

1. **Spot-check drip posts** — verify no broken links in recently staged content
2. **Apply "never write /languages/ URL" rule** — add to `antigravity-qa.md` and `writer.md` in `../devnook_content_workspace/agents/subagent-prompts/`
3. **Cloudflare dashboard** — disable Email Address Obfuscation (Scrape Shield → Off) to clear cdn-cgi 404s on 10 pages (carry-over from #29)
4. **Verify sitemap in GSC** — resubmit `https://devnook.dev/sitemap-index.xml`
5. **Repo-wide broken link audit** — sweep remaining published posts using `devnook_25-apr-2026_page-has-links-to-broken_2026-04-25_17-46-11.csv` at repo root

### Deferred (do not do)

- **AdSense integration** — revisit only at 50k visitors/month
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
