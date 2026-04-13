# Stage 5 — Content Pipeline: Writing, QA & Staging (Steps 3–6)

**Goal:** Build the second half of the content pipeline — the Writer Agent, SEO Optimizer, QA Agent, and Staging script. After this stage, running the full pipeline produces approved, staged .md files ready for the drip publisher.

**Depends on:** Stage 4 (registry.db must have queued posts + all utility modules exist)  
**Depends on:** Stage 1 (skill files must be written — especially qa-rejection-criteria.md, seo-writing-rules.md, devnook-brand-voice.md)  
**Unlocks:** Stage 6 (publishing picks up staged content) and Stage 7 (launch)  
**Estimated session time:** 1–2 focused sessions (~3–5 hours total)  
**LLM for this stage:** Gemini Flash (writer) + Gemini 2.5 Pro (editorial posts) + Gemini Flash (SEO/QA)

---

## Deliverables Checklist

- [ ] `agents/content-team/writer_agent.py`
- [ ] `agents/content-team/seo_optimizer.py`
- [ ] `agents/content-team/qa_agent.py`
- [ ] `agents/content-team/staging.py`
- [ ] Full pipeline end-to-end test passes (keyword → staged .md)

---

## File: `agents/content-team/writer_agent.py`

```python
"""
Step 3: Writer Agent
Takes queued posts from registry.db, loads the appropriate template,
calls Gemini to generate content, and saves the draft .md file.
"""

import re
from pathlib import Path
from datetime import date
from agents.utils import registry
from agents.utils.gemini_client import call_gemini
from agents.skills import load_skill

CONTENT_SCHEMA = load_skill("content-schema")
BRAND_VOICE = load_skill("devnook-brand-voice")
SEO_RULES = load_skill("seo-writing-rules")

TEMPLATES_DIR = Path("templates/templates")
DRAFTS_DIR = Path("agents/content-team/drafts")

SYSTEM = f"""You are a technical writer for devnook.dev. Write high-quality developer content.

{BRAND_VOICE}
{SEO_RULES}
{CONTENT_SCHEMA}"""

def load_template(template_id: str) -> str:
    """Load a template file by its ID."""
    type_map = {
        "lang": "language-post",
        "guide": "guide",
        "blog": "blog",
        "cheatsheet": "cheatsheet",
        "tool-exp": "tool-explainer"
    }
    prefix = template_id.rsplit("-v", 1)[0]
    folder = type_map.get(prefix, prefix)
    path = TEMPLATES_DIR / folder / f"{template_id}.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""

def choose_model(post: dict) -> str:
    """
    Select Gemini model based on content type and quality needs.
    - Editorial/blog: Pro (better reasoning, nuance)
    - Language posts: Flash (high volume, consistent structure)  
    - Guides: Flash (structured format)
    """
    if post["category"] == "blog" or post["template_id"] in ["blog-v4", "guide-v1"]:
        return "pro"
    return "flash"

def write_post(post: dict) -> str:
    """Generate markdown content for a queued post."""
    template = load_template(post["template_id"])
    model = choose_model(post)
    
    # Build context string for this specific post
    context = f"""
Post metadata:
- Slug: {post['slug']}
- Title: {post['title']}
- Description: {post['description']}
- Category: {post['category']}
- Language: {post.get('language', 'N/A')}
- Concept: {post.get('concept', 'N/A')}
- Primary keyword: {post['keyword']}
- Template: {post['template_id']}
- Target word count: {get_word_count_target(post['category'])}

Template structure to follow:
{template}
"""
    
    prompt = f"""Write a complete, publication-ready markdown post for devnook.dev.

{context}

Requirements:
1. Start with complete YAML frontmatter (use the exact schema for this content type)
2. Set published_date to today: {date.today().isoformat()}
3. Follow the template structure exactly
4. Write at least {get_word_count_target(post['category'])} words
5. Include at least 2 working code examples (for language posts/guides)
6. Add 3–5 internal links in format: [descriptive text](/category/slug)
   Use realistic DevNook URLs from these patterns:
   - /languages/python/list-comprehensions
   - /guides/what-is-rest-api
   - /tools/json-formatter
   - /cheatsheets/python-string-methods
7. Follow brand voice rules — no banned phrases
8. Primary keyword "{post['keyword']}" must appear in first 100 words

Write the complete markdown file content:"""
    
    return call_gemini(prompt, model=model, system=SYSTEM, max_tokens=6000)

def get_word_count_target(category: str) -> int:
    targets = {
        "languages": 1200,
        "guides": 1800,
        "blog": 1500,
        "cheatsheets": 800,
        "tools": 650
    }
    return targets.get(category, 1200)

def save_draft(slug: str, content: str) -> Path:
    """Save draft to agents/content-team/drafts/{slug}.md"""
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    path = DRAFTS_DIR / f"{slug}.md"
    path.write_text(content, encoding="utf-8")
    return path

def run(limit: int = 20) -> dict:
    """Write posts for all queued items in registry."""
    queued = registry.get_queued_posts(limit=limit)
    
    drafted = 0
    failed = 0
    
    for post in queued:
        post = dict(post)
        try:
            print(f"  Writing: {post['slug']}")
            content = write_post(post)
            file_path = save_draft(post["slug"], content)
            
            registry.update_post_status(
                post["slug"], 
                "drafted",
                file_path=str(file_path)
            )
            drafted += 1
            
        except Exception as e:
            print(f"  Failed '{post['slug']}': {e}")
            registry.update_post_status(post["slug"], "queued",  # keep in queue
                                        qa_notes=str(e))
            failed += 1
    
    return {"processed": len(queued), "passed": drafted, "rejected": failed}
```

