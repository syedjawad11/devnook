# DevNook Content Workspace

> Content pipeline for devnook.dev. Always read this file first.
> Astro site lives at `../devnook/`. Architecture details → `../devnook/docs/ARCHITECTURE.md`.

## Session start

Do not open drafts, `data/registry.db` directly, or session history logs unless explicitly asked.

---

## TODO (session #66, 2026-05-29)

1. **Stage 14 next** — Editorial content queue: pick best 10–20 from `editorial_opportunity` primary tier (252 keywords) and queue into `posts` for writing via `pipeline.core.runner`.
2. **Pipeline B routine DISABLED** — `keyword_set_id=6` (`git-commands-cheat-sheet-developers`) conflicts with `/cheatsheets/git-commands-cheatsheet`. Decide: (a) update existing cheatsheet, (b) repurpose cluster, or (c) delete id=6 and re-seed. Re-enable routine after a `keyword_sets` row with `status='ready'` is confirmed.
3. **GSC ping not wired** — `GOOGLE_SERVICE_ACCOUNT_JSON` secret needs to be set in GitHub Actions repo secrets (`syedjawad11/devnook`). See `agents/publish/gsc_ping.py`.
4. **Editorial language rule** — Never queue Python/JS/TS language syntax topics as editorial content. Those belong to `/languages/` programmatic section. Python + JS/TS clusters already skipped in `editorial_opportunity`.

---

## Workspace Overview

This workspace owns the full content pipeline for devnook.dev:

- **Pipeline B** — keyword-first, cluster-driven: Stage 0 (harvest) → Stage 1 (keywords) → Stage 2 (write) → Stage 3 (QA+publish)
- **SEO Optimizer** — rewrites published articles using DataForSEO keyword research
- **Publisher** — staged posts → `../devnook/src/content/` + git push

---

## Subagent Architecture

```
ORCHESTRATOR (Sonnet main session)
  ├── @pipeline-b-orchestrator-v2   — .claude/agents/pipeline-b-orchestrator-v2.md
  ├── @pipeline-b-stage0            — .claude/agents/pipeline-b-stage0-harvest-cluster.md  [LOCAL ONLY]
  ├── @pipeline-b-stage1            — .claude/agents/pipeline-b-stage1-keywords.md
  ├── @pipeline-b-stage2            — .claude/agents/pipeline-b-stage2-writer.md
  ├── @pipeline-b-stage3            — .claude/agents/pipeline-b-stage3-qa-publish.md
  ├── @content-planner              — .claude/agents/content-planner.md
  ├── @content-writer               — .claude/agents/content-writer.md
  ├── @content-publisher            — .claude/agents/content-publisher.md
  ├── @gsc-analyst                  — .claude/agents/gsc-analyst.md
  └── @seo-optimizer                — .claude/agents/seo-optimizer.md
```

Invoke via `@agent-name` in Claude Code session. No Python spawning needed.

---

## MCP Servers

| Server | Purpose |
|--------|---------|
| dataforseo | Keyword research, search volume, SERP analysis |
| gsc | Google Search Console — impressions, clicks, quick_wins |

---

## Workflow Patterns

**Pipeline B — daily AI/Productivity/Comparisons articles:**
`@pipeline-b-orchestrator-v2` — cluster selection → Stage 1 keywords → Stage 2 write → Stage 3 QA+publish

**Pipeline B manual stage run:**
`@pipeline-b-stage1 CLUSTER_ID=<id>` → `@pipeline-b-stage2 KEYWORD_SET_ID=<id>` → `@pipeline-b-stage3 KEYWORD_SET_ID=<id>`

**Stage 0 (keyword harvest — LOCAL ONLY, never CCR):**
`@pipeline-b-stage0` — harvests DataForSEO via MCP, clusters, scores viability, writes to DB

**Workflow E — SEO rewrite (on-demand):**
Pick slug from `data/rewrite-queue.json` → `@seo-optimizer SLUG=...` → verify build → commit+push

**NOTE:** GSC quick_wins is NEVER used in Workflow E. All language articles are rewritten regardless of GSC performance.

---

## Key Paths

