# Section Selection Guide

Use this guide to pick 5–9 sections for each article. Follow all steps in order.

---

## Step 1 — Identify Article Type

Read the article's `concept`, `title`, and `difficulty` frontmatter fields.

| Type | Signals |
|---|---|
| **concept** | Title is a noun phrase ("Closures", "Async Await", "Promises", "Goroutines"). `concept` field has no verb. |
| **how-to** | Title starts with "How to…" or is a verb phrase ("Parse JSON", "Handle Exceptions"). |
| **comparison** | Title contains "vs", "vs.", or compares two things explicitly. |
| **reference** | Cheatsheet-style or syntax reference. Usually `difficulty: beginner`. |

When in doubt: if the article explains WHAT something is → concept. If it explains HOW to do something → how-to.

---

## Step 2 — Required Buckets Per Article

Every article must include exactly:
- **1 opening** (from `sections-openings.md`)
- **1–2 core sections** (from `sections-core.md`)
- **1–2 code sections** (from `sections-code.md`)
- **0–2 practical sections** (from `sections-practical.md`) — optional but adds depth
- **0–1 comparison section** (from `sections-comparison.md`) — optional
- **1 closing** (from `sections-closings.md`)

Total range: **5–9 sections**. Aim for 6–7 for intermediate articles, 5–6 for beginner.

---

## Step 3 — Opening Selection

Pick **exactly one** opening:

| Article type | First choice | Alternatives |
|---|---|---|
| Concept article | `open-mental-model` | `open-problem`, `open-scenario` |
| How-to article | `open-problem` | `open-tldr`, `open-scenario` |
| Comparison article | `open-problem` | `open-quick`, `open-tldr` |
| Error/debugging | `open-error` | `open-problem` |
| Reference/beginner | `open-quick` | `open-tldr` |

Only use `open-error` when the article is specifically about diagnosing or fixing an error.

---

## Step 4 — Core Section Selection

Pick **1–2 core sections**:

| Article type | Preferred |
|---|---|
| Concept | `core-design-decision`, `core-how-it-works` |
| How-to | `core-syntax-detail`, `core-how-it-works` |
| Comparison | `core-design-decision` |
| Reference | `core-syntax-detail`, `core-definition` |

Avoid `core-spec-reading` unless the article genuinely walks through a language specification detail.

---

## Step 5 — Code Section Selection

Pick **1–2 code sections**:

| Context | Preferred |
|---|---|
| Explaining a concept | `code-minimal`, `code-side-by-side` |
| Tutorial / step-by-step | `code-walkthrough`, `code-realistic` |
| Multiple ways to do it | `code-variations`, `code-before-after` |
| Cross-language comparison | `code-side-by-side` |

Use `code-side-by-side` when the article already includes a comparison section — they pair naturally.

---

## Step 6 — Practical Sections (optional, 0–2)

Add practical sections for intermediate or advanced articles, or when the topic has real-world gotchas. Skip for beginner/reference articles.

| Context | Use |
|---|---|
| Topic has common mistakes | `prac-gotchas` or `prac-common-mistakes` |
| Topic is sometimes misused | `prac-when-not-to` |
| Topic has surprising edge cases | `prac-edge-cases` |
| Topic has performance implications | `prac-performance` |
| Topic appears in production systems | `prac-production-patterns` |

---

## Step 7 — Comparison Section (optional, 0–1)

Add a comparison section when:
- The article is a concept article AND the concept exists in other languages with notable differences
- The article already discusses cross-language context in its opening or core

Choose:
- `comp-cross-language` — comparing the same concept across 2–4 languages
- `comp-alternatives` — comparing multiple approaches within the same language
- `comp-history` — only when historical evolution genuinely explains the current design
- `comp-spec-comparison` — only for standards or formal spec comparisons

Do NOT force a comparison section if the topic is narrow or language-specific (e.g., "How to format strings in PHP" doesn't need cross-language comparison).

---

## Step 8 — Closing Selection

Pick **exactly one** closing:

| Context | Use |
|---|---|
| One key insight dominates the article | `close-one-thing` |
| Tutorial or learning-path article | `close-next` |
| Article is 2,500+ words | `close-recap` |
| Reference or how-to with discrete rules | `close-checklist` |
| Essay or philosophical article | `close-open-question` |

For concept articles under 2,000 words, `close-one-thing` is almost always correct.
For how-to articles, `close-checklist` or `close-next` work well.

---

## Step 9 — Diversity Check

After selecting your section combo, check it against recent history for this language.

1. Read `rewrite-tracker.json` → find this language's `last_sections` array (up to 3 recent combos)
2. For each recent combo, count how many of your selected section IDs appear in it
3. Calculate overlap percentage: `matching sections ÷ your combo size`
4. If overlap ≥ 50% with ANY recent combo → swap at least 1 section (different ID, same bucket)
5. Repeat check until overlap with all recent combos is < 50%

**Example**: Your combo is 6 sections. A recent combo shares 3 of them → 50% overlap → swap 1 section from any bucket.

If this is the first article for a language (no history in tracker), skip the diversity check.

---

## Quick Reference — All Section IDs

**Openings:** `open-quick` · `open-problem` · `open-mental-model` · `open-error` · `open-scenario` · `open-tldr`

**Core:** `core-how-it-works` · `core-definition` · `core-syntax-detail` · `core-design-decision` · `core-spec-reading`

**Code:** `code-minimal` · `code-realistic` · `code-walkthrough` · `code-before-after` · `code-variations` · `code-side-by-side`

**Practical:** `prac-gotchas` · `prac-when-not-to` · `prac-edge-cases` · `prac-performance` · `prac-common-mistakes` · `prac-production-patterns` · `prac-testing`

**Comparison:** `comp-cross-language` · `comp-alternatives` · `comp-history` · `comp-spec-comparison`

**Closings:** `close-recap` · `close-next` · `close-one-thing` · `close-checklist` · `close-open-question`
