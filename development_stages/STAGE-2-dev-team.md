# Stage 2 — Developer Team Agents (Astro Site Builder)

**Goal:** Build the two Python scripts that generate and maintain the entire Astro codebase. `scaffold.py` runs once to create the full Astro project. `update.py` runs after each content pipeline run to refresh language hubs and homepage stats.

**Depends on:** Stage 1 (read `agents/skills/astro-conventions.md` before writing these scripts)  
**Unlocks:** Stage 7 (site generation) — but tools and content can be built in Stage 3–5 first  
**Estimated session time:** 1 full session (~3–4 hours)  
**LLM for this stage:** Claude Sonnet via OpenRouter (better code generation quality)

---

## Deliverables Checklist

- [ ] `agents/dev-team/scaffold.py` — generates entire Astro project
- [ ] `agents/dev-team/update.py` — updates existing Astro project with new content
- [ ] Running `python agents/dev-team/scaffold.py` creates a working Astro site in `/src/`

---

## Agent Approach

Both scripts use Claude Sonnet via OpenRouter to generate code. They:
1. Load the `agents/skills/astro-conventions.md` skill file as system context
2. Build the Astro project piece by piece (not in one giant prompt)
3. Write each generated file to disk
4. Log decisions to `agents/content-team/DECISIONS.md`

---

## File: `agents/dev-team/scaffold.py`

### What it generates (full file list)

**Config files:**
- `package.json` — Astro + integrations (image, sitemap, @astrojs/check)
- `astro.config.mjs` — Cloudflare Pages adapter + content collections config
- `tsconfig.json`

**Styles:**
- `src/styles/tokens.css` — all CSS custom properties (colors, fonts, spacing, radius)
- `src/styles/global.css` — reset + base typography

**Layouts:**
- `src/layouts/BaseLayout.astro` — head, meta, NavBar, Footer, schema.org slot
- `src/layouts/PostLayout.astro` — article layout with sidebar + TOC
- `src/layouts/ToolLayout.astro` — tool page layout (component + explainer below)

**Components:**
- `src/components/NavBar.astro`
- `src/components/Footer.astro`
- `src/components/PostCard.astro`
- `src/components/ToolCard.astro`
- `src/components/LanguageCard.astro`
- `src/components/CodeBlock.astro`
- `src/components/TagBadge.astro`
- `src/components/SearchBar.astro` (Fuse.js client-side search)
- `src/components/OGImage.astro` (Satori build-time OG generation)
- `src/components/Breadcrumb.astro`
- `src/components/RelatedPosts.astro`

**Pages (static + dynamic):**
- `src/pages/index.astro` — homepage
- `src/pages/languages/index.astro` — languages index
- `src/pages/languages/[lang]/index.astro` — language hub (dynamic)
- `src/pages/languages/[lang]/[concept].astro` — concept post (dynamic)
- `src/pages/guides/index.astro`
- `src/pages/guides/[slug].astro`
- `src/pages/cheatsheets/index.astro`
- `src/pages/cheatsheets/[subject].astro`
- `src/pages/blog/index.astro`
- `src/pages/blog/[slug].astro`
- `src/pages/tools/index.astro`
- `src/pages/tools/[slug].astro`
- `src/pages/404.astro`
- `src/pages/sitemap-index.xml.ts` (Astro sitemap integration)

**Content collections config:**
- `src/content/config.ts` — zod schemas for all 5 content types

**OG image pages:**
- `src/pages/og/languages/[...slug].png.ts`
- `src/pages/og/guides/[slug].png.ts`
- `src/pages/og/tools/[slug].png.ts`
- `src/pages/og/blog/[slug].png.ts`
- `src/pages/og/cheatsheets/[slug].png.ts`

### Script structure outline

```python
#!/usr/bin/env python3
"""
DevNook Dev Team — scaffold.py
Generates the complete Astro project structure for devnook.dev
Run once from project root: python agents/dev-team/scaffold.py
"""

import os
import json
from pathlib import Path
from openrouter_client import call_claude  # see implementation notes below

SKILLS_DIR = Path("agents/skills")
PROJECT_ROOT = Path(".")

ASTRO_CONVENTIONS = (SKILLS_DIR / "astro-conventions.md").read_text()

SYSTEM_PROMPT = f"""You are an expert Astro developer building devnook.dev.
Follow these conventions exactly:

{ASTRO_CONVENTIONS}

When generating code:
- Use exact token names from tokens.css
- Follow the component naming conventions
- Write complete, working code (no placeholders)
- Use TypeScript where applicable
"""

def generate_file(filename: str, description: str, context: str = "") -> str:
    """Call Claude to generate a single file."""
    prompt = f"Generate the complete contents of `{filename}` for devnook.dev. {description}"
    if context:
        prompt += f"\n\nAdditional context:\n{context}"
    return call_claude(system=SYSTEM_PROMPT, prompt=prompt)

def write_file(path: str, content: str):
    """Write content to file, creating directories as needed."""
    full_path = PROJECT_ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"  ✓ {path}")

def scaffold():
    print("=== DevNook Scaffold — Starting ===\n")

    # 1. Config files
    print("→ Generating config files...")
    write_file("package.json", generate_file("package.json", "Astro project with @astrojs/cloudflare, @astrojs/sitemap, sharp, fuse.js, @resvg/resvg-js, satori"))
    write_file("astro.config.mjs", generate_file("astro.config.mjs", "Cloudflare Pages adapter, content collections, sitemap integration, image optimization"))
    write_file("tsconfig.json", generate_file("tsconfig.json", "TypeScript config for Astro project"))

    # 2. Styles
    print("→ Generating styles...")
    write_file("src/styles/tokens.css", generate_file("src/styles/tokens.css", "All CSS custom properties: colors, fonts (Outfit + JetBrains Mono), spacing scale, border radius, shadows"))
    write_file("src/styles/global.css", generate_file("src/styles/global.css", "CSS reset, base typography using font tokens, link styles, code styles"))

    # 3. Content config
    print("→ Generating content config...")
    write_file("src/content/config.ts", generate_file("src/content/config.ts", "Zod schemas for all 5 content collections: languages, guides, cheatsheets, blog, tools"))

    # 4. Layouts
    print("→ Generating layouts...")
    # ... (continue for each layout and component)

    # 5. Components
    # ... 

    # 6. Pages
    # ...

    print("\n=== Scaffold Complete ===")
    print("Run: npm install && npm run dev")

if __name__ == "__main__":
    scaffold()
```

