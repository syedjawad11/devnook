# Claude Code Task — Pipeline B Redesign: Keyword-First (Cluster-Driven Topics)

## Goal

Pipeline B currently runs topic-first: each row in `data/pipeline-b-topics.json` triggers a Stage 1 keyword fetch for that specific topic, and Stage 1 fails (`insufficient_keywords`) whenever the topic has no viable keyword volume. This wastes orchestrator runs on dead topics and forces us to manually curate a topic list that might or might not match SEO reality.

We're flipping it. The new flow:

1. **Stage 0 (NEW)** — harvest a large keyword pool from broad seed *buckets* (not topics), cluster the pool by semantic similarity, score each cluster, and write viable clusters to a new table. This runs occasionally (weekly or on-demand), not per-article.
2. **Stage 1 (REFACTORED)** — instead of taking `TOPIC_ID` and fetching keywords, it takes `CLUSTER_ID`, reads the already-clustered keywords, and synthesizes the topic metadata (title, slug, description). The cluster *becomes* the topic.
3. **Stages 2 and 3 — unchanged.** Their input contract is `KEYWORD_SET_ID`, and Stage 1's output still produces that. They don't care where the keyword_set came from.

The `data/pipeline-b-topics.json` file becomes obsolete and gets deleted at the end of this refactor.

---

## Required reading before you start

1. [pipelineB.md](pipelineB.md) — the current source of truth for Pipeline B. Read this first to understand what's there and what's NOT changing.
2. [.claude/agents/pipeline-b-stage1-keywords.md](.claude/agents/pipeline-b-stage1-keywords.md) — current Stage 1 agent prompt. Most of this gets rewritten.
3. [.claude/agents/pipeline-b-stage2-writer.md](.claude/agents/pipeline-b-stage2-writer.md) — Stage 2 prompt. **Do not modify** — it consumes `KEYWORD_SET_ID` and that contract stays.
4. [.claude/agents/pipeline-b-stage3-qa-publish.md](.claude/agents/pipeline-b-stage3-qa-publish.md) — Stage 3 prompt. **Do not modify.**
5. [.claude/agents/pipeline-b-orchestrator-v2.md](.claude/agents/pipeline-b-orchestrator-v2.md) — orchestrator. Will need small changes to pull from clusters instead of topics.json.
6. The DataForSEO MCP tool surface — Stage 1 already calls `keyword_suggestions` and `related_keywords`. Stage 0 will reuse the same MCP calls.

Confirm the actual current schema of `data/keywords.db` before writing migrations — the schema in pipelineB.md is described but I haven't verified column names. Inspect the live DB first.

---

## Decisions already made — take these as given

1. **Keyword thresholds stay the same as current Pipeline B:**
   - Primary: KD ≤ 30, volume ≥ 500, need ≥ 2 per cluster
   - Secondary: KD ≤ 20, volume ≥ 500, need ≥ 6 per cluster
   - Long-tail (≥ 3 words): need ≥ 1 per cluster (10–20% of final 8–12 keyword set)
   - Target final set: 8–12 keywords per article

2. **Embeddings: Gemini `text-embedding-004` (free tier).** Batched, stored as float32 BLOB in the keywords table. Do not use OpenAI embeddings.

3. **Clustering: cosine similarity, agglomerative, threshold = 0.18 cosine distance** (≈ 0.82 similarity). Module-level constant so we can tune after seeing real output.

4. **Seed buckets are broad themes, not articles.** Stored in `data/pipeline-b-seed-buckets.json`. Valid: `ai coding assistants`, `developer productivity`, `vs code`, `github actions`. Invalid (too narrow — these are articles, not buckets): `ai documentation tools`, `best vs code extensions for python`.

5. **DataForSEO budget per Stage 0 run: hard cap of $2.** Cap keywords fetched per bucket at 1,000. Dedupe against existing `keyword_pool` rows before making any API call for a known keyword.

