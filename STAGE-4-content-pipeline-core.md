# Stage 4 — Content Pipeline: Research & Planning (Steps 1–2)

**Goal:** Build the first half of the content pipeline — the orchestrator script plus the Keyword Agent and Planner Agent. After this stage you can run `python run-pipeline.py --step keyword` and `--step planner` to fill `registry.db` with a queue of content ready to write.

**Depends on:** Stage 1 (skill files + registry.db schema)  
**Unlocks:** Stage 5 (writing needs a filled queue)  
**Estimated session time:** 1 focused session (~2–3 hours)  
**LLM for this stage:** Gemini Flash (keyword research) + Gemini 2.5 Pro (planner scoring)

---

## Deliverables Checklist

- [ ] `agents/content-team/run-pipeline.py` — orchestrator with step routing
- [ ] `agents/content-team/keyword_agent.py` — Google Autocomplete + scoring
- [ ] `agents/content-team/planner_agent.py` — opportunity ranking + template assignment
- [ ] `agents/content-team/registry.db` — initialized with schema from Stage 1
- [ ] `agents/utils/gemini_client.py` — Gemini API wrapper (free tier)
- [ ] `agents/utils/openrouter_client.py` — Claude via OpenRouter wrapper
- [ ] Running `python run-pipeline.py --steps keyword,planner` populates registry.db queue

---

## Architecture Overview

```
run-pipeline.py  (orchestrator)
├── --step keyword   → keyword_agent.py
├── --step planner   → planner_agent.py
├── --step writer    → writer_agent.py        [Stage 5]
├── --step seo       → seo_optimizer.py       [Stage 5]
├── --step qa        → qa_agent.py            [Stage 5]
└── --step staging   → staging.py             [Stage 5]
```

All agents share:
- `agents/utils/gemini_client.py` — Gemini API calls
- `agents/utils/openrouter_client.py` — Claude via OpenRouter
- `agents/utils/registry.py` — SQLite read/write helpers
- `agents/skills/` — loaded as context strings

---

## File: `agents/utils/gemini_client.py`

```python
"""
Gemini API client for DevNook content agents.
Uses the free tier: Flash for bulk, Flash-Lite for fast/cheap, Pro for quality.
"""

import os
import requests
import time

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

MODELS = {
    "flash": "gemini-1.5-flash",           # bulk generation (fast, free)
    "flash-lite": "gemini-1.5-flash-8b",   # very fast, even cheaper
    "pro": "gemini-2.5-pro-preview-0506",  # quality writing (free but rate-limited)
}

def call_gemini(prompt: str, model: str = "flash", system: str = "", 
                max_tokens: int = 4096, retry: int = 3) -> str:
    """Call Gemini API with retry on rate limit."""
    model_id = MODELS.get(model, model)
    url = f"{BASE_URL}/{model_id}:generateContent?key={GEMINI_API_KEY}"
    
    contents = []
    if system:
        contents.append({"role": "user", "parts": [{"text": f"[System context]\n{system}"}]})
        contents.append({"role": "model", "parts": [{"text": "Understood. I will follow these instructions."}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    
    for attempt in range(retry):
        try:
            response = requests.post(url, json={
                "contents": contents,
                "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}
            }, timeout=60)
            
            if response.status_code == 429:  # Rate limited
                wait = 60 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
                
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            
        except Exception as e:
            if attempt == retry - 1:
                raise
            time.sleep(5)
    
    raise RuntimeError("Gemini API failed after retries")
```

---

## File: `agents/utils/registry.py`