---

## File: `agents/content-team/seo_optimizer.py`

```python
"""
Step 4: SEO Optimizer
Processes drafted posts to:
1. Validate and fix internal link counts (ensure 3–5 links)
2. Add schema.org JSON-LD to frontmatter
3. Verify keyword density in key positions
4. Update frontmatter description if too long/short
"""

import re
import frontmatter
from pathlib import Path
from agents.utils import registry
from agents.utils.gemini_client import call_gemini
from agents.skills import load_skill

SEO_RULES = load_skill("seo-writing-rules")
CONTENT_SCHEMA = load_skill("content-schema")

DRAFTS_DIR = Path("agents/content-team/drafts")

SCHEMA_ORG_TEMPLATES = {
    "languages": "TechArticle",
    "guides": "Article",
    "blog": "BlogPosting",
    "cheatsheets": "Article",
    "tools": "SoftwareApplication"
}

def count_internal_links(content: str) -> int:
    """Count markdown links starting with /"""
    return len(re.findall(r'\[([^\]]+)\]\((/[^\)]+)\)', content))

def count_words(content: str) -> int:
    """Count words in markdown (rough count, excludes frontmatter)"""
    # Remove frontmatter
    clean = re.sub(r'^---.*?---', '', content, flags=re.DOTALL).strip()
    # Remove code blocks (still counts them in word count)
    return len(clean.split())

def validate_description(description: str) -> bool:
    return 100 <= len(description) <= 160

def add_more_links(post: dict, content: str, current_count: int) -> str:
    """Ask Gemini to add more internal links if below minimum."""
    needed = 3 - current_count
    if needed <= 0:
        return content
    
    prompt = f"""This devnook.dev post needs {needed} more internal links added naturally into the text.

Current content:
{content[:3000]}...

Add {needed} internal links using this format: [descriptive text](/category/slug)
Valid URL patterns for devnook.dev:
- /languages/{{lang}}/{{concept}}
- /guides/{{slug}}
- /tools/{{slug}}
- /cheatsheets/{{subject}}

Return the full updated content with links added naturally (don't force them — weave into existing sentences):"""
    
    return call_gemini(prompt, model="flash", max_tokens=6000)

def generate_schema_org(post: dict) -> str:
    """Generate schema.org JSON-LD for a post."""
    schema_type = SCHEMA_ORG_TEMPLATES.get(post.get("category", "languages"), "TechArticle")
    base_url = "https://devnook.dev"
    slug = post.get("slug", "")
    category = post.get("category", "")
    url = f"{base_url}/{category}/{slug}"
    
    if schema_type == "SoftwareApplication":
        return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "{post.get('title', '')}",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Any",
  "offers": {{"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
  "url": "{url}"
}}
</script>"""
    else:
        return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "{schema_type}",
  "headline": "{post.get('title', '')}",
  "description": "{post.get('description', '')}",
  "datePublished": "{post.get('published_date', '')}",
  "author": {{"@type": "Organization", "name": "DevNook"}},
  "publisher": {{"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"}},
  "url": "{url}"
}}
</script>"""

def process_post(slug: str) -> dict:
    """Process a single drafted post through SEO optimization."""
    draft_path = DRAFTS_DIR / f"{slug}.md"
    if not draft_path.exists():
        return {"status": "error", "reason": "draft not found"}
    
    post = frontmatter.load(str(draft_path))
    content = post.content
    meta = post.metadata
    
    issues = []
    
    # 1. Check/fix internal links
    link_count = count_internal_links(content)
    if link_count < 3:
        content = add_more_links(meta, content, link_count)
        link_count = count_internal_links(content)
        issues.append(f"Added links (now {link_count})")
    
    # 2. Check description length
    desc = meta.get("description", "")
    if not validate_description(desc):
        issues.append(f"Description length issue: {len(desc)} chars")
    
    # 3. Add schema.org to frontmatter
    meta["schema_org"] = generate_schema_org(meta)
    
    # 4. Count words
    word_count = count_words(content)
    meta["actual_word_count"] = word_count
    
    # 5. Save optimized file
    new_post = frontmatter.Post(content, **meta)
    draft_path.write_text(frontmatter.dumps(new_post), encoding="utf-8")
    
    registry.update_post_status(slug, "optimized", 
                                word_count=word_count,
                                internal_links=link_count)
    
    return {"status": "ok", "word_count": word_count, "links": link_count, "issues": issues}

def run() -> dict:
    """Process all drafted posts."""
    from agents.utils.registry import get_db
    with get_db() as db:
        posts = db.execute("SELECT slug FROM posts WHERE status='drafted'").fetchall()
    
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
        else:
            failed += 1
    
    return {"processed": processed, "passed": passed, "rejected": failed}
```

