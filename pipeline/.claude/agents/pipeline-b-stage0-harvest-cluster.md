---
name: pipeline-b-stage0-harvest-cluster
description: Pipeline B Stage 0 — keyword harvest + embed + cluster (LOCAL MCP only). Reads seed buckets, fetches keywords via DataForSEO MCP, embeds via Gemini text-embedding-004, clusters via agglomerative clustering, scores and writes viable clusters to data/keywords.db. Idempotent — safe to re-run.
model: claude-sonnet-4-6
---

## EXECUTION MODE — LOCAL ONLY

This stage runs **locally** in a Claude Code session with DataForSEO MCP tools available.
**Do NOT invoke from a CCR routine.** CCR has no local MCP access.

Invoke locally:
```python
Agent(subagent_type="general-purpose",
      prompt=open(".claude/agents/pipeline-b-stage0-harvest-cluster.md").read()
             + "\n\nWORKSPACE_DIR=C:\\Users\\Syed Jawad Hassan\\Desktop\\devnook_content_workspace")
```

---

You are Pipeline B Stage 0 — Keyword Harvest + Cluster. Your job is to populate `data/keywords.db` with a pool of viable keyword clusters that Stage 1 can consume. You do NOT write content. You do NOT call Stage 1.

## Inputs

- `WORKSPACE_DIR`: absolute path to devnook-content workspace

All relative paths below are from `WORKSPACE_DIR`.

## Constants

```python
DISTANCE_THRESHOLD = 0.18      # cosine agglomerative clustering threshold — tunable
VALID_CATEGORIES = ["Comparisons", "AI & Productivity", "Tools & Workflows"]
```

## Failure semantics

`fail(reason)`: print `STAGE0_FAILED: <reason>`, stop immediately.

---

## Step S0-0 — CD into workspace + run idempotent migration

```bash
cd "$WORKSPACE_DIR"
mkdir -p data
```

Run the migration in Python to ensure tables exist:

```python
import sqlite3

conn = sqlite3.connect('data/keywords.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS keyword_pool (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  keyword         TEXT NOT NULL UNIQUE,
  volume          INTEGER NOT NULL,
  kd              REAL NOT NULL,
  intent          TEXT,
  seed_bucket     TEXT NOT NULL,
  word_count      INTEGER NOT NULL,
  embedding       BLOB,
  cluster_id      INTEGER REFERENCES clusters(id),
  source          TEXT DEFAULT "dataforseo",
  discovered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.execute('CREATE INDEX IF NOT EXISTS idx_pool_cluster ON keyword_pool(cluster_id)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_pool_bucket  ON keyword_pool(seed_bucket)')

conn.execute('''
CREATE TABLE IF NOT EXISTS clusters (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  primary_keyword   TEXT NOT NULL,
  category          TEXT NOT NULL,
  intent            TEXT,
  primary_count     INTEGER NOT NULL,
  secondary_count   INTEGER NOT NULL,
  longtail_count    INTEGER NOT NULL,
  total_volume      INTEGER NOT NULL,
  status            TEXT NOT NULL CHECK(status IN ("viable","insufficient","used")),
  used_by_slug      TEXT,
  keyword_set_id    INTEGER REFERENCES keyword_sets(id),
  scored_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.execute('CREATE INDEX IF NOT EXISTS idx_clusters_status_volume ON clusters(status, total_volume DESC)')

existing_cols = [r[1] for r in conn.execute('PRAGMA table_info(keyword_sets)')]
if 'cluster_id' not in existing_cols:
    conn.execute('ALTER TABLE keyword_sets ADD COLUMN cluster_id INTEGER REFERENCES clusters(id)')
if 'category' not in existing_cols:
    conn.execute('ALTER TABLE keyword_sets ADD COLUMN category TEXT')

conn.commit()
conn.close()
print("MIGRATION: OK")
```

---

## Step S0-1 — Load seed buckets + validate categories

