# Stage 1 — Skills & Institutional Knowledge

**Goal:** Write the 6 agent skill files, set up logging templates, and define the SQLite registry schema. These files are the "brain" injected into every LLM system prompt — completing this stage makes all future agents smarter and more consistent.

**Depends on:** Nothing (this is the foundation)  
**Unlocks:** All other stages (every agent references these files)  
**Estimated session time:** 1 focused session (~2–3 hours)

---

## Deliverables Checklist

- [ ] `agents/skills/astro-conventions.md`
- [ ] `agents/skills/tool-build-patterns.md`
- [ ] `agents/skills/content-schema.md`
- [ ] `agents/skills/seo-writing-rules.md`
- [ ] `agents/skills/devnook-brand-voice.md`
- [ ] `agents/skills/qa-rejection-criteria.md`
- [ ] `agents/content-team/DECISIONS.md` (template)
- [ ] `agents/content-team/PIPELINE_LOG.md` (template)
- [ ] `agents/content-team/registry-schema.sql` (SQLite DDL)

---

## File 1: `agents/skills/astro-conventions.md`

Write this file with the following content (verbatim — this is injected into agent prompts):

```markdown
# DevNook — Astro Conventions

## Project Identity
- Framework: Astro (latest stable)
- Hosting: Cloudflare Pages
- Domain: devnook.dev
- Node version: 20+

## Styling Rules
- NO Tailwind. All styles use tokens.css custom properties.
- Global design tokens live at: `src/styles/tokens.css`
- Component-scoped styles use Astro's `<style>` blocks only.
- Fonts: Outfit (body/UI) + JetBrains Mono (code blocks), loaded via @font-face in tokens.css.
- Breakpoint: 768px (single breakpoint, mobile-first).

## Token Reference (key values)
- --color-bg: #0d0d0d
- --color-surface: #161616
- --color-border: #2a2a2a
- --color-text: #e8e8e8
- --color-text-muted: #8a8a8a
- --color-accent: #6ee7b7 (mint green)
- --color-accent-2: #7c3aed (purple)
- --font-body: 'Outfit', sans-serif
- --font-mono: 'JetBrains Mono', monospace
- --radius-sm: 4px
- --radius-md: 8px
- --radius-lg: 16px
- --space-1 through --space-8: 4px increments (4, 8, 12, 16, 24, 32, 48, 64)

## URL Structure
- `/` → Homepage
- `/languages/{lang}` → Language hub (e.g., /languages/python)
- `/languages/{lang}/{concept}` → Individual concept post
- `/guides/{slug}` → Educational guide
- `/cheatsheets/{subject}` → Cheat sheet
- `/tools/{slug}` → Browser-based tool
- `/blog/{slug}` → Blog/comparison post
- `/languages/` → Languages index
- `/guides/` → Guides index
- `/tools/` → Tools index

## Component Naming
- PascalCase filenames: `NavBar.astro`, `ToolCard.astro`, `PostCard.astro`
- Layouts in `src/layouts/`: `BaseLayout.astro`, `PostLayout.astro`, `ToolLayout.astro`
- Shared components in `src/components/`
- Page files in `src/pages/` follow URL structure

## Content Collections
- Language posts: `src/content/languages/{lang}/{concept}.md`
- Guides: `src/content/guides/{slug}.md`
- Cheat sheets: `src/content/cheatsheets/{subject}.md`
- Blog posts: `src/content/blog/{slug}.md`
- Tools: `src/content/tools/{slug}.md` (SEO explainer page)
- Tool components: `src/components/tools/{slug}.astro`

## Key Components to Know
- `NavBar.astro` — sticky top nav, 6 items: Tools, Languages, Guides, Cheatsheets, Blog, Search
- `Footer.astro` — simple 2-column footer with links + copyright
- `PostCard.astro` — card for content list pages (title, description, tags, date)
- `ToolCard.astro` — card for tools index (name, description, tier badge, icon)
- `LanguageCard.astro` — card for language hubs (logo, post count, featured topics)
- `CodeBlock.astro` — syntax-highlighted code block (JetBrains Mono, dark theme)
- `TagBadge.astro` — small pill/badge for category/tag display
- `SearchBar.astro` — client-side fuzzy search (Fuse.js)
- `OGImage.astro` — Satori-based OG image generator (used at build time)

## Important Rules
1. Never use Tailwind or utility classes.
2. Every page must include BaseLayout which handles <head>, NavBar, Footer.
3. Content is Markdown with YAML frontmatter — never JSX in content files.
4. Tool pages have TWO files: the Astro component (interactive) + the content .md (SEO text).
5. Use Astro's content collections API with `getCollection()` — not custom file reads.
6. All internal links must be relative (no hardcoded domain).
7. Images: only OG images auto-generated; no body images for programmatic posts.
```