6. **`pipeline-b-topics.json` gets deleted at the end of this refactor.** Clusters are the new queue. Orchestrator reads from the `clusters` table.

7. **Stages 2 and 3 are not touched.** If you find yourself editing them, stop — something has gone wrong with the design.

8. **Stage 0 is LOCAL ONLY**, same as current Stage 1. It uses DataForSEO MCP, which is only available in the local environment.

---

## What stays exactly the same

- All of Stage 2 (`pipeline-b-stage2-writer.md`) and its 2,500-word hard floor, voice selection, FAQ requirement, schema_org embedding, etc.
- All of Stage 3 (`pipeline-b-stage3-qa-publish.md`) including all 15 QA hard-fail checks.
- The `keyword_sets` and `keywords` tables in `data/keywords.db` — their existing columns stay. We're adding columns, not changing what's there.
- The Stage 1 output format (`STAGE1_RESULT: success / KEYWORD_SET_ID: <id> / SLUG: <slug> / ...`). Stage 2 parses this, so the contract holds.
- The topic lifecycle terminology — `keywords_ready → draft_ready → done` — but now it lives on the `clusters` row, not on a topics.json entry.

---

## Step 1 — Schema additions to `data/keywords.db`

Add via an idempotent migration. Use `PRAGMA table_info` checks; do not drop or rename anything.

```sql
-- New: raw keyword pool from Stage 0 harvest
CREATE TABLE IF NOT EXISTS keyword_pool (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  keyword         TEXT NOT NULL UNIQUE,
  volume          INTEGER NOT NULL,
  kd              REAL NOT NULL,
  intent          TEXT,
  seed_bucket     TEXT NOT NULL,
  word_count      INTEGER NOT NULL,
  embedding       BLOB,                    -- NULL until cluster phase runs
  cluster_id      INTEGER REFERENCES clusters(id),
  source          TEXT DEFAULT 'dataforseo',
  discovered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pool_cluster ON keyword_pool(cluster_id);
CREATE INDEX IF NOT EXISTS idx_pool_bucket ON keyword_pool(seed_bucket);

-- New: viable article-sized clusters
CREATE TABLE IF NOT EXISTS clusters (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  primary_keyword   TEXT NOT NULL,
  intent            TEXT,
  primary_count     INTEGER NOT NULL,
  secondary_count   INTEGER NOT NULL,
  longtail_count    INTEGER NOT NULL,
  total_volume      INTEGER NOT NULL,
  status            TEXT NOT NULL CHECK(status IN ('viable','insufficient','used')),
  used_by_slug      TEXT,                  -- set when Stage 1 consumes the cluster
  keyword_set_id    INTEGER REFERENCES keyword_sets(id),
  scored_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clusters_status ON clusters(status);

-- Add a back-reference on keyword_sets to the cluster it came from
ALTER TABLE keyword_sets ADD COLUMN cluster_id INTEGER REFERENCES clusters(id);
```

Why both `keyword_pool` and the existing `keywords` table? `keyword_pool` is the raw harvested universe (thousands of rows, most unused). `keywords` stays as the selected 8–12 per keyword_set (joined to keyword_set_id, used by Stage 2). When Stage 1 consumes a cluster, it copies the selected subset from `keyword_pool` into `keywords` with a `keyword_set_id`. This keeps Stage 2's queries unchanged.

---

## Step 2 — Seed bucket config

**New file:** `data/pipeline-b-seed-buckets.json`

```json
{
  "buckets": [
    "ai coding assistants",
    "developer productivity",
    "code review",
    "api design",
    "testing tools",
    "github actions",
    "docker",
    "vs code",
    "terminal tools",
    "deployment",
    "database tools",
    "monitoring and observability",
    "authentication",
    "web performance",
    "browser devtools"
  ],
  "max_keywords_per_bucket": 1000,
  "filters": {
    "min_volume": 500,
    "max_kd": 30
  }
}
```

