# devnook.dev Content Pipeline — Architecture Specification

**Version:** 1.0
**Owner:** Jawad
**Purpose:** Define the complete architecture for an automated, two-pipeline content system that (A) rewrites existing devnook.dev articles for SEO and (B) generates one new AI/Productivity article per day. Both pipelines run end-to-end with no human review gate — quality-checker is the final authority before auto-publish.

---

## 1. Project Overview

devnook.dev needs an automated content engine that delivers two parallel outputs:

- **Pipeline A — Rewrite Optimizer:** Takes existing published articles (currently ~50-60) that were written without proper keyword research and rewrites them with full SEO optimization.
- **Pipeline B — Daily Generator:** Produces one new long-form article per day in the AI/Productivity category, fully researched, written, and published.

Both pipelines share infrastructure (DataForSEO, GSC, caching, quality gates) and follow the same **Writing Standards** and **On-Page SEO Checklist** defined in this document. The only differences are inputs, output specifications, and a few pipeline-specific subagents.

### Critical operating principle

There is **no manual human review gate**. Quality-checker is the sole final authority. If an article passes all checks, it auto-publishes to the live site. If it fails, it retries up to N times, then is logged as failed for inspection. This means quality-checker must be rigorous — every check defined in this spec is mandatory.

---

## 2. Pipeline Specifications

### Pipeline A — Rewrite Optimizer

| Parameter | Value |
|---|---|
| Trigger | On-demand (single article) or batch mode (queue) |
| Input | Existing published article (Claude Code discovers location) |
| Word count target | 1,500-2,000 words |
| Keywords per article | 5-10 (1 primary + 2-3 secondary + 3-6 semantic supporting) |
| Keyword filter | `search_volume >= 500 AND keyword_difficulty < 30` |
| Intent filter | `informational` or `navigational` |
| Output | Rewritten article published to live site |

### Pipeline B — Daily AI/Productivity Generator

| Parameter | Value |
|---|---|
| Trigger | Once per day (Claude Code schedules) |
| Input | Topic from internal queue or auto-discovered seed |
| Category | AI / Productivity only |
| Word count target | 2,500-3,500 words |
| Keywords per article | 7-12 (1-2 primary + 3-4 secondary + 4-6 semantic supporting) |
| Keyword filter | `search_volume >= 500 AND keyword_difficulty < 30` |
| Intent filter | `informational` (primary), `commercial` allowed for tool comparisons |
| Output | New article published to live site + image/diagram suggestions logged |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                            │
│  - Reads queue (existing articles for A, topics for B)          │
│  - Dispatches to subagents in order                             │
│  - Manages state and retries                                    │
│  - Triggers publish on quality pass                             │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌──────────────────┐   ┌──────────────────┐
│ article-      │    │ kw-researcher    │   │ competitor-      │
│ auditor (A)   │    │ (both pipelines) │   │ analyzer (both)  │
│ - Pulls GSC   │    │ - DataForSEO MCP │   │ - SERP via       │
│ - Identifies  │    │ - Filters server │   │   DataForSEO     │
│   gaps        │    │   side           │   │ - Crawl4AI scrape│
└───────────────┘    │ - Caches results │   │ - Extracts gaps  │
                     └──────────────────┘   └──────────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │   content writers       │
                  │  - content-rewriter (A) │
                  │  - content-writer (B)   │
                  │  Both follow Writing    │
                  │  Standards + SEO        │
                  │  Checklist              │
                  └─────────────────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │   quality-checker       │
                  │  - Full SEO checklist   │
                  │  - Writing quality      │
                  │  - Schema validation    │
                  │  - PASS → auto-publish  │
                  │  - FAIL → retry up to 2x│
                  └─────────────────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │   publisher             │
                  │  - Commits to repo      │
                  │  - Triggers deploy      │
                  │  - Updates state        │
                  └─────────────────────────┘
