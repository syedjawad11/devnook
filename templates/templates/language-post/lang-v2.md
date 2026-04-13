---
# AGENT INSTRUCTIONS — DO NOT PUBLISH THIS BLOCK
# Template: lang-v2 — Problem First
# Use when: concept solves a well-known pain point; reader likely already hit the problem
# Word target: 900–1,100 words
# Variant counter: registry.db → template_counters WHERE content_type = 'language-post'
#
# Fill every field marked [FILL]. Remove all AGENT INSTRUCTIONS blocks before publishing.
---

---
title: "[FILL: How to {action with concept} in {Language}? — e.g. How to Handle Errors in Go?]"
description: "[FILL: One sentence. What problem this solves and how {Language} handles it. 140–155 chars.]"
language: "[FILL: python | javascript | typescript | go | rust | java | csharp | php | ruby | swift | kotlin | cpp]"
concept: "[FILL: slug form]"
difficulty: "[FILL: beginner | intermediate | advanced]"
template_id: "lang-v2"
tags: ["[FILL: language]", "[FILL: concept]", "[FILL: 2–3 related tags]"]
related_tools: ["[FILL]"]
related_posts: ["[FILL: 2–3 related post slugs]"]
related_cheatsheet: "[FILL]"
published_date: "[FILL: YYYY-MM-DD]"
og_image: "[FILL]"
---

<!-- AGENT: Open with the problem, not the solution. Describe a realistic situation where a {Language} developer gets stuck or frustrated without this concept. Make it feel familiar. 2–3 sentences max. No solution yet. -->

## The Problem

<!-- AGENT: Show a broken or naive code example — the "before" state. What does a developer typically write before they know this concept? Annotate why it fails or falls short. 10–18 lines. -->

```{language}
# [FILL: naive / broken approach with comments explaining the problem]
```

<!-- AGENT: 2–3 sentences. What goes wrong at runtime, or why this approach doesn't scale / is error-prone. Be specific — "throws a NullPointerException" not "causes issues". -->

## The {Language} Solution: {Concept}

<!-- AGENT: Introduce the concept as the direct answer to the problem above. Define it in 2–3 sentences. Then immediately show the fixed version of the broken code from above. -->

```{language}
# [FILL: corrected version using the concept, with inline comments]
```

<!-- AGENT: Explain what changed and why it works. 60–90 words. Reference specific lines if helpful. -->

## How {Concept} Works in {Language}

<!-- AGENT: Now go deeper. Explain the mechanics — what {Language} is doing under the hood, or what the syntax rules are. This is the conceptual explanation that follows naturally after the reader already sees the solution working. 120–150 words. No code needed unless it illustrates a mechanic. -->

## Going Further — Real-World Patterns

<!-- AGENT: Show 1–2 more advanced or idiomatic uses of this concept in {Language}. These should reflect patterns a mid-level developer would actually use in production. Each pattern gets a code block + 2–3 sentence explanation. Total 150–200 words including code. -->

**Pattern 1: [FILL: pattern name]**

```{language}
# [FILL]
```

<!-- explanation -->

**Pattern 2: [FILL: pattern name]** *(optional — include if it adds value)*

```{language}
# [FILL]
```

<!-- explanation -->

## What to Watch Out For

<!-- AGENT: 2–3 gotchas or edge cases specific to {Language}'s implementation of this concept. Format each as a short paragraph or bold label + explanation. Prioritise gotchas that are non-obvious or {Language}-specific. 80–120 words total. -->

## Summary

<!-- AGENT: 3–5 sentence recap. Restate the problem, how {concept} solves it, and the one key thing to remember. Should work as a standalone paragraph someone could read without the rest of the article. -->

## Related

<!-- AGENT: Link to 2–3 related posts on the site (other concepts in this language, or the same concept in another language). Link to the {Language} cheat sheet if one exists. Link to any relevant tool. Use relative URLs. -->
