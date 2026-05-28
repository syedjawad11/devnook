import json, sqlite3

TOPIC_ID = 4
conn = sqlite3.connect('data/registry.db')
row = conn.execute("SELECT id FROM keyword_sets WHERE topic_id=? AND status='ready' ORDER BY id DESC LIMIT 1", (TOPIC_ID,)).fetchone()
conn.close()
keyword_set_id = row[0] if row else None

with open('data/pipeline-b-topics.json') as f:
    topics_data = json.load(f)
for t in topics_data:
    if t['id'] == TOPIC_ID:
        t['status'] = 'keywords_ready'
        if keyword_set_id:
            t['keyword_set_id'] = keyword_set_id
        break
with open('data/pipeline-b-topics.json', 'w') as f:
    json.dump(topics_data, f, indent=2)
print(f"TOPIC_STATUS: topic_id={TOPIC_ID} -> keywords_ready (keyword_set_id={keyword_set_id})")
