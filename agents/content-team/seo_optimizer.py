"""
SEO Optimizer — schema.org JSON-LD injection + keyword-density checks.
Internal link insertion is handled by link_utility.py (Linker step).
"""

import re
import sys
import frontmatter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.registry import get_db, update_post_status

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DRAFTS_DIR = Path(__file__).resolve().parent / "drafts"

# Maps category → schema.org @type
_SCHEMA_ORG_TYPES = {
    "languages":   "TechArticle",
    "guides":      "Article",
    "blog":        "BlogPosting",
    "cheatsheets": "Article",
    "tools":       "SoftwareApplication",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def count_internal_links(content: str) -> int:
    """Count markdown links with paths starting with /"""
    return len(re.findall(r'\[([^\]]+)\]\((/[^\)]+)\)', content))


def count_words(content: str) -> int:
    """Count words in markdown body (rough count, excludes frontmatter)."""
    clean = re.sub(r'^---.*?---', '', content, flags=re.DOTALL).strip()
    return len(clean.split())


def validate_description(description: str) -> bool:
    return 100 <= len(description) <= 160



def generate_schema_org(meta: dict) -> str:
    """Generate schema.org JSON-LD string for a post."""
    schema_type = _SCHEMA_ORG_TYPES.get(meta.get("category", ""), "TechArticle")
    base_url = "https://devnook.dev"
    slug = meta.get("slug", "")
    category = meta.get("category", "")
    url = f"{base_url}/{category}/{slug}"

    title = str(meta.get("title", "")).replace('"', '\\"')
    description = str(meta.get("description", "")).replace('"', '\\"')
    published_date = str(meta.get("published_date", ""))

    if schema_type == "SoftwareApplication":
        return (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "SoftwareApplication",\n'
            f'  "name": "{title}",\n'
            '  "applicationCategory": "DeveloperApplication",\n'
            '  "operatingSystem": "Any",\n'
            '  "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},\n'
            f'  "url": "{url}"\n'
            '}\n'
            '</script>'
        )
    else:
        return (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            f'  "@type": "{schema_type}",\n'
            f'  "headline": "{title}",\n'
            f'  "description": "{description}",\n'
            f'  "datePublished": "{published_date}",\n'
            '  "author": {"@type": "Organization", "name": "DevNook"},\n'
            '  "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},\n'
            f'  "url": "{url}"\n'
            '}\n'
            '</script>'
        )


def process_post(slug: str) -> dict:
    """Process a single drafted post through SEO optimization."""
    draft_path = DRAFTS_DIR / f"{slug}.md"
    if not draft_path.exists():
        return {"status": "error", "reason": "draft_not_found"}

    try:
        post = frontmatter.load(str(draft_path))
    except Exception as e:
        return {"status": "error", "reason": f"frontmatter_parse_error: {e}"}

    content = post.content
    meta = dict(post.metadata)

    issues = []

    # 1. Check description length
    link_count = count_internal_links(content)
    desc = meta.get("description", "")
    if not validate_description(str(desc)):
        issues.append(f"description_length:{len(str(desc))}")

    # 3. Add schema.org to frontmatter
    meta["schema_org"] = generate_schema_org(meta)

    # 4. Count words
    word_count = count_words(content)
    meta["actual_word_count"] = word_count

    # 5. Save optimized file
    new_post = frontmatter.Post(content, **meta)
    draft_path.write_text(frontmatter.dumps(new_post), encoding="utf-8")

    update_post_status(
        slug,
        "optimized",
        word_count=word_count,
        internal_links=link_count,
    )

    return {
        "status": "ok",
        "word_count": word_count,
        "links": link_count,
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run() -> dict:
    """Process all drafted posts through SEO optimization."""
    with get_db() as db:
        posts = db.execute(
            "SELECT slug FROM posts WHERE status='drafted'"
        ).fetchall()

    if not posts:
        print("  No drafted posts to optimize.")
        return {"processed": 0, "passed": 0, "rejected": 0}

    print(f"  Optimizing {len(posts)} posts...")

    processed = 0
    passed = 0
    failed = 0

    for row in posts:
        slug = row["slug"]
        print(f"  SEO: {slug}")
        result = process_post(slug)
        processed += 1

        if result["status"] == "ok":
            passed += 1
            if result["issues"]:
                print(f"    issues: {result['issues']}")
        else:
            failed += 1
            print(f"    [ERROR] {result.get('reason')}")

    print(f"  Done — passed={passed}, failed={failed}")

    return {"processed": processed, "passed": passed, "rejected": failed}


if __name__ == "__main__":
    result = run()
    print(f"\nResult: {result}")
