-- DevNook Content Registry
-- Run: sqlite3 agents/content-team/registry.db < registry-schema.sql

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,           -- languages, guides, blog, cheatsheets, tools
    language TEXT,                    -- python, javascript, etc. (null if not lang post)
    concept TEXT,                     -- kebab-case concept name (null if not lang post)
    template_id TEXT NOT NULL,        -- lang-v1, guide-v2, etc.
    status TEXT NOT NULL DEFAULT 'discovered',
    -- Status flow: discovered → queued → drafted → optimized → approved → staged → published
    keyword TEXT,                     -- primary SEO keyword
    opportunity_score REAL,          -- planner agent score (0–100)
    word_count INTEGER,
    similarity_score REAL,           -- TF-IDF similarity to nearest existing post
    internal_links INTEGER,
    published_date TEXT,             -- YYYY-MM-DD
    staged_at TEXT,                  -- ISO timestamp
    published_at TEXT,               -- ISO timestamp
    file_path TEXT,                  -- relative path to .md file
    qa_status TEXT,                  -- approved, rejected, warning
    qa_notes TEXT,                   -- JSON string of QA results
    rejection_reason TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS template_counters (
    template_id TEXT PRIMARY KEY,
    usage_count INTEGER DEFAULT 0,
    last_used TEXT
);

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,
    search_volume_estimate INTEGER,
    competition TEXT,                 -- low, medium, high
    assigned_slug TEXT,              -- FK to posts.slug (nullable)
    status TEXT DEFAULT 'discovered', -- discovered, assigned, published
    discovered_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT NOT NULL,
    step TEXT NOT NULL,              -- keyword, planner, writer, seo, qa, staging
    posts_processed INTEGER DEFAULT 0,
    posts_passed INTEGER DEFAULT 0,
    posts_rejected INTEGER DEFAULT 0,
    duration_seconds REAL,
    notes TEXT,
    model_used TEXT,                 -- actual model used (may be fallback)
    fallback_triggered INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    estimated_cost_usd REAL DEFAULT 0.0,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Initialize template counters
INSERT OR IGNORE INTO template_counters (template_id, usage_count) VALUES
    ('lang-v1', 0), ('lang-v2', 0), ('lang-v3', 0), ('lang-v4', 0), ('lang-v5', 0),
    ('guide-v1', 0), ('guide-v2', 0), ('guide-v3', 0), ('guide-v4', 0),
    ('blog-v1', 0), ('blog-v2', 0), ('blog-v3', 0), ('blog-v4', 0), ('blog-v5', 0),
    ('cheatsheet-v1', 0), ('cheatsheet-v2', 0), ('cheatsheet-v3', 0), ('cheatsheet-v4', 0),
    ('tool-exp-v1', 0), ('tool-exp-v2', 0), ('tool-exp-v3', 0), ('tool-exp-v4', 0);

CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_language ON posts(language);
CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);
