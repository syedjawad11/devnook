# DevNook — Operational Status

> Single home for **ephemeral** state: active routines, content queue, and pending
> one-off tasks. The `CLAUDE.md` files hold durable instructions only and point here.
> Keep this file current; when an item is done, remove it (git history is the record).

**Last updated:** 2026-06-12

---

## Active routines

All routines run as remote CCR agents (`claude-sonnet-4-6`, source `syedjawad11/devnook`)
and publish via `git push origin HEAD`. Times in UTC; Malta is CEST (UTC+2).

| Routine | Trigger ID | Cron | Status | Notes |
|---------|-----------|------|--------|-------|
| Editorial publisher (`/blog/`, `/guides/`) | `trig_01Xc9GuTZmzJAQXXAD7KZXUs` | `0 23 * * *` (01:00 Malta) | ✅ Healthy | ER-9 `git push` bug fixed 2026-05-30 |
| Language publisher (`/languages/`) | `trig_015wteVF9kPq2mNxR7sT4wXz` | `0 3 * * *` (05:00 Malta) | ✅ Active | URL = frontmatter `concept`, not filename |
| Rewrite routine (thin `/languages/` posts) | `trig_01VJJqhYwLmK3nP8rT5vX2zQ` | `0 1 * * *` (03:00 Malta) | ✅ Active | Overwrites in place; never changes slug/concept |
| Cheatsheet rewriter (`/cheatsheets/`) | `trig_01VVSqp7cL8c6N6VvScXLSg2` | `0 2 * * *` (04:00 Malta) | ✅ Active | Full rewrite approach (not append); confirmed working (regex run 2026-06-09) |
| Pipeline B (keyword-first cluster) | `trig_012dkTjBKiB8M9ASkKZ1c1Gk` | `0 14 * * *` (16:00 Malta) | ✅ Re-enabled | id=7 `react-vs-angular-vs-vue-comparison` is ready; id=5 git-commands collision fixed (marked skip 2026-06-10) |

Routine "how it works" / gotchas are documented in memory
(`project_editorial_routine`, `project_language_routine`, `project_rewrite_routine`).

---

## Content queue

| Section | Queued | Notes |
|---------|--------|-------|
| Editorial | 3 posts (ids 104, 106, 107) | Next 23:00 UTC run picks id 104 `what-is-cross-join-in-sql`, then 106 `stack-vs-heap-memory`, 107 `what-are-indexes-in-sql`. Top up from `editorial_opportunity` primary tier when low. |
| Language | — | id 105 `typescript-tuples` was published manually to `/languages/typescript/tuples/` on 2026-06-04 (pulled from the editorial queue; TS syntax belongs in `/languages/`, not editorial). |
| Rewrite | 5 thinnest posts seeded | From `language_rewrite_queue`. |
| Cheatsheet rewrite | 4 sheets queued (order 2–5) | `cheatsheet_rewrite_queue`: ~~regex~~ ✅ → docker → git → linux → python-string. Drain runs 2–5 scheduled: 23:45 UTC Jun 9, 04:45 / 09:45 / 14:45 UTC Jun 10. IDs: trig_016ixMLFvpxR66u5kKxehDmS / trig_01KFVotP7UozupcLQJYpoCzX / trig_015ZLwrp9VfxFYeV7XkkxiMd / trig_01H7J4LaCY2nowpVvhjj2onK |

Verify against the DB (from `pipeline/`):
`python -c "import sqlite3; print(sqlite3.connect('data/registry.db').execute(\"SELECT status, content_type, COUNT(*) FROM posts GROUP BY 1,2\").fetchall())"`

---

## Pending one-off tasks

- [ ] **Remove `DEVNOOK_REPO_PAT` secret** from `syedjawad11/devnook` — no longer needed
  in the monorepo.

---

## Recently completed (rolling — prune freely)

- 2026-06-12 — **Ahrefs SEO audit fixes (2026-06-08 crawl).** Resolved all four issue categories: (A) 5 broken internal 404 links fixed — `/tools/regex-tester-online-java` → `/tools/regex-tester/` (2 files), `/tools/sitemap-generator-from-url` → `/tools/sitemap-generator/` (3 files, tool_slug mismatch); (B) 2 dead blog links repointed to `https://docs.github.com/actions`; (C) 1 broken external link fixed (`supermaven.com/docs` → `supermaven.com/`); (D) `fix_trailing_slashes.py` ran — 105 trailing-slash fixes across 25 content files; (E) all 5 CCR agent prompts updated so `url_map` now emits trailing-slash URLs — recurrence prevented. Build: 123 pages, 0 errors.