| Path | Purpose |
|------|---------|
| `data/registry.db` | SQLite registry — single source of truth |
| `data/sqldump.sql` | Human-readable schema dump (committed alongside DB) |
| `data/pipeline-b-runs.log` | Pipeline B run log (JSONL) |
| `data/pipeline-b-seed-buckets.json` | Seed buckets for Stage 0 keyword harvest |
| `data/rewrite-queue.json` | SEO rewrite queue — all published language articles |
| `.claude/agents/` | Native subagent prompt files (tracked in git) |
| `agents/publish/publish.py` | Drip publisher — moves staging → devnook, commits, pushes |
| `agents/publish/gsc_ping.py` | Google Search Console Indexing API |
| `agents/skills/content-style-system.md` | Single source of truth — 720 lines: templates, voices, SEO rules, frontmatter spec |
| `agents/skills/seo-writing-rules.md` | SEO writing rules |
| `agents/skills/qa-rejection-criteria.md` | QA rejection criteria |
| `content-staging/` | Staging queue (FIFO, registry insertion order) |
| `../devnook/src/content/` | Published content destination |

---

## Registry Schema (key columns)

See `../site/docs/ARCHITECTURE.md` for full schema including `clusters`, `keyword_pool`, `keyword_sets`.

```sql
posts (
  slug TEXT PRIMARY KEY,
  title TEXT,
  description TEXT,
  category TEXT,          -- blog | guides | cheatsheets | languages | tools
  language TEXT,
  concept TEXT,
  template_id TEXT,
  keyword TEXT,
  status TEXT,            -- queued → outlined → drafted → linked → approved → published | rejected
  content_type TEXT,      -- programmatic | editorial
  source TEXT,
  published_at TEXT,
  published_date TEXT
)
```

---

## Important Rules

| Rule | Impact |
|------|--------|
| `content-style-system.md` is single source of truth | All writing agents must read it before writing. Approved voices: terse-senior, thoughtful-explainer, tutorial-guide. |
| Pipeline B 2,500-word hard floor | QA hard-fail below 2,500 words |
| No `## Related` sections in post body | PostLayout.astro auto-derives related list. `strip_related_section()` in publish.py is the safety net. |
| `pipeline/core/` uses Anthropic API directly | `outline.py` and `write.py` call `anthropic.Anthropic()`. Requires `ANTHROPIC_API_KEY`. Agent prompts still used for ad-hoc work. |
| Meta description minimum 120 chars | Always verify with `len()` — agent self-reported counts unreliable |
| Frontmatter values with `: ` must be quoted | Colon+space in unquoted values breaks YAML parse at Astro build time |
| No H1 in markdown body | PostLayout.astro renders title as `<h1>`; body `# Title` = duplicate H1 |
| No `/languages/` URL fabrication | Never write a `/languages/` URL unless exact path verified from registry. Use `concept`, not filename slug. |
| External links: 1–2 per article | Zero external links = automatic QA rejection |
| `publish.py` uses `shutil.move()` | Deletes from `content-staging/` on move; `content-staging/` MUST be in `git add` in CI workflows |

---

## Environment Variables

```bash
GOOGLE_SERVICE_ACCOUNT_JSON=...    # GSC Indexing API — GitHub Actions secret
DEVNOOK_REPO_PAT=...               # PAT with write access to devnook repo — GitHub Actions secret
GH_PAT=...                         # PAT for content workspace CI commits
```

---

## Pipeline Core (Stage 9+)

`pipeline/core/` — Python modules replacing the agent-prompt pipeline tail.

Status lifecycle: `queued → outlined → drafted → linked → approved → published`

```bash
# Full pipeline run on a queued post
python -m pipeline.core.runner --slug my-slug

# Dry run (validate only — no API calls, no writes)
python -m pipeline.core.runner --slug my-slug --dry-run

# Resume from a specific stage
python -m pipeline.core.runner --slug my-slug --from-stage write

# Single stage
python -m pipeline.core.runner --slug my-slug --stage qa

# Seed a test post into the queue
python -m pipeline.core.runner --seed-post --slug test-slug \
  --title "My Title" --category blog --keyword "primary keyword" --template blog-v5
```

Run from `pipeline/` root. Requires `pip install -r requirements.txt`.

---

## How to Run

```bash
# Status check
python -c "import sqlite3; db=sqlite3.connect('data/registry.db'); [print(r) for r in db.execute('SELECT status, content_type, COUNT(*) FROM posts GROUP BY 1,2')]"

# Manual publish (N posts) — legacy drip publisher
python agents/publish/publish.py --count N
```

Subagents invoked via `@agent-name` directly in Claude Code session.

---

## CI Workflows

- `.github/workflows/drip-publish.yml` — daily 08:00 UTC cron (2 posts/day)
- `.github/workflows/on-demand-publish.yml` — manual trigger

Both workflows:
1. Checkout content workspace (GH_PAT) + devnook into `../devnook` (DEVNOOK_REPO_PAT)
2. Run `publish.py` — moves files AND commits+pushes to devnook
3. Commit `content-staging/` deletions + `data/registry.db` changes to this repo