```python
"""
SQLite registry helpers for DevNook pipeline agents.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path("agents/content-team/registry.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def slug_exists(slug: str) -> bool:
    with get_db() as db:
        return db.execute("SELECT 1 FROM posts WHERE slug=?", (slug,)).fetchone() is not None

def get_queued_posts(limit: int = 50) -> list:
    with get_db() as db:
        return db.execute(
            "SELECT * FROM posts WHERE status='queued' ORDER BY opportunity_score DESC LIMIT ?",
            (limit,)
        ).fetchall()

def get_published_slugs() -> list[str]:
    with get_db() as db:
        rows = db.execute("SELECT slug FROM posts WHERE status IN ('approved','staged','published')").fetchall()
        return [r["slug"] for r in rows]

def add_post(slug: str, title: str, description: str, category: str, 
             language: str = None, concept: str = None, template_id: str = None,
             keyword: str = None, opportunity_score: float = None) -> bool:
    """Add a post to the registry. Returns False if slug already exists."""
    if slug_exists(slug):
        return False
    with get_db() as db:
        db.execute("""
            INSERT INTO posts (slug, title, description, category, language, concept, 
                             template_id, keyword, opportunity_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'queued')
        """, (slug, title, description, category, language, concept, 
               template_id, keyword, opportunity_score))
    return True

def update_post_status(slug: str, status: str, **kwargs):
    """Update post status and any additional fields."""
    with get_db() as db:
        fields = ["status=?", "updated_at=datetime('now')"]
        values = [status]
        for key, val in kwargs.items():
            fields.append(f"{key}=?")
            values.append(val)
        values.append(slug)
        db.execute(f"UPDATE posts SET {', '.join(fields)} WHERE slug=?", values)

def get_next_template(category: str) -> str:
    """Round-robin template selection for a category."""
    template_map = {
        "languages": ["lang-v1", "lang-v2", "lang-v3", "lang-v4", "lang-v5"],
        "guides": ["guide-v1", "guide-v2", "guide-v3", "guide-v4"],
        "blog": ["blog-v1", "blog-v2", "blog-v3", "blog-v4", "blog-v5"],
        "cheatsheets": ["cheatsheet-v1", "cheatsheet-v2", "cheatsheet-v3", "cheatsheet-v4"],
        "tools": ["tool-exp-v1", "tool-exp-v2", "tool-exp-v3", "tool-exp-v4"],
    }
    templates = template_map.get(category, ["lang-v1"])
    with get_db() as db:
        # Get the least-used template for this category
        results = db.execute("""
            SELECT template_id, usage_count FROM template_counters 
            WHERE template_id IN ({})
            ORDER BY usage_count ASC LIMIT 1
        """.format(",".join("?" * len(templates))), templates).fetchone()
        template = results["template_id"] if results else templates[0]
        db.execute("UPDATE template_counters SET usage_count=usage_count+1, last_used=datetime('now') WHERE template_id=?", (template,))
    return template

def log_pipeline_run(run_date: str, step: str, processed: int, passed: int, 
                     rejected: int, duration: float, notes: str = ""):
    with get_db() as db:
        db.execute("""
            INSERT INTO pipeline_runs (run_date, step, posts_processed, posts_passed, 
                                      posts_rejected, duration_seconds, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (run_date, step, processed, passed, rejected, duration, notes))
```

---

## File: `agents/content-team/run-pipeline.py`

```python
#!/usr/bin/env python3
"""
DevNook Content Pipeline Orchestrator
Runs the 6-step content creation pipeline.

Usage:
  python run-pipeline.py --steps keyword,planner      # Steps 1-2
  python run-pipeline.py --steps writer,seo,qa,staging  # Steps 3-6
  python run-pipeline.py --steps all                   # Full pipeline
  python run-pipeline.py --steps keyword               # Single step

Environment variables required:
  GEMINI_API_KEY        — for keyword, planner, writer, seo, qa agents
  OPENROUTER_API_KEY    — (optional) fallback when Gemini is rate-limited
"""

import argparse
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.utils import registry

STEPS = ["keyword", "planner", "writer", "seo", "qa", "staging"]

def run_step(step: str) -> dict:
    start = time.time()
    today = date.today().isoformat()
    
    if step == "keyword":
        from agents.content_team.keyword_agent import run as run_keyword
        result = run_keyword()
    elif step == "planner":
        from agents.content_team.planner_agent import run as run_planner
        result = run_planner()
    elif step == "writer":
        from agents.content_team.writer_agent import run as run_writer
        result = run_writer()
    elif step == "seo":
        from agents.content_team.seo_optimizer import run as run_seo
        result = run_seo()
    elif step == "qa":
        from agents.content_team.qa_agent import run as run_qa
        result = run_qa()
    elif step == "staging":
        from agents.content_team.staging import run as run_staging
        result = run_staging()
    else:
        raise ValueError(f"Unknown step: {step}")
    
    duration = time.time() - start
    registry.log_pipeline_run(today, step, result.get("processed", 0), 
                               result.get("passed", 0), result.get("rejected", 0), duration)
    return result

def main():
    parser = argparse.ArgumentParser(description="DevNook Content Pipeline")
    parser.add_argument("--steps", default="all", 
                        help="Comma-separated steps or 'all'. Steps: keyword,planner,writer,seo,qa,staging")
    args = parser.parse_args()
    
    steps_to_run = STEPS if args.steps == "all" else args.steps.split(",")
    
    print(f"=== DevNook Pipeline — {date.today()} ===")
    print(f"Running steps: {', '.join(steps_to_run)}\n")
    
    for step in steps_to_run:
        print(f"→ Step: {step.upper()}")
        result = run_step(step)
        print(f"  Processed: {result.get('processed', '?')} | "
              f"Passed: {result.get('passed', '?')} | "
              f"Rejected: {result.get('rejected', '?')}")
    
    print("\n=== Pipeline Complete ===")

if __name__ == "__main__":
    main()
```

