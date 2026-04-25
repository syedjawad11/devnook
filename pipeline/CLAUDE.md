# DevNook Content Workspace — Claude Session Log

> Content pipeline for devnook.dev. Always read this file first. Astro site lives at `../devnook/`.

## Session start — do NOT auto-read these files

Unless explicitly asked, do not open drafts, registry.db directly, or session history logs.

---

## Workspace Overview

This workspace owns the full content pipeline for devnook.dev:
- **Planner** — keyword discovery → registry (status=queued)
- **Writer** — queued posts → `agents/content-team/drafts/{slug}.md` (status=drafted)
- **Ingest** — `../web_content/output/` → drafts (antigravity, status=drafted)
- **Antigravity QA** — fixes + approves antigravity drafts (status=approved)
- **Publisher** — staged posts → `../devnook/src/content/` + git commit + push

The Astro site repo is at `../devnook/`. No content pipeline code lives there.

---

## Subagent Architecture

```
ORCHESTRATOR (Sonnet main session)
  ├── Planner   (Haiku)  — agents/subagent-prompts/planner.md
  ├── Writer    (Sonnet) — agents/subagent-prompts/writer.md
  ├── Ingest    (Haiku)  — agents/subagent-prompts/ingest.md
  ├── Antigravity QA (Sonnet) — agents/subagent-prompts/antigravity-qa.md
  └── Publisher (Haiku)  — agents/subagent-prompts/publisher.md
```

Orchestrator spawns subagents via `Agent()` tool. No Python LLM calls anywhere.

---

## Workflow Patterns

**Workflow A — weekly programmatic content:**
Planner → Ingest (parallel) → Writer (batch=5) → Publisher

**Workflow A2 — antigravity (web-scraped) content:**
Ingest (from `../web_content/output/`) → Antigravity QA (batch=10) → Publisher

**Workflow D — status check:**
Inline sqlite3 query (no subagent needed)

---

## Key Paths

| Path | Purpose |
|------|---------|
| `agents/content-team/registry.db` | SQLite registry (36 published / 12 staged / 10 rejected as of 2026-04-25) |
| `agents/content-team/registry.py` | DB helpers — get_db, update_post_status, get_queued_posts, get_published_slugs, log_pipeline_run, get_next_template |
| `agents/content-team/drafts/` | Writer output, QA-approved posts |
| `agents/content-team/staging.py` | Moves approved drafts → content-staging/ |
| `agents/content-team/templates/` | Post template files (lang-v1 through v5, guide-v1 through v4, etc.) |
| `agents/publish/publish.py` | Drip publisher — moves content-staging/ → ../devnook/src/content/, updates registry, pings GSC, commits+pushes devnook |
| `agents/publish/gsc_ping.py` | Google Search Console Indexing API |
| `content-staging/` | Staging area (FIFO queue, oldest-mtime-first) |
| `agents/subagent-prompts/` | Subagent prompt files |
| `agents/skills/` | Shared skill files (SEO rules, brand voice, content schema, QA criteria) |
| `../web_content/output/` | Antigravity ingest source |
| `../devnook/src/content/` | Published content destination |

---

## Registry Schema (key columns)

```sql
posts (
  slug TEXT PRIMARY KEY,
  title TEXT,
  description TEXT,
  category TEXT,          -- blog, guides, cheatsheets, languages, tools
  language TEXT,          -- for languages category only
  concept TEXT,
  template_id TEXT,
  keyword TEXT,
  opportunity_score REAL,
  status TEXT,            -- queued → drafted → approved → staged → published (or rejected)
  content_type TEXT,      -- programmatic | editorial | antigravity
  source TEXT,
  qa_status TEXT,
  file_path TEXT,
  published_at TEXT,
  published_date TEXT,
  created_at TEXT,
  updated_at TEXT,
  staged_at TEXT
  -- + ~6 more SEO/meta columns
)
```

---

## Important Rules

