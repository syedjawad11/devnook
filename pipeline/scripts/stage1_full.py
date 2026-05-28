"""
Full Stage 1 pipeline: filter -> longtail enforcement -> DB insert
Fixes:
1. secondary_pool excludes only selected_primary (not full primary_pool)
2. Longtail trim replacements must satisfy KD<=20 for secondary positions
3. Longtail add candidates must satisfy KD constraints for their position type
"""
import json, re, math, sqlite3, datetime

STOPWORDS = {
    "a","an","the","in","on","at","to","for","of","and","or","with","by","how",
    "use","using","best","get","make","your","you","what","when","why","which",
    "who","will","can","from","this","that","into","over","after","before","also"
}
VALID_INTENTS = {"informational", "commercial", "commercial_investigation"}

def tokens(phrase):
    words = re.sub(r'[^a-z0-9 ]', '', phrase.lower()).split()
    return {w for w in words if len(w) >= 4 and w not in STOPWORDS}

def tokens_overlap(kw_tokens, seed_tokens):
    for kt in kw_tokens:
        for st in seed_tokens:
            if kt.startswith(st) or st.startswith(kt):
                return True
    return False

def score(kw):
    return (kw["search_volume"] * 0.5) + ((30 - kw["keyword_difficulty"]) * 10)

def is_longtail(kw):
    return len(kw["keyword"].split()) >= 3 and kw["search_volume"] >= 500

seed_keyword = "prompt engineering for developers"
seed_tokens = tokens(seed_keyword)

with open('data/stage1_candidates.json') as f:
    candidates = json.load(f)

# S1-3: Relevance guard
relevant = [k for k in candidates if tokens_overlap(tokens(k["keyword"]), seed_tokens)]
print(f"RELEVANCE_FILTER: {len(candidates)} total -> {len(relevant)} relevant (seed_tokens={seed_tokens})")

# Primary pool: KD <= 30, vol >= 500
primary_pool = sorted(
    [k for k in relevant
     if k["keyword_difficulty"] <= 30
     and k["search_volume"] >= 500
     and k.get("intent", "informational") in VALID_INTENTS],
    key=score, reverse=True
)

selected_primary = primary_pool[:2]
primary_kws = {k["keyword"].lower() for k in selected_primary}

# Secondary pool: KD <= 20, vol >= 500, not already selected as primary
secondary_pool = sorted(
    [k for k in relevant
     if k["keyword_difficulty"] <= 20
     and k["search_volume"] >= 500
     and k.get("intent", "informational") in VALID_INTENTS
     and k["keyword"].lower() not in primary_kws],
    key=score, reverse=True
)

selected_secondary = secondary_pool[:10]
total = len(selected_primary) + len(selected_secondary)

print(f"POOL: primary_pool={len(primary_pool)} secondary_pool={len(secondary_pool)}")
print(f"SELECTED: primary={len(selected_primary)} secondary={len(selected_secondary)} total={total}")
print("Primary keywords:")
for k in selected_primary:
    print(f"  {k['keyword']} vol={k['search_volume']} kd={k['keyword_difficulty']} intent={k.get('intent')}")
print("Secondary keywords:")
for k in selected_secondary:
    lt = '[longtail]' if is_longtail(k) else ''
    print(f"  {k['keyword']} vol={k['search_volume']} kd={k['keyword_difficulty']} {lt}")

# S1-4: Longtail enforcement
selected = list(selected_primary) + list(selected_secondary)
longtails = [k for k in selected if is_longtail(k)]
non_longtails = [k for k in selected if not is_longtail(k)]
lt_count = len(longtails)

min_lt = math.ceil(0.10 * total)
max_lt = math.floor(0.20 * total)
print(f"\nLONGTAIL_CHECK: count={lt_count} target=[{min_lt}, {max_lt}] total={total}")

