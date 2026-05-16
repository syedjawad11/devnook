# Content Quality Recovery Plan 2.0 — Rewrite Language Articles

## Context

Google is penalizing DevNook's language articles for AI-scaled content patterns (rigid templates, identical tail sections, homogeneous structure). The new content model in `New_ContentStrategy/` solves this by using a modular section system (30 sections, 6 buckets), 5 rotating voices, and diversity enforcement. The goal is to rewrite all 50 articles (45 published + 5 staged) in-place — URLs unchanged — using this new model, with a Claude Routine doing 4 articles per session autonomously.

---

## Current State

| Item | Detail |
|------|--------|
| Published language articles | **45** across 13 languages |
| Staged (unpublished) | **5** articles in content workspace queue |
| Publishing schedule | **PAUSED** — cron commented out in `drip-publish.yml` |
| Cron file | `devnook_content_workspace/.github/workflows/drip-publish.yml` |

**Language breakdown (45 published):**
- javascript: 8 · python: 7 · cpp: 5 · java: 5 · kotlin: 4 · rust: 4 · go: 3 · typescript: 3 · php: 2 · csharp: 1 · google-forms: 1 · ruby: 1 · swift: 1

---

## Folder Decisions — New_ContentStrategy/

### Keep as-is
- `SKILL.md` — master procedure guide
- `sections-openings.md`, `sections-core.md`, `sections-code.md`, `sections-practical.md`, `sections-comparison.md`, `sections-closings.md`
- `voices.md`, `seo-rules.md`
- `example-1-concept.md`, `example-2-howto.md`

### Remove (Python/SQLite pipeline — unusable by Claude routines)
- `migration.sql`
- `INSTALL.md`
- `select_sections.py`

### Add
- `SELECTION-GUIDE.md` — selection algorithm in Claude-readable natural language
- `REWRITE-WORKFLOW.md` — self-contained routine instructions
- `rewrite-queue.json` — 50 articles ordered by oldest pubDate, status=pending/done
- `rewrite-tracker.json` — per-language section history (last 3 combos, for diversity check)

---

## Rewrite Queue — Priority Order

Oldest `published_date` first (all articles with the same date sorted alphabetically within that date).

---

## Claude Routine Setup

**Two routines per day (Malta time, CEST = UTC+2):**

| Routine | Malta | UTC | Cron |
|---------|-------|-----|------|
| Session A | 1:00 AM | 23:00 prev day | `0 23 * * *` |
| Session B | 7:00 AM | 05:00 | `0 5 * * *` |

**Per session:** 4 articles  
**Rate:** 8 articles/day  
**Duration:** 50 ÷ 8 = ~7 days

### What each routine session does

1. Read `rewrite-queue.json` — pick next 4 `pending` articles (oldest pubDate)
2. For each article:
   - Read the existing file from `src/content/languages/{lang}/{slug}.md`
   - Read `rewrite-tracker.json` for that language (last 3 section combos)
   - Use `SELECTION-GUIDE.md` to pick 5-9 sections (avoid >50% overlap with recent)
   - Pick voice from `voices.md` (rotating away from previous article on same language)
   - Rewrite body prose only — ALL frontmatter preserved (title, description, tags, pubDate, faqs, schema_org, etc.)
   - Update `rewrite-tracker.json` with new combo for that language
   - Mark article `done` in `rewrite-queue.json`
3. Commit: `content: rewrite 4 language articles — new content model [session N of 13]`
4. Push to `main` → Cloudflare auto-deploys
5. If 0 pending entries remain → routine exits, sends notification

---

## Resume Publishing (after all 50 done)

1. Re-enable cron in `drip-publish.yml` — restore `schedule:` block
2. The 5 formerly-staged articles are already live (pushed to devnook repo during routine)
3. Disable both rewrite routines via `/schedule`

---

## Frontmatter Rules (important)

- **Never change:** title, description, tags, pubDate, language, concept, og_image, schema_org, related_posts, faqs
- **Update:** `actual_word_count` to reflect new count
- **Add:** `sections_used: [...]` and `voice: [voice-id]`
- **Change:** `template_id` from `lang-v4` → `modular-v1`
- **URL never changes** — the `concept` field drives the URL

---

## Verification Per Session

- Spot-check 1 article: frontmatter intact, no duplicate H1, FAQPage JSON-LD valid, word count in range
- After all sessions: run Ahrefs crawl to confirm content pattern diversity
