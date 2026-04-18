# DevNook — Claude Session Log

> Always read this file first at the start of a new session. Updated at end of every session.

---

## Project Overview

**DevNook** (devnook.dev) is a developer resource site targeting 1,000+ programmatic content pieces + 18 free browser-based client-side tools, monetized via Google AdSense.

**Domain:** devnook.dev (registered Cloudflare, April 2026)  
**Tech stack:** Astro + Cloudflare Pages + Claude Code subagents  
**Content model:** "Concentric Rings" — tools → web fundamentals → language concepts  
**Agent model:** Claude Code subagents (Haiku/Sonnet), Python utilities for non-LLM ops, GitHub Actions publishing

---

## Stage Progress

| Stage | Status | Session Completed |
|-------|--------|-------------------|
| 1 — Skills | ✅ Complete | 2026-04-10 |
| 2 — Dev Team | ✅ Complete | 2026-04-10 |
| 3 — Tools Team | ✅ Complete | 2026-04-11 |
| 4 — Content Pipeline Core | ✅ Complete | 2026-04-12 |
| 5 — Content Pipeline Write | ✅ Complete | 2026-04-12 |
| 6 — Publishing | ✅ Complete | 2026-04-13 |
| 7 — Launch | ✅ Live — light-theme reskin complete | 2026-04-15 |
| 8 — Subagent Architecture | 🚧 Phase 2 complete (session 13) | 2026-04-17 |

---

## Last Session Summary

**Session Date:** 2026-04-18 (session 19)
**Session Goal:** Fix broken related links (75/89 returning 404) — build-time existence filter (Option A).

### Status: ✅ Complete — build passing, 60 pages, 0 errors

### What was done

1. **Fixed `src/layouts/PostLayout.astro`** — added `getCollection` import + build-time pathMap that resolves `related_posts` string paths into `{title, slug, category}` objects, filtering out any path not matching a real page. Also fixed a pre-existing bug where raw `string[]` was passed to `RelatedPosts` (which expects objects), causing blank titles on every page.

2. **Fixed `src/pages/tools/[slug].astro`** — added `filteredRelatedTools` computed from a `Set` of valid tool paths; "Related tools" sidebar card now only renders when ≥1 linked tool actually exists.

3. **Root causes addressed:**
   - Aspirational links to unpublished pages (majority): silently dropped at build time
   - Slug mismatch in languages content: pathMap uses `e.slug` which matches actual Astro routes
   - Fix is self-healing — links automatically appear as new content is published

### Next session priorities (session 20)

1. **Remaining 7 Antigravity articles** — QA → Publisher pipeline:
   - how-to-implement-singleton-design-pattern-in-javascript
   - how-to-parse-json-in-javascript
   - how-to-send-http-request-in-cpp
   - how-to-set-environment-variables-in-java
   - how-to-set-environment-variables-in-php
   - how-to-use-data-class-in-kotlin
   - how-to-write-closure-in-swift
2. **Scale Writer** — run Writer on 2 queued editorial posts (CSS minification, HTML minification)
3. **Fix 2–3 minor website UI issues** (user noticed during review — not yet specified)
4. **Verify GSC** — confirm sitemap submission + indexing working (if user completed GSC setup)

### Deferred (do NOT do until traffic hits 50k visitors/month)
- **AdSense integration** — explicitly deferred by user; revisit only at 50k visitors/month threshold

### Deferred (unchanged)
- Blog filter chips functional wiring (decorative only)
- Search bar wiring (SearchBar.astro parked on disk)
- Orphan `sitemap-generator-from-url.md` cleanup

Historical session summaries (sessions 4–10) moved to [session-history.md](session-history.md).

---

## Key File Locations

**Architecture plan** — `development_stages/subagent-architecture-plan.md`  
**Subagent prompts** — `agents/subagent-prompts/{planner,writer,ingest,antigravity-qa,builder,publisher}.md`  
**Agent skills** — `agents/skills/{astro-conventions,content-schema,devnook-brand-voice,qa-rejection-criteria,seo-writing-rules,tool-build-patterns}.md`  
**Registry** — `agents/content-team/registry.db` (25 columns, includes content_type + source)  
**Drafts** — `agents/content-team/drafts/`  
**Antigravity ingest source** — `../web_content/output/`  
**Astro site** — `src/` (building cleanly, 60 pages, 17 tools)  
**GitHub repo** — `https://github.com/syedjawad11/DevNook-.git` (main branch, Cloudflare Pages auto-deploy)

---

## Subagent Architecture Quick Reference

```
ORCHESTRATOR (Opus/Sonnet main session)
  ├── Content Team
  │   ├── Planner  (Haiku)  — keyword discovery → posts table (status=queued)
  │   ├── Writer   (Sonnet) — drafts/{slug}.md (status=drafted, qa validated)
  │   └── Ingest   (Haiku)  — ../web_content/output/ → drafts/ (status=drafted)
  ├── Dev Team
  │   └── Builder  (Sonnet) — Astro edits + npm run build
  └── Publish Team
      └── Publisher (Haiku) — drafts → staging → src/content

Orchestrator: spawns subagents, reviews JSON reports (~200 tokens each),
              commits + pushes only on user approval.
Python scripts: retained as non-LLM utilities (DB ops, file moves, HTTP scraping).
  └── Antigravity QA (Sonnet) — fixes + approves antigravity drafts before publish
```