```

---

## 4. Pipeline A — Detailed Flow

### Step A1: Article Ingestion
- Orchestrator reads next article from queue
- Claude Code locates the article file (handled internally by Claude Code's workflow)
- Extract: title, full body, H2/H3 structure, existing frontmatter, current keywords (if any), word count, embedded images and current alt text

### Step A2: GSC Performance Analysis
**Subagent:** `article-auditor`
- Query GSC MCP for the article URL, last 90 days
- Pull: all queries with impressions, position, CTR, clicks
- Identify **near-miss queries**: position 8-20 with ≥100 impressions/month
- Identify **declining queries**: position dropped ≥3 spots in last 30 days
- Output: prioritized list of opportunity queries

### Step A3: Keyword Research
**Subagent:** `kw-researcher`
- Seeds: primary_topic + GSC near-miss queries + GSC declining queries
- DataForSEO endpoints to call:
  - `dataforseo_labs/google/related_keywords/live`
  - `dataforseo_labs/google/keyword_suggestions/live`
  - `dataforseo_labs/google/keyword_ideas/live` (optional, for breadth)
- **Mandatory filter (server-side):**
  ```json
  {
    "filters": [
      ["keyword_data.keyword_info.search_volume", ">=", 500],
      "and",
      ["keyword_properties.keyword_difficulty", "<", 30],
      "and",
      ["keyword_data.search_intent_info.main_intent", "in", ["informational", "navigational"]]
    ],
    "order_by": ["keyword_data.keyword_info.search_volume,desc"],
    "limit": 100
  }
  ```
- All results cached to SQLite before returning (30-day TTL)

### Step A4: Keyword Selection
**Subagent:** `kw-researcher` (continues)
- Score each candidate:
  ```
  score = (search_volume * 0.5)
        + ((30 - keyword_difficulty) * 10)
        + GSC_proximity_bonus
  ```
  Where `GSC_proximity_bonus = +50` if the keyword already appears in the GSC near-miss list.
- Select final 5-10:
  - 1 primary (highest score, best intent match)
  - 2-3 secondary (related, distinct angles)
  - 3-6 semantic supporting (LSI terms, related concepts)
- Output: structured JSON with primary/secondary/supporting classification + intent tag per keyword

### Step A5: Competitor SERP Analysis
**Subagent:** `competitor-analyzer`
- DataForSEO `serp/google/organic/live`: pull top 5 ranking URLs for primary keyword
- Crawl4AI scrapes those 5 URLs
- Extract:
  - H2/H3 structure (what subtopics they cover)
  - Word counts (set the rewrite's target depth)
  - Semantic terms they use repeatedly
  - Schema types they implement
  - Content gaps (subtopics ≤2 of 5 competitors cover well — opportunity)
- Output: `competitor-pattern-summary.json`

### Step A6: Rewrite Generation
**Subagent:** `content-rewriter`
- Inputs:
  - Original article (preserve unique opinions, code examples, personal voice)
  - Selected keywords from A4
  - Competitor patterns from A5
  - Voice/style guide (Claude Code selects appropriate one from existing designed files)
  - Writing Standards module (Section 7)
  - On-Page SEO Checklist (Section 8)
- Constraints:
  - 1,500-2,000 words
  - Primary KW in title, H1, first 100 words, and conclusion
  - Secondary KWs distributed across H2s (one per H2 minimum)
  - Semantic supporting keywords woven naturally through body
  - All original code blocks preserved (validated post-write)
  - At least 2 competitor gaps filled
- Output: rewritten article in markdown with frontmatter

### Step A7: Quality Check
**Subagent:** `quality-checker` — see Section 9 for full checklist

### Step A8: Auto-Publish
**Subagent:** `publisher` — see Section 10

---

## 5. Pipeline B — Detailed Flow

### Step B1: Topic Selection
- Orchestrator pulls next topic from queue (Claude Code manages topic discovery and queue)
- Verify topic not already covered (check against existing article state)
- Topic must fall within AI / Productivity category

### Step B2: Keyword Research
**Subagent:** `kw-researcher`
- Broader expansion than Pipeline A (no existing article context)
- Same DataForSEO endpoints as A3
- Same server-side filter as A3 (KD <30, volume ≥500)
- Pull 30-50 candidates before clustering

### Step B3: Keyword Clustering & Selection
**Subagent:** `kw-researcher` (continues)
- Cluster candidates by sub-intent:
  - Tutorial / How-to
  - Comparison
  - Listicle
  - Explainer / Definition
  - Review
- Select 7-12 keywords:
  - 1-2 primary (highest score per scoring formula in A4)
  - 3-4 secondary
  - 4-6 semantic supporting
- Determine article format from dominant cluster intent

### Step B4: Competitor SERP Analysis
**Subagent:** `competitor-analyzer`
- Same as A5, but pull top 5-7 competitors instead of 5
- Average competitor word count informs final length within 2,500-3,500 range
- Content gap identification is critical (Pipeline B's "better than competitors" requirement)

### Step B5: Outline Generation
**Subagent:** `content-writer` (outline mode)
- Generate H1, H2s (8-12), H3 substructure
- Map each keyword to specific section (no clustering all in one place)
- Required sections: intro with TL;DR, problem framing, main body, examples/code, FAQ, conclusion + CTA
- Flag: required code snippets, tables, diagrams

### Step B6: Article Generation
**Subagent:** `content-writer` (full mode)
- Inputs:
  - Outline from B5
  - Keyword map from B3
  - Competitor gaps from B4
  - Voice/style guide (Claude Code selects appropriate one)
  - Writing Standards module
  - On-Page SEO Checklist
- Constraints:
  - 2,500-3,500 words
  - Primary KW in title, H1, first 100 words, conclusion, and at least one H2
  - Secondary KWs distributed (one per H2 minimum)
  - Working code examples where applicable
  - At least 1 comparison table or structured list
  - FAQ section with 3-5 questions (use People Also Ask data from DataForSEO if available)
  - Conclusion with clear CTA
  - At least 3 competitor gaps filled
- Output: article markdown + frontmatter

### Step B7: Image/Diagram Suggestions
**Subagent:** `content-writer` (post-generation)
- Generate `image-suggestions.md` alongside the article
- Per suggestion include:
  - Location in article (e.g., "after H2: How Claude Code subagents work")
  - Suggested type (diagram / screenshot / illustration / chart)
  - Description (1-2 sentences)
  - Suggested alt text (descriptive, may include secondary keyword if natural)
- Minimum 3 image suggestions per article, maximum 6
- **This step is exclusive to Pipeline B.**

### Step B8: Quality Check
**Subagent:** `quality-checker` — see Section 9

### Step B9: Auto-Publish
**Subagent:** `publisher` — see Section 10

---

## 6. Subagent Responsibility Matrix

| Subagent | Pipeline A | Pipeline B | Core Responsibility |
|---|---|---|---|
| `orchestrator` | ✅ | ✅ | Queue management, dispatch, retry logic, state tracking |
| `article-auditor` | ✅ | ❌ | GSC analysis, near-miss identification |
| `kw-researcher` | ✅ | ✅ | All DataForSEO calls, filtering, scoring, caching |
| `competitor-analyzer` | ✅ | ✅ | SERP pull, competitor scraping, gap identification |
| `content-rewriter` | ✅ | ❌ | Rewrites existing article preserving unique assets |
| `content-writer` | ❌ | ✅ | Generates new article from scratch + image suggestions |
| `quality-checker` | ✅ | ✅ | Final SEO + writing quality validation (sole publish gate) |
| `publisher` | ✅ | ✅ | Commits article, triggers deploy, updates state |

---

## 7. Writing Standards (Both Writers)

All content produced by `content-rewriter` and `content-writer` must satisfy these requirements:

### Content Quality

| Requirement | Definition / Validation |
|---|---|
| **Semantic** | Keywords used naturally in context, related LSI terms woven in, no stuffing |
| **Skimmable** | Paragraphs ≤4 sentences; bullet/numbered lists where appropriate; bolded key terms; clear H2/H3 hierarchy; TL;DR or summary in intro |
| **Easy to read** | Flesch Reading Ease ≥60; avg sentence length ≤20 words; no jargon walls |
| **Better than competitors** | Must cover what competitors cover plus fill at least 2 (Pipeline A) or 3 (Pipeline B) identified content gaps |
| **Grammatically correct** | Validated by quality-checker |
| **Active voice** | Passive voice ratio ≤10% across the article |
| **Valuable to users** | Every section must answer a real question or solve a real problem; no filler |
| **Naturally written** | Varied sentence structure; no AI cliché phrases (see banned-phrase list); voice consistent with selected voice/style guide |

### Banned Phrases (enforced by quality-checker)

A non-exhaustive list. Maintained as `banned-phrases.txt` (Claude Code creates and maintains):
- "In conclusion,"
- "It's important to note,"
- "delve into" / "delving into"
- "navigate the landscape" / "navigating the"
- "in today's fast-paced world"
- "harness the power of"
- "unlock the potential"
- "game-changer" / "game-changing"
- "revolutionize" / "revolutionizing"
- "cutting-edge" (when used as filler)
- "robust solution"
- "seamlessly integrate"
- "leverage" (when "use" would work)
- "Furthermore," (when overused — limit to 1 per article)
- "Moreover," (same limit)

If any banned phrase appears more than once or in a forced way, quality-checker fails the draft.

---

## 8. On-Page SEO Checklist (Both Writers)

### Must-haves (mandatory — quality-checker rejects on any miss)

| Element | Pipeline A | Pipeline B | Notes |
|---|---|---|---|
| Primary KW in title | ✅ | ✅ | Front-loaded, within first 60 chars |
| Primary KW in H1 | ✅ | ✅ | H1 typically matches title in Astro |
| Primary KW in ≥1 H2 | ✅ | ✅ | |
| Primary KW in first 100 words | ✅ | ✅ | |
| Primary KW in conclusion | ✅ | ✅ | |
| Meta description | ✅ | ✅ | 150-160 chars, includes primary KW |
| Image alt text | If images | ✅ | Descriptive, may include keyword naturally |
| Internal links | ✅ | ✅ | Handled by internal-linking plugin (already installed) |
| External links | ✅ (2-3) | ✅ (3-5) | Authoritative sources only |
| Schema markup (JSON-LD) | ✅ | ✅ | Auto-selected: Article / HowTo / FAQ based on intent |
| Frontmatter complete | ✅ | ✅ | title, description, keywords, category, tags, date, author |

### Additional requirements

- **Internal link suggestions:** Generated by quality-checker for the internal-linking plugin to consume (plugin handles actual insertion)
- **External authoritative reference suggestions:** Writer includes inline; quality-checker validates domain authority of cited sources
- **Image/diagram ideas:** Pipeline B only — generated as separate `image-suggestions.md` file

### Schema Markup Templates

Writer selects automatically:
- `Article` — default for explainers, news, opinion
- `HowTo` — for tutorials with explicit step structure
- `FAQ` — embedded within article when FAQ section is present (both Article + FAQ schemas can coexist)
- `SoftwareApplication` or `Product` — when reviewing/comparing tools (Pipeline B)

JSON-LD is embedded in the article frontmatter or as an inline script block, per Astro conventions.

---

## 9. Quality Checker — Full Checklist

Quality-checker is the **sole publish gate**. It runs every check below. ANY failure → return to writer subagent with specific failure reason. Maximum 2 retries. If still failing after retry 2, log to `failed-articles.log` and skip.

### SEO Validation

- [ ] Primary KW in title
- [ ] Primary KW in H1
- [ ] Primary KW in ≥1 H2
- [ ] Primary KW in first 100 words
- [ ] Primary KW in conclusion
- [ ] Meta description present, 150-160 chars, contains primary KW
- [ ] Schema markup present and valid JSON-LD
- [ ] Frontmatter complete (title, description, keywords, category, tags, date)
- [ ] External links present and authoritative (Pipeline A: 2-3, Pipeline B: 3-5)
- [ ] Image alt text descriptive (where images exist)

### Writing Quality

- [ ] Word count in target range (A: 1500-2000, B: 2500-3500)
- [ ] Passive voice ratio ≤10%
- [ ] Average sentence length ≤20 words
- [ ] Flesch Reading Ease ≥60
- [ ] No paragraph longer than 4 sentences
- [ ] No banned phrase used more than once
- [ ] No forced/awkward keyword insertion (semantic naturalness check)

### Keyword Distribution

- [ ] Primary KW density: 0.8% - 1.5%
- [ ] Secondary KW density: 0.3% - 0.7% each
- [ ] Each secondary KW appears in at least one H2 or H3
- [ ] Semantic supporting terms distributed (no single section monopolizes)

### Content Coverage

- [ ] Required competitor gaps filled (A: ≥2, B: ≥3)
- [ ] FAQ section present (mandatory for B, optional for A)
- [ ] Conclusion with CTA present
- [ ] All original code examples preserved (Pipeline A only)

### Pipeline B Additional

- [ ] `image-suggestions.md` present with 3-6 suggestions
- [ ] At least 1 comparison table or structured list in article body
- [ ] Working code examples (where topic applies)

### Output

Quality-checker produces `quality-report.md` for every article (whether passed or failed) containing:
- Pass/fail per check
- Specific failure reasons (if any)
- Suggested fixes (sent back to writer on retry)
- Final verdict: PUBLISH / RETRY / FAIL

---

## 10. Publisher Subagent — Auto-Publish Flow

Triggered only when quality-checker returns PUBLISH.

### Steps

1. **Final integrity check:** Confirm article markdown is valid, frontmatter parses, no broken markdown syntax
2. **Internal link insertion:** Hand article off to the internal-linking plugin (already installed); plugin inserts links based on suggestions from quality-checker
3. **Commit to repo:** Place article in correct Astro content collection path (Claude Code determines path based on category)
4. **Deploy trigger:** Cloudflare Pages auto-deploys on commit; no manual trigger needed
5. **State update:** Mark article as `published` in state with timestamp and live URL
6. **Post-publish:** Submit URL to Google Search Console for indexing (via GSC MCP if endpoint available, else log for manual submission)
7. **Notification (optional):** Log publish to `published.log` with article ID, URL, primary keyword, publish time

### Rollback

If publish fails (commit error, repo conflict, deploy failure):
- Mark state as `publish-failed`
- Article remains in `output/` directory
- Log error to `runs.log`
- Do not retry automatically — Claude Code handles next steps

---

## 11. State Management

### `data/article-state.json`

Tracks every article through the pipeline. Schema:

```json
{
  "articles": [
    {
      "id": "uuid",
      "pipeline": "A" | "B",
      "source_path": "path/or/topic",
      "primary_keyword": "string",
      "status": "queued" | "researching" | "writing" | "quality-checking" | "publishing" | "published" | "failed",
      "retries": 0,
      "last_failure_reason": null,
      "created_at": "iso-timestamp",
      "published_at": "iso-timestamp | null",
      "live_url": "string | null"
    }
  ]
}
```

### `data/kw-cache.sqlite`

Schema:
```sql
CREATE TABLE keyword_cache (
  keyword TEXT PRIMARY KEY,
  search_volume INTEGER,
  keyword_difficulty INTEGER,
  search_intent TEXT,
  cpc REAL,
  competition_level TEXT,
  raw_response TEXT,
  fetched_at TIMESTAMP,
  expires_at TIMESTAMP
);

