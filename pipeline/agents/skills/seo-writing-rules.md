# DevNook — SEO Writing Rules

## Content Principles (apply to every article)

Every article must be:
- **Semantic** — explain the topic comprehensively; naturally include related concepts and entities
- **Skimmable** — scannable headings, short paragraphs, bullets where appropriate
- **Easy to read** — plain language, short sentences, no jargon without explanation
- **Active voice** — "Python raises an error" not "an error is raised by Python"
- **Valuable** — fully satisfy user intent; answer what the reader came to learn
- **Naturally written** — keyword usage must feel native, never forced
- **Grammatically correct** — no errors; write for a professional developer audience
- **Better than competitor content** — go deeper, use better examples, cover edge cases

---

## Word Count Requirements (Minimum — QA will reject below these)

| Content Type | Minimum | Target |
|-------------|---------|--------|
| Editorial post (blog, guides) | 2,500 words | 3,000–4,000 words |
| Language post | 1,500 words | 2,000–2,500 words |
| Cheat sheet | 1,500 words | 1,800–2,500 words (+ tables) |
| Tool explainer | 1,500 words | 1,800–2,500 words |

Tables, code blocks, and lists count toward word count.

---

## Keyword Targeting Rules

### Counts (mandatory for every article)
- **Primary keywords:** 2–3 per article
- **Secondary keywords:** 6–12 per article

### Selection Criteria

**All categories except language posts and rewritten articles:**
- KD < 20 preferred; KD < 30 acceptable
- Minimum search volume: 500/month

**Language posts and rewritten articles:**
- Prioritize the highest search volume available within the keyword pool
- Choose the lowest possible KD among high-volume candidates
- No hard volume floor (take what's available in niche language segments)

### Keyword Coverage in Content
- Primary keyword: appears 4–8 times (naturally, never forced)
- Appears in: title (except rewrites — see below), first 100 words, at least one H2, last paragraph
- Secondary keywords: weave in naturally throughout — aim for each appearing 1–3 times
- LSI/related terms: use 3–5 additional related terms throughout

---

## Rewrite Exception

For article **rewrites only**, the requirement to include the primary keyword in the title may be relaxed. All other SEO and content rules apply in full.

---

## Heading Structure
- H1: **Do not write an H1 in the markdown body.** The Astro layout renders `frontmatter.title` as the page `<h1>`. A `# heading` line in the body creates a duplicate H1 (SEO penalty).
- H2: Major sections (3–6 per post)
- H3: Subsections under H2 (use for FAQ answers, sub-topics)
- H4: Only if truly needed. Never use H5/H6.
- H2s must contain the primary keyword or a close variant in at least ONE H2.

---

## SEO Must-Haves (every article, no exceptions)

- [ ] Primary keyword in the title (except rewrites)
- [ ] Primary keyword in at least one H2 heading
- [ ] Optimized image alt text — descriptive, includes keyword where natural; no "image1.png" or empty alt
- [ ] Internal links (see Internal Links section)
- [ ] External links (see External Links section)
- [ ] Schema markup (see Schema.org section)

---

## Internal Links
- Minimum: 3 internal links per post
- Maximum: 8 internal links per post
- Must link to: at least 1 tool page + at least 1 related language/guide post
- Link text must be descriptive (no "click here")
- No self-linking

## External Links
- Minimum: 1 external link per post (QA rejects zero external links)
- Maximum: 2 external links per post
- Must point to relevant, authoritative resources: MDN, official language docs, W3C, Wikipedia, reputable vendor documentation, academic papers, or high-authority editorial sources (smashing, css-tricks, freecodecamp)
- Links must be directly relevant to the topic being discussed
- No affiliate links; no commercial product pages unless the article is about that product

---

## Code Blocks
- Language posts and guides MUST have at least 2 code examples
- Code must be runnable/complete (not pseudocode snippets)
- Use fenced code blocks with language tag: ```python
- For multi-step tutorials: one code block per major step

---

## Schema.org (required — added during QA/publish stage)
- Language posts: use `TechArticle` schema
- Guides: use `Article` schema with `educationalLevel`
- Tool pages: use `SoftwareApplication` schema
- Blog posts: use `BlogPosting` schema
- Cheat sheets: use `Article` schema

---

## Meta Description
- 140–160 characters (QA rejects outside this range)
- Include primary keyword naturally
- Call-to-action phrasing preferred ("Learn how to...", "Discover...", "Free online...")

---

## Title SEO Patterns
- Language posts: "How to {concept} in {Language} [+ Examples]"
- Comparisons: "{A} vs {B}: Key Differences Explained"
- Guides: "{Topic}: The Complete Guide ({Year})"
- Cheat sheets: "{Language} {Topic} Cheat Sheet"
- Tool pages: "{Tool Name} — Free Online {Tool Type}"

---

## URL/Slug Rules
- All lowercase, kebab-case
- No stop words (no: the, a, an, of, for, in... unless part of keyword)
- Max 60 characters
- Examples: `python-list-comprehensions`, `json-vs-xml`, `javascript-promises-guide`

---

## Duplicate Content Prevention
- Primary check: compare against registry.db `slug` column — reject if slug exists
- Secondary check: TF-IDF similarity against all staged/published posts — reject if >70% similar
- Title uniqueness: no two posts with same first 8 words in title
