import sqlite3
from pathlib import Path
from typing import Optional


def get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def get_post(slug: str, db_path: Path) -> Optional[dict]:
    conn = get_conn(db_path)
    row = conn.execute("SELECT * FROM posts WHERE slug=?", (slug,)).fetchone()
    conn.close()
    return dict(row) if row else None


def set_post_status(slug: str, new_status: str, db_path: Path, **extras) -> None:
    conn = get_conn(db_path)
    if extras:
        set_clause = ", ".join(f"{k}=?" for k in extras)
        vals = list(extras.values()) + [slug]
        conn.execute(
            f"UPDATE posts SET status=?, {set_clause}, updated_at=datetime('now') WHERE slug=?",
            [new_status] + vals,
        )
    else:
        conn.execute(
            "UPDATE posts SET status=?, updated_at=datetime('now') WHERE slug=?",
            [new_status, slug],
        )
    conn.commit()
    conn.close()


def get_keywords_for_slug(slug: str, db_path: Path) -> list[dict]:
    conn = get_conn(db_path)
    rows = conn.execute(
        """SELECT k.keyword, k.keyword_type, k.search_volume, k.keyword_difficulty
           FROM keywords k
           JOIN keyword_sets ks ON k.keyword_set_id = ks.id
           WHERE ks.slug = ?
           ORDER BY k.keyword_type, k.search_volume DESC""",
        (slug,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_keyword_set_for_slug(slug: str, db_path: Path) -> Optional[dict]:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT * FROM keyword_sets WHERE slug=? ORDER BY id DESC LIMIT 1", (slug,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def slug_is_published(slug: str, db_path: Path) -> bool:
    conn = get_conn(db_path)
    row = conn.execute(
        "SELECT 1 FROM posts WHERE slug=? AND status='published'", (slug,)
    ).fetchone()
    conn.close()
    return row is not None


def cluster_already_used(cluster_id: int, exclude_slug: str, db_path: Path) -> bool:
    conn = get_conn(db_path)
    row = conn.execute(
        """SELECT 1 FROM clusters c
           JOIN keyword_sets ks ON ks.cluster_id = c.id
           JOIN posts p ON p.slug = ks.slug
           WHERE c.id = ? AND p.slug != ? AND p.status IN ('approved','published')
           LIMIT 1""",
        (cluster_id, exclude_slug),
    ).fetchone()
    conn.close()
    return row is not None
