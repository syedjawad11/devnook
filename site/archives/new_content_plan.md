# Content Pipeline Split — DevNook ↔ Antigravity

## Context

DevNook's current content pipeline (`agents/content-team/`) runs all 6 steps — keyword, planner, writer, seo, qa, staging — through a single SQLite registry and a single Claude Sonnet writer. The volume engine is the 50-concept × 12-language matrix (~600 programmatic posts), and running all of that through our local writer is both slow and expensive.

The user has already stood up an Antigravity sandbox at [../web_content/](../web_content/) (fully outside this repo) with its own `local_registry.db`, its own `content_team/keyword_agent.py` + `writer_agent.py` + `seo_optimizer.py`, its own `templates/language-post/`, and a running tally in `pipeline_memory.md`. Five pSEO markdown files have already been produced and are sitting in [../web_content/output/](../web_content/output/), waiting to be ingested.

The goal of this refactor is to firewall DevNook's pipeline so it **only handles editorial** work (guides, blog, cheatsheets, tools), and add a new **ingest** step that pulls Antigravity's `output/*.md` into DevNook's drafts/registry so the existing seo → qa → staging tail runs unchanged on both content streams. Antigravity's internals are out of scope — the contract between the two systems is solely the markdown files in `web_content/output/` and their frontmatter.

### Confirmed decisions (user, 2026-04-15)
1. **Drop `languages` category from DevNook's writer entirely.** Clean firewall, no race.
2. **Trim DevNook's keyword seed matrix to editorial rings only** (Ring 1 tool-adjacent, Ring 2 web fundamentals, Ring 4 AI/editorial). Language × concept seeds removed.
3. **Ingested Antigravity files still run through DevNook's `seo_optimizer.py`** so the registry-driven internal linking layer applies uniformly.
4. **Slug collisions on ingest → skip + log.** No silent overwrites.

---

## Architecture after refactor

```
DevNook side (agents/content-team/run-pipeline.py)
  keyword  → editorial seeds only
  planner  → editorial categories only
  writer   → editorial only (guides/blog/cheatsheets/tools)
  ingest   → NEW: reads ../web_content/output/*.md, writes drafts + registry rows
  seo      → runs on BOTH editorial drafts and ingested pSEO files
  qa       → runs on BOTH
  staging  → moves approved files into content-staging/

Antigravity side (../web_content/, out-of-repo, already operational)
  keyword → planner → writer → seo_optimizer → drops .md into output/
  Uses its own local_registry.db and pipeline_memory.md
  Zero coupling with DevNook's registry; the only handoff is files in output/
```

---

## Implementation steps

### Step 1 — Add `content_type` + `source` columns to registry
**File:** [agents/content-team/registry-schema.sql](agents/content-team/registry-schema.sql), [agents/content-team/registry.db](agents/content-team/registry.db)

- Add to `posts` table:
  - `content_type TEXT CHECK(content_type IN ('editorial','programmatic'))` — default `'editorial'`
  - `source TEXT CHECK(source IN ('claude_code','antigravity'))` — default `'claude_code'`
- Write an idempotent migration at the top of `registry.db` initialization (or a one-off `migrate.py`) that does `ALTER TABLE posts ADD COLUMN ... IF NOT EXISTS` via `PRAGMA table_info` check.
- Backfill existing rows: `content_type = 'programmatic'` where `category = 'languages'`, `'editorial'` otherwise; `source = 'claude_code'` for all.

**Why:** gives us a clean filter for writer/ingest branching and an audit trail in PIPELINE_LOG.md. Needed before Step 4 can filter the writer queue cleanly.

### Step 2 — Trim keyword seed matrix to editorial only
**File:** [agents/content-team/keyword_agent.py](agents/content-team/keyword_agent.py) (SEED_TOPICS dict at line 27)

- Delete the `concepts` / per-language sub-dict entirely from SEED_TOPICS.
- Keep `tool_adjacent`, `guides` (Ring 1/2), and whatever Ring 4 AI/editorial seeds exist.
- Leave the `fetched_seeds` cache table alone — old language rows stay cached, just won't be re-queried.
- Add a short comment at the top of SEED_TOPICS explaining the split: `# Programmatic lang×concept seeds live in ../web_content/content_team/keyword_agent.py`

**Why:** prevents DevNook from ever scoring or queuing a language×concept keyword again. Antigravity owns that seed space.

### Step 3 — Gate planner by category
**File:** [agents/content-team/planner_agent.py](agents/content-team/planner_agent.py) (CLASSIFY_PROMPT at line 43, insert-post logic at line 150)

- In the CLASSIFY_PROMPT, drop `languages` from the allowed `category` enum so the LLM can't classify into it.
- In the insert loop, if a row somehow still comes back with `category = 'languages'`, skip it and log to PIPELINE_LOG.md.
- Set `content_type = 'editorial'` and `source = 'claude_code'` on every insert.

