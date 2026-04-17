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
| 8 — Subagent Architecture | 🚧 Phase 1 complete (session 12) | 2026-04-17 |

---

## Last Session Summary

**Session Date:** 2026-04-17 (session 12)
**Session Goal:** Execute Phase 1 of the subagent architecture plan designed in session 11.

### Status: ✅ PHASE 1 COMPLETE

### What was completed

1. **Schema migration** — Added `content_type` and `source` columns to `registry.db` posts table.
   - 17 existing posts → `content_type='editorial'`, `source='claude_code'`
   - 14 existing posts → `content_type='programmatic'`, `source='claude_code'`
   - Table now has 25 columns (was 23)

2. **Subagent prompt files** — Created `agents/subagent-prompts/` with 5 prompt templates:
   - `planner.md` (Haiku) — keyword discovery + queuing
   - `writer.md` (Sonnet) — article writing + SEO + QA
   - `ingest.md` (Haiku) — Antigravity file ingestion + mapping contract
   - `builder.md` (Sonnet) — Astro site dev + 5 gotchas embedded
   - `publisher.md` (Haiku) — drafts → staging → src/content

3. **CLAUDE.md trimmed** — Sessions 4–10 moved to `session-history.md`. File reduced from 588 to ~150 lines.

4. **Planner smoke test** — [TBD — complete after Step 3 confirm]

### Commits pushed
- None yet — pending user approval at end of session

### Next session priorities (session 13 — Phase 2)

1. **Writer subagent test** — Write 3 test editorial articles, validate quality vs old pipeline
2. **Ingest subagent test** — Ingest Antigravity output files from `../web_content/output/`
3. **Publisher subagent test** — Stage + publish test content
4. **Full pipeline dry run** — Planner → Writer → Publisher end-to-end

### Deferred (unchanged)
- AdSense, GSC, gsc_ping.py
- GitHub Actions drip-publish automation
- Blog filter chips functional wiring (decorative only)
- Search bar wiring (SearchBar.astro parked on disk)
- Orphan `sitemap-generator-from-url.md` cleanup

Historical session summaries (sessions 4–10) moved to [session-history.md](session-history.md).

---

## Key File Locations

**Architecture plan** — `development_stages/subagent-architecture-plan.md`  
**Subagent prompts** — `agents/subagent-prompts/{planner,writer,ingest,builder,publisher}.md`  
**Agent skills** — `agents/skills/{astro-conventions,content-schema,devnook-brand-voice,qa-rejection-criteria,seo-writing-rules,tool-build-patterns}.md`  
**Registry** — `agents/content-team/registry.db` (25 columns, includes content_type + source)  
**Drafts** — `agents/content-team/drafts/`  
**Antigravity ingest source** — `../web_content/output/`  
**Astro site** — `src/` (building cleanly, 43+ pages)  
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
```

**Workflow patterns:**
- Pattern A (weekly content run): Planner → Ingest (parallel) → Writer (batch=5) → Publisher
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

---

## Environment Variables Required

```bash
ANTHROPIC_API_KEY=sk-ant-...       # writer, qa agents + tools-team
GEMINI_API_KEY=AIza...             # legacy — not used in subagent architecture
GOOGLE_SERVICE_ACCOUNT_JSON=...    # GSC pinging (future)
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