---

## File 2: `agents/skills/tool-build-patterns.md`

```markdown
# DevNook — Tool Build Patterns

## Tool Architecture

### Tier 1 — Pure Client-Side (JavaScript only)
- No server needed. Runs entirely in the browser.
- Implemented as: Astro component with `<script>` tag + vanilla JS or small library.
- Deployment: static file on Cloudflare Pages.
- Examples: JSON formatter, Base64 encoder, regex tester, color picker, hash generator.

### Tier 2 — AI-Powered (Cloudflare Worker)
- Requires server-side LLM call (Gemini API).
- Implemented as: Astro component (UI) + Cloudflare Worker (API proxy).
- Worker handles: API key security, rate limiting, response streaming.
- Examples: Code explainer, SQL query builder, regex generator, diff summarizer.

## Tool Spec JSON Schema

Every tool starts with a spec file at `agents/tools-team/tool-specs/{slug}.json`:

```json
{
  "slug": "json-formatter",
  "name": "JSON Formatter & Validator",
  "description": "Format, validate, and minify JSON instantly in your browser.",
  "tier": 1,
  "category": "data",
  "tags": ["json", "formatter", "validator", "minify"],
  "seo_keywords": ["json formatter online", "json validator", "format json"],
  "related_tools": ["base64-encoder", "url-encoder"],
  "related_content": ["what-is-json", "json-vs-xml"],
  "icon": "braces",
  "input_type": "textarea",
  "output_type": "textarea",
  "features": ["Format (2-space indent)", "Minify", "Validate with error line", "Copy to clipboard"],
  "worker_endpoint": null
}
```

For Tier 2 tools, `worker_endpoint` is set to the Cloudflare Worker URL.

## File Generation per Tool

Running `build-tool.py --spec {slug}.json` generates 3 files:

1. `src/components/tools/{slug}.astro` — interactive UI component
2. `src/pages/tools/{slug}.astro` — page that wraps the component + SEO content
3. `src/content/tools/{slug}.md` — SEO explainer article (500–800 words)

For Tier 2, also generates:
4. `workers/{slug}/index.js` — Cloudflare Worker
5. `workers/{slug}/wrangler.toml` — Cloudflare Worker config

## Astro Tool Component Structure

```astro
---
// No server-side props needed for Tier 1
---
<div class="tool-container" id="tool-{slug}">
  <div class="tool-header">
    <h2>{Tool Name}</h2>
    <p class="tool-desc">{one-line description}</p>
  </div>
  <div class="tool-body">
    <!-- Input area -->
    <!-- Controls/buttons -->
    <!-- Output area -->
  </div>
  <div class="tool-status" aria-live="polite"></div>
</div>
<script>
  // All tool logic here — vanilla JS only
  // No framework dependencies
</script>
<style>
  /* Component-scoped styles using tokens */
  .tool-container { ... }
</style>
```

## SEO Explainer Structure (content .md)

```yaml
---
title: "{Tool Name} — Free Online Tool"
description: "{2-sentence description targeting primary keyword}"
category: tools
tags: [tag1, tag2, tag3]
tool_slug: "{slug}"
seo_keywords: [keyword1, keyword2, keyword3]
related_tools: [slug1, slug2]
related_content: [slug1, slug2]
published_date: "YYYY-MM-DD"
og_image: "/og/tools/{slug}.png"
---
```

Body: 500–800 words. Structure:
1. What is this tool? (1 paragraph)
2. How to use it (numbered steps)
3. When would you use this? (3–5 bullet use cases)
4. FAQ (3–4 questions in H3 format)

## Cloudflare Worker Pattern (Tier 2)

```javascript
export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    const { prompt } = await request.json();
    // Call Gemini API using env.GEMINI_API_KEY
    // Stream response back
    return new Response(stream, { headers: { ...corsHeaders, 'Content-Type': 'text/event-stream' } });
  }
}
```

## Wrangler Config Template

```toml
name = "{slug}-worker"
main = "index.js"
compatibility_date = "2024-01-01"