**Why:** second line of defense — even if a language×concept keyword leaks through Step 2, the planner refuses to queue it.

### Step 4 — Gate writer by content_type
**File:** [agents/content-team/writer_agent.py](agents/content-team/writer_agent.py) (queue read near line 40, run loop around line 132)

- Change the queued-post query to `WHERE status='queued' AND content_type='editorial'`.
- No other changes — writer logic stays exactly the same for the four remaining categories.
- Remove the `languages` entry from `_TYPE_MAP` (line 47-53) since it's now unreachable. Leave the template folder on disk (Antigravity uses it — it lives outside this repo, so it's already separate anyway).

**Why:** even if Steps 2–3 both fail, writer_agent physically cannot pick up a programmatic row.

### Step 5 — New `ingest_agent.py`
**New file:** `agents/content-team/ingest_agent.py`

Reusing patterns from [agents/content-team/staging.py](agents/content-team/staging.py) (file-move loop, status transition) and [agents/content-team/writer_agent.py](agents/content-team/writer_agent.py) (frontmatter parsing via `python-frontmatter`, draft write path).

**Contract:**
- Input: `../web_content/output/*.md` (path resolved relative to repo root).
- Output: file copied to `agents/content-team/drafts/{slug}.md` + row inserted into `posts` with `status='drafted'`, `content_type='programmatic'`, `source='antigravity'`.

**Frontmatter mapping** (sample verified from [../web_content/output/how-to-parse-json-in-javascript.md](../web_content/output/how-to-parse-json-in-javascript.md)):
| Antigravity field | DevNook `posts` column |
|---|---|
| filename stem | `slug` |
| `title` | `title` |
| `description` | `description` |
| `language` | `language` |
| `concept` | `concept` |
| `template_id` | `template_id` |
| — (hardcoded) | `category = 'languages'` |
| — (hardcoded) | `content_type = 'programmatic'` |
| — (hardcoded) | `source = 'antigravity'` |
| — (hardcoded) | `status = 'drafted'` |
| `published_date` | — (ignored; staging.py sets `staged_at`) |
| `keyword` | synthesize from title if absent |

**Slug collision handling** (per user decision):
- Before insert, `SELECT id, status FROM posts WHERE slug = ?`. If hit: skip the file (do not copy, do not insert), append a line to PIPELINE_LOG.md with slug + existing status + Antigravity filename. Continue with next file.

**Run contract** (mirrors other agents so run-pipeline.py can wire it up uniformly):
```python
def run() -> dict:
    # returns {"processed": int, "ingested": int, "skipped_collision": int,
    #          "model_used": None, "tokens": 0, "cost": 0.0}
```

- Deletion policy: after a successful copy, move the sandbox file from `web_content/output/` to `web_content/output/_ingested/{slug}.md` so the next run doesn't re-scan it. Do NOT delete — the user may want Antigravity's pipeline_memory.md and the sandbox archive to line up.

### Step 6 — Wire ingest into the orchestrator
**File:** [agents/content-team/run-pipeline.py](agents/content-team/run-pipeline.py) (`run_step` at line 43, CLI parsing, STEPS order)

- Add `ingest` to the valid steps list, positioned **after** `writer` and **before** `seo`.
- New `--steps all` sequence: `keyword,planner,writer,ingest,seo,qa,staging`.
- Log the ingest run into `pipeline_runs` using the same pattern as other steps (line 69-81) — `processed`, `model_used=None`, `tokens=0`, `cost=0`.
- Ensure `--steps writer,seo,qa,staging` still works unchanged for people who want to skip ingest.

**Why ingest before seo (not after writer-only):** user confirmed they want DevNook's `seo_optimizer.py` to run on Antigravity output so the registry-driven internal link insertion is uniform across both streams. Putting ingest between writer and seo means both drafts (editorial + programmatic) land in the same `drafts/` directory and seo_optimizer picks them all up with no code changes on its side.

### Step 7 — Verify seo/qa/staging are content_type-agnostic
**Files read-only check:** [agents/content-team/seo_optimizer.py](agents/content-team/seo_optimizer.py), [agents/content-team/qa_agent.py](agents/content-team/qa_agent.py), [agents/content-team/staging.py](agents/content-team/staging.py)

