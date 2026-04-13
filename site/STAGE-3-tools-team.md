# Stage 3 — Tools Team Agent (18 Client-Side Developer Tools)

**Goal:** Build the tool spec system and `build-tool.py` script that generates all 18 browser-based developer tools. All tools run entirely in the browser — no server, no API calls, no Cloudflare Workers.

**Depends on:** Stage 1 (read `tool-build-patterns.md` + `astro-conventions.md` skill files)  
**Depends on:** Stage 2 (Astro scaffold must exist for tools to be written into)  
**Unlocks:** Stage 7 (launch needs 10+ working tools)  
**Estimated session time:** 1 session (specs + build-tool.py + generate all tools)  
**LLM for this stage:** Claude Sonnet via OpenRouter

---

## Deliverables Checklist

- [ ] `agents/tools-team/build-tool.py` — reads spec, generates 3 files per tool (always, no exceptions)
- [ ] `agents/tools-team/tool-specs/` — all 18 specs present and validated
- [ ] Running `python agents/tools-team/build-tool.py --spec json-formatter` generates working tool files
- [ ] `npm run build` succeeds with generated tool files

---

## The 18 Tools — 4 Build Batches

### Batch 1 — Formatters & Converters

1. `json-formatter` — JSON Formatter & Validator
2. `html-formatter` — HTML Formatter & Minifier
3. `sql-formatter` — SQL Formatter (basic indentation)
4. `csv-to-json` — CSV ↔ JSON Converter (bidirectional)
5. `markdown-to-html` — Markdown to HTML Converter

### Batch 2 — Encoders & Decoders

6. `base64-encoder` — Base64 Encoder/Decoder
7. `url-encoder` — URL Encoder/Decoder
8. `jwt-decoder` — JWT Decoder (client-side decode only, no verify)
9. `hash-generator` — Hash Generator (MD5, SHA-1, SHA-256, SHA-512 via SubtleCrypto)

### Batch 3 — Generators & Builders

10. `uuid-generator` — UUID v4 Generator
11. `meta-tag-generator` — HTML Meta Tag Generator (title, description, OG, Twitter cards)
12. `sitemap-generator` — XML Sitemap Generator from URL list
13. `readme-generator` — README.md Template Generator (client-side, no AI)
14. `cron-parser` — Cron Expression Builder & Explainer

### Batch 4 — Testers & Utilities

15. `regex-tester` — Regex Tester & Match Highlighter
16. `diff-viewer` — Text Diff Checker (side-by-side)
17. `colour-converter` — Colour Converter (HEX ↔ RGB ↔ HSL ↔ named colours)

> **Decision (April 2026):** All tools are client-side only. No AI-powered tools, no Cloudflare Workers.
> Reasons: (1) API costs uncontrollable at scale; (2) client-side is faster and works offline;
> (3) privacy advantage — nothing leaves the user's browser; (4) zero ongoing infrastructure cost.

---

## Tool Spec JSON Format

Create `agents/tools-team/tool-specs/{slug}.json` for each tool. Example:

```json
{
  "slug": "json-formatter",
  "name": "JSON Formatter & Validator",
  "description": "Format, validate, and minify JSON instantly in your browser. No data sent to servers.",
  "tier": "client-side",
  "batch": 1,
  "category": "data",
  "icon": "braces",
  "tags": ["json", "formatter", "validator", "minify", "beautify"],
  "seo_keywords": ["json formatter online", "json validator free", "format json online", "json beautifier"],
  "primary_keyword": "json formatter online",
  "related_tools": ["csv-to-json", "hash-generator"],
  "related_content": ["what-is-json", "json-vs-xml"],
  "input_label": "Paste JSON here",
  "output_label": "Formatted JSON",
  "features": [
    "Format with 2 or 4 space indent",
    "Minify (remove whitespace)",
    "Validate with line-specific error messages",
    "Copy to clipboard",
    "Clear button"
  ],
  "controls": [
    {"type": "button", "label": "Format", "action": "format"},
    {"type": "button", "label": "Minify", "action": "minify"},
    {"type": "button", "label": "Validate", "action": "validate"},
    {"type": "select", "label": "Indent", "options": ["2 spaces", "4 spaces", "tabs"], "default": "2 spaces"}
  ],
  "template_id": "tool-exp-v1"
}
```

Note: `tier` is always `"client-side"`. No `worker_endpoint` field.

---

## File: `agents/tools-team/build-tool.py`

Always generates exactly **3 files** per tool:
1. `src/components/tools/{slug}.astro` — interactive UI component (vanilla JS)
2. `src/pages/tools/{slug}.astro` — SEO page with schema.org markup
3. `src/content/tools/{slug}.md` — SEO explainer (200–300 words)

CLI options:
- `--spec {slug}` — build one tool
- `--all` — build all specs
- `--batch {1|2|3|4}` — build all tools in a batch
- `--list` — list all specs with batch number

---

## Build Order for This Stage

### Step 1: Write the script and 3 test specs
1. Write `build-tool.py`
2. Write `tool-specs/json-formatter.json`
3. Write `tool-specs/base64-encoder.json`
4. Write `tool-specs/regex-tester.json`

### Step 2: Validate the pipeline
```bash
python agents/tools-team/build-tool.py --spec json-formatter
# Check generated files exist and look correct
npm run build  # should succeed
```

### Step 3: Write all remaining specs
Write the other 14 spec JSON files using the schema above.

### Step 4: Generate all tools by batch
```bash
python agents/tools-team/build-tool.py --batch 1
python agents/tools-team/build-tool.py --batch 2
python agents/tools-team/build-tool.py --batch 3
python agents/tools-team/build-tool.py --batch 4
npm run build  # should succeed with all 17 tools
```

---

## Verification

- [ ] `build-tool.py --list` shows exactly 17 specs (or 18 if count is confirmed)
- [ ] `build-tool.py --spec json-formatter` runs without errors
- [ ] `src/components/tools/json-formatter.astro` exists with working JS
- [ ] `src/content/tools/json-formatter.md` has valid frontmatter with `tier: "client-side"`
- [ ] `http://localhost:4321/tools/json-formatter` renders correctly
- [ ] Tool actually works in browser (paste JSON → format → shows result)
- [ ] Copy to clipboard button works
- [ ] Mobile layout looks correct at 768px
- [ ] `npm run build` succeeds with all tools
- [ ] No `workers/` directory created (client-side only)
- [ ] Lighthouse scores: Performance ≥ 90 on tool pages