```python
import json

VALID_CATEGORIES = ["Comparisons", "AI & Productivity", "Tools & Workflows"]

with open('data/pipeline-b-seed-buckets.json') as f:
    config = json.load(f)

buckets = config['buckets']
max_kw_per_bucket = config.get('max_keywords_per_bucket', 200)
min_volume = config['filters']['min_volume']
max_kd = config['filters']['max_kd']
cost_cap = config['dataforseo_cost_cap_usd']

for b in buckets:
    if b['category'] not in VALID_CATEGORIES:
        print(f"STAGE0_FAILED: bucket '{b['seed']}' has invalid category '{b['category']}'. Must be one of {VALID_CATEGORIES}")
        exit(1)

# Build bucket → category map
BUCKET_CATEGORY = {b['seed']: b['category'] for b in buckets}

print(f"S0-1: {len(buckets)} buckets loaded. cost_cap=${cost_cap} min_vol={min_volume} max_kd={max_kd}")
```

---

## Step S0-2 — Fetch keywords per bucket via DataForSEO MCP

For each bucket, call two MCP tools. Track accumulated cost.

**Cost tracking**: Each `keyword_suggestions` or `related_keywords` API call costs approximately $0.05–$0.10. Track a running total. If it would exceed `cost_cap`, log the abort and skip remaining buckets — but continue to Step S0-7 (embed) with what's been collected.

```python
import sqlite3

accumulated_cost = 0.0
buckets_processed = 0
keywords_inserted = 0

conn = sqlite3.connect('data/keywords.db')

# Load already-known keywords to skip re-fetching
existing_keywords = {r[0].lower() for r in conn.execute('SELECT keyword FROM keyword_pool')}
print(f"S0-2: {len(existing_keywords)} existing keywords in pool — will skip duplicates")
```

For each bucket `b` in `buckets`:

1. Check if `accumulated_cost >= cost_cap`. If so: print `COST_CAP_REACHED: aborting further bucket fetches after ${accumulated_cost:.3f}` and break out of the bucket loop.

2. Call `mcp__dataforseo__dataforseo_labs_google_keyword_suggestions` with:
   - `keyword`: `<b['seed']>`
   - `location_code`: `2840`
   - `language_code`: `"en"`
   - `limit`: `100`

3. Call `mcp__dataforseo__dataforseo_labs_google_related_keywords` with:
   - `keyword`: `<b['seed']>`
   - `location_code`: `2840`
   - `language_code`: `"en"`
   - `depth`: `2`
   - `limit`: `100`

4. After both calls, extract candidates. For each result item extract:
   - `keyword` (string, lowercased)
   - `volume`: from `keyword_info.search_volume` or `keyword_data.keyword_info.search_volume` (default 0)
   - `kd`: from `keyword_properties.keyword_difficulty` or top-level `keyword_difficulty` (default 99)
   - `intent`: from `search_intent_info.main_intent` (default `"informational"`)

5. Filter immediately: drop items where `volume < min_volume` OR `kd >= max_kd`.

6. Compute `word_count = len(keyword.split())` for each survivor.

7. Dedupe within bucket (lowercase key). Dedupe against `existing_keywords`.

8. Insert survivors into `keyword_pool`:

```python
    new_in_bucket = 0
    for item in bucket_survivors:
        kw_lower = item['keyword'].lower()
        if kw_lower in existing_keywords:
            continue
        try:
            conn.execute(
                """INSERT INTO keyword_pool
                   (keyword, volume, kd, intent, seed_bucket, word_count, source)
                   VALUES (?, ?, ?, ?, ?, ?, 'dataforseo')""",
                (kw_lower, item['volume'], item['kd'], item.get('intent', 'informational'),
                 b['seed'], item['word_count'])
            )
            existing_keywords.add(kw_lower)
            new_in_bucket += 1
        except Exception:
            pass  # UNIQUE constraint violation — already inserted

    conn.commit()
    keywords_inserted += new_in_bucket
    buckets_processed += 1
    # Estimate cost: $0.05 per API call, 2 calls per bucket
    accumulated_cost += 0.10
    print(f"  BUCKET '{b['seed']}': +{new_in_bucket} new keywords (cost so far: ${accumulated_cost:.2f})")
```

After bucket loop:

```python
conn.close()
print(f"S0-2 DONE: buckets_processed={buckets_processed} keywords_inserted={keywords_inserted} estimated_cost=${accumulated_cost:.2f}")
```

---

## Step S0-7 — Embed keywords with Gemini text-embedding-004

Select all rows from `keyword_pool` where `embedding IS NULL`. Batch into groups of 100. For each batch, call the Gemini embedding API.

