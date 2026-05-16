# REWRITE-WORKFLOW.md

This is the complete self-contained instruction set for the DevNook language article rewrite routine. Follow every step exactly in order. Do not skip steps. Do not deviate.

**Working directory:** `c:\Users\Syed Jawad Hassan\Desktop\devnook`  
**Repository:** push to `main` branch, Cloudflare auto-deploys on every push.

---

## Step 0 — Read These Files Before Starting

Read all of these before touching any article. You need them throughout the session.

1. `New_ContentStrategy/SELECTION-GUIDE.md` — section selection algorithm (read fully)
2. `New_ContentStrategy/voices.md` — all 5 voices with examples (read fully)
3. `New_ContentStrategy/rewrite-queue.json` — the article queue
4. `New_ContentStrategy/rewrite-tracker.json` — per-language section history

Do NOT read the section files yet — read them per-article as needed.

---

## Step 1 — Pick Articles for This Session

Read `rewrite-queue.json`. Take the **next 3 articles** where `"status": "pending"`, ordered by `order` number ascending (lowest number first).

- If fewer than 3 pending articles remain, process all remaining pending ones.
- If 0 pending articles remain, skip to the **Stop Condition** section at the bottom.

Note the current `sessions_completed` value — you'll use it to label commits.

---

## Step 2 — Process Each Article (repeat for each)

### 2a — Read the Article

Read the full file from `file_path` in the queue entry.