- Confirm none of them filter by `category='languages'` in a way that would exclude programmatic (the explore pass suggests they're all category-agnostic — verify once before shipping).
- In particular: `qa_agent.py` has per-category word-count minimums (languages=1000). Check that `languages` is still in that map — we want ingested pSEO posts to hit the 1000-word bar.
- `staging.py` path logic (line 32) already routes `languages` → `content-staging/languages/{lang}/`. Leave as-is.

**No code changes expected here.** If anything is broken, fix it in a follow-up rather than bundling with this refactor.

### Step 8 — Docs + CLAUDE.md update
**Files:** [CLAUDE.md](CLAUDE.md), [agents/content-team/DECISIONS.md](agents/content-team/DECISIONS.md)

- CLAUDE.md "Agent Architecture Quick Reference" diagram: add the ingest step to the 6 → 7 step pipeline. Add a one-liner under "Important Decisions Log" noting the Antigravity split.
- DECISIONS.md: append a dated entry capturing the 4 user decisions above and the frontmatter mapping contract (Step 5 table).
- `run-pipeline.py` table in CLAUDE.md ("How to Run Agents"): add `"run ingest"` → `python agents/content-team/run-pipeline.py --steps ingest` row.

---

## Critical files touched

| File | Role | Change type |
|---|---|---|
| [agents/content-team/registry-schema.sql](agents/content-team/registry-schema.sql) | DB schema | ADD columns |
| [agents/content-team/registry.db](agents/content-team/registry.db) | DB file | migrate + backfill |
| [agents/content-team/keyword_agent.py](agents/content-team/keyword_agent.py) | Step 1 | trim SEED_TOPICS |
| [agents/content-team/planner_agent.py](agents/content-team/planner_agent.py) | Step 2 | drop languages from allowed categories |
| [agents/content-team/writer_agent.py](agents/content-team/writer_agent.py) | Step 3 | filter queue by content_type |
| `agents/content-team/ingest_agent.py` | Step 4 (NEW) | NEW FILE |
| [agents/content-team/run-pipeline.py](agents/content-team/run-pipeline.py) | Orchestrator | add ingest step |
| [CLAUDE.md](CLAUDE.md) | Docs | update architecture diagram + run commands |
| [agents/content-team/DECISIONS.md](agents/content-team/DECISIONS.md) | Docs | append decision entry |

Untouched (verified safe): `seo_optimizer.py`, `qa_agent.py`, `staging.py`, `llm_router.py`, `utils/registry.py`.

---

## Verification plan

**After Step 1 (schema):**
```bash
python -c "import sqlite3; db=sqlite3.connect('agents/content-team/registry.db'); \
  print([r for r in db.execute('PRAGMA table_info(posts)') if r[1] in ('content_type','source')]); \
  print(list(db.execute('SELECT content_type, source, COUNT(*) FROM posts GROUP BY 1,2')))"
```
Expect both new columns present and backfill counts nonzero.

**After Steps 2-4 (editorial firewall):**
```bash
python agents/content-team/run-pipeline.py --steps keyword,planner
# Then:
python -c "import sqlite3; db=sqlite3.connect('agents/content-team/registry.db'); \
  print(list(db.execute(\"SELECT category, COUNT(*) FROM posts WHERE status='queued' GROUP BY category\")))"
```
Expect zero rows in `languages` category.

**After Step 5 (ingest agent, dry run):**
```bash
python agents/content-team/run-pipeline.py --steps ingest
```
Expect:
- 5 files moved from `../web_content/output/` → `../web_content/output/_ingested/`
- 5 new rows in `posts` with `status='drafted'`, `content_type='programmatic'`, `source='antigravity'`, `category='languages'`
- 5 markdown files now in `agents/content-team/drafts/`
- PIPELINE_LOG.md has an ingest batch entry

**After Step 6 (full pipeline):**
```bash
python agents/content-team/run-pipeline.py --steps ingest,seo,qa,staging
```
Expect all 5 ingested posts flow through to `content-staging/languages/{lang}/` with `status='staged'`.

**Collision test:**
- Re-run `--steps ingest` on an already-ingested batch (drop a duplicate file back into `output/` by hand). Expect: 0 processed, 1 skipped_collision, PIPELINE_LOG.md has a collision entry, no DB mutation.

**Rollback:**
- Schema migration is additive only; no destructive changes. If the refactor needs to be reverted, `git revert` the commit and the two new columns stay in the DB harmlessly. The `ingest_agent.py` file can be deleted without side effects.

---

## Out of scope (deferred)

- Any changes inside `../web_content/` — Antigravity owns its own code.
- Schema sync between `local_registry.db` and `registry.db`. Handoff is markdown files only, deliberately.
- Adding programmatic keyword discovery back to DevNook for cross-checking Antigravity coverage — future "coverage gap" report can query both DBs externally.
- GitHub Actions drip-publish wiring (separate workstream per CLAUDE.md "Next session priorities").
- The Antigravity sandbox's own seo_optimizer vs DevNook's — both will run in sequence per user decision 3. If we later find double-optimization is harmful, revisit.
