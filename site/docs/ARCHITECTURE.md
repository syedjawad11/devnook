# DevNook Architecture

## Site Overview

- **Framework:** Astro 4.x, static output (`output: 'static'`)
- **Hosting:** Cloudflare Pages — auto-deploy on push to `main`
- **Content:** Markdown files in `src/content/` written by the content pipeline
- **Tools:** 18 client-side browser tools in `public/tools/*.html`, routed via `src/pages/tools/[slug].astro`

---

## Monorepo Layout

Site and pipeline live in one repo (`syedjawad11/devnook`) since the Stage 8 merge.

```
devnook/
├── site/                       ← Astro site (this sub-project)
│   ├── src/content/            ← Published posts (written by the pipeline)
│   ├── src/plugins/            ← Build-time rehype/remark plugins
│   ├── agents/subagent-prompts/← Dev subagent prompts
│   └── docs/ARCHITECTURE.md    ← this file
├── pipeline/                   ← Content pipeline (formerly devnook_content_workspace)
│   ├── .claude/agents/         ← Pipeline subagent prompts
│   ├── agents/publish/publish.py ← Drip publisher
│   └── data/registry.db        ← SQLite registry
├── docs/                       ← Monorepo overview (ARCHITECTURE.md) + STATUS.md
└── CLAUDE.md                   ← root nav
```

The pipeline pushes finished posts to `devnook/src/content/` via a PAT-authenticated git push.

---

## Content Pipeline (Pipeline B — keyword-first, cluster-driven)

### Stage 0 — Harvest & Cluster (LOCAL ONLY)
- Calls DataForSEO `keyword_suggestions/live` per seed bucket
- Embeds keywords via Gemini `text-embedding-004` (768-dim)
- Clusters with `AgglomerativeClustering(metric='cosine', distance_threshold=0.18)`
- Scores viability: `primary≥2 AND secondary≥6 AND longtail≥1`
- Writes to `keyword_pool` and `clusters` tables in `data/registry.db`

### Stage 1 — Keywords
- Input: `CLUSTER_ID`
- Reads `keyword_pool WHERE cluster_id=?`
- Selects 8–12 keywords (primary KD<30/vol≥500, secondary KD<40/vol≥1000)
- Synthesizes title, slug, description via Gemini Flash
- Writes `keyword_sets` + `keywords` rows; marks cluster `used`

### Stage 2 — Writer
- Input: `keyword_set_id`
- Reads keywords from DB; writes 2,500–3,500 word draft to `content-staging/`
- Categories: `Comparisons`, `AI & Productivity`, `Tools & Workflows`

### Stage 3 — QA + Publish
- 2,500-word hard floor; schema enum check; link validity; dup check; cluster-collision guard
- On pass: moves file from `content-staging/` to `devnook/src/content/`, commits, pushes
- Updates registry: `status='published'`, `published_at`, `published_date`

### Orchestrator (v2)
- Counts viable clusters; auto-triggers Stage 0 top-up if low
- Selects top-N by volume; loops Stage 1→2→3 per cluster
- `MAX_ARTICLES_PER_RUN=5` (configurable)

---

## Registry Schema

Single DB at `data/registry.db` (in content workspace).

### `posts` (main content registry)
```sql
posts (
  slug TEXT PRIMARY KEY,
  title TEXT,
  description TEXT,
  category TEXT,          -- blog | guides | cheatsheets | languages | tools
  language TEXT,          -- for languages category only
  concept TEXT,           -- URL segment for /languages/{lang}/{concept}
  template_id TEXT,
  keyword TEXT,
  opportunity_score REAL,
  status TEXT,            -- queued → drafted → approved → staged → published | rejected
  content_type TEXT,      -- programmatic | editorial
  source TEXT,            -- pipeline_a | pipeline_b
  qa_status TEXT,
  file_path TEXT,
  published_at TEXT,
  published_date TEXT,
  created_at TEXT
)
```