Extract from frontmatter (you'll need these):
- `language`, `concept`, `title`, `description`, `tags`, `difficulty`
- `published_date`, `og_image`, `schema_org`, `related_posts`, `faqs`
- `category`, `related_cheatsheet`, `related_content`, `related_tools`
- Current `template_id` (you'll change this)
- Current `sections_used`, `voice` (may not exist on old articles — that's fine)

### 2b — Read Language History

In `rewrite-tracker.json`, look up this article's `language` key.
- Note `last_sections` (up to 3 recent section combos for this language)
- Note `last_voice`

If no entry exists for this language, treat it as empty history.

### 2c — Select Sections

Follow `SELECTION-GUIDE.md` step by step.

After you have your section list (5–9 sections), open ONLY the section bucket files you need:
- `New_ContentStrategy/sections-openings.md`
- `New_ContentStrategy/sections-core.md`
- `New_ContentStrategy/sections-code.md`
- `New_ContentStrategy/sections-practical.md`
- `New_ContentStrategy/sections-comparison.md`
- `New_ContentStrategy/sections-closings.md`

Read the full specification for each selected section. The spec tells you what the section should accomplish, its length target, forbidden patterns, and example prose. Follow the spec.

### 2d — Select Voice

From `voices.md`:
- If `last_voice` exists for this language: pick any voice that is NOT the same.
- No history: use `thoughtful-explainer` for concept articles, `tutorial-guide` for how-to articles, `terse-senior` for reference/syntax articles.
- Track which voices you use across articles in this session — do not use the same voice more than once per session if you have 3+ articles.

Read the full voice spec for your chosen voice before writing. Voice drift is detectable — maintain the voice throughout the entire article.

### 2e — Write the Article Body

Write the complete rewritten article. This is a full rewrite of the body prose — keep the frontmatter structure and all preserved fields, update the fields listed below.

**Frontmatter — PRESERVE EXACTLY (do not change):**
- `title`
- `description`
- `tags`
- `published_date`
- `language`
- `concept`
- `og_image`
- `schema_org`
- `related_posts`
- `faqs`
- `category`
- `difficulty`
- `related_cheatsheet`
- `related_content`
- `related_tools`

**Frontmatter — UPDATE:**
- `actual_word_count` → count the new body word count (approximate is fine, ±50 words)
- `template_id` → set to `modular-v1`
- `sections_used` → list of selected section IDs, e.g. `[open-problem, core-design-decision, code-side-by-side, prac-gotchas, close-one-thing]`
- `voice` → the selected voice ID (e.g. `thoughtful-explainer`)

**Body — Mandatory rules:**

1. **No H1 in the body.** `PostLayout.astro` renders `frontmatter.title` as the page `<h1>`. Any `# Title` line in the body creates a second H1 — Ahrefs flags this. Use only `##` H2 and below for section headings.

2. **H2 headings are natural prose.** Never use section IDs as headings. "Open Problem" is a section spec name — not a heading. Write headings like: "When TypeScript Catches What JavaScript Misses" or "The Performance Trap Nobody Warns You About".

3. **Target word count:**
   - `difficulty: intermediate` → 1,400–2,000 words
   - `difficulty: beginner` → 1,000–1,500 words
   - `difficulty: advanced` → 1,600–2,200 words

4. **Voice consistency.** No drift. Read the voice spec before writing and check against it after writing. If two voice styles appear in the same article, rewrite.

5. **No forbidden vocabulary.** Check your draft for: professional, comprehensive, fundamental, robust, indispensable, crucial, critical, essential, powerful, elegant, drastically, absolutely, meticulously, seamlessly, leverages, utilizes, employs (as synonym for "uses"), facilitates, in conclusion, in summary, to summarise, it's important to note that, in this article, in this guide, this post will. Remove every instance.

6. **Code examples must be accurate.** No pseudocode unless the section spec explicitly allows it. Code blocks must be valid syntax for the language.

7. **No explanatory comments in code** unless the WHY is non-obvious. Never comment what the code does — only why a non-obvious choice was made.

8. **No duplicate content from the existing article.** The rewrite is new prose, not a lightly edited version of the original. If a section carries over the same concept, the angle and framing must differ.

### 2f — Update the Tracker

After writing the article, update `rewrite-tracker.json`:

- Add the new section combo to `last_sections` for this language.
  - Keep only the most recent 3 combos (drop the oldest if there are already 3).
- Set `last_voice` to the voice used.

If the language key doesn't exist yet in the tracker, create it:
```json
"language-name": {
  "last_sections": [["section-a", "section-b", ...]],
  "last_voice": "voice-id"
}
```

### 2g — Update the Queue

In `rewrite-queue.json`, for this article's entry:
- Set `"status": "done"`
- Set `"rewritten_on": "YYYY-MM-DD"` (today's date)
- Set `"session": [sessions_completed + 1]`

Also update the top-level counters:
- Increment `done_count` by 1
- Decrement `pending_count` by 1

Do NOT increment `sessions_completed` yet — do that once after all articles in this session are done.

---

## Step 3 — Commit and Push

After all articles in this session are written and both JSON files updated, run:

```
git add src/content/languages/ New_ContentStrategy/rewrite-queue.json New_ContentStrategy/rewrite-tracker.json
```

Then commit (replace N, X, Y with actual numbers):

```
git commit -m "content: rewrite N language articles — new content model [session X of Y]"
```

Where:
- **N** = number of articles rewritten this session (3 for normal sessions, fewer if queue nearly empty)
- **X** = `sessions_completed + 1` (the session number you're completing)
- **Y** = rough total: `ceiling(total ÷ 3)` = 16

Then:
```
git push origin main
```

After successful push, increment `sessions_completed` in `rewrite-queue.json` by 1, then:

```
git add New_ContentStrategy/rewrite-queue.json
git commit -m "chore: rewrite session X complete — pending_count remaining"
git push origin main
```

---

## Stop Condition

If `pending_count` in `rewrite-queue.json` reaches 0 after updating:

1. Do NOT re-enable the drip-publish cron.
2. Output this message: "Rewrite complete. All 47 articles rewritten. Review articles and re-enable drip-publish manually when ready."
3. End the session.

---

## Quality Spot-Check (do for the last article each session)

Before committing, verify:
- [ ] No `# H1` in the body
- [ ] Frontmatter fields that should be preserved are unchanged (especially `schema_org`, `faqs`, `concept`, `published_date`)
- [ ] `template_id` is `modular-v1`
- [ ] `sections_used` and `voice` are present
- [ ] `actual_word_count` is updated
- [ ] No forbidden vocabulary in the body
- [ ] Voice is consistent throughout (re-read the voice spec and compare)