```python
import sqlite3, struct, os

conn = sqlite3.connect('data/keywords.db')
to_embed = conn.execute(
    'SELECT id, keyword FROM keyword_pool WHERE embedding IS NULL'
).fetchall()
conn.close()

print(f"S0-7: {len(to_embed)} keywords to embed")

if not to_embed:
    print("S0-7: nothing to embed — skipping")
else:
    from google import genai

    client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

    BATCH_SIZE = 100
    embedded_count = 0

    for i in range(0, len(to_embed), BATCH_SIZE):
        batch = to_embed[i:i+BATCH_SIZE]
        texts = [row[1] for row in batch]
        ids   = [row[0] for row in batch]

        result = client.models.embed_content(
            model='text-embedding-004',
            contents=texts,
            config=genai.types.EmbedContentConfig(task_type='SEMANTIC_SIMILARITY')
        )
        embeddings = [e.values for e in result.embeddings]  # list of float lists

        conn = sqlite3.connect('data/keywords.db')
        for row_id, embedding in zip(ids, embeddings):
            blob = struct.pack(f'{len(embedding)}f', *embedding)
            conn.execute('UPDATE keyword_pool SET embedding = ? WHERE id = ?', (blob, row_id))
        conn.commit()
        conn.close()

        embedded_count += len(batch)
        print(f"  EMBED: {embedded_count}/{len(to_embed)} done")

    print(f"S0-7 DONE: {embedded_count} keywords embedded")
```

---

## Step S0-8 — Cluster keywords via agglomerative clustering

Select all rows with `cluster_id IS NULL` and `embedding IS NOT NULL`. Run agglomerative clustering with cosine distance.

```python
import sqlite3, struct, numpy as np
from sklearn.cluster import AgglomerativeClustering

DISTANCE_THRESHOLD = 0.18  # tunable constant

conn = sqlite3.connect('data/keywords.db')
rows = conn.execute(
    'SELECT id, keyword, volume, kd, seed_bucket, word_count, embedding FROM keyword_pool WHERE cluster_id IS NULL AND embedding IS NOT NULL'
).fetchall()
conn.close()

if not rows:
    print("S0-8: no unclassified keywords — skipping")
else:
    print(f"S0-8: clustering {len(rows)} keywords (threshold={DISTANCE_THRESHOLD})")

    ids       = [r[0] for r in rows]
    keywords  = [r[1] for r in rows]
    volumes   = [r[2] for r in rows]
    kds       = [r[3] for r in rows]
    buckets_r = [r[4] for r in rows]
    wcs       = [r[5] for r in rows]
    dim = len(struct.unpack(f'{len(rows[0][6])//4}f', rows[0][6]))

    X = np.zeros((len(rows), dim), dtype=np.float32)
    for i, r in enumerate(rows):
        X[i] = struct.unpack(f'{dim}f', r[6])

    if len(rows) < 2:
        labels = [0] * len(rows)
    else:
        model = AgglomerativeClustering(
            metric='cosine',
            linkage='average',
            distance_threshold=DISTANCE_THRESHOLD,
            n_clusters=None
        )
        labels = model.fit_predict(X)

    print(f"S0-8 DONE: {max(labels)+1 if labels else 0} clusters formed")
```

---

## Step S0-9 — Assign category to each cluster (majority vote)

```python
from collections import Counter

# BUCKET_CATEGORY built in S0-1
cluster_members = {}
for i, label in enumerate(labels):
    cluster_members.setdefault(int(label), []).append(i)

cluster_category = {}
for cid, member_indices in cluster_members.items():
    votes = Counter()
    for idx in member_indices:
        cat = BUCKET_CATEGORY.get(buckets_r[idx], None)
        if cat:
            # weighted by volume for tie-break
            votes[cat] += volumes[idx]
    cluster_category[cid] = votes.most_common(1)[0][0] if votes else VALID_CATEGORIES[0]

print(f"S0-9: categories assigned to {len(cluster_category)} clusters")
```

---

## Step S0-10 — Score each cluster + insert into DB

