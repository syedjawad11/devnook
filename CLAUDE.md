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

**Session Date:** 2026-04-17 (session 13)
**Session Goal:** Execute Phase 2 — full pipeline dry run with all subagents.

### Status: ✅ PHASE 2 COMPLETE

### What was completed

1. **Writer subagent** — 3 editorial guides written from queued registry posts, all QA passed (1,600–1,740 words each), saved to `agents/content-team/drafts/`, registry updated to `status=drafted, qa_status=passed`.

2. **Ingest subagent** — 10 Antigravity files ingested from `../web_content/output/`. Copied to drafts, inserted into registry (`source=antigravity`, `content_type=programmatic`, `status=drafted`), originals archived to `_ingested/`.

3. **Publisher subagent** — 3 editorial guides staged then published to `src/content/guides/`. Registry updated to `status=published`.

4. **Build verified** — `npm run build` passed cleanly: 52 pages (up from 43+).

### Registry state after session
- published: 23 | drafted: 10 (Antigravity) | queued: 2 | rejected: 10 | staged: 1

### Next session priorities (session 14)

1. **Scale Writer** — run Writer on remaining 2 queued editorial posts + queue more via Planner
2. **Antigravity QA gate** — decide: auto-approve `source=antigravity` drafts or run QA pass before publish
3. **GitHub Actions drip publish** — automate 2–3 posts/day from staged content
4. **AdSense + GSC setup** — submit sitemap, enable AdSense

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
