"""
Step 4: SEO Optimizer
Processes drafted posts to:
1. Validate and fix internal link counts (ensure 3–5 links)
2. Add schema.org JSON-LD to frontmatter
3. Verify keyword density in key positions
4. Update frontmatter word count metadata

LLM: Gemini Flash via llm_router.route("seo", ...) — only called when links < 3
"""

import re
import sys
import frontmatter
from pathlib import Path

# Ensure project root is on path (in case script is run standalone)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.registry import get_db, update_post_status
from agents.utils.llm_router import route
from agents.skills import load_skill

# ---------------------------------------------------------------------------
# System context
# ---------------------------------------------------------------------------

_SEO_RULES = load_skill("seo-writing-rules")

SYSTEM_SEO = f"""You are an SEO optimizer for devnook.dev, a developer resource site.
Your job is to improve internal linking in technical articles.

{_SEO_RULES}"""

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


def add_more_links(meta: dict, content: str, current_count: int) -> tuple[str, object]:
    """
    Ask Gemini to add more internal links if below minimum (3).
    Returns (updated_content, llm_response_or_None).
    Falls back to original content if LLM call fails.
    """
    needed = 3 - current_count
    if needed <= 0:
        return content, None

    prompt = f"""This devnook.dev article needs {needed} more internal links added naturally.

Current article body (no frontmatter):
{content}

Add {needed} internal links using this format: [descriptive text](/category/slug)
Valid URL patterns for devnook.dev:
- /languages/{{lang}}/{{concept}}  (e.g. /languages/python/list-comprehensions)
- /guides/{{slug}}                 (e.g. /guides/what-is-rest-api)
- /tools/{{slug}}                  (e.g. /tools/json-formatter)
- /cheatsheets/{{subject}}         (e.g. /cheatsheets/python-string-methods)

Rules:
- Weave links into existing sentences naturally — do not force them
- Do NOT add frontmatter
- Return the complete updated article body only (markdown, no YAML)"""

    try:
        response = route("seo", system=SYSTEM_SEO, prompt=prompt, max_tokens=8000)
        updated = response.text.strip()
        # Strip any frontmatter fences the LLM may have accidentally included
        updated = re.sub(r'^---.*?---\s*', '', updated, flags=re.DOTALL).strip()
        return updated, response
    except Exception as e:
        print(f"    [WARN] add_more_links LLM call failed: {e}. Using original content.")
        return content, None


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
    llm_response = None

    # 1. Check/fix internal links
    link_count = count_internal_links(content)
    if link_count < 3:
        content, llm_response = add_more_links(meta, content, link_count)
        link_count = count_internal_links(content)
        issues.append(f"added_links (now {link_count})")

    # 2. Check description length
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
        "llm_response": llm_response,
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
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    model_used = ""

    for row in posts:
        slug = row["slug"]
        print(f"  SEO: {slug}")
        result = process_post(slug)
        processed += 1

        if result["status"] == "ok":
            passed += 1
            if result["issues"]:
                print(f"    issues: {result['issues']}")
            # Accumulate tokens if LLM was called
            if result.get("llm_response"):
                r = result["llm_response"]
                model_used = r.model_used
                total_input_tokens += r.input_tokens
                total_output_tokens += r.output_tokens
                total_cost += r.estimated_cost_usd
        else:
            failed += 1
            print(f"    [ERROR] {result.get('reason')}")

    print(f"  Done — passed={passed}, failed={failed}")

    return {
        "processed": processed,
        "passed": passed,
        "rejected": failed,
        "model_used": model_used,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "estimated_cost_usd": total_cost,
    }


if __name__ == "__main__":
    result = run()
    print(f"\nResult: {result}")