**Workflow patterns:**
- Pattern A (weekly content run): Planner → Ingest (parallel) → Writer (batch=5) → Publisher
- Pattern A2 (Antigravity publish): Ingest → Antigravity QA (batch=10) → Publisher
- Pattern B (new tool): Orchestrator checks spec → Builder → review + commit
- Pattern C (bug fix): Orchestrator describes → Builder → review + commit
- Pattern D (status check): inline sqlite3 query — no subagent needed

---

## Important Decisions Log

| Decision | Reason | Impact |
|----------|--------|--------|
| No Tailwind | Cleaner diffs, no purge complexity | All styles in tokens.css custom properties |
| Plain Python scripts | No containers, no cloud scheduler | Local execution, simpler debugging |
| SQLite + markdown for memory | No external memory framework | registry.db + PIPELINE_LOG.md |
| 22 templates, round-robin | Prevents spam signals | Template counters tracked in registry.db |
| Drip publish (not bulk) | Google Scaled Content Abuse mitigation | 2–3 posts/day via GitHub Actions |
| All tools client-side only | API costs uncontrollable; privacy; zero infra | 18 tools, no Workers, no AI-powered tools |
| Switched from hybrid to static output | OG endpoints import satori which crashes Cloudflare Workers runtime | `output: 'static'`, no adapter |
| Global CSS in `public/styles/` not `src/styles/` | Astro only copies `public/` to `dist/`; absolute `/styles/*` refs need public/ | Never put absolute-path CSS in src/ |
| PostCard prop is `href` not `slug` | All 5 call sites use `href`; was `slug` before session 8 | Never rename back to slug/url/path |
| `tools/[slug].astro` uses `import.meta.glob` | Dynamic `await import()` crashes Vite static analysis | Never switch to dynamic import for tool loading |
| Never call `build-tool.py build_tool()` for existing tools | Writes 3 files including page that collides with dynamic route | Call `generate_seo_explainer()` + `write_file()` directly |
| Always uninstall adapter when removing from config | Package presence kept Pages in Functions mode even with `output: 'static'` | `npm uninstall` in same commit as config removal |
| Nuclear reset beats debugging poisoned Pages state | Sessions 6–7 couldn't clear Functions-mode flags via commits or cache | Delete + recreate Pages project; preserve repo + DNS |
| Subagent architecture replaces Python LLM pipeline | Monolithic Opus session burned context and token budget | 5 subagents (Haiku/Sonnet) in isolated contexts; Opus as orchestrator only |
| Languages category owned by Antigravity | Clean firewall; DevNook editorial only (guides/blog/cheatsheets/tools) | Planner + Writer must never queue languages posts |
| Antigravity QA never rejects | Gemini Pro 3.1 content trusted; QA fixes structural/SEO issues only | antigravity-qa subagent always sets qa_status='passed'; word range 1500–2500 |
| Use `@astrojs/sitemap` not custom sitemap | Custom `sitemap-index.xml.ts` was broken (missing child sitemaps) | `@astrojs/sitemap@3.2.1` — v3.7+ incompatible with Astro 4.x |

---

## Environment Variables Required

```bash
ANTHROPIC_API_KEY=sk-ant-...       # writer, qa agents + tools-team
GEMINI_API_KEY=AIza...             # legacy — not used in subagent architecture
GOOGLE_SERVICE_ACCOUNT_JSON=...    # GSC Indexing API — add as GitHub secret for drip-publish
```

---

## Content Targets

| Ring | Content Type | Target | Status |
|------|-------------|--------|--------|
| Ring 1 | Tool-adjacent guides | ~80 posts | 0 / 80 |
| Ring 2 | Web dev fundamentals | ~200 posts | 0 / 200 |
| Ring 3 | Language concepts | ~600+ posts | 0 / 600 |
| Ring 4 | AI/comparison/editorial | ~200 posts | 0 / 200 |
| Tools | Browser-based dev tools | 18 (client-side) | 0 / 18 |

**Publishing velocity target:** 1,000+ posts in 6 months

---

## How to Run (Subagent Architecture)

```
Invoke subagents via the Agent() tool in the main Opus/Sonnet session.
Pass contents of agents/subagent-prompts/{name}.md as the prompt body.

Status check (no subagent):
  python -c "import sqlite3; db=sqlite3.connect('agents/content-team/registry.db');
  [print(r) for r in db.execute('SELECT status, content_type, source, COUNT(*) FROM posts GROUP BY 1,2,3')]"

Build site:
  npm run build

Dev server:
  npm run dev
```