---

## File: `agents/content-team/keyword_agent.py`

```python
"""
Step 1: Keyword Agent
Discovers keyword opportunities using Google Autocomplete API.
Scores them and adds new ones to registry.db keywords table.
"""

import requests
import time
import json
from agents.utils import registry
from agents.utils.gemini_client import call_gemini

# Seed topics that generate keyword expansion
SEED_TOPICS = {
    "languages": [
        "how to {concept} in python",
        "how to {concept} in javascript", 
        "python {concept} tutorial",
        "javascript {concept} example",
        # ... extended list of seed patterns
    ],
    "concepts": [
        "list comprehension", "async await", "decorator", "generator",
        "closure", "recursion", "sorting", "filtering", "mapping",
        "string formatting", "file handling", "error handling",
        "class inheritance", "interface", "enum", "type hints",
        "regular expressions", "datetime", "json parsing",
        "HTTP requests", "database queries", "environment variables",
        # Ring 3: 50 concepts × 12 languages = 600+ posts
    ],
    "languages_list": [
        "python", "javascript", "typescript", "go", "rust",
        "java", "csharp", "php", "ruby", "swift", "kotlin", "cpp"
    ],
    "tool_adjacent": [
        "json formatter", "base64 decode", "regex tester online",
        "unix timestamp converter", "uuid generator", "jwt decoder",
        "html entity encoder", "cron expression", "css gradient generator",
        "markdown preview", "diff viewer", "color picker online"
    ],
    "guides": [
        "what is REST API", "how does HTTP work", "what is JWT",
        "difference between authentication and authorization",
        "what is Big O notation", "how does garbage collection work"
    ]
}

def fetch_autocomplete(query: str) -> list[str]:
    """Get Google Autocomplete suggestions for a query."""
    url = "https://suggestqueries.google.com/complete/search"
    try:
        resp = requests.get(url, params={"client": "firefox", "q": query}, timeout=10)
        return resp.json()[1] if resp.status_code == 200 else []
    except:
        return []

def score_keyword(keyword: str, existing_slugs: list[str]) -> float:
    """
    Score a keyword 0-100 based on:
    - Length (3-6 words = sweet spot)
    - Not already in registry
    - Question/intent keywords score higher
    - Language-specific score higher (more specific = better conversion)
    """
    score = 50.0
    words = keyword.lower().split()
    
    # Length scoring
    if 3 <= len(words) <= 6:
        score += 20
    elif len(words) <= 2:
        score -= 20
    
    # Intent signals
    if any(w in keyword.lower() for w in ["how to", "what is", "difference", "tutorial", "example"]):
        score += 15
    
    # Language-specific
    languages = ["python", "javascript", "typescript", "go", "rust", "java", "kotlin", "swift"]
    if any(lang in keyword.lower() for lang in languages):
        score += 10
    
    # Already exists penalty
    slug = keyword.lower().replace(" ", "-").replace("?", "")
    if any(slug in existing for existing in existing_slugs):
        score -= 100  # Will be filtered out
    
    return min(max(score, 0), 100)

def run() -> dict:
    """Main keyword agent runner."""
    print("  Loading existing slugs from registry...")
    existing_slugs = registry.get_published_slugs()
    
    discovered = 0
    skipped = 0
    
    # Generate keywords from all seed combinations
    keywords_to_check = set()
    
    # Tool-adjacent (Ring 1) — highest priority
    for query in SEED_TOPICS["tool_adjacent"]:
        suggestions = fetch_autocomplete(query)
        keywords_to_check.update(suggestions[:5])
        time.sleep(0.5)  # Be nice to Google
    
    # Language + Concept combinations (Ring 3)
    for concept in SEED_TOPICS["concepts"][:20]:  # Process 20 concepts per run
        for lang in SEED_TOPICS["languages_list"]:
            query = f"how to {concept} in {lang}"
            suggestions = fetch_autocomplete(query)
            keywords_to_check.update(suggestions[:3])
        time.sleep(0.2)
    
    # Score and store new keywords
    for keyword in keywords_to_check:
        score = score_keyword(keyword, existing_slugs)
        if score < 0:
            skipped += 1
            continue
            
        from agents.utils.registry import get_db
        with get_db() as db:
            try:
                db.execute(
                    "INSERT OR IGNORE INTO keywords (keyword, competition, status) VALUES (?, 'unknown', 'discovered')",
                    (keyword,)
                )
                discovered += 1
            except:
                skipped += 1
    
    return {"processed": len(keywords_to_check), "passed": discovered, "rejected": skipped}
```

---

## File: `agents/content-team/planner_agent.py`

