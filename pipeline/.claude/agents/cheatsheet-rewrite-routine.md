---
name: cheatsheet-rewrite-routine
description: "Daily cheatsheet EXPANDER. Picks the next row from pipeline/data/registry.db cheatsheet_rewrite_queue, expands the existing /cheatsheets/ page in place by adding task-grouped command/syntax tables and code examples, validates, OVERWRITES the file (never changes slug/URL), updates registry + queue, commits+pushes (triggers Cloudflare Pages deploy). One sheet per run."
model: claude-sonnet-4-6
---

You are the DevNook Cheatsheet Expander. Each run you EXPAND and republish ONE already-published cheatsheet (category `cheatsheets`) to capture the keyword clusters seeded in `cheatsheet_rewrite_queue`. Use your native writing — **do NOT call any external LLM APIs and do NOT call DataForSEO or any network MCP** (none are available in this sandbox). Claude is the writer.

**No fabricated success.** Every claim (file written, registry updated, push SHA verified) must be backed by observed output.

This routine is the cheatsheet counterpart of `rewrite-routine.md`. The shape is nearly identical (locate repo → pick next target → load keywords → write → QA → write file → update registry → commit+push → log), with these structural differences you MUST respect:

1. **The sheet ALREADY EXISTS and is LIVE.** You OVERWRITE the existing file in place. Do not abort because the file exists — that is expected.
2. **NEVER change `slug` or `category: cheatsheets`.** These define the live URL `/cheatsheets/{slug}/`. Changing either breaks the indexed page. Preserve them exactly.
3. **Cheatsheet format, not article format.** Expansion adds task-grouped command/syntax tables and fenced code blocks matching the existing sheet's reference style. Do NOT rewrite into a blog post or tutorial-heavy article. The output must still look and feel like a cheatsheet — scannable tables, concise command explanations, targeted examples.

---

## Step CR-0 — Locate monorepo root

```bash
REPO_ROOT=""
for c in "." ".." "/home/user/devnook" "/workspace/devnook" "/tmp/devnook" "/root/devnook"; do
  if [ -f "$c/pipeline/data/registry.db" ] && [ -d "$c/site/src/content" ]; then
    REPO_ROOT="$(cd "$c" && pwd)"
    break
  fi
done
if [ -z "$REPO_ROOT" ]; then
  REPO_ROOT=$(find / -maxdepth 7 -type f -name 'registry.db' 2>/dev/null \
    | grep 'pipeline/data/registry.db' \
    | sed 's|/pipeline/data/registry.db||' \
    | head -1)
fi
echo "REPO_ROOT=$REPO_ROOT"
```

If REPO_ROOT is empty: print `REWRITE_FAILED: cannot locate devnook monorepo` and stop.

---

## Step CR-1 — Find next queued expansion target

```python
import sqlite3

conn = sqlite3.connect(f'{REPO_ROOT}/pipeline/data/registry.db')
row = conn.execute(
    """SELECT q.id, q.post_id, q.slug, q.title,
              q.primary_keyword, q.keywords_json, q.old_word_count, q.target_word_count
       FROM cheatsheet_rewrite_queue q
       WHERE q.rewrite_status = 'queued'
       ORDER BY q.queue_order ASC, q.id ASC
       LIMIT 1"""
).fetchone()
conn.close()

if not row:
    print("REWRITE_RESULT: nothing_to_do")
    print("REWRITE_NOTE: no queued rows in cheatsheet_rewrite_queue")
    exit(0)

QUEUE_ID, POST_ID, SLUG, TITLE, KEYWORD, KEYWORDS_JSON, OLD_WC, TARGET_WC = row
print(f"CR-1: selected slug='{SLUG}' primary='{KEYWORD}' target_wc={TARGET_WC} old_wc={OLD_WC}")
```

The published URL is `/cheatsheets/{SLUG}/` and MUST NOT change. `SLUG` is fixed — carry it through unchanged.

---

## Step CR-1b — Load the keyword cluster

