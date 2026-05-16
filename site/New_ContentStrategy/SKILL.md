---
name: language-post-generator
description: Use this skill whenever you need to write, draft, regenerate, or rewrite a programming language tutorial for DevNook — any article that will live under /languages/{language}/{concept}/ (e.g. /languages/python/closures/, /languages/javascript/destructuring/). Covers the full modular section system, voice rotation, diversity tracking against registry.db, and writer-time SEO. Trigger this skill for ALL language posts including Python, JavaScript, TypeScript, Go, Rust, Java, C#, PHP, Ruby, Swift, Kotlin, and C++ — even if the user just says "write a post about X in Python" or "regenerate this article" without explicitly mentioning the skill. Also trigger when a Planner agent brief specifies content_type=language-post.
---

# DevNook Language Post Generator

This skill produces long-form (1,500–3,500 word) tutorial articles for the /languages/ section of devnook.dev, using a modular section library + voice rotation + diversity tracking. The goal is to produce structurally distinctive articles that don't share Google's "scaled AI content" fingerprint.

## What this skill is solving

The previous template system used 5 rigid templates that all ended with the same three sections ("Under the Hood: Performance & Mechanics", "Advanced Edge Cases", "Testing X in Y"). Google detected the pattern as scaled AI content and refused to index ~25% of pages. This skill replaces that system with:

1. **A modular section library** (30 sections across 6 buckets) instead of fixed templates
2. **A selection algorithm** that picks 5–9 sections per article based on topic intent
3. **A diversity check** ensuring no two consecutive articles on the same language share more than 50% of sections
4. **A voice rotation** across 5 distinct authorial voices
5. **No mandatory "fingerprint" sections** — the three problem sections from before are now opt-in and rare

## The procedure

For every article generation, follow these steps in order.

### Step 1 — Receive the brief

You'll receive a brief from the Planner agent containing:
- `language` (e.g., "python")
- `concept` (e.g., "closures")
- `target_keyword`
- `secondary_keywords` (list)
- `intent` — one of: `how-to`, `explainer`, `concept`, `debug`, `reference`
- `difficulty` — `beginner` | `intermediate` | `advanced`
- Topic flags: `is_abstract`, `is_syntax_heavy`, `is_error_driven`, `has_performance_implications`, `has_cross_language_analog`

If any required field is missing, ask the Planner agent for it. Do not invent metadata.

### Step 2 — Run the selection algorithm

Execute `python select_sections.py --brief <path-to-brief.json>` (or import and call `select_sections()` if running inside another Python process).

The algorithm:
1. Connects to `agents/content-team/registry.db`
2. Queries the last 3 published articles for the same language
3. Determines section count (5–9) and distributes across buckets:
   - Always: 1 opening + 1 closing
   - Core: 1–2 sections
   - Code: 1–3 sections
   - Practical: 0–2 sections
   - Comparison: 0–1 sections
4. Applies topic-driven gates (e.g., if `is_error_driven`, forces `open-error`)
5. Verifies diversity: rejects any selection sharing >50% of sections with the last 3 articles, retries up to 10 times
6. Picks a voice that wasn't used in the previous article on the same language
7. Returns JSON with: `sections` (ordered list of section IDs), `voice`, `word_target`

If the algorithm exits with an error, do not proceed. Report to the Planner agent.

### Step 3 — Load the selected section instructions

For each section ID in the returned `sections` list, find its instructions in the corresponding bucket file:

- Openings → `sections-openings.md`
- Core → `sections-core.md`
- Code → `sections-code.md`
- Practical → `sections-practical.md`
- Comparison → `sections-comparison.md`
- Closings → `sections-closings.md`

Each section file has a table of contents at the top. Jump to the section ID's heading and read the full instructions before writing that section.

### Step 4 — Load the voice instructions

Read the relevant voice from `voices.md`. The voice determines sentence rhythm, vocabulary, register, and forbidden phrasings. Voice is the most important consistency lever — voice drift across an article is the second-biggest AI tell after structural uniformity.

### Step 5 — Load SEO rules

Read `seo-rules.md` once at the start of generation. These are writer-time rules (title, meta description, keyword placement, heading hierarchy). Post-write SEO (internal link insertion, schema markup) is handled by the separate `seo_optimizer.py` step in the pipeline — DO NOT do that work here.