CREATE INDEX idx_expires ON keyword_cache(expires_at);
```

TTL: 30 days. kw-researcher must check cache before any DataForSEO call.

---

## 12. Tooling Stack

### MCPs (configured in `.claude/settings.json` — Claude Code sets this up)

- **DataForSEO MCP** — primary keyword research, SERP data
- **GSC MCP** — existing article performance (Pipeline A)
- Other MCPs as needed (Claude Code determines)

### Plugins / Existing Tools

- **Internal linking plugin** — already installed; receives link suggestions from quality-checker; inserts links into final article
- **Voice/style guide files** — already designed; Claude Code selects appropriate one per article based on topic/category
- **Crawl4AI** — already configured; used by competitor-analyzer

### Storage

- **SQLite** — keyword cache, state management
- **Local markdown files** — drafts and final articles
- **Astro content collection** — final publish destination

---

## 13. Error Handling & Retry Logic

### Subagent failures

| Failure type | Retry policy |
|---|---|
| DataForSEO API error | 3 retries with exponential backoff (1s, 4s, 16s) |
| GSC API error | 2 retries, then proceed without GSC data (Pipeline A only) |
| Crawl4AI timeout | 2 retries, then proceed with fewer competitors |
| Writer subagent failure | 2 retries with refined prompt |
| Quality-checker rejection | Send back to writer with reasons, max 2 rewrite cycles |
| Publisher failure | No auto-retry; log and stop for that article |

### Pipeline-level failure

If an article fails after all retries:
- Status → `failed`
- Logged with full context to `failed-articles.log`
- Pipeline continues with next article in queue
- Failed articles never block subsequent runs

---

## 14. Cost Projections

### One-time costs (Pipeline A — rewrite 60 articles)

- DataForSEO: ~$3-9 total (3 endpoints/article × 60 articles, server-side filtering keeps costs minimal)
- All other tools: free / already paid

### Recurring costs (Pipeline B — 365 articles/year)

- DataForSEO: ~$30-75/year (4 endpoints/article × 365)
- All other tools: free / already paid

### Year 1 total: ~$35-85 for ~425 articles

DataForSEO PAYG $50 deposit covers the first ~6-9 months comfortably with caching benefits compounding over time.

---

## 15. Notes for Claude Code Implementation

### What Claude Code creates from this spec

1. All seven subagent definition files in `.claude/agents/`
2. `CLAUDE.md` project-level rules
3. `.claude/settings.json` with MCP connections
4. Initial SQLite schema setup
5. State file initialization
6. Logging configuration
7. Banned-phrases list (initial seed from Section 7)
8. Any scripts needed for orchestration

### What Claude Code is responsible for figuring out

- Exact Astro repo structure and article file paths
- Voice/style guide file selection logic (matching topic to appropriate guide)
- Topic queue management for Pipeline B (discovery method, deduplication)
- Daily trigger mechanism (manual command vs. scheduled)
- Internal-linking plugin invocation interface

### Implementation principles

- **Cache aggressively:** Every DataForSEO response goes to SQLite first
- **Fail loudly, recover gracefully:** Errors logged with full context; pipeline continues
- **Quality over volume:** Better to fail-and-log a bad article than publish one that doesn't meet the checklist
- **No external review needed:** Quality-checker is the sole gate; trust it but make it strict

### What this spec does NOT cover (intentionally)

- File system layout beyond high-level structure (Claude Code decides)
- Specific MCP tool names/parameters (Claude Code discovers via tool_search)
- Cron/scheduling implementation details (Claude Code handles)
- Voice/style guide content (already exists, Claude Code references)
- Internal-linking plugin internals (already installed, Claude Code invokes)

---

## End of Specification

This document is the source of truth for the devnook.dev content pipeline architecture. Claude Code reads this spec and builds the implementation accordingly. Any deviation from this spec by Claude Code must be flagged and approved before proceeding.