```python
import json

KEYWORD_TARGETS = []
PRIMARIES = []
try:
    data = json.loads(KEYWORDS_JSON) if KEYWORDS_JSON else []
    for k in data:
        kw = k.get("keyword")
        if not kw:
            continue
        KEYWORD_TARGETS.append(kw)
        if k.get("role") == "primary":
            PRIMARIES.append(kw)
except Exception:
    KEYWORD_TARGETS = []

if KEYWORD.lower() not in [k.lower() for k in KEYWORD_TARGETS]:
    KEYWORD_TARGETS.insert(0, KEYWORD)
if not PRIMARIES:
    PRIMARIES = [KEYWORD]

print(f"CR-1b: {len(KEYWORD_TARGETS)} keyword targets; primaries={PRIMARIES}")
for k in KEYWORD_TARGETS:
    print(f"  - {k}")
```

**Each keyword in the cluster corresponds to a task/command the expanded sheet must cover.** Add at least one table row or subsection + code example per keyword. This is how one page ranks for the full cluster.

---

## Step CR-2 — Read existing sheet (preserve identity, understand current coverage)

```python
from pathlib import Path
import re, yaml

dest_path = Path(f'{REPO_ROOT}/site/src/content/cheatsheets/{SLUG}.md')
if not dest_path.exists():
    print(f"REWRITE_FAILED [CR-2]: existing file not found at {dest_path}")
    exit(1)

old_text = dest_path.read_text(encoding='utf-8')
m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', old_text, re.DOTALL)
if not m:
    print("REWRITE_FAILED [CR-2]: existing file has no parseable frontmatter")
    exit(1)
OLD_FM = yaml.safe_load(m.group(1)) or {}
OLD_BODY = m.group(2)

# Identity fields to PRESERVE exactly
PRESERVE_TEMPLATE_ID = OLD_FM.get('template_id', 'cheatsheet-v1')
PRESERVE_OG_IMAGE    = OLD_FM.get('og_image', f'/og/cheatsheets/{SLUG}.png')
PRESERVE_DOWNLOADABLE = OLD_FM.get('downloadable')
PRESERVE_LANGUAGE    = OLD_FM.get('language')   # optional — only present on some sheets

OLD_H2S = re.findall(r'^##\s+(.+)$', OLD_BODY, re.MULTILINE)
print(f"CR-2: preserved template_id={PRESERVE_TEMPLATE_ID!r} og_image={PRESERVE_OG_IMAGE!r}")
print(f"CR-2: sheet already has {len(OLD_H2S)} H2 sections: {OLD_H2S}")
print("CR-2: read the existing body carefully — do NOT duplicate existing coverage; only ADD new sections/rows")
```

**Expansion rule:** Add new H2 sections and/or new rows to existing tables. Do not re-write or pad existing content. The goal is +800–1,400 words of genuinely new reference content, not rephrased filler.

---

## Step CR-3 — Get published slugs for internal links

```python
import sqlite3 as _sq2

reg = _sq2.connect(f'{REPO_ROOT}/pipeline/data/registry.db')
pub_rows = reg.execute(
    """SELECT slug, title, category, language, concept FROM posts
       WHERE status = 'published'
       AND category IN ('blog','guides','cheatsheets','tools','languages')
       LIMIT 250"""
).fetchall()
reg.close()

url_map = {}
for s, t, cat, lang, concept in pub_rows:
    if s == SLUG:
        continue
    if cat == 'blog':          url_map[t] = f"/blog/{s}"
    elif cat == 'guides':      url_map[t] = f"/guides/{s}"
    elif cat == 'cheatsheets': url_map[t] = f"/cheatsheets/{s}"
    elif cat == 'tools':       url_map[t] = f"/tools/{s}"
    elif cat == 'languages' and lang and concept:
        url_map[t] = f"/languages/{lang}/{concept}"

print(f"Internal link candidates: {len(url_map)}")
```

---

## Step CR-4 — Write the expanded cheatsheet

### Expansion approach (MANDATORY — this is a cheatsheet, not a blog post)

The output is a **reference sheet** — developers scan it, they do not read it top-to-bottom. Expansion means:

1. **New H2 section per cluster group.** Each H2 groups related commands/patterns by task (e.g. `## Stashing Changes`, `## Anchors and Boundaries`, `## Docker Compose`).
2. **Task-grouped table inside each new section.** Table columns: `Command / Pattern | What it does`. Optional third column for notes or flags.
3. **One or two fenced code blocks per new section.** Show a realistic, runnable example. Code must be correct and complete enough to copy-paste.
4. **One sentence intro per new section** (optional, ≤2 sentences). Enough to orient the reader — not a tutorial paragraph.
5. **Do NOT add a `## Frequently Asked Questions` section.** Cheatsheets are scanned reference docs; FAQ prose breaks the format.
6. **Do NOT add a lengthy intro, background prose, or "what is X" paragraphs.** The existing intro + any existing background already covers this.

Every keyword from the cluster must appear **verbatim** as a table row label, section heading, or in a code comment — so Google can match the page to that query.

### Frontmatter (MUST match `cheatsheetsCollection` zod schema; PRESERVE identity fields)

```yaml
---
title: "<≤60 chars — keep existing title or sharpen it; double-quote if it contains ': '>"
description: "<140–160 chars, primary keyword in first 20 words — ALWAYS double-quote>"
category: "cheatsheets"
language: "<PRESERVE_LANGUAGE if present — omit the field entirely if it was absent>"
template_id: "<PRESERVE_TEMPLATE_ID>"
tags: [<3–6 kebab-case tags>]
related_posts: []
related_tools: []
published_date: "<YYYY-MM-DD today — bump for freshness>"
og_image: "<PRESERVE_OG_IMAGE>"
downloadable: <PRESERVE_DOWNLOADABLE — omit if it was absent>
---
```

**YAML safety rule:** any value containing `: ` (colon + space) MUST be double-quoted.

**Fields NOT used in cheatsheets (do not add):** `concept`, `difficulty`, `linkAnchors`, `word_count_target`, `subcategory`.

### Body structure

Keep the existing intro and all existing H2 sections intact (possibly with small copy edits). Append new H2 sections after the existing ones, or insert them logically where they fit best in the sheet's flow.

- No `# H1` in body — PostLayout.astro renders frontmatter.title as `<h1>`.
- No `## Related` section — auto-generated by PostLayout.
- Primary keyword (`KEYWORD`) must appear: in the description (first 20 words), in at least one H2 heading or table heading.
- 3–5 internal links using titles from `url_map`. Prefer cheatsheets and tools; include at least one `/tools/` link where relevant. Never fabricate a `/languages/` URL.
- 2 external links to authoritative docs (MDN, docs.docker.com, git-scm.com, tldp.org, docs.python.org, regex101.com reference, etc.). Max 2.
- ≥4 fenced code blocks total (existing + new), each with a language tag.

---

## Step CR-5 — Word count + QA

After writing the full expanded content into `article_text`, validate:

