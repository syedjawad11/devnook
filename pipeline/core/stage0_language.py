"""
stage0_language.py — Language opportunity queue.

Reads from language_opportunity table (populated by the @pipeline-b-stage0-language
LOCAL-ONLY agent that calls DataForSEO MCP tools).

Usage:
  python -m pipeline.core.runner --profile language --limit 5
"""

import sqlite3
from pathlib import Path
from typing import Any

LANGUAGES: list[str] = [
    "python", "javascript", "typescript", "go", "rust",
    "java", "csharp", "php", "ruby", "swift", "kotlin", "cpp",
]

CONCEPTS: list[str] = [
    "async await", "class inheritance", "closure", "context manager",
    "dataclass", "decorator pattern", "dictionary comprehension",
    "environment variables", "error handling", "file handling",
    "generator function", "http requests", "json parsing", "lambda function",
    "list comprehension", "recursion example", "regex pattern",
    "sorting algorithm", "string formatting", "type hints",
]

# Display names for canonical keyword construction
LANG_DISPLAY: dict[str, str] = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "go": "go",
    "rust": "rust",
    "java": "java",
    "csharp": "c#",
    "php": "php",
    "ruby": "ruby",
    "swift": "swift",
    "kotlin": "kotlin",
    "cpp": "c++",
}


def run_migration(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS language_opportunity (
          id               INTEGER PRIMARY KEY AUTOINCREMENT,
          language         TEXT NOT NULL,
          concept          TEXT NOT NULL,
          canonical_keyword TEXT,
          volume           INTEGER DEFAULT 0,
          kd               REAL DEFAULT 0,
          opportunity_score REAL DEFAULT 0,
          has_demand       INTEGER DEFAULT 0,
          keywords_json    TEXT,
          status           TEXT DEFAULT 'pending'
                           CHECK(status IN ('pending','queued','skipped')),
          fetched_at       TEXT DEFAULT (datetime('now')),
          UNIQUE(language, concept)
        )
    """)
    # Add keywords_json to existing DBs that predate this column
    try:
        conn.execute("ALTER TABLE language_opportunity ADD COLUMN keywords_json TEXT")
        conn.commit()
    except Exception:
        pass  # Column already exists
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_lang_opp_score
        ON language_opportunity(has_demand, opportunity_score DESC)
    """)
    conn.commit()
    conn.close()


def upsert_opportunity(
    db_path: Path,
    language: str,
    concept: str,
    canonical_keyword: str,
    volume: int,
    kd: float = 0.0,
) -> None:
    """Insert or update one concept×language cell."""
    has_demand = 1 if volume > 0 else 0
    opportunity_score = float(volume) * (100.0 - kd) / 100.0
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """INSERT INTO language_opportunity
               (language, concept, canonical_keyword, volume, kd,
                opportunity_score, has_demand, fetched_at)
           VALUES (?,?,?,?,?,?,?,datetime('now'))
           ON CONFLICT(language, concept) DO UPDATE SET
               canonical_keyword = excluded.canonical_keyword,
               volume            = excluded.volume,
               kd                = excluded.kd,
               opportunity_score = excluded.opportunity_score,
               has_demand        = excluded.has_demand,
               fetched_at        = excluded.fetched_at""",
        (language, concept, canonical_keyword, volume, kd, opportunity_score, has_demand),
    )
    conn.commit()
    conn.close()


def upsert_keywords_json(
    db_path: Path,
    language: str,
    concept: str,
    keywords_json: str,
) -> None:
    """Store the selected 8-12 keyword targets for a concept×language cell."""
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """UPDATE language_opportunity
           SET keywords_json = ?
           WHERE language = ? AND concept = ?""",
        (keywords_json, language, concept),
    )
    conn.commit()
    conn.close()


def list_briefs(db_path: Path, limit: int = 5) -> list[dict[str, Any]]:
    """Return top-N language opportunities ordered by opportunity_score DESC."""
    run_migration(db_path)
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute(
        """SELECT language, concept, canonical_keyword, volume, kd, opportunity_score
           FROM language_opportunity
           WHERE has_demand = 1
           ORDER BY opportunity_score DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {
            "language": r[0],
            "concept": r[1],
            "canonical_keyword": r[2],
            "volume": r[3],
            "kd": r[4],
            "opportunity_score": round(r[5], 1),
        }
        for r in rows
    ]


def count_status(db_path: Path) -> dict[str, int]:
    """Return row counts grouped by status + demand summary."""
    run_migration(db_path)
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute(
        "SELECT status, COUNT(*) FROM language_opportunity GROUP BY status"
    ).fetchall()
    demand = conn.execute(
        "SELECT has_demand, COUNT(*) FROM language_opportunity GROUP BY has_demand"
    ).fetchall()
    conn.close()
    counts = {r[0]: r[1] for r in rows}
    counts["_with_demand"] = next((r[1] for r in demand if r[0] == 1), 0)
    counts["_total"] = sum(r[1] for r in rows)
    return counts
