"""Shared fixtures for link_utility tests."""

import sqlite3
import tempfile
from pathlib import Path
import pytest


SCHEMA_SQL = Path(__file__).resolve().parents[1] / "registry-schema.sql"


@pytest.fixture
def tmp_registry(tmp_path):
    """Temp SQLite registry pre-populated with fixture posts."""
    db_path = tmp_path / "registry.db"
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL.read_text())

    conn.executemany(
        """INSERT INTO posts
           (slug, title, category, language, concept, template_id, status, opportunity_score)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            ("python-list-comprehensions", "Python List Comprehensions", "languages",
             "python", "list-comprehensions", "lang-v1", "published", 80.0),
            ("what-is-rest-api", "What is a REST API", "guides",
             None, None, "guide-v1", "published", 75.0),
            ("json-formatter", "JSON Formatter Tool", "tools",
             None, None, "tool-exp-v1", "published", 60.0),
        ],
    )
    conn.commit()
    conn.close()
    return str(db_path)


@pytest.fixture
def tmp_draft(tmp_path):
    """Helper: write a draft file and return its path."""
    def _make(slug, category, body, frontmatter_extra=""):
        text = (
            f"---\nslug: {slug}\ncategory: {category}\ntitle: Test Post\n"
            f"{frontmatter_extra}---\n\n{body}"
        )
        p = tmp_path / f"{slug}.md"
        p.write_text(text, encoding="utf-8")
        return str(p)
    return _make
