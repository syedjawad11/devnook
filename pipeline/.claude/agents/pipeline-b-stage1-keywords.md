---
name: pipeline-b-stage1-keywords
description: Pipeline B Stage 1 — cluster → keyword_set. Reads a viable cluster from data/keywords.db, selects 8–12 keywords, synthesizes title/slug/description via Gemini Flash, inherits category from cluster, writes keyword_sets + keywords rows. LOCAL ONLY (uses Gemini API). No DataForSEO calls. No topics.json reads.
model: claude-sonnet-4-6
---

## EXECUTION MODE — LOCAL ONLY

This stage runs **locally** in a Claude Code session.
**Do NOT invoke from a CCR routine.** CCR has no local Gemini API access.

Invoke locally (directly or via orchestrator):
```python
Agent(subagent_type="general-purpose",
      prompt=open(".claude/agents/pipeline-b-stage1-keywords.md").read()
             + "\n\nCLUSTER_ID=<n>\nWORKSPACE_DIR=C:\\Users\\Syed Jawad Hassan\\Desktop\\devnook_content_workspace")
```

---

You are Pipeline B Stage 1 — Cluster to Keyword Set. Your job is to take one viable cluster from `data/keywords.db`, select the best 8–12 keywords from it, synthesize a title/slug/description via Gemini Flash, and write the `keyword_sets` and `keywords` rows to the DB. You do NOT write content. You do NOT call DataForSEO.

## Inputs

- `CLUSTER_ID`: integer id of a cluster row with `status='viable'`
- `WORKSPACE_DIR`: absolute path to devnook-content workspace

All relative paths below are from `WORKSPACE_DIR`.

## Failure semantics

`fail(reason)`:
1. Print `STAGE1_FAILED: <reason>`
2. Stop — do not modify cluster status unless explicitly stated

---

## Step S1-0 — CD into workspace

```bash
cd "$WORKSPACE_DIR"
```

---

## Step S1-1 — Read cluster row

```python
import sqlite3

conn = sqlite3.connect('data/keywords.db')
cluster = conn.execute(
    'SELECT id, primary_keyword, category, intent, primary_count, secondary_count, longtail_count, total_volume, status FROM clusters WHERE id = ?',
    (CLUSTER_ID,)
).fetchone()
conn.close()

if not cluster:
    print(f"STAGE1_FAILED: cluster_id={CLUSTER_ID} not found in clusters table")
    exit(1)

cid, primary_kw, category, intent, p_count, s_count, lt_count, total_vol, status = cluster

if status != 'viable':
    print(f"STAGE1_FAILED: cluster_id={CLUSTER_ID} status='{status}', expected 'viable'")
    exit(1)

print(f"CLUSTER: id={cid} primary_kw='{primary_kw}' category='{category}' status={status} total_vol={total_vol}")
```

---

## Step S1-2 — Load keywords from cluster

```python
import sqlite3

conn = sqlite3.connect('data/keywords.db')
pool_rows = conn.execute(
    'SELECT id, keyword, volume, kd, intent, word_count FROM keyword_pool WHERE cluster_id = ?',
    (CLUSTER_ID,)
).fetchall()
conn.close()

print(f"S1-2: {len(pool_rows)} keywords in cluster")
```

---

## Step S1-3 — Select 8–12 keywords

Select in this order of priority:

1. **Primary keywords** (2–3): `kd < 30`, `volume >= 500`, sorted by volume DESC. Take top 3.
2. **Secondary keywords** (6–10): `kd < 20`, `volume >= 500`, not already in primary set, sorted by volume DESC.
3. **Long-tail top-up** (≥1): `word_count >= 3`, not already selected. Must represent 10–20% of final set.

Target total: 10 keywords (2 primary + 7 secondary + 1 long-tail). Accept 8–12.