[vars]
TOOL_SLUG = "{slug}"

# Set via: wrangler secret put GEMINI_API_KEY
```

## Important Rules
1. Tier 1 tools: zero external HTTP requests. Self-contained.
2. Tier 2 tools: never expose API key in frontend. Always proxy through Worker.
3. All tools must work without JavaScript disabled for the static SEO page.
4. Copy-to-clipboard must use navigator.clipboard API with fallback.
5. Error messages must be human-readable (not raw exception strings).
6. Tool UI must be functional on mobile (768px breakpoint).
```

---

## File 3: `agents/skills/content-schema.md`

```markdown
# DevNook — Content Schema

## Content Types & Template IDs

### Language Posts (`/languages/{lang}/{concept}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| lang-v1 | Definition First | Terminology, what-is questions |
| lang-v2 | Problem First | How-to, debugging topics |
| lang-v3 | Code First | Syntax, operators, built-ins |
| lang-v4 | Concept Across Languages | Cross-language comparisons |
| lang-v5 | Tutorial/Build-Along | Step-by-step project posts |

### Guides (`/guides/{slug}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| guide-v1 | Encyclopedia | Deep reference topics |
| guide-v2 | Quick Answer + Deep Dive | FAQ-style topics |
| guide-v3 | Problem → Solution | Debugging, troubleshooting |
| guide-v4 | Reference Card | Cheat-sheet style guides |

### Blog Posts (`/blog/{slug}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| blog-v1 | Head-to-Head Comparison | X vs Y posts |
| blog-v2 | Use-Case Driven Comparison | "When to use X vs Y" |
| blog-v3 | Listicle | Top N lists |
| blog-v4 | Deep-Dive Editorial | Opinion/analysis pieces |
| blog-v5 | How-To Tutorial | Practical walkthroughs |

### Cheat Sheets (`/cheatsheets/{subject}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| cheatsheet-v1 | Syntax Reference | Language syntax, operators |
| cheatsheet-v2 | Task-Oriented | "How do I..." reference |
| cheatsheet-v3 | Tiered Beginner→Advanced | Skill-level progression |
| cheatsheet-v4 | Two-Column Comparison | Side-by-side reference |

### Tool Explainers (`/tools/{slug}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| tool-exp-v1 | What + Why + How | General tool pages |
| tool-exp-v2 | Problem First | Pain-point-led pages |
| tool-exp-v3 | Feature Focused | Feature-rich tools |
| tool-exp-v4 | FAQ Style | Common-question-heavy tools |

Template files are at: `templates/templates/{type}/{template-id}.md`

## Frontmatter Schemas

### Language Post
```yaml
---
title: "How to {concept} in {Language}"
description: "{1–2 sentence description targeting primary keyword, under 160 chars}"
category: languages
language: python  # lowercase slug
concept: list-comprehensions  # kebab-case
template_id: lang-v1
tags: [python, list-comprehension, functional-programming]
related_posts:
  - /languages/python/generators
  - /languages/python/lambda-functions
related_tools:
  - /tools/python-repl
published_date: "YYYY-MM-DD"
og_image: "/og/languages/{lang}/{concept}.png"
word_count_target: 1200  # minimum
---
```

### Guide
```yaml
---
title: "{Topic}: A Complete Guide"
description: "{description under 160 chars}"
category: guides
template_id: guide-v1
tags: [tag1, tag2, tag3]
related_posts:
  - /languages/python/...
related_tools:
  - /tools/...
published_date: "YYYY-MM-DD"
og_image: "/og/guides/{slug}.png"
word_count_target: 1800
---
```

### Blog Post
```yaml
---
title: "{title}"
description: "{description}"
category: blog
template_id: blog-v1
tags: [tag1, tag2]
related_posts: []
related_tools: []
published_date: "YYYY-MM-DD"
og_image: "/og/blog/{slug}.png"
word_count_target: 1500
---
```