---

## File: `agents/content-team/qa_agent.py`

```python
"""
Step 5: QA Agent
Validates all optimized posts against rejection criteria.
See agents/skills/qa-rejection-criteria.md for the full rules.
"""

import re
import json
import frontmatter
from pathlib import Path
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from agents.utils import registry
from agents.skills import load_skill

QA_CRITERIA = load_skill("qa-rejection-criteria")
BRAND_VOICE = load_skill("devnook-brand-voice")

DRAFTS_DIR = Path("agents/content-team/drafts")

VALID_CATEGORIES = {"languages", "guides", "blog", "cheatsheets", "tools"}
VALID_TEMPLATE_IDS = {
    "lang-v1", "lang-v2", "lang-v3", "lang-v4", "lang-v5",
    "guide-v1", "guide-v2", "guide-v3", "guide-v4",
    "blog-v1", "blog-v2", "blog-v3", "blog-v4", "blog-v5",
    "cheatsheet-v1", "cheatsheet-v2", "cheatsheet-v3", "cheatsheet-v4",
    "tool-exp-v1", "tool-exp-v2", "tool-exp-v3", "tool-exp-v4"
}

BANNED_PHRASES = [
    "let's dive in", "buckle up", "in this article, we will",
    "without further ado", "it's worth noting that",
    "in conclusion", "to summarize", "in summary",
    "at the end of the day", "game-changer", "leverage"
]

MIN_WORD_COUNTS = {
    "languages": 1000,
    "guides": 1500,
    "blog": 1200,
    "cheatsheets": 600,
    "tools": 500
}

def check_similarity(new_content: str, existing_contents: list) -> float:
    """Returns max TF-IDF similarity score (0–1). Reject if > 0.70"""
    if not existing_contents:
        return 0.0
    corpus = existing_contents + [new_content]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        return float(scores.max())
    except:
        return 0.0

def check_heading_hierarchy(content: str) -> bool:
    """Verify no heading level is skipped (H1→H2→H3, not H1→H3)."""
    headings = re.findall(r'^(#{1,6})\s', content, re.MULTILINE)
    levels = [len(h) for h in headings]
    for i in range(1, len(levels)):
        if levels[i] > levels[i-1] + 1:
            return False
    return True

def validate_post(slug: str, existing_contents: list) -> dict:
    """Run all QA checks on a post. Returns status and list of failures."""
    draft_path = DRAFTS_DIR / f"{slug}.md"
    if not draft_path.exists():
        return {"status": "rejected", "failures": ["draft_not_found"], "warnings": []}
    
    post = frontmatter.load(str(draft_path))
    meta = post.metadata
    content = post.content
    full_text = frontmatter.dumps(post)
    
    failures = []
    warnings = []
    
    # === STRUCTURAL CHECKS ===
    required_fields = ["title", "description", "published_date", "template_id", "category"]
    for field in required_fields:
        if not meta.get(field):
            failures.append(f"missing_field:{field}")
    
    if meta.get("category") not in VALID_CATEGORIES:
        failures.append(f"invalid_category:{meta.get('category')}")
    
    if meta.get("template_id") not in VALID_TEMPLATE_IDS:
        failures.append(f"invalid_template_id:{meta.get('template_id')}")
    
    desc = meta.get("description", "")
    if len(desc) > 160:
        failures.append(f"description_too_long:{len(desc)}")
    elif len(desc) < 100:
        failures.append(f"description_too_short:{len(desc)}")
    
    # Validate date format
    try:
        datetime.strptime(str(meta.get("published_date", "")), "%Y-%m-%d")
    except:
        failures.append("invalid_date_format")
    
    # === CONTENT QUALITY CHECKS ===
    word_count = meta.get("actual_word_count", len(content.split()))
    min_words = MIN_WORD_COUNTS.get(meta.get("category", "languages"), 1000)
    if word_count < min_words:
        failures.append(f"word_count_too_low:{word_count}<{min_words}")
    elif word_count < min_words * 1.1:
        warnings.append(f"word_count_borderline:{word_count}")
    
    # Code blocks for language posts and guides
    if meta.get("category") in ["languages", "guides"]:
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
    
    # Code block language tags
    untagged = re.findall(r'```\s*\n', content)
    if untagged:
        failures.append(f"code_block_no_language:{len(untagged)}")
    
    # === DUPLICATE DETECTION ===
    similarity = check_similarity(content, existing_contents)
    if similarity > 0.70:
        failures.append(f"duplicate_content:{similarity:.2f}")
    
    # Title uniqueness check (done via registry.db in run())
    
    # === TITLE LENGTH WARNING ===
    title = meta.get("title", "")
    if len(title) > 65:
        warnings.append(f"title_too_long:{len(title)}")
    
    qa_result = {
        "slug": slug,
        "qa_status": "approved" if not failures else "rejected",
        "word_count": word_count,
        "similarity_score": similarity,
        "internal_links": link_count,
        "rejections": failures,
        "warnings": warnings,
        "qa_timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return qa_result

def run() -> dict:
    """Run QA on all optimized posts."""
    from agents.utils.registry import get_db
    
    with get_db() as db:
        posts = db.execute("SELECT slug FROM posts WHERE status='optimized'").fetchall()
        # Load all approved post content for similarity check
        approved_paths = db.execute(
            "SELECT file_path FROM posts WHERE status IN ('approved','staged','published') AND file_path IS NOT NULL"
        ).fetchall()
    
    # Load existing content for TF-IDF comparison
    existing_contents = []
    for row in approved_paths:
        if row["file_path"]:
            p = Path(row["file_path"])
            if p.exists():
                existing_contents.append(p.read_text(encoding="utf-8"))
    
    processed = 0
    approved = 0
    rejected = 0
    
    for row in posts:
        slug = row["slug"]
        print(f"  QA: {slug}")
        result = validate_post(slug, existing_contents)
        processed += 1
        
        qa_status = result["qa_status"]
        
        registry.update_post_status(
            slug,
            qa_status,
            qa_status=qa_status,
            qa_notes=json.dumps(result),
            word_count=result["word_count"],
            similarity_score=result["similarity_score"],
            internal_links=result["internal_links"],
            rejection_reason="; ".join(result["rejections"]) if result["rejections"] else None
        )
        
        if qa_status == "approved":
            approved += 1
        else:
            rejected += 1
            print(f"    REJECTED: {', '.join(result['rejections'])}")
    
    return {"processed": processed, "passed": approved, "rejected": rejected}
```

---

## File: `agents/content-team/staging.py`

```python
"""
Step 6: Staging
Moves approved posts from drafts/ to /content-staging/.
The drip publisher (GitHub Actions) picks up from content-staging/.
"""

import shutil
from pathlib import Path
from datetime import datetime
from agents.utils import registry

DRAFTS_DIR = Path("agents/content-team/drafts")
STAGING_DIR = Path("content-staging")

def get_staging_path(post: dict) -> Path:
    """Determine where in content-staging the file should go."""
    category = post["category"]
    slug = post["slug"]
    
    if category == "languages":
        lang = post.get("language", "misc")
        return STAGING_DIR / "languages" / lang / f"{slug}.md"
    else:
        return STAGING_DIR / category / f"{slug}.md"

def run() -> dict:
    """Move all approved posts to content-staging."""
    from agents.utils.registry import get_db
    
    with get_db() as db:
        posts = db.execute("SELECT * FROM posts WHERE status='approved'").fetchall()
    
    moved = 0
    failed = 0
    now = datetime.utcnow().isoformat() + "Z"
    
    STAGING_DIR.mkdir(exist_ok=True)
    
    for post in posts:
        post = dict(post)
        slug = post["slug"]
        draft_path = DRAFTS_DIR / f"{slug}.md"
        
        if not draft_path.exists():
            print(f"  Missing draft: {slug}")
            failed += 1
            continue
        
        staging_path = get_staging_path(post)
        staging_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(str(draft_path), str(staging_path))
        
        registry.update_post_status(
            slug, "staged",
            staged_at=now,
            file_path=str(staging_path)
        )
        
        print(f"  Staged: {slug} → {staging_path}")
        moved += 1
    
    print(f"\n  Total in staging: {STAGING_DIR} tree")
    return {"processed": len(posts), "passed": moved, "rejected": failed}
```

---

## End-to-End Pipeline Test

After building all 4 agents, run the complete pipeline:

```bash
# 1. Make sure registry has queued posts (from Stage 4)
sqlite3 agents/content-team/registry.db "SELECT COUNT(*) FROM posts WHERE status='queued';"

# 2. Run write → seo → qa → stage
python agents/content-team/run-pipeline.py --steps writer,seo,qa,staging

# 3. Check results
sqlite3 agents/content-team/registry.db \
  "SELECT status, COUNT(*) FROM posts GROUP BY status;"

# 4. Inspect a staged file
ls content-staging/languages/python/
cat content-staging/languages/python/python-list-comprehensions.md | head -30
```

---

## Verification

- [ ] `python run-pipeline.py --steps writer` creates draft files in `agents/content-team/drafts/`
- [ ] `python run-pipeline.py --steps seo` updates drafts with schema.org and additional links
- [ ] `python run-pipeline.py --steps qa` approves at least 70% of drafts
- [ ] QA rejection reasons are logged in registry.db `qa_notes` column
- [ ] `python run-pipeline.py --steps staging` moves approved files to `content-staging/`
- [ ] Content in `content-staging/` has valid frontmatter
- [ ] Word count in staged files meets minimums
- [ ] No duplicate slugs between staged files
- [ ] Full pipeline `--steps all` runs without crashing
- [ ] After 1 full pipeline run: at least 10 staged posts ready for publishing