| Rule | Impact |
|------|--------|
| Antigravity QA never rejects | Trusted Gemini content; QA fixes structural/SEO only, always sets qa_status='passed', word range 1500–2500 |
| Languages category owned by Antigravity | Planner + Writer must never queue languages posts |
| Publisher staging query uses `status IN ('staged')` | Use `staging.py` to move approved → staged before publishing |
| `publish.py` uses `shutil.move()` | Deletes from content-staging/ on move; content-staging/ MUST be in `git add` in CI workflows |
| Related posts not written by agents | PostLayout.astro auto-derives related list at render time. Agents must NOT write `## Related` sections. `strip_related_section()` in publish.py is the safety net. |
| `related_posts` frontmatter field unused | Leave as `[]` in all new drafts |
| No API-based Python LLM calls | All LLM work goes through Agent() subagent invocations; no llm_router, no anthropic SDK in Python |

---

## Environment Variables

```bash
GOOGLE_SERVICE_ACCOUNT_JSON=...    # GSC Indexing API — GitHub Actions secret
DEVNOOK_REPO_PAT=...               # PAT with write access to devnook repo — GitHub Actions secret
GH_PAT=...                         # PAT for content workspace CI commits
```

---

## How to Run

```bash
# Status check
python -c "import sqlite3; db=sqlite3.connect('agents/content-team/registry.db'); [print(r) for r in db.execute('SELECT status, content_type, COUNT(*) FROM posts GROUP BY 1,2')]"

# Manual publish (N posts)
python agents/publish/publish.py --count N

# Stage approved drafts
python agents/content-team/staging.py

# Spawn subagent (example — Writer for 5 queued posts)
# In Claude Code session: Agent(prompt=open('agents/subagent-prompts/writer.md').read(), ...)
```

---

## CI Workflows

- `.github/workflows/drip-publish.yml` — daily 08:00 UTC cron (3 posts/day)
- `.github/workflows/on-demand-publish.yml` — manual trigger

Both workflows:
1. Checkout this content workspace (with GH_PAT)
2. Checkout devnook into `../devnook` (with DEVNOOK_REPO_PAT)
3. Run `publish.py` — publisher moves files AND commits+pushes to devnook
4. Commit content-staging/ deletions + registry.db changes to this repo

---

## Last Session (2026-04-25, #27)

**Status:** ✅ Workspace split complete. Content pipeline migrated from devnook/ into this dedicated workspace.

### What was done
- Created `devnook_content_workspace/` with fresh `git init`
- Copied all pipeline files (content-team, publish, subagent-prompts, skills, workflows, content-staging)
- Excluded LLM-caller Python files (`*_agent.py`, `llm_router.py`, `gemini_client.py`, `build-tool.py`)
- Fixed `registry.py` DB_PATH (simplified to `Path(__file__).parent / "registry.db"`)
- Fixed `staging.py` import (now imports registry directly from same directory)
- Fixed `publish.py`: CONTENT_DIR now points to `../devnook/src/content/`; added cross-repo git block
- Updated both CI workflows: added devnook checkout step, updated pip path, removed src/content from CI git add
- Also done earlier in session 27: related-posts auto-derivation fix in PostLayout.astro + strip_related_section() in publish.py

### Migration status (session 27 end state)

Phases 1–5 complete. Two phases remain before the split is fully live:

- **Phase 6 (point of no return)** — `git rm -r` pipeline dirs from devnook once CI is confirmed working
- **Phase 7** — create private GitHub repo for this workspace, push initial commit, add secrets

### Next session priorities (#28)

1. **Phase 7 — Wire up CI**: create private GitHub repo, `git add` + initial commit, push, add secrets: `GOOGLE_SERVICE_ACCOUNT_JSON`, `DEVNOOK_REPO_PAT`, `GH_PAT`
2. **Phase 6 — Clean devnook**: after CI is confirmed, `git rm -r agents/content-team agents/publish agents/utils agents/tools-team agents/dev-team content-staging templates` in devnook; commit + push
3. **Verify first automated drip** — confirm drip-publish.yml commits devnook content AND content-staging deletions in the two-repo flow
4. **Monitor queue drain** — 12 staged at 3/day drains ~2026-05-09
5. **Next antigravity batch** — after queue drains

### Registry state
- 36 published / 12 staged / 10 rejected as of 2026-04-25
- One stale registry entry fixed: `python-file-handling-tutorial` was stuck as "staged" but already live; corrected to "published"