### Cheat Sheet
```yaml
---
title: "{Language/Topic} Cheat Sheet"
description: "{description}"
category: cheatsheets
language: python  # if applicable
template_id: cheatsheet-v1
tags: [tag1, tag2]
related_posts: []
related_tools: []
published_date: "YYYY-MM-DD"
og_image: "/og/cheatsheets/{subject}.png"
downloadable: true
---
```

### Tool Explainer
```yaml
---
title: "{Tool Name} — Free Online Tool"
description: "{description}"
category: tools
tool_slug: json-formatter
template_id: tool-exp-v1
tags: [tag1, tag2]
related_tools: []
related_content: []
published_date: "YYYY-MM-DD"
og_image: "/og/tools/{slug}.png"
word_count_target: 600
---
```

## Post Status Flow

```
discovered → queued → drafted → optimized → approved → staged → published
```

- `discovered`: keyword found, not yet planned
- `queued`: assigned template and language, ready for writing
- `drafted`: writer agent output exists, not yet SEO-optimized
- `optimized`: SEO optimizer has processed it
- `approved`: QA agent passed it
- `staged`: file moved to /content-staging/
- `published`: drip publisher moved it to /src/content/ and deployed

## Target Languages (Ring 3)
python, javascript, typescript, go, rust, java, csharp, php, ruby, swift, kotlin, cpp

## Content Volume Targets
- Ring 1 (tool-adjacent): ~80 posts
- Ring 2 (web dev fundamentals): ~200 posts
- Ring 3 (language concepts): ~600+ posts (50 concepts × 12 languages)
- Bonus (AI/comparison/editorial): ~200 posts
- **Total target: 1,000+ posts**
```

---

## File 4: `agents/skills/seo-writing-rules.md`

```markdown
# DevNook — SEO Writing Rules

## Word Count Requirements (Minimum — QA will reject below these)
| Content Type | Minimum | Target |
|-------------|---------|--------|
| Language post | 1,000 words | 1,200 words |
| Guide | 1,500 words | 1,800–2,500 words |
| Blog post | 1,200 words | 1,500–2,000 words |
| Cheat sheet | 600 words | 800 words (+ tables) |
| Tool explainer | 500 words | 600–800 words |

Tables, code blocks, and lists count toward word count.

## Heading Structure
- H1: Title (only one, matches `title` frontmatter exactly or closely)
- H2: Major sections (3–6 per post)
- H3: Subsections under H2 (use for FAQ answers, sub-topics)
- H4: Only if truly needed. Never use H5/H6.
- H2s must contain the primary keyword or a close variant in at least ONE H2.

## Keyword Density
- Primary keyword: appears 4–8 times (naturally, not forced)
- Appears in: title, first 100 words, at least one H2, last paragraph
- LSI/related terms: use 3–5 related terms throughout
- Never stuff — if it sounds unnatural, remove it

## Internal Links
- Minimum: 3 internal links per post
- Maximum: 8 internal links per post
- Must link to: at least 1 tool page + at least 1 related language/guide post
- Link text must be descriptive (no "click here")
- No self-linking

## Code Blocks
- Language posts and guides MUST have at least 2 code examples
- Code must be runnable/complete (not pseudocode snippets)
- Use fenced code blocks with language tag: ```python
- For multi-step tutorials: one code block per major step

## Schema.org (added by SEO optimizer)
- Language posts: use `TechArticle` schema
- Guides: use `Article` schema with `educationalLevel`
- Tool pages: use `SoftwareApplication` schema
- Blog posts: use `BlogPosting` schema
- Cheat sheets: use `Article` schema

## Meta Description
- 140–160 characters (QA rejects outside this range)
- Include primary keyword naturally
- Call-to-action phrasing preferred ("Learn how to...", "Discover...", "Free online...")

## Title SEO Patterns
- Language posts: "How to {concept} in {Language} [+ Examples]"
- Comparisons: "{A} vs {B}: Key Differences Explained"
- Guides: "{Topic}: The Complete Guide ({Year})"
- Cheat sheets: "{Language} {Topic} Cheat Sheet"
- Tool pages: "{Tool Name} — Free Online {Tool Type}"

## URL/Slug Rules
- All lowercase, kebab-case
- No stop words (no: the, a, an, of, for, in... unless part of keyword)
- Max 60 characters
- Examples: `python-list-comprehensions`, `json-vs-xml`, `javascript-promises-guide`

## Duplicate Content Prevention
- Primary check: compare against registry.db `slug` column — reject if slug exists
- Secondary check: TF-IDF similarity against all staged/published posts — reject if >70% similar
- Title uniqueness: no two posts with same first 8 words in title
```

