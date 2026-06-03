"""
publish.py — Stage: approved → published

Moves the approved draft to site/src/content/, updates the registry, and pings GSC.
DEVNOOK_PATH env var must point to the Astro site root (default: pipeline/../site).
Git commit is handled by the caller (CI workflow or manual).

Pure Python — no API calls.
Idempotent: skips if post is already 'published'.
"""

import json
import os
import re
import shutil
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Union

from ._db import get_post, set_post_status
from ._types import StageResult

_RELATED_SECTION_RE = re.compile(
    r"\n[ \t]*##[ \t]+Related\b[^\n]*\n.*?(?=\n##[ \t]|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def _get_site_dir(pipeline_dir: Path) -> Path:
    env = os.environ.get("DEVNOOK_PATH")
    if env:
        return Path(env)
    return pipeline_dir.parent / "site"


def _get_category_path(category: str, language: str | None) -> str:
    if category == "languages" and language:
        return f"languages/{language}"
    return category


def _strip_related_section(text: str) -> tuple[str, bool]:
    cleaned = _RELATED_SECTION_RE.sub("", text)
    modified = cleaned != text
    if modified:
        cleaned = cleaned.rstrip() + "\n"
    return cleaned, modified


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
    if status == "published":
        return StageResult(processed=0, details={"skipped": "already published"}).to_dict()
    if status != "approved":
        return StageResult(error=f"Expected status='approved', got '{status}'").to_dict()

    draft_path = pipeline_dir / "agents" / "content-team" / "drafts" / f"{slug}.md"
    if not draft_path.exists():
        return StageResult(error=f"Draft not found: {draft_path}").to_dict()

    category = post.get("category", "blog")
    language = post.get("language") or None
    concept = post.get("concept") or None

    site_dir = _get_site_dir(pipeline_dir)
    content_dir = site_dir / "src" / "content"
    cat_path = _get_category_path(category, language)
    dest_dir = content_dir / cat_path
    dest_path = dest_dir / f"{slug}.md"

    if dry_run:
        return StageResult(
            processed=1,
            written=1,
            details={
                "dry_run": True,
                "would_publish_to": str(dest_path),
            },
        ).to_dict()

    text = draft_path.read_text(encoding="utf-8")
    text, stripped = _strip_related_section(text)

    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(draft_path), str(dest_path))
    if stripped:
        dest_path.write_text(text, encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    today = date.today().isoformat()
    rel_path = str(dest_path.relative_to(site_dir))

    set_post_status(
        slug,
        "published",
        db_path,
        published_at=now,
        published_date=today,
        file_path=rel_path,
    )

    # Build live URL (Google discovers it via the auto-generated sitemap).
    # Trailing slash is required: it's the site's canonical form, and the
    # no-slash variant 301-redirects — submitting it yields "Page with redirect".
    if category == "languages" and language and concept:
        live_url = f"https://devnook.dev/languages/{language}/{concept}/"
    else:
        live_url = f"https://devnook.dev/{category}/{slug}/"

    return StageResult(
        processed=1,
        written=1,
        details={
            "published_to": str(dest_path),
            "live_url": live_url,
            "stripped_related_section": stripped,
        },
    ).to_dict()