- 2026-06-11 — **Full 3-phase SEO implementation plan complete** (`developer_site_seo_case study/13-implementation-priority-plan.md`). All phases done: Phase 0 (6 cusp-of-page-1 optimizations), Phase 1 (cheatsheet + tool page expansions), Phase 2 (9 new gap articles + 3 existing-page expansions). No further tasks from that plan.

- 2026-06-11 — **Phase 2 Steps 3 + 4 complete.** Step 3 (`5d107dd`): expanded HTTP Status Codes, ChatGPT vs Claude, Python List Comprehension. Step 4: targeted content additions to 6 cusp-of-page-1 pages — C++ try-catch (`std::expected` section), markdown-to-html (syntax quick reference), Ruby JSON (`oj` gem pattern), Swift closures (`Result` type section), Kotlin data class (`@JvmRecord` section), Python URL-encode (`requests` library section). Regex cheatsheet skipped (rewritten 2026-06-09, already sufficient). Build: 123 pages, no errors.

- 2026-06-10 — **Phase 2 seeded.** 9 new articles queued in registry (html-reference-guide, markdown-cheatsheet, css-basics-cheatsheet, python-math-numbers, cpp-data-structures-stl, cpp-string-methods, cpp-loops-control-flow, java-data-structures, tmux-cheatsheet). Pipeline B blocker resolved: keyword_set_id=5 marked skip.
- 2026-06-10 — **Phase 1 Part 2 complete.** Expanded 3 tool pages with Quick Reference panels + SEO content (`7325c4c`). json-formatter: XML↔JSON converter tab + JSON Minify section (targets `json minify` KD2/$47 CPC, `xml to json` KD1). html-formatter: HTML Quick Reference panel + fixed longstanding CSS truncation (targets `html divider` KD4, `blink html` KD10). sql-formatter: SQL Quick Reference panel + fixed CSS truncation (targets `coalesce sql` KD10, `sql window functions` KD14, `group by sql` KD8).

- 2026-06-09 — Cheatsheet rewrite routine confirmed working. `regex-cheatsheet` fully rewritten and live (`5d617dd`). Drain runs 2–5 scheduled to complete by 14:45 UTC Jun 10. Root cause of initial failed run: CCR was fired 9 min before the push landed on origin/main (merge conflict delayed the push to 18:46 UTC; CCR cloned at ~18:37 UTC). Second fire succeeded cleanly.

- 2026-06-04 — Published `typescript-tuples` to `/languages/typescript/tuples/` (manual,
  not via routine). It had been mistakenly seeded into the editorial queue (id 105); TS
  syntax topics belong in the programmatic `/languages/` section per `pipeline/CLAUDE.md`.
  Registry row 105 converted in place (category→languages, content_type→programmatic,
  status→published); editorial queue dropped from 4 to 3 (ids 104, 106, 107). Build passed
  (120 pages), all internal links resolve.
- 2026-06-03 — Fixed "Page with redirect" (GSC): canonical URLs are directory-style
  (trailing slash); the no-slash variant 301-redirects. Switched all URL emitters to
  the trailing-slash form (commit `503a3a8`): `publish.py` + `core/publish.py` live_url,
  `astro.config.mjs` permalink/url frontmatter normalization, and all three cloud routine
  prompts (editorial/language/rewrite) + Pipeline B prompts — schema.org JSON-LD `url`,
  live_url logging, and `LIVE_URL` output. Routines load prompts from the repo at each
  fire, so the fix takes effect on the next scheduled run; no trigger recreation needed.
  **Convention going forward:** every devnook URL emitted must end with `/`.
- 2026-05-31 — Archived legacy repo `syedjawad11/devnook-content` and removed the local
  `devnook_content_workspace/` folder (superseded by `pipeline/`).
- 2026-05-30 — Editorial routine ER-9 `git push origin HEAD` fix verified
  (`websockets-vs-http` published, live 200).
- 2026-05-30 — GSC Indexing API decommissioned (unsupported on `sc-domain:` properties).
- 2026-05-29 — Redesign stages 1–13 complete (see `site/docs/devnook-redesign-stages.md`).