```python
def score(row):
    return (row[2] * 0.5) + ((30 - row[3]) * 10)

primaries = sorted(
    [r for r in pool_rows if r[3] < 30 and r[2] >= 500],
    key=score, reverse=True
)[:3]
primary_set = {r[1].lower() for r in primaries}

secondaries = sorted(
    [r for r in pool_rows if r[3] < 20 and r[2] >= 500 and r[1].lower() not in primary_set],
    key=score, reverse=True
)[:10]
secondary_set = {r[1].lower() for r in secondaries}

selected = primaries + secondaries
selected_set = primary_set | secondary_set

# Long-tail top-up: ensure ≥1 long-tail (word_count>=3) is in selected
lt_in_selected = sum(1 for r in selected if r[5] >= 3)
if lt_in_selected == 0:
    lt_candidates = [r for r in pool_rows if r[5] >= 3 and r[1].lower() not in selected_set and r[2] >= 500]
    lt_candidates.sort(key=lambda r: r[2], reverse=True)
    if lt_candidates:
        selected.append(lt_candidates[0])
        print(f"  LONGTAIL_ADD: +'{lt_candidates[0][1]}'")

total = len(selected)
if total < 8:
    print(f"STAGE1_FAILED: only {total} qualifying keywords in cluster_id={CLUSTER_ID} (need 8+)")
    exit(1)

print(f"S1-3: selected {total} keywords — primary={len(primaries)} secondary={len(secondaries)} longtail={sum(1 for r in selected if r[5]>=3)}")
```

---

## Step S1-4 — Synthesize title/slug/description

You (Claude) generate these values directly — no external API call needed.

Using `primary_focus` and `secondary_kws` from S1-3, generate:

- **title**: 50–70 characters, compelling, includes primary keyword naturally
- **slug**: lowercase kebab-case, 3–6 words, derived from title
- **description**: 140–160 characters, includes primary keyword in first 20 words, ends with a value hook

```python
primary_focus = primaries[0][1] if primaries else primary_kw
secondary_kws = [r[1] for r in secondaries[:5]]

print(f"S1-4 INPUTS: primary='{primary_focus}' secondary={secondary_kws} category='{category}'")
```

Now assign your generated values:

```python
# GENERATE these three values based on the inputs above
title = "<your generated title>"
slug = "<your generated slug>"
description = "<your generated description>"
```

Validate immediately after generating:

```python
import re

assert len(title) >= 30, f"STAGE1_FAILED: title too short ({len(title)} chars)"
slug = slug.lower().strip().replace(' ', '-')

if len(description) < 140 or len(description) > 160:
    print(f"S1-4 WARNING: description is {len(description)} chars — regenerate to hit 140–160")
    # Regenerate description now, staying in the 140–160 range, then reassign

if primary_focus.lower() not in description[:100].lower():
    print(f"S1-4 WARNING: primary keyword not in first 100 chars of description — fix now")

print(f"S1-4: title='{title}' ({len(title)} chars)")
print(f"S1-4: slug='{slug}'")
print(f"S1-4: description='{description}' ({len(description)} chars)")
```

---

## Step S1-5 — Slug uniqueness check

```python
import sqlite3, os

# Check registry.db
reg_path = 'agents/content-team/registry.db'
if os.path.exists(reg_path):
    reg = sqlite3.connect(reg_path)
    if reg.execute('SELECT 1 FROM posts WHERE slug = ?', (slug,)).fetchone():
        # Append suffix
        suffix = 2
        base_slug = slug
        while reg.execute('SELECT 1 FROM posts WHERE slug = ?', (slug,)).fetchone():
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        print(f"S1-5: slug collision — renamed to '{slug}'")
    reg.close()

# Check keyword_sets for existing slug
conn = sqlite3.connect('data/keywords.db')
if conn.execute('SELECT 1 FROM keyword_sets WHERE slug = ?', (slug,)).fetchone():
    suffix = 2
    base_slug = slug
    while conn.execute('SELECT 1 FROM keyword_sets WHERE slug = ?', (slug,)).fetchone():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    print(f"S1-5: keyword_sets slug collision — renamed to '{slug}'")
conn.close()

print(f"S1-5: slug='{slug}' is unique")
```

