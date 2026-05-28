"""
write.py — Stage: outlined → drafted

Calls Claude API to write the full article from the outline.
Reads content-style-system.md, seo-writing-rules.md for style guidance.
Saves draft to pipeline/agents/content-team/drafts/{slug}.md.
Idempotent: skips if post is already past 'outlined'.
"""

import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Union

import anthropic

from ._db import get_post, set_post_status, get_keywords_for_slug
from ._types import StageResult

MODEL = "claude-sonnet-4-6"
INPUT_COST_PER_M = 3.0
OUTPUT_COST_PER_M = 15.0

ALREADY_PAST = {"drafted", "linked", "approved", "published"}


def _calc_cost(usage: anthropic.types.Usage) -> tuple[int, float]:
    total = usage.input_tokens + usage.output_tokens
    cost = (
        usage.input_tokens * INPUT_COST_PER_M
        + usage.output_tokens * OUTPUT_COST_PER_M
    ) / 1_000_000
    return total, cost


def _count_words(text: str) -> int:
    body = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
    return len(body.split())


def _load_skill(skills_dir: Path, filename: str) -> str:
    path = skills_dir / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _build_system_prompt(skills_dir: Path) -> str:
    style = _load_skill(skills_dir, "content-style-system.md")
    seo = _load_skill(skills_dir, "seo-writing-rules.md")
    brand = _load_skill(skills_dir, "devnook-brand-voice.md")

    return f"""You are a technical writer for devnook.dev, a developer resource site.

You write clear, precise, code-heavy articles for working developers. No fluff. No marketing speak.

## Brand Voice & Style
{brand}

## SEO Writing Rules
{seo}

## Content Style System
{style}

## Critical rules (hard-fail at QA if violated)
- Do NOT write a # H1 heading — frontmatter title renders as <h1> automatically.
- Do NOT write a "## Related" section — it's auto-generated at render time.
- Frontmatter MUST start on line 1 with exactly `---`.
- YAML values containing `: ` must be quoted.
- description must be 140–160 characters.
- Every code block must have a language tag (```python, ```bash, etc.).
- Minimum 1–2 external links to authoritative sources.
- Minimum 3 internal links (devnook.dev/...) — do not fabricate /languages/ paths.
  Only link to paths you are confident exist: /tools/, /guides/, /blog/ slugs are safer.
"""


