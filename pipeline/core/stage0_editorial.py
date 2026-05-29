"""
stage0_editorial.py — Editorial opportunity queue.

Reads from editorial_opportunity table (populated by the @pipeline-b-stage0-editorial
LOCAL-ONLY agent that calls DataForSEO MCP tools).

Tier classification:
  primary      — Vol 100–800, KD < 15   (low-comp, achievable)
  secondary    — Vol > 500,  KD < 30    (higher-comp, medium-term)
  fallback     — KD < 35               (queued last, tagged as stretch)
  low-confidence — zero volume or zero KD (manual review bucket)

Usage:
  python -m pipeline.core.runner --profile editorial --limit 10
"""

import sqlite3
from pathlib import Path
from typing import Any


def classify_tier(volume: int, kd: float) -> str:
    if volume == 0 or kd == 0:
        return "low-confidence"
    if 100 <= volume <= 800 and kd < 15:
        return "primary"
    if volume > 500 and kd < 30:
        return "secondary"
    if kd < 35:
        return "fallback"
    return "low-confidence"


def run_migration(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS editorial_opportunity (
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
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_edit_opp_tier
        ON editorial_opportunity(tier, opportunity_score DESC)
    """)
    conn.commit()
    conn.close()


def upsert_opportunity(
    db_path: Path,
    topic_seed: str,
    cluster_label: str,
    keyword: str,
    volume: int,
    kd: float = 0.0,
    source: str = "matrix",
) -> None:
    """Insert one keyword opportunity. First-write wins on UNIQUE(keyword) conflict."""
    tier = classify_tier(volume, kd)
    opportunity_score = float(volume) * (100.0 - kd) / 100.0 if kd < 100 else 0.0
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """INSERT INTO editorial_opportunity
               (topic_seed, cluster_label, keyword, volume, kd,
                tier, source, opportunity_score, fetched_at)
           VALUES (?,?,?,?,?,?,?,?,datetime('now'))
           ON CONFLICT(keyword) DO NOTHING""",
        (topic_seed, cluster_label, keyword, volume, kd, tier, source, opportunity_score),
    )
    conn.commit()
    conn.close()


def list_briefs(db_path: Path, limit: int = 10) -> list[dict[str, Any]]:
    """Return top-N editorial opportunities: primaries first, then secondary, then fallback."""
    run_migration(db_path)
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute(
        """SELECT topic_seed, cluster_label, keyword, volume, kd, tier, opportunity_score
           FROM editorial_opportunity
           WHERE tier IN ('primary','secondary','fallback')
             AND status = 'pending'
           ORDER BY
             CASE tier
               WHEN 'primary'   THEN 1
               WHEN 'secondary' THEN 2
               WHEN 'fallback'  THEN 3
               ELSE 4
             END,
             opportunity_score DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {
            "topic_seed": r[0],
            "cluster_label": r[1],
            "keyword": r[2],
            "volume": r[3],
            "kd": r[4],
            "tier": r[5],
            "opportunity_score": round(r[6], 1),
        }
        for r in rows
    ]


def count_by_tier(db_path: Path) -> dict[str, int]:
    """Return row counts grouped by tier."""
    run_migration(db_path)
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute(
        "SELECT tier, COUNT(*) FROM editorial_opportunity GROUP BY tier"
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}