### Step 6 — Write the article

Compose the article in the order the algorithm specified. Section order is: opening → core sections → code sections → practical sections → comparison section (if any) → closing.

Critical rules during writing:

- **Hit the word target** — within ±15%. If you can't fill the target naturally, the algorithm may have selected too many sections; flag this rather than padding.
- **Use only the assigned voice** — no mixing
- **Never include section types that weren't selected** — if your assigned sections don't include `prac-testing`, do not add a testing section because the topic "seems to need it." If you feel strongly a missing section is needed, stop and report this rather than adding it. The discipline is the whole point.
- **Section names in the article should NOT match the section IDs.** The IDs (`open-quick`, `core-syntax-detail`, etc.) are internal. The actual H2 in the published article should be topical to the content — e.g., for `open-problem` writing about Ruby exception handling, the H2 might be "When Your Rescue Block Doesn't Catch What You Think" rather than "The Problem". Pick H2 wording fresh per article from the section's voice guidance.
- **No forbidden phrasings** — see `voices.md` for the avoid list. Specifically never use: "professional", "comprehensive", "fundamental", "robust", "indispensable", "drastically", "absolutely", "leverages", "utilizes" (unless quoted).

### Step 7 — Write the frontmatter

Standard frontmatter for language posts:

```yaml
---
title: "[Article title — see seo-rules.md for format guidance]"
description: "[140-160 char meta description]"
language: "[e.g. python]"
concept: "[e.g. closures]"
difficulty: "[beginner | intermediate | advanced]"
target_keyword: "[primary keyword]"
secondary_keywords: ["[k1]", "[k2]"]
sections_used: ["[section-id-1]", "[section-id-2]", ...]
voice: "[voice-id]"
word_count: [actual count, not target]
published_date: "[YYYY-MM-DD]"
og_image: "og-default"
---
```

The `sections_used` and `voice` fields are required — the downstream pipeline reads them to update the registry.

### Step 8 — Hand off to the pipeline

Save the article to `agents/content-team/drafts/{slug}.md`. The seo_optimizer agent picks it up from there, adds internal links and schema, then qa_agent validates, then staging moves it to `content-staging/`.

After successful save, the calling pipeline will record the section usage:

```sql
INSERT INTO post_sections (post_slug, section_id, position, voice)
VALUES (?, ?, ?, ?);
```

This is what feeds the diversity check on the next article. You don't run this insert yourself — the pipeline does.

## File map

| File | Lines | Read when |
|---|---|---|
| `SKILL.md` (this file) | ~250 | Always, at start |
| `select_sections.py` | ~250 | Always, to run the algorithm |
| `sections-openings.md` | ~400 | When picking/writing the opening |
| `sections-core.md` | ~350 | When writing core explanation sections |
| `sections-code.md` | ~400 | When writing code/example sections |
| `sections-practical.md` | ~450 | When writing practical sections |
| `sections-comparison.md` | ~300 | Only if comparison was selected |
| `sections-closings.md` | ~350 | When writing the closing |
| `voices.md` | ~400 | Always, after algorithm returns voice |
| `seo-rules.md` | ~250 | Always, once at start |
| `example-1-concept.md` | ~250 | Reference when uncertain about structure |
| `example-2-howto.md` | ~200 | Reference when uncertain about structure |
| `migration.sql` | ~50 | One-time database setup |

## Critical rules summary

1. Run the algorithm BEFORE writing. Do not pick sections yourself.
2. Follow the assigned voice throughout the article. No voice mixing.
3. Never add sections not in the algorithm's output.
4. Word target is firm (±15%). Padding to hit it is forbidden.
5. Article H2s are topical, never the section IDs.
6. Frontmatter MUST include `sections_used`, `voice`, and `word_count`.
7. Topic flags in the brief drive forced section inclusions. Honor them.
8. Post-write SEO (links, schema) is handled by `seo_optimizer.py`, not here.

## When to escalate instead of proceeding

Stop and report to the Planner if:
- The brief is missing required fields
- The algorithm fails or times out
- The selected sections don't make sense for the topic
- The word target seems impossible (e.g., too few sections for 3,500 words)
- You can't pick a voice that wasn't used last

Don't silently work around these — they're signals the upstream pipeline has a bug.
