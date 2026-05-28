"""
outline.py — Stage: queued → outlined

Calls Claude API to generate a structured section outline for a post.
Saves outline JSON to pipeline/data/outlines/{slug}.json.
Idempotent: skips if post is already past 'queued'.
"""

import json
import os
from pathlib import Path
from typing import Union

import anthropic

from ._db import get_post, set_post_status, get_keywords_for_slug, get_keyword_set_for_slug
from ._types import StageResult

MODEL = "claude-sonnet-4-6"
INPUT_COST_PER_M = 3.0
OUTPUT_COST_PER_M = 15.0

ALREADY_PAST = {"outlined", "drafted", "linked", "approved", "published"}

_OUTLINE_PROMPT = """\
You are a technical content planner for devnook.dev, a developer resource site.

Given a content brief, produce a structured article outline as JSON.
The outline MUST be detailed enough for a writer to produce a full article without further research.

## Brief

Title: {title}
Category: {category}
Primary keyword: {primary_keyword}
Secondary keywords: {secondary_keywords}
Template: {template_id}
Target word count: {word_count_target}

## Output format (JSON only — no markdown wrapper, no commentary)

{{
  "title": "Exact SEO-optimised title",
  "description": "Meta description 140-160 chars, includes primary keyword",
  "template_id": "{template_id}",
  "sections": [
    {{
      "heading": "Section H2 heading (first one must contain primary keyword variant)",
      "intent": "What this section accomplishes for the reader",
      "target_words": 400
    }}
  ],
  "must_cover": ["key point 1", "key point 2"],
  "code_examples_needed": 2,
  "external_links": [
    {{"text": "anchor text", "url": "https://...", "reason": "why this authority link"}}
  ]
}}

Rules:
- 5–8 sections total. First section = opening hook. Last section = takeaway/next steps.
- One H2 must contain the primary keyword or a close variant.
- Total target_words across all sections must sum to approximately {word_count_target}.
- external_links: 1–2 authority sources only. Must be real, well-known URLs.
- description: exactly 140–160 characters.
"""


def _calc_cost(usage: anthropic.types.Usage) -> tuple[int, float]:
    total = usage.input_tokens + usage.output_tokens
    cost = (
        usage.input_tokens * INPUT_COST_PER_M
        + usage.output_tokens * OUTPUT_COST_PER_M
    ) / 1_000_000
    return total, cost


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
    if status != "queued":
        return StageResult(
            error=f"Expected status='queued', got '{status}'"
        ).to_dict()

    keywords = get_keywords_for_slug(slug, db_path)
    kset = get_keyword_set_for_slug(slug, db_path)

    primary_kws = [k["keyword"] for k in keywords if k["keyword_type"] == "primary"]
    secondary_kws = [k["keyword"] for k in keywords if k["keyword_type"] == "secondary"]
    primary_keyword = primary_kws[0] if primary_kws else post.get("keyword", slug.replace("-", " "))

    category = post.get("category") or (kset.get("category") if kset else "blog")
    template_id = post.get("template_id", "blog-v5")
    word_count_target = 2500 if category != "languages" else 1500

    prompt = _OUTLINE_PROMPT.format(
        title=post["title"],
        category=category,
        primary_keyword=primary_keyword,
        secondary_keywords=", ".join(secondary_kws[:6]),
        template_id=template_id,
        word_count_target=word_count_target,
    )

    if dry_run:
        mock_outline = {
            "title": post["title"],
            "description": f"Learn about {primary_keyword} on devnook.dev.",
            "template_id": template_id,
            "sections": [
                {"heading": f"What is {primary_keyword}", "intent": "Opening", "target_words": 300},
                {"heading": "How it works", "intent": "Core concept", "target_words": 600},
                {"heading": "Examples", "intent": "Code examples", "target_words": 800},
                {"heading": "Best practices", "intent": "Practical tips", "target_words": 500},
                {"heading": "Next steps", "intent": "Closing", "target_words": 300},
            ],
            "must_cover": [f"{primary_keyword} fundamentals"],
            "code_examples_needed": 2,
            "external_links": [],
        }
        # Always write outline file so write stage can proceed in dry_run chain
        outlines_dir = pipeline_dir / "data" / "outlines"
        outlines_dir.mkdir(parents=True, exist_ok=True)
        (outlines_dir / f"{slug}.json").write_text(
            json.dumps(mock_outline, indent=2), encoding="utf-8"
        )
        return StageResult(
            processed=1,
            written=1,
            model=MODEL,
            details={"outline_sections": 5, "dry_run": True},
        ).to_dict()

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fence if present
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        outline = json.loads(raw)
    except json.JSONDecodeError as e:
        return StageResult(error=f"Outline JSON parse failed: {e}\nRaw: {raw[:200]}").to_dict()

    tokens, cost = _calc_cost(response.usage)

    if not dry_run:
        outlines_dir = pipeline_dir / "data" / "outlines"
        outlines_dir.mkdir(parents=True, exist_ok=True)
        outline_path = outlines_dir / f"{slug}.json"
        outline_path.write_text(json.dumps(outline, indent=2), encoding="utf-8")

        set_post_status(slug, "outlined", db_path)

    return StageResult(
        processed=1,
        written=1,
        model=MODEL,
        tokens=tokens,
        cost=round(cost, 6),
        details={"outline_sections": len(outline.get("sections", []))},
    ).to_dict()
