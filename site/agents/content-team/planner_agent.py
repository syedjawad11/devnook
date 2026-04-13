"""
Step 2: Planner Agent
Takes discovered keywords from the keywords table, calls Gemini Flash to classify
each one (category, slug, title, description, opportunity_score), assigns a
round-robin template, and adds it to the posts table as status='queued'.

LLM: Gemini Flash via llm_router.route("planner", ...)
"""

import sys
import json
import re
from pathlib import Path

# Ensure project root is on path (in case script is run standalone)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.registry import get_db, add_post, get_next_template
from agents.utils.llm_router import route
from agents.skills import load_skill

# ---------------------------------------------------------------------------
# System context — loaded once at import
# ---------------------------------------------------------------------------

_CONTENT_SCHEMA = load_skill("content-schema")
_SEO_RULES = load_skill("seo-writing-rules")

SYSTEM = f"""You are a content planner for devnook.dev, a developer resource site.

{_CONTENT_SCHEMA}

{_SEO_RULES}

Always respond with valid JSON only — no explanation, no markdown fences."""


# ---------------------------------------------------------------------------
# Per-keyword classification prompt
# ---------------------------------------------------------------------------

CLASSIFY_PROMPT = """For the keyword: "{keyword}"

Classify this keyword and generate post metadata. Respond with a single JSON object:

{{
  "category": "<one of: languages | guides | blog | cheatsheets>",
  "language": "<programming language slug e.g. python, javascript — or null if not language-specific>",
  "concept": "<core concept in kebab-case e.g. list-comprehension — or null if not a language post>",
  "slug": "<URL slug: lowercase, kebab-case, max 60 chars, omit stop words>",
  "title": "<SEO title following our title patterns, max 70 chars>",
  "description": "<meta description 140-160 chars, naturally includes the keyword>",
  "opportunity_score": <integer 0-100 based on these criteria:
    80-100: very specific long-tail, clear intent, low competition expected
    60-79:  good keyword, moderate specificity
    40-59:  broad topic, higher competition expected
    0-39:   skip this keyword (too generic, navigational, or off-topic)>
}}

keyword: "{keyword}"
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict | None:
    """Extract the first JSON object from an LLM response."""
    # Strip markdown fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def _is_valid_meta(meta: dict) -> bool:
    required = ["category", "slug", "title", "description", "opportunity_score"]
    return all(meta.get(k) for k in required)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run() -> dict:
    """Classify discovered keywords and queue them as posts. Returns pipeline result dict."""

    # Fetch unprocessed keywords (batch of 10 per run for testing)
    with get_db() as db:
        rows = db.execute(
            "SELECT keyword FROM keywords WHERE status='discovered' ORDER BY ROWID LIMIT 10"
        ).fetchall()

    if not rows:
        print("  No discovered keywords to process.")
        return {"processed": 0, "passed": 0, "rejected": 0}

    print(f"  Planning {len(rows)} keywords...")

    processed = 0
    queued = 0
    rejected = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0
    model_used = ""

    for row in rows:
        keyword = row["keyword"]
        processed += 1

        try:
            prompt = CLASSIFY_PROMPT.format(keyword=keyword)
            response = route("planner", system=SYSTEM, prompt=prompt, max_tokens=512)

            model_used = response.model_used
            total_input_tokens += response.input_tokens
            total_output_tokens += response.output_tokens
            total_cost += response.estimated_cost_usd

            meta = _extract_json(response.text)

            if not meta or not _is_valid_meta(meta):
                print(f"  [SKIP] '{keyword}' — could not parse JSON response")
                rejected += 1
                with get_db() as db:
                    db.execute(
                        "UPDATE keywords SET status='rejected' WHERE keyword=?", (keyword,)
                    )
                continue

            score = int(meta.get("opportunity_score", 0))
            if score < 40:
                rejected += 1
                with get_db() as db:
                    db.execute(
                        "UPDATE keywords SET status='rejected' WHERE keyword=?", (keyword,)
                    )
                continue

            category = meta["category"]
            template_id = get_next_template(category)

            added = add_post(
                slug=meta["slug"],
                title=meta["title"],
                description=meta["description"],
                category=category,
                language=meta.get("language"),
                concept=meta.get("concept"),
                template_id=template_id,
                keyword=keyword,
                opportunity_score=float(score),
            )

            if added:
                queued += 1
                with get_db() as db:
                    db.execute(
                        "UPDATE keywords SET status='assigned', assigned_slug=? WHERE keyword=?",
                        (meta["slug"], keyword),
                    )
                print(f"  [QUEUED] {meta['slug']} (score={score}, template={template_id})")
            else:
                # Slug already exists
                rejected += 1
                with get_db() as db:
                    db.execute(
                        "UPDATE keywords SET status='rejected' WHERE keyword=?", (keyword,)
                    )

        except Exception as e:
            print(f"  [ERROR] '{keyword}': {e}")
            rejected += 1

    print(
        f"  Done — queued={queued}, rejected={rejected}, "
        f"cost=${total_cost:.4f}"
    )

    return {
        "processed": processed,
        "passed": queued,
        "rejected": rejected,
        "model_used": model_used,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "estimated_cost_usd": total_cost,
    }