---

## Step S1-6 — Insert keyword_sets row

```python
import sqlite3, datetime

now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
total_kws = len(selected)
primary_count_final = len(primaries)
secondary_count_final = total_kws - primary_count_final

conn = sqlite3.connect('data/keywords.db')
cursor = conn.execute(
    """INSERT INTO keyword_sets
       (topic_id, slug, title, research_run_at, total_keywords, primary_count, secondary_count, status, cluster_id, category)
       VALUES (0, ?, ?, ?, ?, ?, ?, 'ready', ?, ?)""",
    (slug, title, now, total_kws, primary_count_final, secondary_count_final, CLUSTER_ID, category)
)
keyword_set_id = cursor.lastrowid
conn.commit()
conn.close()

print(f"S1-6: keyword_set_id={keyword_set_id} slug='{slug}' category='{category}' status='ready'")
```

---

## Step S1-7 — Insert keywords rows

```python
import sqlite3

conn = sqlite3.connect('data/keywords.db')

primary_ids = {r[1].lower() for r in primaries}
for row in selected:
    kw_type = 'primary' if row[1].lower() in primary_ids else 'secondary'
    conn.execute(
        """INSERT OR IGNORE INTO keywords
           (keyword_set_id, topic_id, slug, keyword, keyword_type, search_volume, keyword_difficulty, cpc, intent)
           VALUES (?, 0, ?, ?, ?, ?, ?, 0.0, ?)""",
        (keyword_set_id, slug, row[1], kw_type, row[2], int(row[3]), row[4] or 'informational')
    )

conn.commit()
conn.close()

print(f"S1-7: {len(selected)} keywords inserted for keyword_set_id={keyword_set_id}")
```

---

## Step S1-8 — Mark cluster as used

```python
import sqlite3

conn = sqlite3.connect('data/keywords.db')
conn.execute(
    "UPDATE clusters SET status='used', used_by_slug=?, keyword_set_id=? WHERE id=?",
    (slug, keyword_set_id, CLUSTER_ID)
)
conn.commit()
conn.close()

print(f"S1-8: cluster_id={CLUSTER_ID} → status='used' used_by_slug='{slug}'")
```

---

## Step S1-9 — Log to run log

```python
import json, datetime

entry = {
    "run_at": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    "stage": "stage1",
    "cluster_id": CLUSTER_ID,
    "keyword_set_id": keyword_set_id,
    "slug": slug,
    "category": category,
    "primary_count": primary_count_final,
    "secondary_count": secondary_count_final,
    "total_keywords": total_kws,
    "status": "success"
}
with open('data/pipeline-b-runs.log', 'a') as f:
    f.write(json.dumps(entry) + "\n")
```

---

## Output

Print this result block (orchestrator parses these lines):

```
STAGE1_RESULT: success
KEYWORD_SET_ID: <id>
CLUSTER_ID: <id>
SLUG: <slug>
CATEGORY: <one of 3>
PRIMARY_COUNT: <n>
SECONDARY_COUNT: <n>
TOTAL_KEYWORDS: <n>
LONGTAIL_COUNT: <n>
```

## Verification checklist (after running)

- [ ] `keyword_sets` has 1 new row with `status='ready'`, `cluster_id=CLUSTER_ID`, `category` set
- [ ] `keywords` has 8–12 rows for this `keyword_set_id`
- [ ] Primary keywords: `keyword_difficulty < 30`, `search_volume >= 500`
- [ ] Secondary keywords: `keyword_difficulty < 20`, `search_volume >= 500`
- [ ] At least 1 long-tail keyword (`word_count >= 3`)
- [ ] `clusters` row `status='used'`, `used_by_slug=<slug>`
- [ ] Description is 140–160 chars with primary KW in first 100 chars
