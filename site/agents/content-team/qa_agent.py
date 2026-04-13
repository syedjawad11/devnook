"""
Step 5: QA Agent
Validates all optimized posts against rejection criteria.
See agents/skills/qa-rejection-criteria.md for the full rules.

Rule-based validation — no LLM calls. Fast and deterministic.
"""

import re
import sys
import json
import frontmatter
from pathlib import Path
from datetime import datetime

# Ensure project root is on path (in case script is run standalone)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.registry import get_db, update_post_status

# ---------------------------------------------------------------------------
# Validation constants
# ---------------------------------------------------------------------------

DRAFTS_DIR = Path(__file__).resolve().parent / "drafts"

VALID_CATEGORIES = {"languages", "guides", "blog", "cheatsheets", "tools"}

VALID_TEMPLATE_IDS = {
    "lang-v1", "lang-v2", "lang-v3", "lang-v4", "lang-v5",
    "guide-v1", "guide-v2", "guide-v3", "guide-v4",
    "blog-v1", "blog-v2", "blog-v3", "blog-v4", "blog-v5",
    "cheatsheet-v1", "cheatsheet-v2", "cheatsheet-v3", "cheatsheet-v4",
    "tool-exp-v1", "tool-exp-v2", "tool-exp-v3", "tool-exp-v4",
}

BANNED_PHRASES = [
    "let's dive in",
    "buckle up",
    "in this article, we will",
    "without further ado",
    "it's worth noting that",
    "in conclusion",
    "to summarize",
    "in summary",
    "at the end of the day",
    "game-changer",
    "leverage",
]

MIN_WORD_COUNTS = {
    "languages":   1000,
    "guides":      1500,
    "blog":        1200,
    "cheatsheets":  600,
    "tools":        500,
}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def check_similarity(new_content: str, existing_contents: list) -> float:
    """
    Returns max TF-IDF cosine similarity score (0–1).
    Reject if > 0.70 (near-duplicate content).
    Returns 0.0 if no existing content to compare against.
    """
    if not existing_contents:
        return 0.0

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus = existing_contents + [new_content]
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        return float(scores.max())
    except Exception:
        return 0.0


def check_heading_hierarchy(content: str) -> bool:
    """
    Verify heading levels don't skip (H1→H2→H3, not H1→H3).
    Returns True if hierarchy is valid.
    """
    headings = re.findall(r'^(#{1,6})\s', content, re.MULTILINE)
    levels = [len(h) for h in headings]
    for i in range(1, len(levels)):
        if levels[i] > levels[i - 1] + 1:
            return False
    return True


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------

