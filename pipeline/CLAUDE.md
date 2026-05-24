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
- **GSC Analyst** — Google Search Console data analysis, quick_wins ranking
- **SEO Optimizer** — rewrites published articles using DataForSEO keyword research + content-style-system.md

The Astro site repo is at `../devnook/`. No content pipeline code lives there.

---

## Subagent Architecture

```
ORCHESTRATOR (Sonnet main session)
  ├── @content-planner   (Haiku)   — .claude/agents/content-planner.md
  ├── @content-writer    (Sonnet)  — .claude/agents/content-writer.md
  ├── @content-ingest    (Haiku)   — .claude/agents/content-ingest.md
  ├── @antigravity-qa    (Sonnet)  — .claude/agents/antigravity-qa.md
  ├── @content-publisher (Haiku)   — .claude/agents/content-publisher.md
  ├── @gsc-analyst       (Sonnet)  — .claude/agents/gsc-analyst.md
  └── @seo-optimizer     (Sonnet)  — .claude/agents/seo-optimizer.md
```

Invoke via `@agent-name` in Claude Code session (native subagent syntax). No `Agent(prompt=open(...))` spawning needed.

---

## MCP Servers

Configured in `.mcp.json` and `.claude/settings.json`:

| Server | Purpose |
|--------|---------|
| dataforseo | Keyword research, search volume, SERP analysis |
| gsc | Google Search Console — impressions, clicks, quick_wins |

---

## Workflow Patterns

**Workflow A — weekly programmatic content:**
`@content-planner` → `@content-ingest` (parallel) → `@content-writer` (batch=5) → `@content-publisher`

**Workflow A2 — antigravity (web-scraped) content:**
`@content-ingest` (from `../web_content/output/`) → `@antigravity-qa` (batch=10) → `@content-publisher`

**Workflow D — status check:**
Inline sqlite3 query (no subagent needed)

**Workflow E — SEO rewrite (on-demand):**
Pick slug from `data/rewrite-queue.json` → `@seo-optimizer SLUG=...` → verify build → commit+push

**NOTE**: GSC quick_wins is NEVER used in Workflow E. All language articles are rewritten regardless of GSC impressions/clicks. The goal is semantic SEO coverage across all articles, not filtering by GSC performance.

---

## Key Paths

