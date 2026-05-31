# Pipeline B — Full Process (Stage 1 → Stage 3)

Pipeline B produces long-form blog posts (2,500–3,500 words) for devnook.dev. It runs as three independent stages. Stage 1 is local-only (requires DataForSEO MCP). Stages 2 and 3 are invoked by the CCR orchestrator.

---

## Stage 1 — Keyword Research (LOCAL ONLY)

**Goal:** Find 8–12 high-quality, topic-relevant keywords and save them to `data/keywords.db`.

**Invocation:**
```python
Agent(subagent_type="general-purpose",
      prompt=open(".claude/agents/pipeline-b-stage1-keywords.md").read()
             + "\n\nTOPIC_ID=<n>\nWORKSPACE_DIR=C:\\Users\\Syed Jawad Hassan\\Desktop\\devnook_content_workspace")
```

### Steps

| Step | What happens |
|------|-------------|
| S1-0 | `cd` into workspace, `mkdir -p data` |
| S1-1 | Read topic from `data/pipeline-b-topics.json` using `TOPIC_ID` |
| S1-2 | Init `data/keywords.db` (create `keyword_sets` + `keywords` tables if not exist) |
| S1-3 | **Idempotency check** — if a `ready` or `used` keyword_set already exists for this topic, skip entirely |
| S1-4 | **Fetch candidates via MCP** — call `keyword_suggestions` (limit 50) + `related_keywords depth=2` (limit 50) with `location_code=2840, language_code="en"`. Deduplicate and save to `data/stage1_candidates.json` |
| S1-5 | **Topic-relevance guard + pool filtering** — keep only keywords sharing ≥1 token (≥4 chars, prefix-match) with the seed phrase. Then split into primary pool (KD≤30, vol≥500) and secondary pool (KD≤20, vol≥500). Select top 2 primary + up to 10 secondary |
| S1-6 | **Retry with broader seeds** (only if total < 8 or no primary) — re-run `keyword_suggestions` for variants: `"<seed> guide"`, `"<seed> tutorial"`, `"best <seed>"`, `"how to <seed>"`, `"<seed> for developers"`. Merge and re-run S1-5 |
| S1-7 | **Longtail enforcement** — target 10–20% of batch as longtail (≥3 words, vol≥500). Swap in/out keywords to hit target range |
| S1-8 | **Insufficient check** — if total < 8 or no primary keywords: mark topic `insufficient_keywords` in topics JSON, write failure to `data/pipeline-b-runs.log`, print `STAGE1_FAILED`, exit |
| S1-9 | **Insert into DB** — write one row to `keyword_sets` (status=`ready`) + one row per keyword to `keywords` |
| S1-10 | **Update topic status** — set `status: 'keywords_ready'` + `keyword_set_id` in `data/pipeline-b-topics.json` |
| S1-11 | Cleanup temp files: `data/stage1_candidates.json`, `data/stage1_state.json` |

### Keyword thresholds

| Type | KD max | Volume min |
|------|--------|-----------|
| Primary | ≤ 30 | ≥ 500 |
| Secondary | ≤ 20 | ≥ 500 |

### Output
```
STAGE1_RESULT: success
KEYWORD_SET_ID: <id>
TOPIC_ID: <id>
SLUG: <slug>
PRIMARY_COUNT: <n>
SECONDARY_COUNT: <n>
TOTAL_KEYWORDS: <n>
LONGTAIL_COUNT: <n>
```

---

## Stage 2 — Content Writer

**Goal:** Read keywords from `data/keywords.db` and write a 2,500–3,500 word blog post to `agents/content-team/drafts/<slug>.md`.

### Steps

| Step | What happens |
|------|-------------|
| S2-0 | `cd` into workspace |
| S2-1 | Read keyword_set + all keywords from `data/keywords.db` for this `KEYWORD_SET_ID`. Fail if status ≠ `ready` or no primary keywords |
| S2-2 | Read all four skill files: `content-style-system.md`, `seo-writing-rules.md`, `devnook-brand-voice.md`, `content-schema.md` |
| S2-3 | Query `registry.db` for up to 80 published slugs → build `url_map` for internal links. **Never guess `/languages/` URLs** |
| S2-4 | Select voice (`thoughtful-explainer` / `terse-senior` / `tutorial-guide`) + section template (1 opening + 1 closing + 4–6 body H2s = 5–8 total) |
| S2-5 | **Write the article** — see hard rules below |
| S2-6 | **Word count verification** — count with Python regex `\b\w+\b`. If < 2,500: expand before saving |
| S2-7 | Save draft to `agents/content-team/drafts/<slug>.md` |
| S2-8 | Update topic status → `draft_ready`; mark `keyword_set` → `used` in `keywords.db` |

