# DevNook — SEO Writing Rules

## Word Count Requirements (Minimum — QA will reject below these)
| Content Type | Minimum | Target |
|-------------|---------|--------|
| Language post | 1,000 words | 1,200 words |
| Guide | 1,500 words | 1,800–2,500 words |
| Blog post | 1,200 words | 1,500–2,000 words |
| Cheat sheet | 1000 words | 1200–1500 words (+ tables) |
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
