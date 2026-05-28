import sqlite3, datetime, json

TOPIC_ID = 4
with open('data/stage1_state.json') as f:
    state = json.load(f)

selected_primary = state["selected_primary"]
selected_secondary = state["selected_secondary"]
lt_count = state["lt_count"]
total = state["total"]

# Abort if still insufficient
if total < 8 or not selected_primary:
    print(f"STAGE1_FAILED: insufficient_keywords -- {total} qualifying keywords (primary={len(selected_primary)})")
    exit(1)

slug = "prompt-engineering-for-developers"
title = "prompt engineering techniques for developers"
now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

conn = sqlite3.connect('data/registry.db')
cursor = conn.execute(
    """INSERT INTO keyword_sets
       (topic_id, slug, title, research_run_at, total_keywords, primary_count, secondary_count, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, 'ready')""",
    (TOPIC_ID, slug, title, now, total, len(selected_primary), len(selected_secondary))
)
keyword_set_id = cursor.lastrowid

for kw in selected_primary:
    conn.execute(
        """INSERT OR IGNORE INTO keywords
           (keyword_set_id, topic_id, slug, keyword, keyword_type, search_volume, keyword_difficulty, cpc, intent)
           VALUES (?, ?, ?, ?, 'primary', ?, ?, ?, ?)""",
        (keyword_set_id, TOPIC_ID, slug, kw["keyword"],
         kw["search_volume"], kw["keyword_difficulty"], kw.get("cpc", 0.0), kw.get("intent", "informational"))
    )
for kw in selected_secondary:
    conn.execute(
        """INSERT OR IGNORE INTO keywords
           (keyword_set_id, topic_id, slug, keyword, keyword_type, search_volume, keyword_difficulty, cpc, intent)
           VALUES (?, ?, ?, ?, 'secondary', ?, ?, ?, ?)""",
        (keyword_set_id, TOPIC_ID, slug, kw["keyword"],
         kw["search_volume"], kw["keyword_difficulty"], kw.get("cpc", 0.0), kw.get("intent", "informational"))
    )

conn.commit()
conn.close()
print(f"DB_INSERT_OK: keyword_set_id={keyword_set_id} total={total} longtail={lt_count}")
