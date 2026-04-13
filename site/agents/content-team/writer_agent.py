"""
Step 3: Writer Agent
Takes queued posts from registry.db, loads the appropriate template,
calls Claude Sonnet (via llm_router) to generate content, and saves
the draft .md file to agents/content-team/drafts/{slug}.md.

LLM: Claude Sonnet 4.5 via llm_router.route("writer", ...)
"""

import sys
from pathlib import Path
from datetime import date

# Ensure project root is on path (in case script is run standalone)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.registry import get_queued_posts, update_post_status
from agents.utils.llm_router import route
from agents.skills import load_skill

# ---------------------------------------------------------------------------
# System context — loaded once at import
# ---------------------------------------------------------------------------

_BRAND_VOICE = load_skill("devnook-brand-voice")
_SEO_RULES = load_skill("seo-writing-rules")
_CONTENT_SCHEMA = load_skill("content-schema")

SYSTEM = f"""You are a technical writer for devnook.dev, a developer resource site.
Write high-quality, practical developer content that is accurate, concise, and useful.

{_BRAND_VOICE}

{_SEO_RULES}

{_CONTENT_SCHEMA}"""

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

TEMPLATES_DIR = PROJECT_ROOT / "templates" / "templates"
DRAFTS_DIR = Path(__file__).resolve().parent / "drafts"

# Maps template_id prefix → template folder name
_TYPE_MAP = {
    "lang":       "language-post",
    "guide":      "guide",
    "blog":       "blog",
    "cheatsheet": "cheatsheet",
    "tool-exp":   "tool-explainer",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_template(template_id: str) -> str:
    """Load a template file by its ID (e.g. 'lang-v2', 'guide-v1')."""
    prefix = template_id.rsplit("-v", 1)[0]   # "lang-v2" → "lang"
    folder = _TYPE_MAP.get(prefix, prefix)
    path = TEMPLATES_DIR / folder / f"{template_id}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    print(f"  [WARN] Template not found: {path}")
    return ""


def get_word_count_target(category: str) -> int:
    targets = {
        "languages":   1200,
        "guides":      1800,
        "blog":        1500,
        "cheatsheets":  800,
        "tools":        650,
    }
    return targets.get(category, 1200)


def save_draft(slug: str, content: str) -> Path:
    """Save draft markdown to agents/content-team/drafts/{slug}.md"""
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    path = DRAFTS_DIR / f"{slug}.md"
    path.write_text(content, encoding="utf-8")
    return path


def write_post(post: dict) -> str:
    """Generate markdown content for a queued post. Returns the markdown string."""
    template = load_template(post["template_id"])
    word_target = get_word_count_target(post["category"])

    prompt = f"""Write a complete, publication-ready markdown post for devnook.dev.

Post metadata:
- Slug: {post['slug']}
- Title: {post['title']}
- Description: {post['description']}
- Category: {post['category']}
- Language: {post.get('language') or 'N/A'}
- Concept: {post.get('concept') or 'N/A'}
- Primary keyword: {post['keyword']}
- Template ID: {post['template_id']}
- Target word count: {word_target}

Template structure to follow:
{template}

Requirements:
1. Start with complete YAML frontmatter using these exact fields:
   title, description, published_date, category, language (if applicable),
   concept (if applicable), template_id, tags (list), difficulty (if applicable)
2. Set published_date to today: {date.today().isoformat()}
3. Set category to: {post['category']}
4. Set template_id to: {post['template_id']}
5. Follow the template structure exactly — replace every [FILL: ...] placeholder
6. Write at least {word_target} words but STRICTLY no more than 2000 words. Be concise and practical.
7. Include at least 2 working code examples with language tags (for language/guide posts)
8. Add 3–5 internal links using format: [descriptive text](/category/slug)
   Use realistic DevNook URL patterns:
   - /languages/python/list-comprehensions
   - /guides/what-is-rest-api
   - /tools/json-formatter
   - /cheatsheets/python-string-methods
9. Follow brand voice rules — no banned phrases
10. Primary keyword "{post['keyword']}" must appear in the first 100 words

Write the complete markdown file content (frontmatter + body):"""

    response = route("writer", system=SYSTEM, prompt=prompt, max_tokens=8000)
    return response


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run(limit: int = 20) -> dict:
    """Write posts for all queued items in registry. Returns pipeline result dict."""
    queued = get_queued_posts(limit=limit)

    if not queued:
        print("  No queued posts to write.")
        return {"processed": 0, "passed": 0, "rejected": 0}

    print(f"  Writing {len(queued)} posts...")

    drafted = 0
    failed = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    model_used = ""

    for row in queued:
        post = dict(row)
        slug = post["slug"]

        try:
            print(f"  Writing: {slug}")
            response = write_post(post)

            model_used = response.model_used
            total_input_tokens += response.input_tokens
            total_output_tokens += response.output_tokens
            total_cost += response.estimated_cost_usd

            text = response.text.strip()
            import re
            text = re.sub(r"^```(?:markdown|md)?\s*\n", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\n```\s*$", "", text)
            
            file_path = save_draft(slug, text)

            update_post_status(
                slug,
                "drafted",
                file_path=str(file_path),
            )
            drafted += 1
            print(f"  [DRAFTED] {slug} ({response.output_tokens} tokens)")

        except Exception as e:
            print(f"  [ERROR] '{slug}': {e}")
            # Keep in queue for retry; store error note
            update_post_status(slug, "queued", qa_notes=str(e))
            failed += 1

    print(f"  Done — drafted={drafted}, failed={failed}, cost=${total_cost:.4f}")

    return {
        "processed": len(queued),
        "passed": drafted,
        "rejected": failed,
        "model_used": model_used,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "estimated_cost_usd": total_cost,
    }


if __name__ == "__main__":
    result = run()
    print(f"\nResult: {result}")