```python
"""
Step 2: Planner Agent
Takes discovered keywords from keywords table, scores them for opportunity,
assigns template IDs, and adds them to posts table as 'queued'.
"""

import json
from agents.utils import registry
from agents.utils.gemini_client import call_gemini
from agents.skills import load_skill

CONTENT_SCHEMA = load_skill("content-schema")
SEO_RULES = load_skill("seo-writing-rules")

SYSTEM = f"""You are a content planner for devnook.dev. 
{CONTENT_SCHEMA}
{SEO_RULES}"""

def classify_keyword(keyword: str) -> dict:
    """Use Gemini to classify a keyword and generate post metadata."""
    prompt = f"""For the keyword: "{keyword}"

Determine:
1. category: one of [languages, guides, blog, cheatsheets, tools]
2. language: which programming language (null if not language-specific)
3. concept: the core concept in kebab-case (null if not language post)
4. slug: URL slug (lowercase, kebab-case, max 60 chars, no stop words)
5. title: SEO-optimized title following the title patterns in our rules
6. description: meta description (140-160 chars, includes keyword)
7. opportunity_score: 0-100 based on keyword specificity and search intent
   - 80-100: Very specific, clear intent, long-tail
   - 60-80: Good keyword, moderate competition expected
   - 40-60: Broad topic, may face competition
   - Below 40: Skip it

Respond with JSON only, no explanation:
{{"category": "...", "language": "...", "concept": "...", "slug": "...", 
  "title": "...", "description": "...", "opportunity_score": 75}}"""
    
    response = call_gemini(prompt, model="flash", system=SYSTEM)
    # Parse JSON from response
    import re
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    return json.loads(json_match.group()) if json_match else None

def run() -> dict:
    """Main planner agent runner."""
    from agents.utils.registry import get_db
    
    # Get unprocessed keywords
    with get_db() as db:
        keywords = db.execute(
            "SELECT keyword FROM keywords WHERE status='discovered' ORDER BY ROWID LIMIT 100"
        ).fetchall()
    
    processed = 0
    queued = 0
    rejected = 0
    
    for row in keywords:
        keyword = row["keyword"]
        
        try:
            meta = classify_keyword(keyword)
            if not meta or meta.get("opportunity_score", 0) < 40:
                rejected += 1
                with get_db() as db:
                    db.execute("UPDATE keywords SET status='rejected' WHERE keyword=?", (keyword,))
                continue
            
            # Assign template using round-robin
            template_id = registry.get_next_template(meta["category"])
            
            # Add to posts queue
            added = registry.add_post(
                slug=meta["slug"],
                title=meta["title"],
                description=meta["description"],
                category=meta["category"],
                language=meta.get("language"),
                concept=meta.get("concept"),
                template_id=template_id,
                keyword=keyword,
                opportunity_score=meta["opportunity_score"]
            )
            
            if added:
                queued += 1
                with get_db() as db:
                    db.execute("UPDATE keywords SET status='assigned', assigned_slug=? WHERE keyword=?",
                              (meta["slug"], keyword))
            else:
                rejected += 1  # slug already exists
                
            processed += 1
            
        except Exception as e:
            print(f"  Error planning '{keyword}': {e}")
            rejected += 1
    
    return {"processed": processed, "passed": queued, "rejected": rejected}
```

---

## Skills Loader Utility (`agents/skills/__init__.py`)

```python
"""Load skill files as strings for injection into agent prompts."""
from pathlib import Path

SKILLS_DIR = Path(__file__).parent

def load_skill(name: str) -> str:
    """Load a skill file by name (without .md extension)."""
    path = SKILLS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""
```

---

## Setup & Environment

Create `.env.example` in project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Create `agents/requirements.txt`:
```
requests>=2.31.0
scikit-learn>=1.3.0
python-frontmatter>=1.1.0
google-auth>=2.23.0
google-auth-httplib2>=0.1.1
python-dotenv>=1.0.0
```

Initialize registry before first run:
```bash
sqlite3 agents/content-team/registry.db < agents/content-team/registry-schema.sql
```

---

## Verification

- [ ] `python -m pytest agents/tests/test_keyword_agent.py` passes
- [ ] `python run-pipeline.py --steps keyword` discovers at least 20 new keywords
- [ ] `sqlite3 agents/content-team/registry.db "SELECT COUNT(*) FROM keywords;"` > 0
- [ ] `python run-pipeline.py --steps planner` queues at least 10 posts
- [ ] `sqlite3 agents/content-team/registry.db "SELECT slug, title, template_id, opportunity_score FROM posts WHERE status='queued' LIMIT 5;"` shows valid data
- [ ] Template distribution is varied (not all lang-v1)
- [ ] No duplicate slugs in registry
