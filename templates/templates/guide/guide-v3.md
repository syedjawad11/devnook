---
# AGENT INSTRUCTIONS — DO NOT PUBLISH THIS BLOCK
# Template: guide-v3 — Problem → Solution
# Use when: concept directly solves a pain point developers search for; search intent is "how do I fix/do X"
# Word target: 900–1,100 words
# Variant counter: registry.db → template_counters WHERE content_type = 'guide'
#
# Fill every field marked [FILL]. Remove all AGENT INSTRUCTIONS blocks before publishing.
---

---
title: "[FILL: How {Concept} Solves [problem] — e.g. How CORS Works and How to Fix It]"
description: "[FILL: What {concept} is, the problem it solves, and how to work with it as a developer. 140–155 chars.]"
category: "[FILL: web-concepts | http | dns | apis | formats | dev-tools | security]"
template_id: "guide-v3"
tags: ["[FILL]", "[FILL]", "[FILL]"]
related_tools: ["[FILL]"]
related_posts: ["[FILL]"]
related_cheatsheet: "[FILL]"
published_date: "[FILL]"
og_image: "[FILL]"
---

<!-- AGENT: Open with the problem, not the concept. Describe the scenario a developer is in when they need to know about {concept}. Should feel like reading their mind. 2–3 sentences. -->

## Why This Happens

<!-- AGENT: Explain the root cause of the problem. Don't introduce {concept} by name yet — explain the underlying mechanism that creates the situation. 100–130 words. -->

## What is {Concept}?

<!-- AGENT: Now introduce {concept} as the explanation for what the reader just learned. Define it clearly in 3–5 sentences. Make the connection between the problem and the concept explicit. -->

## How {Concept} Works

<!-- AGENT: Walk through the mechanism. What does {concept} actually do? If there's a flow (request → server checks → response), describe it. 120–160 words. A step-by-step list is appropriate here. -->

1. [FILL]
2. [FILL]
3. [FILL]
4. [FILL] *(add or remove steps as needed)*

## The Fix / How to Work With It

<!-- AGENT: Practical implementation. Code, config, or commands that let the developer work with {concept} correctly. Annotated. This is the section people scrolled to — make it immediately actionable. -->

```[language or format]
# [FILL: working implementation]
```

<!-- AGENT: 2–3 sentences. What this does and any critical options or flags to know. -->

## Common Mistakes

<!-- AGENT: 2–3 specific errors developers make when dealing with {concept}. Each: bold mistake label → what goes wrong → the correct approach. 90–120 words total. Prefer mistakes that cause real, hard-to-debug issues. -->

**[FILL: mistake]** — [FILL: what goes wrong and the fix]

**[FILL: mistake]** — [FILL: what goes wrong and the fix]

## Quick Reference

<!-- AGENT: 4–6 bullet points. The facts a developer needs to keep in mind when working with {concept}. Written as reminders, not explanations. -->

- [FILL]
- [FILL]
- [FILL]
- [FILL]

## Related

<!-- AGENT: Links to related guides, tools, cheat sheet. Include a link to the most relevant tool on the site if one exists. -->