---

## File 5: `agents/skills/devnook-brand-voice.md`

```markdown
# DevNook — Brand Voice & Writing Style

## Brand Identity
DevNook is a **developer resource site**, not a blog. The tone is professional, direct, and genuinely helpful. We respect the reader's time and intelligence.

## Target Audience
- **Primary**: Mid-level developers (2–5 years experience) who want quick, reliable reference
- **Secondary**: Beginners who are searching for clear explanations
- **Never talk down** to the reader. Assume they know the basics of their language.
- **Never over-explain** basics that any developer knows (what a variable is, etc.)

## Tone
- Direct and confident, not hedging ("This will", not "This might")
- Conversational but not casual (no slang, no "Let's dive in!", no "Buckle up!")
- No filler phrases: banned list below
- Technically precise — correct over simple when the distinction matters

## Banned Phrases (QA will flag these)
- "Let's dive in"
- "Buckle up"
- "In this article, we will..."
- "Without further ado"
- "It's worth noting that"
- "In conclusion" / "To summarize" / "In summary"
- "At the end of the day"
- "Game-changer"
- "Leverage" (as a verb)
- Excessive exclamation marks (max 1 per post, ideally 0)

## Opening Paragraphs
- First sentence: state the answer or frame the problem — do NOT start with a question
- Wrong: "Have you ever wondered how Python handles list comprehensions?"
- Right: "Python list comprehensions let you build lists in a single line using a compact, readable syntax."
- Keep under 3 sentences. Get to the code/content fast.

## Code Examples
- Always real, working code (not pseudocode)
- Include output/result in a comment or separate block when helpful
- Python: use f-strings, not `.format()` or `%s` (unless the post is specifically about those)
- JavaScript: use `const`/`let`, not `var`; arrow functions preferred
- Add a brief comment explaining non-obvious lines
- For comparison posts: show equivalent code in both languages side by side

## Explanatory Style
- Explain concepts by showing them in code first, then explaining why it works
- Use bullet lists for features/characteristics; use numbered lists only for steps
- Max 3 bullet points before breaking into H3 subsections
- Tables: use for comparisons, parameter references, type listings

## Closing Paragraphs
- DO: Point to related content ("For more on X, see our guide to Y")
- DO: Summarize the key takeaway in one sentence
- DON'T: Add "I hope this helped!" or "Happy coding!" type sign-offs

## Post Formatting Checklist
- [ ] No banned phrases
- [ ] First paragraph under 3 sentences with direct opening
- [ ] Code blocks have language tags
- [ ] At least 3 internal links with descriptive anchor text
- [ ] Heading hierarchy is H1 → H2 → H3 (no skipping)
- [ ] Meta description is 140–160 chars
```

---

## File 6: `agents/skills/qa-rejection-criteria.md`

```markdown
# DevNook — QA Rejection Criteria

## Automatic Rejection Conditions (fail any = reject)

### Structural Issues
- [ ] Missing required frontmatter field (any field in schema = fail)
- [ ] `title` missing or empty
- [ ] `description` missing, empty, or >160 characters
- [ ] `description` <100 characters (too short for Google)
- [ ] `published_date` missing or invalid format (must be YYYY-MM-DD)
- [ ] `template_id` not in the valid 22-ID list
- [ ] `category` not one of: languages, guides, blog, cheatsheets, tools

### Content Quality
- [ ] Word count below minimum for content type (see seo-writing-rules.md)
- [ ] Zero code blocks in a language post or guide
- [ ] Fewer than 3 internal links
- [ ] More than 8 internal links
- [ ] Any internal link pointing to a non-existent slug in registry.db
- [ ] Contains any banned phrase from devnook-brand-voice.md
- [ ] Title is identical to an existing post in registry.db
- [ ] First 8 words of title match an existing post

### Duplicate Detection
- [ ] Slug already exists in registry.db (exact match = immediate reject)
- [ ] TF-IDF similarity >70% against any approved/staged/published post
- [ ] >40% sentence-level overlap with any existing post

### Technical Issues
- [ ] Frontmatter YAML is invalid/unparseable
- [ ] Any Markdown heading skips a level (H1→H3 without H2 = fail)
- [ ] Code block missing language tag (``` without python/js/etc.)
- [ ] Internal link format incorrect (must start with /)