### Hard rules for the article

- Minimum **2,500 words** (hard floor — QA will also check this)
- **No `# H1`** in body — Astro layout renders `frontmatter.title` as H1
- Primary keyword in: first 100 words, first H2, meta description (first 20 words), conclusion
- Each secondary keyword: ≥1 mention in body
- **3–5 internal links** (from `url_map`, descriptive anchors)
- **3–5 external links** (authoritative sources: MDN, official docs, Wikipedia, Anthropic/OpenAI/GitHub)
- **FAQ section** with ≥3 Q&A pairs (`## Frequently Asked Questions`)
- **Comparison table or structured list** in the most relevant H2
- ≥1 **code block** with language tag
- No banned phrases from `devnook-brand-voice.md`
- Meta description: **140–160 chars**, primary keyword in first 20 words
- `schema_org` frontmatter: `BlogPosting` + `FAQPage` JSON-LD embedded as escaped string

### Output
```
STAGE2_RESULT: success
SLUG: <slug>
DRAFT_PATH: agents/content-team/drafts/<slug>.md
WORD_COUNT: <n>
TITLE: <title>
DESCRIPTION: <first 60 chars>...
```

---

## Stage 3 — QA + Publish

**Goal:** Validate the draft, run `npm run build`, push to devnook, insert into registry, and mark topic done.

### Steps

| Step | What happens |
|------|-------------|
| S3-0 | `cd` into workspace |
| S3-1 | Verify draft exists at `agents/content-team/drafts/<slug>.md`; read draft + skill files |
| S3-2 | Parse YAML frontmatter + body with Python. Fail if delimiters missing or YAML invalid |
| S3-3 | **QA hard-fail checks** — all 15 checks must pass (see list below). Any failure aborts the run |
| S3-4 | **Copy draft** to `$DEVNOOK_DIR/src/content/blog/<slug>.md`. Fail if file already exists |
| S3-5 | **`npm run build`** in devnook repo. On failure: remove copied file, exit |
| S3-6 | **Git commit + push** to devnook. Verify remote SHA matches local SHA after push |
| S3-7 | **Insert registry row** into `registry.db` (`status='published'`, `source='pipeline_b'`). Verify row exists after insert |
| S3-8 | **GSC URL submission** (best-effort via `mcp__gsc__submit_url`) — non-blocking |
| S3-9 | Update topic status → `done` in `data/pipeline-b-topics.json` |
| S3-10 | Append success entry to `data/pipeline-b-runs.log` |
| S3-11 | Best-effort workspace commit (runs.log + sandbox-layout) to content repo |

### QA hard-fail checks (S3-3)

1. Word count ≥ 2,500
2. `actual_word_count` frontmatter matches body count (±50)
3. All required frontmatter fields present: `title`, `description`, `category`, `template_id`, `tags`, `author`, `published_date`, `og_image`, `actual_word_count`, `schema_org`
4. Meta description length 140–160 chars
5. No `# H1` in body
6. Primary keyword in title
7. Primary keyword in first 100 words
8. Primary keyword in first H2
9. Primary keyword in `## Conclusion` section
10. `## Frequently Asked Questions` section with ≥3 `### ` Q&As
11. Internal links: 3–8
12. No `/languages/` URLs unless verified in registry
13. External links ≥ 3
14. Slug not already in `registry.db`
15. `schema_org` value parses as valid JSON inside `<script>` tags

### Output
```
STAGE3_RESULT: success
SLUG: <slug>
LIVE_URL: https://devnook.dev/blog/<slug>
WORD_COUNT: <n>
BUILD_PASSED: true
DEVNOOK_COMMIT_SHA: <sha>
```

---

## Topic lifecycle

```
pending → keywords_ready → draft_ready → done
                ↓
        insufficient_keywords  (terminal — skip topic)
```

---

## Key files

| File | Purpose |
|------|---------|
| `data/pipeline-b-topics.json` | Topic list with status + keyword_set_id per topic |
| `data/keywords.db` | SQLite: `keyword_sets` + `keywords` tables |
| `agents/content-team/drafts/<slug>.md` | Draft output from Stage 2 |
| `agents/content-team/registry.db` | Published posts registry |
| `data/pipeline-b-runs.log` | Append-only JSONL run history |
| `.claude/agents/pipeline-b-stage1-keywords.md` | Stage 1 agent prompt |
| `.claude/agents/pipeline-b-stage2-writer.md` | Stage 2 agent prompt |
| `.claude/agents/pipeline-b-stage3-qa-publish.md` | Stage 3 agent prompt |
| `.claude/agents/pipeline-b-orchestrator-v2.md` | Orchestrator (coordinates Stages 2–3 in CCR) |