### OpenRouter client (shared utility)

Create `agents/utils/openrouter_client.py`:

```python
import os
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
CLAUDE_MODEL = "anthropic/claude-sonnet-4-5"

def call_claude(system: str, prompt: str, max_tokens: int = 4096) -> str:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://devnook.dev",
            "Content-Type": "application/json"
        },
        json={
            "model": CLAUDE_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens
        }
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
```

---

## File: `agents/dev-team/update.py`

### What it does

Reads `registry.db` to get current content stats and regenerates:
1. `src/pages/index.astro` — updates post count, tool count, featured content
2. `src/pages/languages/[lang]/index.astro` — adds new language hubs as new languages appear in registry
3. `src/pages/languages/index.astro` — updates language list + post counts
4. `src/pages/tools/index.astro` — updates tool count and featured tools list

Run after each content pipeline batch to keep the site in sync with registry.db.

### Script structure outline

```python
#!/usr/bin/env python3
"""
DevNook Dev Team — update.py
Updates Astro pages based on current registry.db state.
Run after content pipeline: python agents/dev-team/update.py
"""

import sqlite3
from pathlib import Path
from agents.utils.openrouter_client import call_claude

DB_PATH = Path("agents/content-team/registry.db")
SKILLS_DIR = Path("agents/skills")

def get_stats(db: sqlite3.Connection) -> dict:
    """Pull current content stats from registry."""
    return {
        "total_published": db.execute("SELECT COUNT(*) FROM posts WHERE status='published'").fetchone()[0],
        "total_staged": db.execute("SELECT COUNT(*) FROM posts WHERE status='staged'").fetchone()[0],
        "languages": db.execute("SELECT language, COUNT(*) as count FROM posts WHERE language IS NOT NULL AND status='published' GROUP BY language").fetchall(),
        "tools_count": db.execute("SELECT COUNT(*) FROM posts WHERE category='tools' AND status='published'").fetchone()[0],
    }

def update_homepage(stats: dict):
    """Regenerate homepage with current stats."""
    ...

def ensure_language_hubs(db: sqlite3.Connection):
    """Create hub pages for any language that has published posts but no hub page."""
    ...

def update():
    with sqlite3.connect(DB_PATH) as db:
        stats = get_stats(db)
        update_homepage(stats)
        ensure_language_hubs(db)
        print(f"Updated site: {stats['total_published']} posts, {stats['tools_count']} tools")

if __name__ == "__main__":
    update()
```

---

## Key Design Decisions for This Stage

1. **Generate files one at a time** — don't prompt Claude for the entire codebase in one call. Each file gets its own prompt with specific context.
2. **Include actual content in generated pages** — the homepage should have real token values, real component names, real section structure (not placeholder comments).
3. **Content collections schema must match frontmatter schemas exactly** — reference `agents/skills/content-schema.md` when generating `src/content/config.ts`.
4. **OG image templates** — 5 designs (language, guide, tool, blog, cheatsheet). Generate these as Satori component functions. Each takes `title`, `description`, `category` as props.
5. **SearchBar uses Fuse.js** — `src/pages/api/search-index.json.ts` generates a static JSON search index at build time. The SearchBar component loads this and uses Fuse.js client-side.

---

## Environment Setup

Before running scaffold.py:
```bash
# Required env vars
export OPENROUTER_API_KEY=your_key_here

# Python deps (create requirements.txt in agents/)
pip install requests sqlite3
```

Create `agents/requirements.txt`:
```
requests>=2.31.0
scikit-learn>=1.3.0
python-frontmatter>=1.1.0
google-auth>=2.23.0
google-auth-httplib2>=0.1.1
```

---

## Verification

After running scaffold.py:
- [ ] `ls src/` shows: components, content, layouts, pages, styles
- [ ] `npm install` completes without errors
- [ ] `npm run dev` starts without errors
- [ ] `http://localhost:4321/` shows homepage
- [ ] `http://localhost:4321/tools/` shows tools index (empty but renders)
- [ ] `http://localhost:4321/languages/` shows languages index
- [ ] `npm run build` completes successfully
- [ ] Lighthouse score on homepage: Performance ≥ 90, SEO ≥ 95