The user will edit this list. Keep structure stable.

---

## Step 3 — Stage 0 agent: `pipeline-b-stage0-harvest-cluster.md`

**New file:** `.claude/agents/pipeline-b-stage0-harvest-cluster.md`

This is a LOCAL ONLY agent, same constraint as current Stage 1 (needs DataForSEO MCP).

**Invocation:**
```python
Agent(subagent_type="general-purpose",
      prompt=open(".claude/agents/pipeline-b-stage0-harvest-cluster.md").read()
             + "\n\nWORKSPACE_DIR=C:\\Users\\Syed Jawad Hassan\\Desktop\\devnook_content_workspace")
```

No TOPIC_ID input — Stage 0 processes all configured buckets in one run.

### Sub-steps

| Step | What happens |
|------|-------------|
| S0-0 | `cd` into workspace; run schema migration if needed |
| S0-1 | Load `data/pipeline-b-seed-buckets.json` |
| S0-2 | **For each bucket** — call `keyword_suggestions` (limit 100) + `related_keywords depth=2` (limit 100) with `location_code=2840, language_code="en"`. Dedupe |
| S0-3 | Filter at fetch time: drop everything with `volume < 500` or `kd >= 30`. Compute `word_count = len(keyword.split())` |
| S0-4 | Dedupe against existing `keyword_pool` rows (skip known keywords entirely — don't waste API budget) |
| S0-5 | Insert survivors into `keyword_pool` with `cluster_id = NULL`, `seed_bucket = <bucket>` |
| S0-6 | After all buckets done: select all rows where `embedding IS NULL` |
| S0-7 | **Batch-embed** through Gemini `text-embedding-004` (batch size 100). Write float32 BLOBs back into `keyword_pool` |
| S0-8 | **Cluster** all rows where `cluster_id IS NULL` using `sklearn.cluster.AgglomerativeClustering(metric='cosine', linkage='average', distance_threshold=0.18, n_clusters=None)` |
| S0-9 | **Score each cluster**:<br>• `primary_keyword` = highest-volume keyword<br>• `primary_count` = count of `kd<30 AND volume>=500`<br>• `secondary_count` = count of `kd<20 AND volume>=500`<br>• `longtail_count` = count of `word_count>=3`<br>• `total_volume` = sum<br>• `status` = `viable` if `primary_count>=2 AND secondary_count>=6 AND longtail_count>=1`, else `insufficient` |
| S0-10 | Insert cluster rows; `UPDATE keyword_pool SET cluster_id = ? WHERE id IN (...)` |
| S0-11 | Append run summary to `data/pipeline-b-runs.log` (buckets processed, keywords harvested, clusters created, viable count, DataForSEO cost) |

### Output
```
STAGE0_RESULT: success
BUCKETS_PROCESSED: <n>
KEYWORDS_HARVESTED: <n>
KEYWORDS_EMBEDDED: <n>
CLUSTERS_CREATED: <n>
VIABLE_CLUSTERS: <n>
INSUFFICIENT_CLUSTERS: <n>
DATAFORSEO_COST_USD: <amount>
```

### Idempotency rules

- Never re-cluster keywords that already have a `cluster_id`. Phase B (cluster step) selects only `WHERE cluster_id IS NULL`.
- Never re-embed keywords that already have an `embedding`. Phase A (embed step) selects only `WHERE embedding IS NULL`.
- Re-running Stage 0 after adding new buckets only processes the new keywords. Existing viable clusters are not disturbed.

### Hard cap

If accumulated DataForSEO cost during the run exceeds $2.00, stop fetching more buckets and proceed to embed/cluster what's been collected. Log the abort to `pipeline-b-runs.log`.

---

## Step 4 — Refactor Stage 1: `pipeline-b-stage1-keywords.md`

The agent name stays the same so the orchestrator interface holds, but the body is mostly rewritten.

**Invocation contract changes:**
```python
# OLD: prompt + "\nTOPIC_ID=<n>\n..."
# NEW:
Agent(subagent_type="general-purpose",
      prompt=open(".claude/agents/pipeline-b-stage1-keywords.md").read()
             + "\n\nCLUSTER_ID=<n>\nWORKSPACE_DIR=C:\\Users\\Syed Jawad Hassan\\Desktop\\devnook_content_workspace")
```

### New sub-steps (replacing all of S1-1 through S1-11)

| Step | What happens |
|------|-------------|
| S1-0 | `cd` into workspace |
| S1-1 | Read cluster row by `CLUSTER_ID`. Fail if `status != 'viable'` |
| S1-2 | Read all member keywords: `SELECT * FROM keyword_pool WHERE cluster_id = ?` |
| S1-3 | **Select final set** of 8–12 keywords:<br>• Top 2–3 primaries (highest volume where `kd<30`)<br>• Top 6–10 secondaries (`kd<20`, by volume)<br>• Ensure ≥ 1 long-tail (`word_count>=3`)<br>• Target 10–20% long-tail share |
| S1-4 | **Synthesize topic metadata** via a tight Gemini Flash call. Inputs: primary keyword, secondaries, long-tails, intent. Outputs: `title`, `slug`, `description` (140–160 chars, primary keyword in first 20 words). Reject and retry if description length out of bounds |
| S1-5 | **Slug uniqueness check** against `registry.db`. If slug collision: append `-2` (or next available suffix), log to `pipeline-b-runs.log` |
| S1-6 | Insert one row into `keyword_sets` with `status='ready'`, `cluster_id=<CLUSTER_ID>`, title, slug, description |
| S1-7 | Insert one row per selected keyword into `keywords` (referencing the new `keyword_set_id`) — these are the rows Stage 2 reads |
| S1-8 | `UPDATE clusters SET status='used', used_by_slug=?, keyword_set_id=? WHERE id=?` |
| S1-9 | Append success entry to `data/pipeline-b-runs.log` |

### Output (unchanged format — Stage 2 still reads this)
```
STAGE1_RESULT: success
KEYWORD_SET_ID: <id>
CLUSTER_ID: <id>
SLUG: <slug>
PRIMARY_COUNT: <n>
SECONDARY_COUNT: <n>
TOTAL_KEYWORDS: <n>
LONGTAIL_COUNT: <n>
```

### What gets deleted from the old Stage 1

- All DataForSEO MCP calls (now done in Stage 0)
- The retry-with-broader-seeds logic (S1-6 in pipelineB.md) — irrelevant; if a cluster passed scoring it's already viable
- The `insufficient_keywords` topic-status handling (now a cluster status, set at scoring time)
- Reading from `data/pipeline-b-topics.json` (file is going away)
- The topic-relevance guard / pool filtering / longtail enforcement — all handled in Stage 0 scoring

### What gets preserved

- Saving to `data/keywords.db`
- The output format that Stage 2 depends on
- Idempotency: if the cluster is already `status='used'`, fail loudly rather than re-processing

---

## Step 5 — Orchestrator changes: `pipeline-b-orchestrator-v2.md`

Minimal edits. The orchestrator currently iterates over topics in `pipeline-b-topics.json`. Change it to iterate over viable clusters:

```sql
SELECT id, primary_keyword, total_volume
FROM clusters
WHERE status = 'viable'
ORDER BY total_volume DESC
LIMIT ?
```

For each cluster: invoke Stage 1 with `CLUSTER_ID=<id>`, then Stage 2 with the resulting `KEYWORD_SET_ID`, then Stage 3.

If zero viable clusters available: orchestrator prints `NO_VIABLE_CLUSTERS — run Stage 0 to refresh the pool` and exits cleanly.

---

## Step 6 — Cleanup

After end-to-end verification (see below) passes:

1. Delete `data/pipeline-b-topics.json`
2. Remove any references to topics.json from CLAUDE.md, orchestrator prompt, and any helper scripts
3. Update [pipelineB.md](pipelineB.md): replace the Stage 1 section with the new flow, add the Stage 0 section, update the topic lifecycle diagram to `harvested → clustered → viable → used → keywords_ready → draft_ready → done`
4. Commit everything

Do not delete `pipeline-b-topics.json` until the new flow has produced at least one successfully published article end-to-end. Belt and suspenders.

---

## Verification plan

**After Step 1 (schema):**
```bash
python -c "import sqlite3; db=sqlite3.connect('data/keywords.db'); \
  print([r[1] for r in db.execute('PRAGMA table_info(keyword_pool)')]); \
  print([r[1] for r in db.execute('PRAGMA table_info(clusters)')]); \
  print([r[1] for r in db.execute('PRAGMA table_info(keyword_sets)') if r[1]=='cluster_id'])"
```
Expect both new tables present and `cluster_id` column on `keyword_sets`.

**After Step 3 (Stage 0 dry run with 2 buckets):**
- Edit seed-buckets.json temporarily to 2 buckets. Invoke Stage 0.
- Expect ~100–500 keywords in `keyword_pool`, all with embeddings, all with a cluster_id assigned.
- `SELECT status, COUNT(*) FROM clusters GROUP BY status` — expect both viable and insufficient counts non-zero.
- Manually eyeball top 5 viable clusters by total_volume: primary keywords should be sensible article topics.
- **Sanity check:** if 0 viable clusters, the distance threshold or thresholds are misaligned with reality. Lower the cosine distance threshold to 0.15 and re-cluster (NULL out cluster_id on affected rows first).

**After Step 4 (Stage 1 with a real cluster_id):**
- Pick a viable cluster manually. Invoke Stage 1 with `CLUSTER_ID=<n>`.
- Expect: new `keyword_sets` row with `status='ready'`, new `keywords` rows (8–12 of them), cluster status flipped to `'used'`.
- Slug should look reasonable; description should be 140–160 chars with primary keyword in first 20 words.

**End-to-end:**
- Invoke the orchestrator. Expect a complete published article on devnook.dev, originating from a cluster, with all Stage 3 QA checks passed.

---

## Out of scope — don't do these in this PR

- Re-clustering / cluster merging / cluster splitting logic
- SERP-overlap clustering
- GSC feedback into cluster scoring
- Anything touching Pipeline A
- Editing Stage 2 or Stage 3 agent prompts
- Adding new DataForSEO endpoints beyond what Stage 1 currently uses (`keyword_suggestions`, `related_keywords`)
- Web UI / dashboard for cluster review

---

## Definition of done

1. Schema migration runs cleanly and is idempotent
2. `data/pipeline-b-seed-buckets.json` exists with the starter list
3. New Stage 0 agent file written, runs end-to-end, produces viable clusters in DB
4. Stage 1 agent refactored, accepts `CLUSTER_ID`, produces a `keyword_set` consumable by unchanged Stage 2
5. Orchestrator pulls from clusters table
6. Stages 2 and 3 produce a published article end-to-end on the new flow
7. `data/pipeline-b-topics.json` deleted; references removed
8. `pipelineB.md` updated to reflect the new 4-stage architecture (0 → 1 → 2 → 3)
9. Final PR comment summarizes: clusters produced, % viable, top 5 viable primaries by volume — this is the smell test

---

## When you're unsure

Confirm assumptions about the current `keywords.db` schema by inspecting the live DB *before* writing the migration. The pipelineB.md doc describes the table structure but I haven't verified column names.

If DataForSEO MCP behavior differs from what current Stage 1 does (e.g., MCP tool name changed, response shape different), stop and surface the discrepancy before writing code that assumes the old shape.

Default to the simpler implementation. Cluster thresholds, scoring formulas, and brief-generation prompts can all be tuned after seeing real output. Ship phase 1 minimal.