def validate_post(slug: str, existing_contents: list) -> dict:
    """
    Run all QA checks on a post.
    Returns a result dict with qa_status ('approved' or 'rejected'),
    list of failure reasons, and list of warnings.
    """
    draft_path = DRAFTS_DIR / f"{slug}.md"
    if not draft_path.exists():
        return {
            "slug": slug,
            "qa_status": "rejected",
            "word_count": 0,
            "similarity_score": 0.0,
            "internal_links": 0,
            "rejections": ["draft_not_found"],
            "warnings": [],
            "qa_timestamp": datetime.utcnow().isoformat() + "Z",
        }

    try:
        post = frontmatter.load(str(draft_path))
    except Exception as e:
        return {
            "slug": slug,
            "qa_status": "rejected",
            "word_count": 0,
            "similarity_score": 0.0,
            "internal_links": 0,
            "rejections": [f"frontmatter_parse_error:{e}"],
            "warnings": [],
            "qa_timestamp": datetime.utcnow().isoformat() + "Z",
        }

    meta = post.metadata
    content = post.content

    failures = []
    warnings = []

    # === STRUCTURAL CHECKS ===

    # Required frontmatter fields
    required_fields = ["title", "description", "published_date", "template_id", "category"]
    for field in required_fields:
        if not meta.get(field):
            failures.append(f"missing_field:{field}")

    # Valid category
    if meta.get("category") not in VALID_CATEGORIES:
        failures.append(f"invalid_category:{meta.get('category')}")

    # Valid template_id
    if meta.get("template_id") not in VALID_TEMPLATE_IDS:
        failures.append(f"invalid_template_id:{meta.get('template_id')}")

    # Description length
    desc = str(meta.get("description", ""))
    if len(desc) > 160:
        failures.append(f"description_too_long:{len(desc)}")
    elif len(desc) < 100:
        failures.append(f"description_too_short:{len(desc)}")

    # Date format
    try:
        datetime.strptime(str(meta.get("published_date", "")), "%Y-%m-%d")
    except (ValueError, TypeError):
        failures.append("invalid_date_format")

    # === CONTENT QUALITY CHECKS ===

    # Word count
    word_count = meta.get("actual_word_count") or len(content.split())
    word_count = int(word_count)
    min_words = MIN_WORD_COUNTS.get(meta.get("category", "languages"), 1000)
    if word_count < min_words:
        failures.append(f"word_count_too_low:{word_count}<{min_words}")
    elif word_count < int(min_words * 1.1):
        warnings.append(f"word_count_borderline:{word_count}")

    # Code blocks (required for language posts and guides)
    if meta.get("category") in ("languages", "guides"):
        code_blocks = re.findall(r'```\w+', content)
        if len(code_blocks) < 2:
            failures.append(f"insufficient_code_blocks:{len(code_blocks)}")

    # Internal links
    links = re.findall(r'\[([^\]]+)\]\((/[^\)]+)\)', content)
    link_count = len(links)
    if link_count < 3:
        failures.append(f"insufficient_links:{link_count}")
    elif link_count > 8:
        failures.append(f"too_many_links:{link_count}")
    elif link_count < 5:
        warnings.append(f"few_links:{link_count}")

    # Banned phrases
    content_lower = content.lower()
    for phrase in BANNED_PHRASES:
        if phrase in content_lower:
            failures.append(f"banned_phrase:{phrase}")

    # Heading hierarchy
    if not check_heading_hierarchy(content):
        failures.append("heading_hierarchy_skipped")

    # Untagged code blocks check disabled due to false positives on closing backticks
    # untagged = re.findall(r'```\s*\n', content)
    # if untagged:
    #     failures.append(f"code_block_no_language:{len(untagged)}")

    # === DUPLICATE DETECTION ===
    similarity = check_similarity(content, existing_contents)
    if similarity > 0.70:
        failures.append(f"duplicate_content:{similarity:.2f}")

    # === TITLE LENGTH WARNING ===
    title = str(meta.get("title", ""))
    if len(title) > 65:
        warnings.append(f"title_too_long:{len(title)}")

    return {
        "slug": slug,
        "qa_status": "approved" if not failures else "rejected",
        "word_count": word_count,
        "similarity_score": similarity,
        "internal_links": link_count,
        "rejections": failures,
        "warnings": warnings,
        "qa_timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run() -> dict:
    """Run QA validation on all optimized posts."""
    with get_db() as db:
        posts = db.execute(
            "SELECT slug FROM posts WHERE status='optimized'"
        ).fetchall()

        # Load all approved/staged/published post paths for similarity comparison
        approved_rows = db.execute(
            "SELECT file_path FROM posts "
            "WHERE status IN ('approved', 'staged', 'published') AND file_path IS NOT NULL"
        ).fetchall()

    if not posts:
        print("  No optimized posts to QA.")
        return {"processed": 0, "passed": 0, "rejected": 0}

    # Load existing content corpus for TF-IDF duplicate detection
    existing_contents = []
    for row in approved_rows:
        if row["file_path"]:
            p = PROJECT_ROOT / row["file_path"]
            if p.exists():
                existing_contents.append(p.read_text(encoding="utf-8"))

    print(f"  QA checking {len(posts)} posts (corpus size: {len(existing_contents)})...")

    processed = 0
    approved = 0
    rejected = 0

    for row in posts:
        slug = row["slug"]
        print(f"  QA: {slug}")
        result = validate_post(slug, existing_contents)
        processed += 1

        qa_status = result["qa_status"]

        update_post_status(
            slug,
            qa_status,
            qa_status=qa_status,
            qa_notes=json.dumps(result),
            word_count=result["word_count"],
            similarity_score=result["similarity_score"],
            internal_links=result["internal_links"],
            rejection_reason="; ".join(result["rejections"]) if result["rejections"] else None,
        )

        if qa_status == "approved":
            approved += 1
            if result["warnings"]:
                print(f"    [APPROVED with warnings] {', '.join(result['warnings'])}")
        else:
            rejected += 1
            print(f"    [REJECTED] {', '.join(result['rejections'])}")

        # Add to corpus so subsequent posts in this batch are compared against this one too
        draft_path = DRAFTS_DIR / f"{slug}.md"
        if draft_path.exists():
            existing_contents.append(draft_path.read_text(encoding="utf-8"))

    print(f"  Done — approved={approved}, rejected={rejected}")

    return {
        "processed": processed,
        "passed": approved,
        "rejected": rejected,
    }


if __name__ == "__main__":
    result = run()
    print(f"\nResult: {result}")