| Path | Purpose |
|------|---------|
| `agents/content-team/registry.db` | SQLite registry (~74+ published as of session #50) |
| `agents/content-team/registry.py` | DB helpers — get_db, update_post_status, get_queued_posts, get_published_slugs, log_pipeline_run, get_next_template |
| `agents/content-team/drafts/` | Writer output, QA-approved posts |
| `agents/content-team/staging.py` | Moves approved drafts → content-staging/ |
| `agents/content-team/templates/` | Post template files (lang-v1 through v5, guide-v1 through v4, etc.) |
| `agents/publish/publish.py` | Drip publisher — moves content-staging/ → ../devnook/src/content/, updates registry, pings GSC, commits+pushes devnook |
| `agents/publish/gsc_ping.py` | Google Search Console Indexing API |
| `agents/skills/content-style-system.md` | **Single source of truth** — 720 lines: 18 language section templates, 3 approved voices, forbidden language, SEO rules, frontmatter spec |
| `agents/skills/seo-writing-rules.md` | SEO writing rules (superseded by content-style-system.md for language posts) |
| `agents/skills/devnook-brand-voice.md` | Brand voice guidelines |
| `agents/skills/content-schema.md` | Content schema reference |
| `agents/skills/qa-rejection-criteria.md` | QA rejection criteria |
| `content-staging/` | Staging area (FIFO queue, oldest-mtime-first) |
| `data/rewrite-queue.json` | Registry-driven SEO rewrite queue — all published language articles, processed on-demand by @seo-optimizer |
| `.claude/agents/` | Native subagent prompt files (7 agents) — **now tracked in git** (session #52); `settings.json` remains gitignored (contains credentials) |
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
| `content-style-system.md` is the single source of truth | All writing agents and QA agents must read it before writing. Approved voices: terse-senior, thoughtful-explainer, tutorial-guide. Banned: opinionated-commentator, empathetic-debugger. |
| Antigravity QA never rejects | Trusted Gemini content; QA fixes structural/SEO only, always sets qa_status='passed', word range 1500–2500 |
| Languages category owned by Antigravity | Planner + Writer must never queue languages posts |
| Publisher staging query uses `status IN ('staged')` | Use `staging.py` to move approved → staged before publishing |
| `publish.py` uses `shutil.move()` | Deletes from content-staging/ on move; content-staging/ MUST be in `git add` in CI workflows |
| Related posts not written by agents | PostLayout.astro auto-derives related list at render time. Agents must NOT write `## Related` sections. `strip_related_section()` in publish.py is the safety net. |
| `related_posts` frontmatter field unused | Leave as `[]` in all new drafts |
| No API-based Python LLM calls | All LLM work goes through native `@agent-name` subagent invocations; no llm_router, no anthropic SDK in Python |
| Meta description minimum 120 characters | Hard floor for all new posts. SEO rule in `agents/skills/seo-writing-rules.md` (140–160 chars) already satisfies this. Always verify with `len()` — agent self-reported counts are unreliable. |
| Frontmatter values with `: ` must be quoted | Any frontmatter value containing colon+space (e.g. description) must be wrapped in double quotes to avoid YAML parse errors at Astro build time. |
| No H1 in markdown body | PostLayout.astro renders `frontmatter.title` as `<h1>`. A body `# Title` creates a duplicate H1 — Ahrefs flags it. |
| Internal links — no `/languages/` URL fabrication | Agents must never write a `/languages/` URL unless the exact path is verified from INTERNAL_LINKS or registry. Never derive URLs from filenames. |
| External links required — 1–2 per article | Every article must contain 1–2 external links to authoritative sources. Priority order: MDN (JS/CSS/Web APIs) → official language docs (Python, Node.js, Rust etc.) → W3C/WHATWG specs → Wikipedia (CS concepts) → reputable vendor docs (OpenAI, HuggingFace) for AI topics. Place naturally in body prose — not clustered at the end. Zero external links = automatic QA rejection. Both `content-writer.md` and `seo-optimizer.md` enforce this; `qa-rejection-criteria.md` rejects on zero. |

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
```

Subagents are invoked via `@agent-name` directly in the Claude Code session (no Python spawning needed).

---

## CI Workflows

- `.github/workflows/drip-publish.yml` — daily 08:00 UTC cron (2 posts/day as of session #36)
- `.github/workflows/on-demand-publish.yml` — manual trigger

Both workflows:
1. Checkout this content workspace (with GH_PAT)
2. Checkout devnook into `../devnook` (with DEVNOOK_REPO_PAT)
3. Run `publish.py` — publisher moves files AND commits+pushes to devnook
4. Commit content-staging/ deletions + registry.db changes to this repo

---

## Session History

### Sessions #30–#37 (2026-04-26 to 2026-05-10) — summary

- **#30**: Hardened Writer and Antigravity QA against fabricated `/languages/` URLs.
- **#31**: Fixed `validate_language_links()` to catch single-segment malformed paths (e.g. `/languages/how-to-handle-error-in-rust`).
- **#32**: (Content pipeline maintenance — details in session log.)
- **#33**: Fixed over-aggressive language link validator (single_re wrongly flagged `/languages/go`); fixed registry desync for 4 published posts.
- **#34**: Diagnosed Apr 29–30 drip failures (4 staged posts had broken links); stripped 9 broken hyperlinks from 4 staged files; pipeline unblocked.
- **#35**: Diagnosed CI non-failures (workflows were green; publisher silently skipped broken-link posts); published all 4 remaining staged posts manually.
- **#36**: Ingested 8 antigravity articles, QA'd, staged 7 (rejected 1 — SEO cannibalization). Reduced drip cron to 2/day.
- **#37**: Fixed registry desync (3 posts stuck in staged); hardened antigravity-qa.md + writer.md (trailing slash requirement, no H1 in body); ingested + QA'd + staged 15 antigravity posts.

### Sessions #38–#48 — summary

- Built and iterated on voice system: created `agents/skills/content-style-system.md` (720 lines) as single source of truth for all language post writing. Defined 3 approved voices (terse-senior, thoughtful-explainer, tutorial-guide). Banned opinionated-commentator and empathetic-debugger.
- Built `data/rewrite-queue.json` — registry-driven queue for all published language articles.
- Expanded antigravity pipeline; multiple ingest/QA/publish cycles.
- Tuned seo-writing-rules.md and brand voice files.
- Registry grew from ~59 published (post-#37) to ~67 published by #48.

### Last Session (#49, 2026-05-XX)

**Status:** ✅ Complete. GSC MCP verified end-to-end. 7 native subagents built in `.claude/agents/`.

- **GSC MCP verified**: Live site data — 15 clicks, 3,267 impressions, 0.46% CTR, avg position 29.8.
- **Built 7 subagents** in `.claude/agents/`: content-planner, content-writer, content-ingest, antigravity-qa, content-publisher, gsc-analyst, seo-optimizer.
- Old `agents/subagent-prompts/` pattern retired; all subagents now native Claude Code agents invoked via `@agent-name`.

### Last Session (#50, 2026-05-23)

**Status:** ✅ Complete. seo-optimizer pipeline tested end-to-end. `python-string-methods-cheatsheet` rewritten and live.

- **seo-optimizer end-to-end test**: Full pipeline on `python-string-methods-cheatsheet` — keyword research (DataForSEO), rewrite, build verify, commit, push.
- **Article rewritten**: 919 → 1,380 words. Primary keyword `python string methods` (vol: 2,900, diff: 59). First H2 contains keyword. 5 internal links woven in.
- **Two bugs fixed**: (1) Description over 160 chars — agent self-reported incorrectly; always verify with `len()`. (2) Unquoted description with `: ` broke YAML parse at build time.
- **Build passed** (109 pages). Commit `79e6173` pushed to `origin main`. Live at `https://devnook.dev/cheatsheets/python-string-methods-cheatsheet`.
- **rewrite-queue.json rebuilt** from registry: cancelled old 47-article batch queue, regenerated from all published language articles (47 entries, all `status: "pending"`).
- **CLAUDE.md updated** to reflect current subagent architecture, MCP servers, Workflow E, session history through #50.

### Current state after #50

- Registry: **~74 published / 15 staged / 11 rejected**, 0 queued
- Drip: 2/day — revert to 3/day once staging queue is refilled
- `data/rewrite-queue.json`: 47 language articles queued for SEO rewrite, all `status: "pending"`

### Next session priorities (#51)

1. **Scale seo-optimizer** — run `@gsc-analyst REPORT_TYPE=quick_wins`, pick top slugs from `data/rewrite-queue.json`, run `@seo-optimizer SLUG=...` batch.
2. **Deferred** — FAQPage schema validation in Google Rich Results Test; add FAQs to `meta-tag-generator`, `readme-generator`, `sitemap-generator-from-url` tools.
3. **GSC ping** — set `GOOGLE_SERVICE_ACCOUNT_JSON` secret in content workspace GitHub repo to stop "Skipping GSC ping" cron noise.

### Last Session (#51, 2026-05-23)

**Status:** ✅ Complete. Workflow E end-to-end test with new modular-v1 system. `javascript-closures` rewritten and live.

- **Workflow correction codified**: GSC quick_wins is never used in Workflow E. Correct flow: pick from `data/rewrite-queue.json` → DataForSEO keyword research → rewrite → show draft for user approval → publish. Saved as feedback memory.
- **Article rewritten**: `javascript-closures` — 1,044 → 1,258 words. `template_id: modular-v1`. Voice: `thoughtful-explainer`. Sections: open-mental-model, core-how-it-works, code-minimal, code-realistic, prac-gotchas, close-next. Primary keyword `javascript closures` (vol: 1,600, diff: 38). Fixed broken schema_org URL (was `/languages/`, now full path).
- **Build passed** (109 pages). Registry updated. `rewrite-queue.json` updated: order 5 marked done, 46 remaining.

### Last Session (#52, 2026-05-24)

**Status:** ✅ Complete. External links pipeline gap diagnosed and fixed across all agents and QA.

- **Root cause found**: `content-writer.md` had no external link instruction — new articles were written with zero external links. `qa-rejection-criteria.md` was also missing the check, so articles with zero external links passed QA silently.
- **`seo-optimizer.md`** already had external link instructions (correct) — but `content-writer.md` did not.
- **Fixes applied**:
  - `content-writer.md` — added 1–2 external link requirement to body writing rules and self-validate checklist.
  - `qa-rejection-criteria.md` — added "Zero external links" as automatic rejection condition under Content Quality.
- **Articles patched**: `python-string-methods-cheatsheet` and `javascript-closures` already had 1 external link each from seo-optimizer (meeting minimum); committed and pushed to devnook `main`. Cloudflare auto-deployed.
- **`.claude/agents/` now tracked in git**: Removed `.claude/` from `.gitignore`, replaced with `.claude/settings.json` and `.claude/settings.local.json` (credentials stay local). All 7 agent files committed and pushed to content workspace `master`.

### Current state after #52

- Registry: **~74 published / 15 staged / 11 rejected**, 0 queued
- `data/rewrite-queue.json`: 46 language articles pending SEO rewrite (`javascript-closures` done)
- Drip: 2/day — revert to 3/day once staging queue is refilled
- All pipeline agents now enforce external links; QA rejects on zero external links

### Next session priorities (#53)

1. **Continue SEO rewrites** — pick next batch from `data/rewrite-queue.json` (order 1–4 or by topic quality), run DataForSEO research, rewrite under modular-v1 system.
2. **Deferred** — FAQPage schema validation in Google Rich Results Test; add FAQs to `meta-tag-generator`, `readme-generator`, `sitemap-generator-from-url` tools.
3. **GSC ping** — set `GOOGLE_SERVICE_ACCOUNT_JSON` secret in content workspace GitHub repo to stop "Skipping GSC ping" cron noise.
