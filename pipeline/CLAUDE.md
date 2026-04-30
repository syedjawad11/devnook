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
| `agents/content-team/registry.db` | SQLite registry (36 published / 16 staged / 10 rejected as of 2026-04-25) |
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
| Meta description minimum 120 characters | Hard floor for all new posts. Existing SEO rule in `agents/skills/seo-writing-rules.md` (140–160 chars) already satisfies this, but the 120-char floor must be enforced by Writer + QA so no future regression occurs. Past short-meta posts have already been fixed — do not re-audit. |

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

## Last Session (2026-04-26, #30)

**Status:** ✅ Complete. Hardened both Writer and Antigravity QA subagent prompts against fabricated `/languages/` URLs.

### What was done in #30
- **Added constraint to `agents/subagent-prompts/antigravity-qa.md`** (Constraints section, after "Never fabricate internal link slugs"): agents must never write a `/languages/` URL unless the exact path appears verbatim in INTERNAL_LINKS; if not found, strip the hyperlink and leave anchor text as plain text.
- **Added constraint to `agents/subagent-prompts/writer.md`** (Constraints section, after the `## Related` constraint): agents must never write a `/languages/` URL unless the exact path appears verbatim in INTERNAL_LINKS; must not derive URLs from filenames or slugs — correct URL uses `concept` from the registry, accessible only via INTERNAL_LINKS.

### Current state after #30
- Registry unchanged: **36 published / 16 staged / 10 rejected**, 0 queued
- Staged breakdown: 12 language posts (positions 1–12) + 4 cheatsheets (positions 13–16)
- Drip cron (08:00 UTC, 3/day) continues publishing — no manual action needed

### Key rules established / confirmed in #30
- `/languages/` URLs in body prose are only allowed if the exact path is in INTERNAL_LINKS — applies to both Writer and Antigravity QA
- Antigravity QA strips any non-verified `/languages/` hyperlink (anchor text kept); Writer must not derive them at all

### What was done in #31
- **Fixed `validate_language_links()` blind spot** in `agents/publish/publish.py`: added a second regex (`single_re`) that catches and flags malformed single-segment `/languages/{anything}` paths (e.g. `/languages/how-to-handle-error-in-rust`) which previously bypassed the guard entirely. Publisher now runs two passes: single-segment check (always flagged) then two-segment registry check (existing logic).

## Last Session (2026-04-30, #34)

**Status:** ✅ Complete. Fixed broken `/languages/` links blocking the drip queue; pipeline unblocked.

### What was done in #34
- **Diagnosed Apr 29 & Apr 30 drip failures**: 4 of 7 staged posts contained broken `/languages/{lang}/{concept}` cross-references to posts not yet in the registry. The FIFO queue always served these 4 posts first (tied oldest mtime), so every cron run picked 3 broken posts, all 3 failed `validate_language_links()`, and zero posts were published.
- **Fixed 4 staged files** — stripped 9 broken hyperlinks while preserving anchor text (per antigravity-qa.md rule). Also corrected a `list-comprehensions` → `list-comprehension` plural typo in the dictionary comprehension post that pointed to a rejected (404) concept.
  - `content-staging/languages/how-to-use-destructuring-in-javascript.md` — stripped `spread-operator`, `arrow-functions` links
  - `content-staging/languages/how-to-use-interfaces-in-go.md` — stripped `structs`, `error-handling`, `concurrency` links
  - `content-staging/languages/how-to-use-pattern-matching-in-rust.md` — stripped `rust/error-handling`, `python/match-statement`, `go/type-switch` links
  - `content-staging/languages/python/how-to-do-dictionary-comprehension-in-python.md` — fixed `list-comprehension` URL, stripped `generators` link
- **Committed and pushed** fix to `devnook-content` repo (`253e9d2`).

### Current state after #34
- Registry: **45 published / 7 staged / 10 rejected**, 0 queued
- All 7 staged posts now pass validator; drip cron will resume normally at 08:00 UTC May 1
- Queue empties after ~May 2 (7 posts ÷ 3/day)

### Next session priorities
- Run Planner → Writer to refill staging queue (queue empties ~May 2)
- Future improvement (out of scope today): `validate_language_links()` should filter by `status='published'` so rejected/staged concepts can't be linked to

---

## Last Session (2026-04-29, #33)

**Status:** ✅ Complete. Fixed overly aggressive language link validator and registry desync; pipeline unblocked.

### What was done in #33
- **Diagnosed Apr 29 drip failure**: All 7 remaining staged posts were skipped because `validate_language_links()` `single_re` (added in #31) incorrectly flagged valid language category landing page links (`/languages/go`, `/languages/python`, etc.) as malformed single-segment paths.
- **Fixed `validate_language_links()` in `agents/publish/publish.py`**: `single_re` now only flags single-segment paths that contain a hyphen — language names are never hyphenated but post slugs always are. Valid category links like `/languages/go` pass through cleanly.
- **Fixed registry desync**: 4 posts published Apr 25–26 were stuck in `staged` status due to `registry.db` not persisting in those CI commits. Updated to `published`: `how-to-check-regex-pattern-in-javascript`, `how-to-do-file-handling-in-google-colab`, `how-to-parse-json-in-ruby`, `how-to-use-environment-variables-in-rust`.
- **Committed and pushed** both fixes to `devnook-content` repo (`6aa0a54`).

### Current state after #33
- Registry: **45 published / 7 staged / 10 rejected**, 0 queued
- 7 staged posts drain: Apr 30 (3) + May 1 (3) + May 2 (1)
- Queue empty after May 2

### Next session priorities
- Run Planner → Writer to refill staging queue before May 2 (queue empties that day)
