-- registry.db schema dump (auto-generated)
CREATE TABLE clusters (
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
);

CREATE TABLE editorial_opportunity (
          id               INTEGER PRIMARY KEY AUTOINCREMENT,
          topic_seed       TEXT NOT NULL,
          cluster_label    TEXT,
          keyword          TEXT NOT NULL,
          volume           INTEGER DEFAULT 0,
          kd               REAL DEFAULT 0,
          tier             TEXT DEFAULT 'pending'
                           CHECK(tier IN ('primary','secondary','fallback',
                                         'low-confidence','pending')),
          source           TEXT DEFAULT 'matrix',
          opportunity_score REAL DEFAULT 0,
          status           TEXT DEFAULT 'pending'
                           CHECK(status IN ('pending','queued','skipped')),
          fetched_at       TEXT DEFAULT (datetime('now')),
          UNIQUE(keyword)
        );

CREATE TABLE fetched_seeds (seed TEXT PRIMARY KEY, fetched_at TEXT DEFAULT (datetime('now')));

CREATE TABLE keyword_pool (
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
);

CREATE TABLE keyword_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    research_run_at TEXT NOT NULL,
    total_keywords INTEGER,
    primary_count INTEGER,
    secondary_count INTEGER,
    status TEXT DEFAULT 'ready',
    notes TEXT
, cluster_id INTEGER REFERENCES clusters(id), category TEXT, content_collection TEXT DEFAULT 'blog');

CREATE TABLE keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_set_id INTEGER NOT NULL,
    topic_id INTEGER NOT NULL,
    slug TEXT NOT NULL,
    keyword TEXT NOT NULL,
    keyword_type TEXT NOT NULL,
    search_volume INTEGER,
    keyword_difficulty INTEGER,
    cpc REAL,
    intent TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(keyword_set_id, keyword)
);

CREATE TABLE language_opportunity (
          id               INTEGER PRIMARY KEY AUTOINCREMENT,
          language         TEXT NOT NULL,
          concept          TEXT NOT NULL,
          canonical_keyword TEXT,
          volume           INTEGER DEFAULT 0,
          kd               REAL DEFAULT 0,
          opportunity_score REAL DEFAULT 0,
          has_demand       INTEGER DEFAULT 0,
          status           TEXT DEFAULT 'pending'
                           CHECK(status IN ('pending','queued','skipped')),
          fetched_at       TEXT DEFAULT (datetime('now')), keywords_json TEXT,
          UNIQUE(language, concept)
        );

CREATE TABLE pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT NOT NULL,
    step TEXT NOT NULL,              -- keyword, planner, writer, seo, qa, staging
    posts_processed INTEGER DEFAULT 0,
    posts_passed INTEGER DEFAULT 0,
    posts_rejected INTEGER DEFAULT 0,
    duration_seconds REAL,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
, model_used TEXT, fallback_triggered INTEGER DEFAULT 0, input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0, estimated_cost_usd REAL DEFAULT 0.0);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    language TEXT,
    concept TEXT,
    template_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'discovered',
    keyword TEXT,
    opportunity_score REAL,
    word_count INTEGER,
    similarity_score REAL,
    internal_links INTEGER,
    published_date TEXT,
    staged_at TEXT,
    published_at TEXT,
    file_path TEXT,
    qa_status TEXT,
    qa_notes TEXT,
    rejection_reason TEXT,
    created_at TEXT DEFAULT (CURRENT_TIMESTAMP),
    updated_at TEXT DEFAULT (CURRENT_TIMESTAMP),
    content_type TEXT CHECK(content_type IN ('editorial','programmatic')) DEFAULT 'editorial',
    source TEXT CHECK(source IN ('claude_code','antigravity','pipeline_b','pipeline_core')) DEFAULT 'claude_code'
);

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE template_counters (
    template_id TEXT PRIMARY KEY,
    usage_count INTEGER DEFAULT 0,
    last_used TEXT
);

CREATE INDEX idx_edit_opp_tier
        ON editorial_opportunity(tier, opportunity_score DESC)
    ;

CREATE INDEX idx_lang_opp_score
        ON language_opportunity(has_demand, opportunity_score DESC)
    ;

-- Row counts
-- clusters: 7 rows
-- editorial_opportunity: 4681 rows
-- fetched_seeds: 269 rows
-- keyword_pool: 68 rows
-- keyword_sets: 5 rows
-- keywords: 49 rows
-- language_opportunity: 240 rows
-- pipeline_runs: 16 rows
-- posts: 91 rows
-- sqlite_sequence: 8 rows
-- template_counters: 22 rows
