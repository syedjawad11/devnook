# DevNook — Tool Build Patterns

## Tool Architecture

All DevNook tools are **client-side only** — they run entirely in the browser with no server, no API calls, and no ongoing infrastructure cost. Tools are organised into 4 build batches based on category similarity.

### Build Batches

- **Batch 1 — Formatters & Converters:** JSON Formatter, HTML Formatter, SQL Formatter, CSV ↔ JSON Converter, Markdown to HTML Converter
- **Batch 2 — Encoders & Decoders:** Base64 Encoder/Decoder, URL Encoder/Decoder, JWT Decoder, Hash Generator
- **Batch 3 — Generators & Builders:** UUID Generator, Meta Tag Generator, Sitemap Generator, README Generator, Cron Expression Builder
- **Batch 4 — Testers & Utilities:** Regex Tester, Diff Checker, Colour Converter

## Tool Spec JSON Schema

Every tool starts with a spec file at `agents/tools-team/tool-specs/{slug}.json`:

```json
{
  "slug": "json-formatter",
  "name": "JSON Formatter & Validator",
  "description": "Format, validate, and minify JSON instantly in your browser.",
  "tier": "client-side",
  "batch": 1,
  "category": "data",
  "tags": ["json", "formatter", "validator", "minify"],
  "seo_keywords": ["json formatter online", "json validator", "format json"],
  "related_tools": ["base64-encoder", "url-encoder"],
  "related_content": ["what-is-json", "json-vs-xml"],
  "icon": "braces",
  "input_type": "textarea",
  "output_type": "textarea",
  "features": ["Format (2-space indent)", "Minify", "Validate with error line", "Copy to clipboard"]
}
```

Note: `tier` is always `"client-side"`. There is no Tier 2 or AI-powered tooling.

## File Generation per Tool

Running `build-tool.py --spec {slug}` always generates exactly 3 files:

1. `src/components/tools/{slug}.astro` — interactive UI component
2. `src/pages/tools/{slug}.astro` — page that wraps the component + SEO content
3. `src/content/tools/{slug}.md` — SEO explainer article (200–300 words)

## Astro Tool Component Structure

```astro
---
// No server-side props needed — all tools are client-side
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
tier: "client-side"
seo_keywords: [keyword1, keyword2, keyword3]
related_tools: [slug1, slug2]
related_content: [slug1, slug2]
published_date: "YYYY-MM-DD"
og_image: "/og/tools/{slug}.png"
---
```

Body: 200–300 words. Structure:
1. What is this tool? (1 paragraph)
2. How to use it (numbered steps)
3. When would you use this? (2–3 bullet use cases)
4. FAQ (2–3 questions in H3 format)

## Important Rules
1. All tools: zero external HTTP requests. Fully self-contained.
2. All tools must be functional on mobile (768px breakpoint).
3. All tools must work without JavaScript disabled for the static SEO page.
4. Copy-to-clipboard must use `navigator.clipboard` API with a "Copied!" visual feedback for 2 seconds.
5. Error messages must be human-readable (not raw exception strings).
6. Every interactive element needs `aria-labels`; status messages need `aria-live="polite"`.
