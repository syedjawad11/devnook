"""
SQLite registry helpers for DevNook pipeline agents.
All pipeline agents read/write registry.db through this module.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "content-team" / "registry.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def slug_exists(slug: str) -> bool:
    with get_db() as db:
        return db.execute("SELECT 1 FROM posts WHERE slug=?", (slug,)).fetchone() is not None


def get_queued_posts(limit: int = 50) -> list:
    with get_db() as db:
        return db.execute(
            "SELECT * FROM posts WHERE status='queued' ORDER BY opportunity_score DESC LIMIT ?",
            (limit,)
        ).fetchall()


def get_published_slugs() -> list:
    with get_db() as db:
        rows = db.execute(
            "SELECT slug FROM posts WHERE status IN ('approved','staged','published')"
        ).fetchall()
        return [r["slug"] for r in rows]


def add_post(
    slug: str,
    title: str,
    description: str,
    category: str,
    language: str = None,
    concept: str = None,
    template_id: str = None,
    keyword: str = None,
    opportunity_score: float = None,
) -> bool:
    """Add a post to the registry. Returns False if slug already exists."""
    if slug_exists(slug):
        return False
    with get_db() as db:
        db.execute(
            """
            INSERT INTO posts (slug, title, description, category, language, concept,
                               template_id, keyword, opportunity_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued')
            """,
            (slug, title, description, category, language, concept,
             template_id, keyword, opportunity_score),
        )
    return True


def update_post_status(slug: str, status: str, **kwargs):
    """Update post status and any additional fields."""
    with get_db() as db:
        fields = ["status=?", "updated_at=datetime('now')"]
        values = [status]
        for key, val in kwargs.items():
            fields.append(f"{key}=?")
            values.append(val)
        values.append(slug)
        db.execute(f"UPDATE posts SET {', '.join(fields)} WHERE slug=?", values)


def get_next_template(category: str) -> str:
    """Round-robin template selection — returns the least-used template for a category."""
    template_map = {
        "languages":   ["lang-v1", "lang-v2", "lang-v3", "lang-v4", "lang-v5"],
        "guides":      ["guide-v1", "guide-v2", "guide-v3", "guide-v4"],
        "blog":        ["blog-v1", "blog-v2", "blog-v3", "blog-v4", "blog-v5"],
        "cheatsheets": ["cheatsheet-v1", "cheatsheet-v2", "cheatsheet-v3", "cheatsheet-v4"],
        "tools":       ["tool-exp-v1", "tool-exp-v2", "tool-exp-v3", "tool-exp-v4"],
    }
    templates = template_map.get(category, ["lang-v1"])
    placeholders = ",".join("?" * len(templates))
    with get_db() as db:
        result = db.execute(
            f"SELECT template_id FROM template_counters WHERE template_id IN ({placeholders}) "
            f"ORDER BY usage_count ASC LIMIT 1",
            templates,
        ).fetchone()
        template = result["template_id"] if result else templates[0]
        db.execute(
            "UPDATE template_counters SET usage_count=usage_count+1, last_used=datetime('now') "
            "WHERE template_id=?",
            (template,),
        )
    return template


def log_pipeline_run(
    run_date: str,
    step: str,
    processed: int,
    passed: int,
    rejected: int,
    duration: float,
    notes: str = "",
    model_used: str = "",
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost_usd: float = 0.0,
):
    with get_db() as db:
        db.execute(
            """
            INSERT INTO pipeline_runs
                (run_date, step, posts_processed, posts_passed, posts_rejected,
                 duration_seconds, notes, model_used, input_tokens, output_tokens, estimated_cost_usd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_date, step, processed, passed, rejected, duration, notes,
             model_used, input_tokens, output_tokens, estimated_cost_usd),
        )