def _build_user_prompt(post: dict, outline: dict, keywords: list[dict]) -> str:
    primary_kws = [k["keyword"] for k in keywords if k["keyword_type"] == "primary"]
    secondary_kws = [k["keyword"] for k in keywords if k["keyword_type"] in ("secondary", "longtail")]

    today = date.today().isoformat()
    category = post.get("category", "blog")
    language = post.get("language") or ""
    concept = post.get("concept") or ""
    template_id = post.get("template_id", "blog-v5")

    sections_text = "\n".join(
        f'- **{s["heading"]}** (~{s.get("target_words", 400)} words): {s.get("intent", "")}'
        for s in outline.get("sections", [])
    )

    must_cover = "\n".join(f"- {p}" for p in outline.get("must_cover", []))
    ext_links = json.dumps(outline.get("external_links", []), indent=2)

    word_target = 2500 if category != "languages" else 1500

    return f"""Write a complete devnook.dev article based on this outline.

## Post metadata
- Slug: {post["slug"]}
- Category: {category}
- Language: {language or "n/a"}
- Concept: {concept or "n/a"}
- Template: {template_id}
- Primary keywords: {", ".join(primary_kws)}
- Secondary keywords: {", ".join(secondary_kws[:8])}
- Word count target: {word_target}+ words

## Outline
Title: {outline.get("title", post["title"])}
Meta description: {outline.get("description", "")}

Sections:
{sections_text}

Must cover:
{must_cover}

Authoritative external links to include:
{ext_links}

## Frontmatter to use (fill in the values exactly)
```yaml
---
title: "{outline.get("title", post["title"])}"
description: "{outline.get("description", "")}"
category: {category}
{"language: " + language if language else ""}
{"concept: " + concept if concept else ""}
template_id: {template_id}
tags: []
related_posts: []
related_tools: []
published_date: "{today}"
---
```

Write the complete article now, starting with the frontmatter block.
Do NOT write a # H1. Do NOT write ## Related. Follow all style rules.
"""


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
    if status != "outlined":
        return StageResult(error=f"Expected status='outlined', got '{status}'").to_dict()

    outline_path = pipeline_dir / "data" / "outlines" / f"{slug}.json"
    if not outline_path.exists():
        return StageResult(error=f"Outline not found: {outline_path}").to_dict()
    outline = json.loads(outline_path.read_text(encoding="utf-8"))

    keywords = get_keywords_for_slug(slug, db_path)
    skills_dir = pipeline_dir / "agents" / "skills"
    drafts_dir = pipeline_dir / "agents" / "content-team" / "drafts"

    if dry_run:
        # Write a valid draft (padded to meet word floor) so all downstream stages can run
        today = date.today().isoformat()
        category = post.get("category", "blog")
        keyword = post.get("keyword") or slug.replace("-", " ")
        # Pad each section to ~500 words so QA word floor is met
        _pad = (
            f"This section covers important aspects of {keyword} that developers need to "
            f"understand. When working with {keyword}, there are several considerations to "
            f"keep in mind. First, ensure that you have a solid understanding of the basics "
            f"before moving on to more advanced topics. Second, practice with real examples "
            f"to reinforce your understanding. Third, refer to the official documentation "
            f"when in doubt. The following code example demonstrates a typical use case. "
        ) * 11
        sections_body = "".join(
            f"\n## {s['heading']}\n\n{_pad}\n\n```bash\n# Example for {s['heading'].lower()}\necho 'hello world'\n```\n"
            for s in outline.get("sections", [])[1:-1]
        )
        mock_draft = f"""---
title: "{post['title']}"
description: "Learn {keyword} with practical examples and best practices. This complete guide covers everything developers need to know, from basics to advanced patterns."
category: {category}
template_id: {post.get('template_id', 'blog-v5')}
tags: []
related_posts: []
related_tools: []
published_date: "{today}"
---

## Introduction to {keyword.title()}

{_pad}

For more developer tools, explore [devnook tools](/tools/) and [guides](/guides/).
{sections_body}

## Next Steps

You now have a solid foundation for working with {keyword}.
Check out our [tools](/tools/) or explore more [guides](/guides/).
See also the [official documentation](https://www.gnu.org/software/bash/manual/) for reference.
"""
        drafts_dir.mkdir(parents=True, exist_ok=True)
        draft_path = drafts_dir / f"{slug}.md"
        draft_path.write_text(mock_draft, encoding="utf-8")
        return StageResult(
            processed=1,
            written=1,
            model=MODEL,
            details={"dry_run": True, "draft_path": str(draft_path), "word_count": len(mock_draft.split())},
        ).to_dict()

    system_prompt = _build_system_prompt(skills_dir)
    user_prompt = _build_user_prompt(post, outline, keywords)

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    content = response.content[0].text.strip()

    # Strip stray markdown fence if the model wrapped the whole output
    if content.startswith("```markdown"):
        content = content[len("```markdown"):].strip()
        if content.endswith("```"):
            content = content[:-3].strip()

    tokens, cost = _calc_cost(response.usage)
    word_count = _count_words(content)

    drafts_dir.mkdir(parents=True, exist_ok=True)
    draft_path = drafts_dir / f"{slug}.md"
    draft_path.write_text(content, encoding="utf-8")

    set_post_status(slug, "drafted", db_path, word_count=word_count)

    return StageResult(
        processed=1,
        written=1,
        model=MODEL,
        tokens=tokens,
        cost=round(cost, 6),
        details={"word_count": word_count, "draft_path": str(draft_path)},
    ).to_dict()