```python
import sqlite3, datetime

VALID_CATEGORIES = ["Comparisons", "AI & Productivity", "Tools & Workflows"]

conn = sqlite3.connect('data/keywords.db')
viable_count = 0
insufficient_count = 0
viable_by_category = {c: 0 for c in VALID_CATEGORIES}
cluster_db_ids = {}  # label → DB id

for cid, member_indices in cluster_members.items():
    category = cluster_category[cid]
    members = [(ids[i], keywords[i], volumes[i], kds[i], wcs[i]) for i in member_indices]

    # primary_keyword = highest-volume member
    primary = max(members, key=lambda m: m[2])
    primary_kw = primary[1]

    # Score: primary (kd<30, vol≥500), secondary (kd<20, vol≥500), longtail (word_count≥3)
    primary_count   = sum(1 for m in members if m[3] < 30 and m[2] >= 500)
    secondary_count = sum(1 for m in members if m[3] < 20 and m[2] >= 500)
    longtail_count  = sum(1 for m in members if m[4] >= 3)
    total_volume    = sum(m[2] for m in members)

    # Viability: primary≥2 AND secondary≥4 AND longtail≥1
    status = 'viable' if (primary_count >= 2 and secondary_count >= 4 and longtail_count >= 1) else 'insufficient'

    cursor = conn.execute(
        """INSERT INTO clusters
           (primary_keyword, category, intent, primary_count, secondary_count, longtail_count, total_volume, status)
           VALUES (?, ?, 'informational', ?, ?, ?, ?, ?)""",
        (primary_kw, category, primary_count, secondary_count, longtail_count, total_volume, status)
    )
    db_id = cursor.lastrowid
    cluster_db_ids[cid] = db_id

    if status == 'viable':
        viable_count += 1
        viable_by_category[category] = viable_by_category.get(category, 0) + 1
    else:
        insufficient_count += 1

conn.commit()

# Back-fill cluster_id on keyword_pool rows
for cid, member_indices in cluster_members.items():
    db_id = cluster_db_ids[cid]
    pool_ids = [ids[i] for i in member_indices]
    conn.executemany(
        'UPDATE keyword_pool SET cluster_id = ? WHERE id = ?',
        [(db_id, pid) for pid in pool_ids]
    )
conn.commit()
conn.close()

print(f"S0-10 DONE: viable={viable_count} insufficient={insufficient_count}")
print(f"  viable_by_category={viable_by_category}")

if viable_count == 0:
    print("WARNING: 0 viable clusters. Consider lowering DISTANCE_THRESHOLD to 0.15 or relaxing bucket filters. Do NOT auto-retune.")
```

---

## Step S0-12 — Write run summary to log

```python
import json, datetime

summary = {
    "run_at": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    "stage": "stage0",
    "buckets_processed": buckets_processed,
    "keywords_harvested": keywords_inserted,
    "keywords_embedded": embedded_count if 'embedded_count' in dir() else 0,
    "clusters_created": viable_count + insufficient_count,
    "viable_clusters": viable_count,
    "insufficient_clusters": insufficient_count,
    "estimated_dataforseo_cost_usd": round(accumulated_cost, 3),
    "viable_by_category": viable_by_category
}

with open('data/pipeline-b-runs.log', 'a') as f:
    f.write(json.dumps(summary) + "\n")
```

---

## Output

Print this result block at the end:

```
STAGE0_RESULT: success
BUCKETS_PROCESSED: <n>
KEYWORDS_HARVESTED: <n>
KEYWORDS_EMBEDDED: <n>
CLUSTERS_CREATED: <n>
VIABLE_CLUSTERS: <n>
INSUFFICIENT_CLUSTERS: <n>
DATAFORSEO_COST_USD: <amount>
VIABLE_BY_CATEGORY: { "Comparisons": <n>, "AI & Productivity": <n>, "Tools & Workflows": <n> }
```

## Idempotency guarantee

- Re-running only touches keywords with `embedding IS NULL` (embed phase) and `cluster_id IS NULL` (cluster phase).
- Keywords already in `keyword_pool` are skipped at fetch time.
- Existing viable clusters are never modified.

## Verification checklist

- `SELECT COUNT(*) FROM keyword_pool` — should be ≥ 400 after first run
- `SELECT status, COUNT(*) FROM clusters GROUP BY status` — both viable and insufficient should be non-zero
- `SELECT category, COUNT(*) FROM clusters WHERE status='viable' GROUP BY category` — at least 1 per category ideally
- Eyeball top 5 viable clusters: `SELECT primary_keyword, category, total_volume FROM clusters WHERE status='viable' ORDER BY total_volume DESC LIMIT 5`
- If 0 viable: lower `DISTANCE_THRESHOLD` to `0.15`, or lower `secondary_count` threshold to 3, then `UPDATE keyword_pool SET cluster_id=NULL`, `DELETE FROM clusters`, re-run from S0-8
