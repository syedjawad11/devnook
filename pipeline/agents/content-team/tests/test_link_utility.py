"""Tests for agents/content-team/link_utility.py"""

import sys
import importlib.util
from pathlib import Path
import frontmatter

# content-team has a hyphen so standard import won't work
_UTIL = Path(__file__).resolve().parents[1] / "link_utility.py"
_spec = importlib.util.spec_from_file_location("link_utility", _UTIL)
_mod = importlib.util.module_from_spec(_spec)
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root for agents.utils
_spec.loader.exec_module(_mod)
link_post = _mod.link_post
build_anchor_map = _mod.build_anchor_map


def test_fenced_code_not_linked(tmp_registry, tmp_draft):
    body = "Some intro text.\n\n```python\npython list comprehensions example\n```\n"
    path = tmp_draft("my-post", "guides", body)
    result = link_post(path, tmp_registry)
    post = frontmatter.load(path)
    assert "```" in post.content
    # Link inside fenced block must not appear
    assert "[python list comprehensions]" not in post.content


def test_heading_not_linked(tmp_registry, tmp_draft):
    body = "## Python List Comprehensions\n\nSome body text about REST API.\n"
    path = tmp_draft("my-post2", "guides", body)
    link_post(path, tmp_registry)
    post = frontmatter.load(path)
    # Heading line must be unchanged
    assert "## Python List Comprehensions\n" in post.content


def test_self_link_skipped(tmp_registry, tmp_draft):
    body = "This guide is about What is a REST API in detail.\n"
    path = tmp_draft("what-is-rest-api", "guides", body)
    result = link_post(path, tmp_registry)
    post = frontmatter.load(path)
    assert "(/guides/what-is-rest-api)" not in post.content


def test_second_occurrence_not_linked(tmp_registry, tmp_draft):
    body = (
        "Use Python List Comprehensions for filtering.\n"
        "Python List Comprehensions are very useful.\n"
    )
    path = tmp_draft("my-post3", "guides", body)
    link_post(path, tmp_registry)
    post = frontmatter.load(path)
    # Should appear exactly once as a link
    link_count = post.content.count("(/languages/python/list-comprehensions)")
    assert link_count == 1


def test_ninth_anchor_not_linked(tmp_registry, tmp_draft):
    """Cap at 8 links — 9th match must stay plain text."""
    import sqlite3
    conn = sqlite3.connect(tmp_registry)
    # Add 7 more published posts so we have enough anchors
    extras = [
        (f"extra-guide-{i}", f"Extra Guide {i} Topic", "guides",
         None, None, "guide-v1", "published", 50.0)
        for i in range(7)
    ]
    conn.executemany(
        "INSERT INTO posts (slug, title, category, language, concept, template_id, status, opportunity_score) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", extras
    )
    conn.commit()
    conn.close()

    # Body has 9 different anchor mentions
    lines = [f"Read about Extra Guide {i} Topic here.\n" for i in range(7)]
    lines += ["Python List Comprehensions are great.\n"]
    lines += ["Also check What is a REST API for reference.\n"]  # 9th
    body = "".join(lines)

    path = tmp_draft("my-post4", "guides", body)
    result = link_post(path, tmp_registry)
    assert result["links_inserted"] == 8


def test_idempotent(tmp_registry, tmp_draft):
    body = "Python List Comprehensions make code cleaner.\n"
    path = tmp_draft("my-post5", "guides", body)
    r1 = link_post(path, tmp_registry)
    r2 = link_post(path, tmp_registry)
    assert r2["links_inserted"] == 0


def test_frontmatter_untouched(tmp_registry, tmp_draft):
    body = "What is a REST API is a common question.\n"
    path = tmp_draft("my-post6", "blog", body, frontmatter_extra="custom_field: keep_this\n")
    link_post(path, tmp_registry)
    post = frontmatter.load(path)
    assert post.metadata.get("custom_field") == "keep_this"


def test_existing_link_intact(tmp_registry, tmp_draft):
    body = "See [Python List Comprehensions](/languages/python/list-comprehensions) for examples.\n"
    path = tmp_draft("my-post7", "guides", body)
    link_post(path, tmp_registry)
    post = frontmatter.load(path)
    # Original link must be unchanged and no duplicate
    count = post.content.count("(/languages/python/list-comprehensions)")
    assert count == 1
    assert "[Python List Comprehensions](/languages/python/list-comprehensions)" in post.content