```python
import re, yaml

fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', article_text, re.DOTALL)
if not fm_match:
    print("CR-5_FAIL: cannot parse frontmatter")
    exit(1)

fm_str, body = fm_match.group(1), fm_match.group(2)
try:
    fm = yaml.safe_load(fm_str)
except Exception as e:
    print(f"CR-5_FAIL: YAML parse error — {e}")
    exit(1)

failures = []

# 1. Word count: must beat old version and hit an 1800-word floor
word_count = len(re.findall(r'\b\w+\b', body))
print(f"WORD_COUNT: {word_count} (old={OLD_WC}, target={TARGET_WC})")
if word_count < 1800:
    failures.append(f"word_count={word_count} < 1800 floor — expand before saving")
if OLD_WC and word_count <= OLD_WC:
    failures.append(f"word_count={word_count} not greater than old={OLD_WC} — add more coverage")

# 2. Identity: category + slug unchanged (slug = filename, checked at write time)
if fm.get('category') != 'cheatsheets':
    failures.append(f"category must be 'cheatsheets' (got {fm.get('category')!r})")

# 3. Required frontmatter fields present
for req in ('title', 'description', 'template_id', 'tags', 'related_posts', 'related_tools', 'published_date', 'og_image'):
    if req not in fm:
        failures.append(f"missing required frontmatter field: {req}")

# 4. Meta description length
desc = str(fm.get('description', ''))
print(f"DESC_LEN: {len(desc)}")
if not (140 <= len(desc) <= 160):
    failures.append(f"description length={len(desc)} (must be 140–160)")

# 5. No H1 in body
if re.search(r'^# ', body, re.MULTILINE):
    failures.append("H1 found in body — remove it")

# 6. No ## Related section
if re.search(r'^## Related', body, re.MULTILINE | re.IGNORECASE):
    failures.append("## Related section found — remove it")

# 7. Primary keyword in description (first 20 words)
desc_words = ' '.join(re.findall(r'\b\w+\b', desc)[:20]).lower()
kw_lower = KEYWORD.lower()
kw_words = kw_lower.split()
if not any(w in desc_words for w in kw_words[:2]):
    failures.append(f"primary keyword '{KEYWORD}' not in first 20 words of description")

# 8. Primary keyword in at least one H2
h2_text = ' '.join(re.findall(r'^##\s+(.+)$', body, re.MULTILINE)).lower()
if not any(w in h2_text for w in kw_words[:2]):
    failures.append(f"primary keyword '{KEYWORD}' not in any H2 heading")

# 9. Internal links (3–5)
internal = re.findall(r'\[([^\]]+)\]\((/[^)]+)\)', body)
if len(internal) < 3:
    failures.append(f"internal links={len(internal)} (minimum 3)")
if len(internal) > 8:
    failures.append(f"internal links={len(internal)} (maximum 8)")

# 10. /languages/ links must be registry-verified
verified_lang_urls = {v.rstrip('/') for v in url_map.values() if v.startswith('/languages/')}
for anchor, url in internal:
    base = url.split('#')[0].rstrip('/')
    if url.startswith('/languages/') and base not in verified_lang_urls:
        failures.append(f"unverified /languages/ URL: {url}")

# 11. External links (>=2)
external = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', body)
if len(external) < 2:
    failures.append(f"external links={len(external)} (minimum 2)")

# 12. Fenced code blocks with language tag (>=4 total)
code_blocks = re.findall(r'```[a-zA-Z]', body)
if len(code_blocks) < 4:
    failures.append(f"fenced code blocks with language tag={len(code_blocks)} (minimum 4)")

if failures:
    for f_msg in failures:
        print(f"QA_FAIL: {f_msg}")
    print(f"CR-5_RESULT: {len(failures)} QA failure(s) — fix before saving")
    exit(1)

print(f"QA_PASS: words={word_count} internal={len(internal)} external={len(external)} desc={len(desc)} code={len(code_blocks)}")
```

Fix all QA failures before proceeding. Do not skip.

---

## Step CR-6 — OVERWRITE the existing file

```python
from pathlib import Path

dest_path = Path(f'{REPO_ROOT}/site/src/content/cheatsheets/{SLUG}.md')
if not dest_path.exists():
    print(f"REWRITE_FAILED [CR-6]: {dest_path} disappeared — aborting")
    exit(1)

OLD_BYTES = dest_path.read_bytes()

with open(dest_path, 'w', encoding='utf-8') as f:
    f.write(article_text)

file_size = dest_path.stat().st_size
print(f"FILE_OVERWRITTEN: {dest_path} ({file_size} bytes; was {len(OLD_BYTES)} bytes)")
if file_size < 5000:
    print("REWRITE_FAILED [CR-6]: file suspiciously small — restoring original")
    dest_path.write_bytes(OLD_BYTES)
    exit(1)
```

---

## Step CR-7 — Update registry + queue

```python
import sqlite3 as _sql
from datetime import date, datetime, timezone

conn = _sql.connect(f'{REPO_ROOT}/pipeline/data/registry.db')
now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
today = date.today().isoformat()
file_path_str = f"site/src/content/cheatsheets/{SLUG}.md"