if lt_count < min_lt:
    selected_kw_set = {k["keyword"].lower() for k in selected}
    # Longtail add: must satisfy secondary constraints (KD<=20, vol>=500)
    lt_candidates = sorted(
        [k for k in relevant
         if is_longtail(k)
         and k["keyword"].lower() not in selected_kw_set
         and k.get("intent", "informational") in VALID_INTENTS
         and k["keyword_difficulty"] <= 20
         and k["search_volume"] >= 500],
        key=lambda k: k["search_volume"], reverse=True
    )
    while lt_count < min_lt and lt_candidates:
        non_lt_sorted = sorted(non_longtails, key=lambda k: k["search_volume"])
        if not non_lt_sorted:
            break
        to_remove = non_lt_sorted[0]
        to_add = lt_candidates.pop(0)
        selected.remove(to_remove)
        selected.append(to_add)
        non_longtails.remove(to_remove)
        longtails.append(to_add)
        lt_count += 1
        print(f"  LONGTAIL_ADD: +'{to_add['keyword']}' (vol={to_add['search_volume']}) -'{to_remove['keyword']}'")

elif lt_count > max_lt:
    selected_kw_set = {k["keyword"].lower() for k in selected}
    # Longtail trim: replacements must be non-longtail, KD<=20, vol>=500 (secondary constraint)
    short_candidates = sorted(
        [k for k in relevant
         if not is_longtail(k)
         and k["keyword"].lower() not in selected_kw_set
         and k.get("intent", "informational") in VALID_INTENTS
         and k["keyword_difficulty"] <= 20
         and k["search_volume"] >= 500],
        key=lambda k: k["search_volume"], reverse=True
    )
    while lt_count > max_lt and short_candidates:
        lt_sorted = sorted(longtails, key=lambda k: k["search_volume"])
        to_remove = lt_sorted[0]
        to_add = short_candidates.pop(0)
        selected.remove(to_remove)
        selected.append(to_add)
        longtails.remove(to_remove)
        non_longtails.append(to_add)
        lt_count -= 1
        print(f"  LONGTAIL_TRIM: -'{to_remove['keyword']}' +'{to_add['keyword']}' (vol={to_add['search_volume']})")
    if lt_count > max_lt:
        print(f"  NOTE: cannot trim further -- no valid short KD<=20 vol>=500 candidates, proceeding with lt_count={lt_count}")

final_primary = [k for k in selected if k["keyword"].lower() in primary_kws]
final_secondary = [k for k in selected if k["keyword"].lower() not in primary_kws]
total_final = len(selected)

print(f"LONGTAIL_FINAL: lt_count={lt_count} total={total_final} primary={len(final_primary)} secondary={len(final_secondary)}")

# S1-5: DB Insert
TOPIC_ID = 4

if total_final < 8 or not final_primary:
    print(f"STAGE1_FAILED: insufficient_keywords -- {total_final} qualifying keywords (primary={len(final_primary)})")
    exit(1)

slug = "prompt-engineering-for-developers"
title = "prompt engineering techniques for developers"
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

conn = sqlite3.connect('data/registry.db')
cursor = conn.execute(
    """INSERT INTO keyword_sets
       (topic_id, slug, title, research_run_at, total_keywords, primary_count, secondary_count, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, 'ready')""",
    (TOPIC_ID, slug, title, now, total_final, len(final_primary), len(final_secondary))
)
keyword_set_id = cursor.lastrowid

for kw in final_primary:
    conn.execute(
        """INSERT OR IGNORE INTO keywords
           (keyword_set_id, topic_id, slug, keyword, keyword_type, search_volume, keyword_difficulty, cpc, intent)
           VALUES (?, ?, ?, ?, 'primary', ?, ?, ?, ?)""",
        (keyword_set_id, TOPIC_ID, slug, kw["keyword"],
         kw["search_volume"], kw["keyword_difficulty"], kw.get("cpc", 0.0), kw.get("intent", "informational"))
    )
for kw in final_secondary:
    conn.execute(
        """INSERT OR IGNORE INTO keywords
           (keyword_set_id, topic_id, slug, keyword, keyword_type, search_volume, keyword_difficulty, cpc, intent)
           VALUES (?, ?, ?, ?, 'secondary', ?, ?, ?, ?)""",
        (keyword_set_id, TOPIC_ID, slug, kw["keyword"],
         kw["search_volume"], kw["keyword_difficulty"], kw.get("cpc", 0.0), kw.get("intent", "informational"))
    )

conn.commit()
conn.close()
print(f"DB_INSERT_OK: keyword_set_id={keyword_set_id} total={total_final} longtail={lt_count}")
