# SEO Rules — Writer-Time

These rules apply during article generation. Post-write SEO (internal link insertion, schema markup, related-content generation) is handled separately by `seo_optimizer.py` — DO NOT do that work in the skill.

## Title

- **Length:** 50–60 characters (Google truncates around 60)
- **Format:** Topical and specific. NOT formulaic.
- **Include the target keyword** but not at the absolute start unless natural
- **Avoid colons** unless they add real meaning (overused in AI-generated titles)

### Good titles

- "Closures in Python, Quietly Demystified"
- "Why Your TypeScript Interface Won't Extend"
- "Parsing JSON in Ruby Without the Standard Pitfalls"
- "The Closure Loop Bug Every JavaScript Dev Hits Once"

### Bad titles (these are formulaic AI patterns)

- "What is X in Y? — A Complete Guide" (the worst offender — overused everywhere)
- "X in Y: Syntax, Examples & Usage" (template-shaped)
- "How to Use X in Y — A Step-by-Step Guide" (filler words)
- "Mastering X in Y" (cheesy, overused)
- "Understanding X: A Beginner's Guide" (boring, generic)

### Title patterns to rotate across articles

Don't use the same title pattern twice in a row on the same language hub:

- **Demystifying / Unpacking / Behind the scenes:** "Closures in Python, Unpacked"
- **The specific bug / problem:** "The Async Bug That Looks Like a Sync Bug"
- **Decision framing:** "When to Use Generators in Python (And When Not To)"
- **Counter-intuitive framing:** "Why Rust Closures Aren't What You Think"
- **Direct how:** "Parsing JSON in Ruby"

## Meta description

- **Length:** 140–160 characters
- **First 120 characters carry the weight** (Google sometimes truncates beyond)
- **Include the primary keyword** but naturally
- **State the answer or value**, not the topic

### Good

> "Parse JSON in Ruby with the built-in JSON module. Three patterns, with the gotchas that come from inconsistent API response shapes."

### Bad

> "A comprehensive guide to parsing JSON in Ruby, covering everything you need to know about working with JSON data in your Ruby applications."

## Heading hierarchy

- **Exactly one H1** — used by the post layout, derived from `title` frontmatter
- **H2s for each section** in the article body
- **H3s for subsections within a section** (used sparingly)
- **Never skip levels** (H2 → H4 is invalid)

### Section H2 wording

The H2 is the visible section header in the rendered article. The H2 is NOT the section ID.

Section IDs (`open-quick`, `core-syntax-detail`, etc.) are internal — they tell the writer what KIND of section to write. The actual H2 should be topical, written fresh for each article.

Examples of H2 wording derived from the same section ID:

- `prac-gotchas` H2 examples: "Things That Will Trip You Up", "Where This Breaks", "Two Bugs You'll Probably Write First", "The Gotchas That Bite Production Code"
- `core-design-decision` H2 examples: "Why Python Did It This Way", "The Design Trade-off Behind This", "What the Designers Were Solving For"

Rotate H2 phrasings across articles. Never reuse the exact same H2 wording twice on the same language hub.

## Target keyword usage

- **In title:** required, naturally placed
- **In first 100 words of body:** required
- **In at least one H2:** required, naturally — DON'T force it into every H2
- **Density target:** 1–2% (roughly: 1 mention per 50–100 words)
- **Never:** repeat the exact keyword phrase mechanically. Use variants and synonyms.

### Keyword variants

A target keyword of "python closures" should be rendered across the article as:

- "python closures" (exact, used in title and 1–2 places in body)
- "closures in Python" (reordered)
- "Python's closure mechanism" (possessive)
- "closures" (when context makes Python clear)
- "captured variables" / "lexical scope" (semantic variants)

Mechanical repetition of the exact keyword is the easiest spam pattern to detect. Always vary.

## Heading-level keyword usage

- Primary keyword should appear in roughly 1/3 of H2s
- NEVER force keyword into every H2 — that's a strong spam signal
- Secondary keywords (from the brief) should each appear in at least one H2 or body paragraph

## Body content rules

### Length

Hit the word target the algorithm assigned, within ±15%. If the natural article is shorter, don't pad. If you're under by more than 15%, flag — the algorithm may have selected too few sections for the topic.

Forbidden padding patterns:

- "It is important to understand that..." (just say the thing)
- Restating the question you're answering
- Listing things you "could discuss" but won't
- Long preambles before sections start

### Readability

- Paragraphs: 3–5 sentences typically. Some shorter for emphasis. Avoid walls of text.
- Sentence variety: mix lengths. Strings of similar-length sentences are an AI tell.
- Active voice preferred. Passive voice only when the subject genuinely doesn't matter.
- Vary sentence openers. Strings of sentences all starting with "This" or "The" are an AI tell.

### Code blocks

- Always specify the language for syntax highlighting
- Use realistic variable names — `user_email`, not `x`
- Comments should add information, not narrate the code
- Code should run as-is when the language allows it (Python: yes; Java: with a class wrapper acknowledged)

## Internal linking (writer's role)

The writer's role on internal linking is LIMITED:

- **Reference related concepts in prose** where natural — but DON'T add hyperlinks. The seo_optimizer step adds those.
- **Mention specific page slugs in the frontmatter** under `related_posts` if you know them, but it's fine to leave empty — seo_optimizer fills this in.
- **DO NOT** add markdown links like `[X](url)` in the body. seo_optimizer handles all internal link insertion based on the live registry of published content.

This separation matters because the writer doesn't have an up-to-date view of what's published. The seo_optimizer does.

## Frontmatter requirements

Every article must include:

```yaml
title: "..."           # 50-60 chars
description: "..."     # 140-160 chars
language: "..."        # e.g. python
concept: "..."         # e.g. closures
difficulty: "..."      # beginner | intermediate | advanced
target_keyword: "..."  # from brief
secondary_keywords: ["...", "..."]  # from brief
sections_used: ["section-id-1", "section-id-2", ...]  # required for diversity tracking
voice: "..."           # the assigned voice ID
word_count: 0          # actual count, NOT target
published_date: "YYYY-MM-DD"
og_image: "og-default" # build pipeline regenerates
```

## SEO red flags — never do these

These are the writer-side spam patterns that no downstream optimiser can fix:

- **Keyword stuffing.** Mentioning the keyword 10+ times in 1,000 words.
- **Hidden text.** White-on-white, tiny font, off-screen positioning.
- **Fake H1s.** Multiple H1s, or visual styling that makes regular text look like H1.
- **Clickbait titles** that don't match content. "I tried X and you won't believe what happened" — never.
- **Fake author bylines.** Don't invent author names.
- **Manipulative claims.** "The #1 secret to mastering X" — never.
- **AI-generated example data that's wrong.** Don't invent API responses, version numbers, or benchmark numbers. If you don't know, say so or omit.

## Schema.org expectations (writer's role)

The writer does NOT add schema markup. seo_optimizer handles this based on the article's section composition.

The writer's job is to ensure the article HAS the structure that downstream schema generation can pick up:

- Clear H2 sections (becomes Article hasPart)
- If `prac-common-mistakes` is included, the FAQ-style format makes that section eligible for FAQPage schema
- If `code-walkthrough` is included, that section is eligible for HowTo schema

If you're including sections that map to specific schema types, structure them cleanly so the optimizer can pick them up.