## Warning Conditions (flag but do not reject)
- Word count between minimum and +10% of minimum (low but acceptable)
- Fewer than 5 internal links (recommend adding more)
- No H3 subsections (acceptable for short posts)
- Title over 65 characters (may truncate in SERPs)
- Meta description between 130–140 chars (tight but ok)

## Similarity Check Implementation
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_similarity(new_content: str, existing_contents: list[str]) -> float:
    """Returns max similarity score (0–1). Reject if > 0.70"""
    if not existing_contents:
        return 0.0
    corpus = existing_contents + [new_content]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    return float(scores.max())
```

## QA Output Format
The QA agent writes a structured result to registry.db for each post:

```json
{
  "slug": "python-list-comprehensions",
  "qa_status": "approved",  // or "rejected" or "warning"
  "qa_timestamp": "2024-01-15T10:30:00Z",
  "word_count": 1247,
  "similarity_score": 0.23,
  "internal_links": 4,
  "rejections": [],
  "warnings": ["title_length: 68 chars"]
}
```

## Registry.db QA Status Update
When a post passes QA: update `status` column to `approved`.
When a post fails QA: update `status` to `rejected`, log reason in `qa_notes` column.
Rejected posts are NOT deleted — they stay in registry.db for pattern analysis.
```

---

## SQLite Registry Schema (`agents/content-team/registry-schema.sql`)

```sql
-- DevNook Content Registry
-- Run: sqlite3 agents/content-team/registry.db < registry-schema.sql

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,           -- languages, guides, blog, cheatsheets, tools
    language TEXT,                    -- python, javascript, etc. (null if not lang post)
    concept TEXT,                     -- kebab-case concept name (null if not lang post)
    template_id TEXT NOT NULL,        -- lang-v1, guide-v2, etc.
    status TEXT NOT NULL DEFAULT 'discovered',
    -- Status flow: discovered → queued → drafted → optimized → approved → staged → published
    keyword TEXT,                     -- primary SEO keyword
    opportunity_score REAL,          -- planner agent score (0–100)
    word_count INTEGER,
    similarity_score REAL,           -- TF-IDF similarity to nearest existing post
    internal_links INTEGER,
    published_date TEXT,             -- YYYY-MM-DD
    staged_at TEXT,                  -- ISO timestamp
    published_at TEXT,               -- ISO timestamp
    file_path TEXT,                  -- relative path to .md file
    qa_status TEXT,                  -- approved, rejected, warning
    qa_notes TEXT,                   -- JSON string of QA results
    rejection_reason TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS template_counters (
    template_id TEXT PRIMARY KEY,
    usage_count INTEGER DEFAULT 0,
    last_used TEXT
);

CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,
    search_volume_estimate INTEGER,
    competition TEXT,                 -- low, medium, high
    assigned_slug TEXT,              -- FK to posts.slug (nullable)
    status TEXT DEFAULT 'discovered', -- discovered, assigned, published
    discovered_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT NOT NULL,
    step TEXT NOT NULL,              -- keyword, planner, writer, seo, qa, staging
    posts_processed INTEGER DEFAULT 0,
    posts_passed INTEGER DEFAULT 0,
    posts_rejected INTEGER DEFAULT 0,
    duration_seconds REAL,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Initialize template counters
INSERT OR IGNORE INTO template_counters (template_id, usage_count) VALUES
    ('lang-v1', 0), ('lang-v2', 0), ('lang-v3', 0), ('lang-v4', 0), ('lang-v5', 0),
    ('guide-v1', 0), ('guide-v2', 0), ('guide-v3', 0), ('guide-v4', 0),
    ('blog-v1', 0), ('blog-v2', 0), ('blog-v3', 0), ('blog-v4', 0), ('blog-v5', 0),
    ('cheatsheet-v1', 0), ('cheatsheet-v2', 0), ('cheatsheet-v3', 0), ('cheatsheet-v4', 0),
    ('tool-exp-v1', 0), ('tool-exp-v2', 0), ('tool-exp-v3', 0), ('tool-exp-v4', 0);

CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_language ON posts(language);
CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);
```

