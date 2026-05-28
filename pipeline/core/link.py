"""
link.py — Stage: drafted → linked

Validates /languages/ links in the draft against the registry.
Counts total internal links and flags any violations.
Pure Python — no API calls.
Idempotent: skips if post is already past 'drafted'.
"""

import re
import sqlite3
from pathlib import Path
from typing import Union

from ._db import get_post, set_post_status
from ._types import StageResult

ALREADY_PAST = {"linked", "approved", "published"}

# Matches /languages/lang/concept links in markdown
_TWO_SEG_RE = re.compile(r'\]\((/languages/([^/\s"]+)/([^/\s")]+))')
# Single-segment /languages/slug (hyphens indicate a post slug, not a category)
_ONE_SEG_RE = re.compile(r'\]\((/languages/([^/\s")]+))\)')
# Any internal devnook link
_INTERNAL_RE = re.compile(r'\]\((/[^)]+)\)')


def _validate_language_links(text: str, db_path: Path) -> list[str]:
    """Return list of problem descriptions. Empty = clean."""
    problems = []

    for m in _ONE_SEG_RE.finditer(text):
        segment = m.group(2)
        if "-" in segment:
            problems.append(
                f"{m.group(1)} is malformed — missing language subdir (e.g. /languages/python/error-handling)"
            )

    conn = sqlite3.connect(str(db_path))
    for m in _TWO_SEG_RE.finditer(text):
        full_path, lang, segment = m.group(1), m.group(2), m.group(3).rstrip("/")
        concept_row = conn.execute(
            "SELECT 1 FROM posts WHERE language=? AND concept=?", (lang, segment)
        ).fetchone()
        if concept_row:
            continue
        slug_row = conn.execute(
            "SELECT concept FROM posts WHERE language=? AND slug=?", (lang, segment)
        ).fetchone()
        if slug_row:
            problems.append(
                f"{full_path} uses filename slug — correct URL: /languages/{lang}/{slug_row[0]}"
            )
        else:
            problems.append(f"{full_path} not found in registry (broken link)")
    conn.close()
    return problems


def _count_internal_links(text: str) -> int:
    return len(_INTERNAL_RE.findall(text))


def run(
    slug: str,
    db_path: Union[str, Path],
    *,
    dry_run: bool = False,
) -> dict:
    db_path = Path(db_path)
    pipeline_dir = db_path.parent.parent

    post = get_post(slug, db_path)
    if not post:
        return StageResult(error=f"Post '{slug}' not found in registry").to_dict()

    status = post["status"]
    if status in ALREADY_PAST:
        return StageResult(processed=0, details={"skipped": f"already '{status}'"}).to_dict()
    if status != "drafted":
        return StageResult(error=f"Expected status='drafted', got '{status}'").to_dict()

    draft_path = pipeline_dir / "agents" / "content-team" / "drafts" / f"{slug}.md"
    if not draft_path.exists():
        return StageResult(error=f"Draft not found: {draft_path}").to_dict()

    text = draft_path.read_text(encoding="utf-8")
    link_problems = _validate_language_links(text, db_path)
    internal_link_count = _count_internal_links(text)

    details = {
        "internal_links": internal_link_count,
        "link_problems": link_problems,
    }

    if dry_run:
        return StageResult(
            processed=1,
            written=0 if link_problems else 1,
            rejected=1 if link_problems else 0,
            details={**details, "dry_run": True},
        ).to_dict()

    set_post_status(slug, "linked", db_path, internal_links=internal_link_count)

    return StageResult(
        processed=1,
        written=1,
        rejected=0,
        details=details,
    ).to_dict()
