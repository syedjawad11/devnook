"""
qa.py — Stage: linked → approved | rejected

Runs all QA checks:
  1. Schema enum check — required frontmatter fields + language enum validation
  2. Word floor — 2500 editorial / 1500 language
  3. Link validity — /languages/ links against registry (hard fail)
  4. Dup check — slug not already published
  5. Cluster-collision guard — keyword cluster not used by another published post

Pure Python — no API calls.
Idempotent: skips if post is already past 'linked'.
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Union

try:
    import frontmatter as fm
    _HAS_FRONTMATTER = True
except ImportError:
    _HAS_FRONTMATTER = False

from ._db import get_post, set_post_status, get_keyword_set_for_slug, cluster_already_used
from ._types import StageResult

ALREADY_PAST = {"approved", "published"}

VALID_CATEGORIES = {"blog", "guides", "cheatsheets", "languages", "tools"}
VALID_LANGUAGES = {
    "python", "javascript", "typescript", "go", "rust",
    "java", "csharp", "php", "ruby", "swift", "kotlin", "cpp",
}
REQUIRED_FIELDS = {"title", "description", "category", "template_id", "published_date"}

WORD_FLOOR_EDITORIAL = 2500
WORD_FLOOR_LANGUAGE = 1500

_TWO_SEG_RE = re.compile(r'\]\((/languages/([^/\s"]+)/([^/\s")]+))')
_ONE_SEG_RE = re.compile(r'\]\((/languages/([^/\s")]+))\)')


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Returns (metadata, body). Falls back to empty dict if python-frontmatter missing."""
    if _HAS_FRONTMATTER:
        post = fm.loads(text)
        return dict(post.metadata), post.content
    # Minimal YAML parser: extract --- block manually
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    yaml_block = text[3:end].strip()
    body = text[end + 4:].strip()
    meta: dict = {}
    for line in yaml_block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def _count_words(body: str) -> int:
    return len(body.split())


def _check_language_links(text: str, db_path: Path) -> list[str]:
    problems = []
    for m in _ONE_SEG_RE.finditer(text):
        segment = m.group(2)
        if "-" in segment:
            problems.append(f"{m.group(1)}: malformed /languages/ link (missing language subdir)")
    conn = sqlite3.connect(str(db_path))
    for m in _TWO_SEG_RE.finditer(text):
        full_path, lang, segment = m.group(1), m.group(2), m.group(3).rstrip("/")
        if conn.execute(
            "SELECT 1 FROM posts WHERE language=? AND concept=?", (lang, segment)
        ).fetchone():
            continue
        slug_row = conn.execute(
            "SELECT concept FROM posts WHERE language=? AND slug=?", (lang, segment)
        ).fetchone()
        if slug_row:
            problems.append(
                f"{full_path}: uses filename slug — correct path is /languages/{lang}/{slug_row[0]}"
            )
        else:
            problems.append(f"{full_path}: not found in registry")
    conn.close()
    return problems


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
    if status != "linked":
        return StageResult(error=f"Expected status='linked', got '{status}'").to_dict()

    draft_path = pipeline_dir / "agents" / "content-team" / "drafts" / f"{slug}.md"
    if not draft_path.exists():
        return StageResult(error=f"Draft not found: {draft_path}").to_dict()

    text = draft_path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)

    rejections: list[str] = []
    warnings: list[str] = []

    # 1. Schema enum check
    for field in REQUIRED_FIELDS:
        if not meta.get(field):
            rejections.append(f"missing_field:{field}")

    category = meta.get("category", "")
    if category not in VALID_CATEGORIES:
        rejections.append(f"invalid_category:{category}")

    language = meta.get("language", "")
    if language and language not in VALID_LANGUAGES:
        rejections.append(f"invalid_language:{language}")

    desc = str(meta.get("description", ""))
    if desc and not (140 <= len(desc) <= 160):
        warnings.append(f"description_length:{len(desc)} (want 140–160)")

    # 2. Word floor
    word_count = _count_words(body)
    content_type = post.get("content_type", "editorial")
    floor = WORD_FLOOR_LANGUAGE if (category == "languages" or content_type == "programmatic") else WORD_FLOOR_EDITORIAL

    if word_count < floor:
        rejections.append(f"word_count_too_low:{word_count}<{floor}")
    elif word_count < floor * 1.1:
        warnings.append(f"word_count_borderline:{word_count}")

    # 3. Link validity — /languages/ links
    link_problems = _check_language_links(text, db_path)
    for p in link_problems:
        rejections.append(f"broken_link:{p}")

    # 4. Dup check — slug already published
    conn = sqlite3.connect(str(db_path))
    already_published = conn.execute(
        "SELECT 1 FROM posts WHERE slug=? AND status='published'", (slug,)
    ).fetchone()
    conn.close()
    if already_published:
        rejections.append(f"duplicate_slug:{slug} already published")

    # 5. Cluster-collision guard
    kset = get_keyword_set_for_slug(slug, db_path)
    if kset and kset.get("cluster_id"):
        if cluster_already_used(kset["cluster_id"], slug, db_path):
            rejections.append(f"cluster_collision:cluster_id={kset['cluster_id']} used by another published post")

    qa_result = {
        "slug": slug,
        "word_count": word_count,
        "rejections": rejections,
        "warnings": warnings,
        "qa_status": "rejected" if rejections else "approved",
    }

    if dry_run:
        return StageResult(
            processed=1,
            written=0 if rejections else 1,
            rejected=1 if rejections else 0,
            details={**qa_result, "dry_run": True},
        ).to_dict()

    new_status = "rejected" if rejections else "approved"
    rejection_reason = "; ".join(rejections) if rejections else None

    set_post_status(
        slug,
        new_status,
        db_path,
        qa_status=new_status,
        qa_notes=json.dumps(qa_result),
        rejection_reason=rejection_reason,
        word_count=word_count,
    )

    return StageResult(
        processed=1,
        written=0 if rejections else 1,
        rejected=1 if rejections else 0,
        details=qa_result,
    ).to_dict()
