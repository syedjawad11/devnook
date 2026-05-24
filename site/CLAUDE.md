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

## Last Session (2026-05-24, #54)

**Status:** ✅ Pipeline B persistent routine live. Content workspace cleaned (0 staged).

### What was done in #51–#54 (content workspace sessions)

- **#51**: `javascript-closures` rewritten under modular-v1 system (1,044 → 1,258 words). Commit `721f748` pushed to `origin main`.
- **#52**: External links gap fixed across all agents. `python-string-methods-cheatsheet` and `javascript-closures` patched with external links. Commit `b95c4a7` pushed. `.claude/agents/` now tracked in content workspace git.
- **#53**: Pipeline B orchestrator built (`pipeline-b-orchestrator.md`). 20 AI/Productivity topics queued in `data/pipeline-b-topics.json`. Session-only CronCreate test failed (session closed before firing).
- **#54**: 3 stuck Pipeline A posts deleted from staging, registry cleaned to 0 staged. `pipeline-b-orchestrator.md` rewritten to call DataForSEO REST API directly (local MCP cannot be a remote connector). **Pipeline B CCR routine created**: `trig_01LD6ZaMZq3G6R5Aehz7xMHY`, daily 14:00 UTC (16:00 Malta CEST). First run: today 2026-05-24. Manage: `https://claude.ai/code/routines/trig_01LD6ZaMZq3G6R5Aehz7xMHY`.

### Key learnings from #50–#54

- Always verify description length with Python `len()` — agent self-reported counts are unreliable.
- Any frontmatter value containing `: ` must be wrapped in double quotes to avoid YAML parse errors at build time.
- PowerShell here-strings use `@'...'@` syntax — bash-style `cat <<'EOF'` is invalid in PowerShell.
- Local npm MCPs (`npx dataforseo-mcp-server`) cannot be remote connectors — remote CCR routines must call REST APIs directly.
- Never use `[skip ci]` in devnook commit messages — Cloudflare Pages skips the build.
- No H1 in markdown body — `PostLayout.astro` renders `frontmatter.title` as `<h1>`; duplicate H1 flagged by Ahrefs.

### Current pipeline state

- Registry: **~74 published / 0 staged / 14 rejected**
- Pipeline A (`drip-publish.yml`): paused — cron commented out, 0 staged, redesign deferred
- Pipeline B: **live daily at 16:00 Malta** — first run today at 16:00; publishes to `src/content/blog/`
- SEO rewrites: 46 language articles queued in `data/rewrite-queue.json`

### Next session priorities (#55)

1. **Verify first Pipeline B run** — check `../devnook_content_workspace/data/pipeline-b-runs.log` for success entry; visit `https://devnook.dev/blog/how-to-use-claude-code`.
2. **Continue SEO rewrites** — `@seo-optimizer` batch from `data/rewrite-queue.json` under modular-v1 system.
3. **Deferred** — FAQPage schema validation for `meta-tag-generator`, `readme-generator`, `sitemap-generator-from-url`.

### Deferred (do not do)

- **AdSense integration** — revisit only at 50k visitors/month
- **GSC ping** — `GOOGLE_SERVICE_ACCOUNT_JSON` secret never set in content workspace repo. Non-blocking — defer.
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