---

## DECISIONS.md Template (`agents/content-team/DECISIONS.md`)

```markdown
# DevNook Architecture Decisions Log

This file records significant decisions made by agents or manually during development.
Format: Date | Decision | Reason

---

## Template System
- 2024-XX-XX | Using 22 template IDs across 5 content types | Prevents duplicate structure patterns; round-robin via registry.db prevents repetition
- 2024-XX-XX | Template files stored in /templates/templates/ | Agents load them dynamically; no hardcoded structures

## Agent Architecture
- 2024-XX-XX | Plain Python scripts, no framework | No containers, no cloud scheduler; local execution is simpler and cheaper
- 2024-XX-XX | Gemini free tier as primary LLM | Cost optimization; Flash/Flash-Lite for bulk, 2.5 Pro for editorial
- 2024-XX-XX | OpenRouter (Sonnet) for dev/tools agents | Better code quality; used infrequently so cost is low

## Content Strategy
- 2024-XX-XX | No Tailwind | All styles use tokens.css custom properties; cleaner diffs, no purge complexity
- 2024-XX-XX | Safe ramp-up schedule | Google Scaled Content Abuse policy mitigation; starting at 1-2 posts/day

## Publishing
- 2024-XX-XX | GitHub Actions drip at 08:00 UTC | Consistent timing signals for Google crawlers
- 2024-XX-XX | GSC Indexing API after each publish | Speeds up crawl time for new posts

---
_Add new decisions above the line. Oldest decisions at bottom._
```

---

## PIPELINE_LOG.md Template (`agents/content-team/PIPELINE_LOG.md`)

```markdown
# DevNook Pipeline Run Log

---

## Run Template

```
## Run: YYYY-MM-DD

**Step 1 — Keyword Agent**
- Seeds used: [list of seed topics]
- Keywords discovered: X
- After deduplication: Y new keywords queued
- Duration: Xs

**Step 2 — Planner Agent**
- Items ranked: Y
- Items queued for writing: Z
- Template distribution: lang-v1: N, lang-v2: N, ...
- Duration: Xs

**Step 3 — Writer Agent**
- Items attempted: Z
- Drafts created: N
- Failures/retries: N
- Models used: Gemini Flash (N), Gemini Pro (N)
- Duration: Xs

**Step 4 — SEO Optimizer**
- Posts processed: N
- Internal links added: avg N per post
- Schema.org injected: N posts
- Duration: Xs

**Step 5 — QA Agent**
- Posts reviewed: N
- Approved: N
- Rejected: N (reasons: word count N, duplicate N, other N)
- Warnings: N
- Duration: Xs

**Step 6 — Staging**
- Files moved to /content-staging/: N
- Total in staging now: N
- Duration: Xs

**Total pipeline duration:** Xs
**Net new staged posts:** N
```

---

_Most recent runs at top._
```

---

## Execution Instructions for This Stage

1. Create directory `agents/skills/` if it doesn't exist
2. Write each of the 6 skill files exactly as specified above
3. Create `agents/content-team/DECISIONS.md` from the template above
4. Create `agents/content-team/PIPELINE_LOG.md` from the template above
5. Create `agents/content-team/registry-schema.sql` with the SQL DDL above
6. Initialize the database: `sqlite3 agents/content-team/registry.db < agents/content-team/registry-schema.sql`
7. Verify with: `sqlite3 agents/content-team/registry.db ".tables"` — should show: posts, template_counters, keywords, pipeline_runs

## Verification
- [ ] All 6 skill files exist in `agents/skills/`
- [ ] registry.db initializes without errors
- [ ] DECISIONS.md and PIPELINE_LOG.md exist in `agents/content-team/`
- [ ] Running `sqlite3 registry.db "SELECT template_id FROM template_counters;"` returns all 22 template IDs