### `keyword_sets` (Pipeline B topics)
```sql
keyword_sets (
  id INTEGER PRIMARY KEY,
  slug TEXT,
  title TEXT,
  category TEXT,
  cluster_id INTEGER,     -- FK → clusters.id
  status TEXT             -- ready | used | insufficient_keywords
)
```

### `clusters` (keyword clusters from Stage 0)
```sql
clusters (
  id INTEGER PRIMARY KEY,
  label TEXT,
  bucket TEXT,
  category TEXT,
  primary_count INTEGER,
  secondary_count INTEGER,
  longtail_count INTEGER,
  viable INTEGER,         -- 1 if primary≥2 AND secondary≥6 AND longtail≥1
  keyword_set_id INTEGER, -- FK → keyword_sets.id (set when cluster is used)
  status TEXT             -- pending | used
)
```

### `keyword_pool` (harvest universe)
```sql
keyword_pool (
  id INTEGER PRIMARY KEY,
  keyword TEXT,
  search_volume INTEGER,
  keyword_difficulty INTEGER,
  cpc REAL,
  keyword_type TEXT,      -- primary | secondary | longtail
  cluster_id INTEGER,     -- FK → clusters.id
  bucket TEXT,
  embedding BLOB          -- Gemini text-embedding-004 (768 dims, excluded from sqldump)
)
```

---

## Status Lifecycle

```
queued → outlined → drafted → linked → approved → staged → published
                                                          ↘ rejected
```

---

## URL Conventions

- Language posts: `/languages/{language}/{concept}` — `concept` is the canonical slug, NOT the filename
- Blog: `/blog/{slug}`
- Guides: `/guides/{slug}`
- Cheatsheets: `/cheatsheets/{slug}`
- Tools: `/tools/{slug}`

**Critical:** Never derive language post URLs from filenames. Always use `concept` from registry.

### Slug conventions (enforced by schema)

| Field | Rule | Example |
|-------|------|---------|
| `language` | Must be one of the 12 allowed values | `go`, `python`, `javascript` |
| `concept` | Lowercase kebab-case (`/^[a-z0-9-]+$/`) | `goroutines`, `async-await` |
| `slug` (blog/guides) | Lowercase kebab-case | `react-vs-angular-vs-vue-comparison` |

Allowed language values: `python`, `javascript`, `typescript`, `go`, `rust`, `java`, `csharp`, `php`, `ruby`, `swift`, `kotlin`, `cpp`

Any file with `language: "google-forms"` or other non-enum value will cause `astro build` to fail immediately.

---

## Build Plugins

### `src/plugins/auto-internal-links/index.mjs`
Build-time rehype plugin. Scans all content dirs (`guides`, `blog`, `cheatsheets`, `languages`) for anchor matches. Uses `devnookUrlBuilder` to generate correct URLs (language posts use `frontmatter.language` + `frontmatter.concept`). Config: `autoAnchors: true` in `astro.config.mjs`.

Known issue: bare language names ≤6 chars (`go`, `rust`, `swift`, `java`) currently excluded by a string-length gate — fix targeted in Stage 7.

### `src/plugins/related-callouts/index.mjs`
Build-time rehype plugin. Injects up to 3 `<aside class="related-callout">` nodes at interior H2 boundaries. Scoring mirrors `PostLayout.astro`. Per-post opt-out: `excludeRelatedCallouts: true` in frontmatter.

---

## CI Workflows (content workspace)

| Workflow | Trigger | Action |
|----------|---------|--------|
| `drip-publish.yml` | Daily cron 08:00 UTC | Publish 2 staged posts |
| `on-demand-publish.yml` | Manual | Publish N posts |

Both workflows checkout content workspace + devnook side-by-side, run `publish.py`, commit staging deletions + registry changes to content workspace, and push new posts to devnook.

---

## Deployment

Cloudflare Pages — connected to `syedjawad11/devnook`, deploying from root, output dir `dist/`. Every push to `main` triggers a deploy. Do NOT use `[skip ci]` in devnook commit messages — Cloudflare honors it and skips the build.