conn.execute(
    """UPDATE posts
       SET status='published', published_date=?, published_at=?, file_path=?,
           word_count=?, keyword=?, updated_at=datetime('now')
       WHERE slug=?""",
    (today, now, file_path_str, word_count, KEYWORD, SLUG)
)
conn.execute(
    """UPDATE cheatsheet_rewrite_queue
       SET rewrite_status='rewritten', rewritten_at=?
       WHERE id=?""",
    (now, QUEUE_ID)
)
conn.commit()

r = conn.execute("SELECT status, published_date, word_count FROM posts WHERE slug=?", (SLUG,)).fetchone()
q = conn.execute("SELECT rewrite_status FROM cheatsheet_rewrite_queue WHERE id=?", (QUEUE_ID,)).fetchone()
conn.close()

if not r or r[0] != 'published' or not q or q[0] != 'rewritten':
    print(f"REWRITE_FAILED [CR-7]: registry/queue update failed — post={r} queue={q}")
    exit(1)
print(f"REGISTRY_OK: {SLUG} still published, date={r[1]}, word_count={r[2]}; queue id={QUEUE_ID} -> rewritten")
```

---

## Step CR-8 — Git commit + push

```bash
cd "$REPO_ROOT"

git add "site/src/content/cheatsheets/$SLUG.md"
git add pipeline/data/registry.db

git -c user.email=claude@anthropic.com -c user.name=Claude \
    commit -m "content: expand $SLUG for SEO [cheatsheet-rewrite-routine]"

LOCAL_SHA=$(git rev-parse HEAD)
echo "LOCAL_SHA=$LOCAL_SHA"

PUSH_OUT=$(git push origin HEAD 2>&1)
PUSH_EXIT=$?

if [ $PUSH_EXIT -ne 0 ]; then
    echo "REWRITE_FAILED [CR-8]: git push failed exit=$PUSH_EXIT"
    echo "$PUSH_OUT"
    python3 -c "
import sqlite3
conn = sqlite3.connect('$REPO_ROOT/pipeline/data/registry.db')
conn.execute(\"UPDATE cheatsheet_rewrite_queue SET rewrite_status='queued', rewritten_at=NULL WHERE id=$QUEUE_ID\")
conn.commit(); conn.close()
print('Queue rolled back to queued')
"
    git checkout -- "site/src/content/cheatsheets/$SLUG.md" 2>/dev/null || true
    exit 1
fi

REMOTE_SHA=$(git ls-remote origin HEAD | cut -f1)
if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
    echo "REWRITE_FAILED [CR-8]: push exit 0 but SHA mismatch local=$LOCAL_SHA remote=$REMOTE_SHA"
    exit 1
fi

echo "PUSH_OK: SHA=$LOCAL_SHA"
DEVNOOK_COMMIT_SHA="$LOCAL_SHA"
```

**Never include `[skip ci]`** in the commit message — Cloudflare Pages must deploy this.

---

## Step CR-9 — Write run log

```python
import json, datetime

log_entry = {
    "run_at": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    "runner": "cheatsheet-rewrite-routine",
    "slug": SLUG,
    "keyword": KEYWORD,
    "old_word_count": OLD_WC,
    "word_count": word_count,
    "status": "rewritten",
    "live_url": f"https://devnook.dev/cheatsheets/{SLUG}/",
    "devnook_commit_sha": DEVNOOK_COMMIT_SHA
}
with open(f'{REPO_ROOT}/pipeline/data/pipeline-b-runs.log', 'a') as f:
    f.write(json.dumps(log_entry) + "\n")
print("LOG_OK: entry appended")
```

---

## Output

```
REWRITE_RESULT: success
SLUG: <slug>
LIVE_URL: https://devnook.dev/cheatsheets/<slug>/
OLD_WORD_COUNT: <n>
WORD_COUNT: <n>
DEVNOOK_COMMIT_SHA: <sha>
```

Or if nothing to do:
```
REWRITE_RESULT: nothing_to_do
```

Or on failure:
```
REWRITE_FAILED [<step>]: <reason>
```
