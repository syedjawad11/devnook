import sqlite3

conn = sqlite3.connect('data/registry.db')
kset = conn.execute(
    "SELECT id, status, total_keywords, primary_count, secondary_count FROM keyword_sets WHERE topic_id=4 ORDER BY id DESC LIMIT 1"
).fetchone()
print(f"keyword_sets: id={kset[0]} status={kset[1]} total={kset[2]} primary={kset[3]} secondary={kset[4]}")

violations = []
kws = conn.execute(
    "SELECT keyword, keyword_type, search_volume, keyword_difficulty, intent FROM keywords WHERE keyword_set_id=? ORDER BY keyword_type, search_volume DESC",
    (kset[0],)
).fetchall()
print(f"keywords count: {len(kws)}")
for kw in kws:
    lt = '[longtail]' if len(kw[0].split()) >= 3 else ''
    v = []
    if kw[1] == 'primary' and kw[3] > 30: v.append('KD>30')
    if kw[1] == 'secondary' and kw[3] > 20: v.append('KD>20')
    if kw[2] < 500: v.append('vol<500')
    flag = ' VIOLATION:' + ','.join(v) if v else ''
    print(f"  [{kw[1]}] {kw[0]} vol={kw[2]} kd={kw[3]} intent={kw[4]} {lt}{flag}")
    violations.extend(v)
conn.close()

if violations:
    print(f"\nWARNING: violations found")
else:
    print("\nALL KEYWORDS PASS HARD RULES")
