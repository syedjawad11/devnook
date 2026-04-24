# DevNook — Claude Session Log

> Always read this file first at the start of a new session. Updated at end of every session.

## Session start — do NOT auto-read these files

Unless the user explicitly asks ("check X", "read X", "look at X"), **do not** open:

- `new-content-plan.md` / `new_content_plan.md`
- `new-project-summary.md`
- `devnook-site-updates.md`
- `my_file.md`
- `session-history.md` (on demand only — "why did we X in session N?")
- `archives/decisions-archive.md` (on demand only)
- `docs/content-strategy.md` (on demand only — planning velocity, ring coverage)
- Prior chat transcripts

Start each session from this file + MEMORY.md only.

---

## Project Overview

**DevNook** (devnook.dev) — developer resource site, 1,000+ programmatic posts + 18 client-side browser tools, monetized via AdSense (deferred until 50k visitors/month).

**Stack:** Astro + Cloudflare Pages, Claude Code subagents (Haiku/Sonnet), GitHub Actions drip-publish.
**Repo:** `main` branch, Cloudflare Pages auto-deploy.

---

## Stage Progress

| Stage | Status | Completed |
|-------|--------|-----------|
| 1 — Skills | ✅ | 2026-04-10 |
| 2 — Dev Team | ✅ | 2026-04-10 |
| 3 — Tools Team | ✅ | 2026-04-11 |
| 4 — Content Pipeline Core | ✅ | 2026-04-12 |
| 5 — Content Pipeline Write | ✅ | 2026-04-12 |
| 6 — Publishing | ✅ | 2026-04-13 |
| 7 — Launch | ✅ Live | 2026-04-15 |
| 8 — Subagent Architecture | 🚧 Phase 2 complete | 2026-04-17 |

---

## Last Session (2026-04-24, #26)

**Status:** ✅ Fixed silent drip-publish bug that had been stalling the queue since 2026-04-22. Manually published today's 3 posts.

### What was done

- **Investigated "drip ran but nothing changed"**: today's 08:00 UTC drip (commit `1fc0b89`) modified only `registry.db` with zero markdown diffs. Traced back: commits `15f586c` (Apr 22), `e52faa1` (Apr 23), `1fc0b89` (Apr 24) all had the same pathology — only registry.db changed, no content moved. First clean drip was `f8f379a` (Apr 21) which added 3 files to src/content with **no matching content-staging deletions**.
- **Root cause**: [`.github/workflows/drip-publish.yml`](.github/workflows/drip-publish.yml) and [`on-demand-publish.yml`](.github/workflows/on-demand-publish.yml) only ran `git add src/content/ agents/content-team/registry.db`. Meanwhile [`agents/publish/publish.py`](agents/publish/publish.py) uses `shutil.move()` which deletes from `content-staging/` on the runner's FS — but with staging/ not in `git add`, those deletions never got committed. Every fresh checkout restored the stale files, and `get_staged_files()` walks the filesystem (not the DB) picking oldest-by-mtime, so it kept re-picking already-published files forever.
- **Fix committed (`997e8fd`)**: added `content-staging/` to `git add` in both workflow files.
- **Stale staging cleanup**: removed 4 zombie files that had been getting re-picked daily:
  - `content-staging/blog/css-flexbox-vs-grid.md` (live since Apr 21)
  - `content-staging/cheatsheets/git-commands-cheatsheet.md` (live since Apr 21)
  - `content-staging/guides/css-minification-performance-optimization.md` (live since Apr 21)
  - `content-staging/languages/javascript/how-to-implement-singleton-design-pattern-in-javascript.md` (live since Apr 20)
- **Manual drip for today (`39b4ac8`)**: ran `publish.py --count 3` locally. First run picked up 2 more stale files (cpp/http-request, java/lambda — both already live since Apr 20) + 1 real (java/env-vars). Cleaned the last stale, ran --count 2 more to reach 3 real new publishes:
  - `languages/java/how-to-set-environment-variables-in-java`
  - `languages/javascript/how-to-parse-json-in-javascript`
  - `languages/kotlin/how-to-use-data-class-in-kotlin`
- **Timestamp restoration**: the 2 stale re-publishes (cpp/http-request, java/lambda) had their `published_at` and `published_date` overwritten to 2026-04-24 by the broken run. Restored to original 2026-04-20 values via direct SQL so they don't float to the top of recent-posts sorts.
- **Registry state now**: 32 published / 16 staged / 10 rejected. No stale files left in content-staging.

### Next session priorities (#27)

1. **Verify the fix on 2026-04-25 drip** — after 08:00 UTC run, check `git show origin/main --stat` for the scheduled commit. Expected: both `src/content/…md` additions AND `content-staging/…md` deletions in the same commit. If only `registry.db` changes, fix didn't take.
2. **Audit prior "re-publish" registry entries** — the bug inflated `published_at` on at least 2 other posts (css-flexbox, git-commands, css-minification all have Apr 24 timestamps but have been live since Apr 21; they weren't restored this session because the user asked them to count as "today's drip"). Decide whether to restore or leave.
3. **Verify sitemap in GSC** — resubmit `https://devnook.dev/sitemap-index.xml` and confirm no errors (carryover from #24/#25)
4. **Monitor remaining queue drain** — 16 staged, mix of 1 old programmatic (Apr 12), 2 editorial (Apr 17, Apr 20), 6 older antigravity (Apr 17), 7 newer antigravity (Apr 23). At 3/day the queue drains ~2026-05-09.
5. **Next antigravity batch** — after queue drains, ingest + QA the next wave.
6. **Optional**: delete `link_utility.py` + `linker.md` + `agents/content-team/tests/` after a few weeks of stable plugin operation.

### Deferred (do not do)

- **AdSense integration** — revisit only at 50k visitors/month
- Blog filter chips wiring (decorative only)
- Search bar wiring (`SearchBar.astro` parked)
- Orphan `sitemap-generator-from-url.md` cleanup

---

## Key Paths

- Subagent prompts: `agents/subagent-prompts/{planner,writer,ingest,antigravity-qa,builder,publisher}.md`
- Skills: `agents/skills/{name}.md`
- Registry: `agents/content-team/registry.db` (25 columns, includes content_type + source)
- Drafts: `agents/content-team/drafts/`
- Antigravity ingest source: `../web_content/output/`
- Astro site: `src/`

<!-- Architecture plan: development_stages/subagent-architecture-plan.md -->

---

## Subagent Architecture Quick Reference

```
ORCHESTRATOR (Opus/Sonnet main session)
  ├── Content Team
  │   ├── Planner  (Haiku)  — keyword discovery → posts (status=queued)
  │   ├── Writer   (Sonnet) — drafts/{slug}.md (status=drafted, qa validated)
  │   ├── Ingest   (Haiku)  — ../web_content/output/ → drafts/ (status=drafted)
  │   └── Antigravity QA (Sonnet) — fixes + approves antigravity drafts
  │   [Linker retired — build-time rehype plugin handles internal links]
  ├── Dev Team
  │   └── Builder  (Sonnet) — Astro edits + npm run build
  └── Publish Team
      └── Publisher (Haiku) — linked drafts → staging → src/content
```

Orchestrator spawns subagents, reviews JSON reports (~200 tok each), commits + pushes only on user approval. Python scripts retained as non-LLM utilities.

**Workflow patterns:**
- A — weekly content: Planner → Ingest (parallel) → Writer (batch=5) → Publisher
- A2 — antigravity: Ingest → Antigravity QA (batch=10) → Publisher
- B — new tool: Orchestrator → Builder → review + commit
- C — bug fix: Orchestrator → Builder → review + commit
- D — status check: inline sqlite3 query (no subagent)

---

## Important Decisions Log

> Live guardrails only — if you forget these, you will break something. Historical reasoning in [archives/decisions-archive.md](archives/decisions-archive.md).

| Decision | Impact |
|----------|--------|
| No Tailwind | All styles in `tokens.css` custom properties |
| All tools client-side only | 18 tools, no Workers, no AI-powered tools |
| Static output (not hybrid) | `output: 'static'`, no adapter — satori crashes Workers runtime |
| Global CSS in `public/styles/` not `src/styles/` | Astro only copies `public/` to `dist/`; absolute `/styles/*` refs need public/ |
| PostCard prop is `href` not `slug` | All 5 call sites use `href`; never rename to slug/url/path |
| `tools/[slug].astro` uses `import.meta.glob` | Dynamic `await import()` crashes Vite static analysis |
| Never call `build-tool.py build_tool()` for existing tools | Writes page that collides with dynamic route — use `generate_seo_explainer()` + `write_file()` |
| Languages category owned by Antigravity | Planner + Writer must never queue languages posts |
| Antigravity QA never rejects | Trusted Gemini Pro 3.1 content; QA fixes structural/SEO only, always sets `qa_status='passed'`, word range 1500–2500 |
| Linker retired (session 25) | Replaced by `src/plugins/auto-internal-links/index.mjs` (build-time rehype plugin). `link_utility.py` + `linker.md` kept dormant in repo. Publisher staging query now uses `status IN ('drafted','linked')`. Existing `linked` rows in registry kept as historical data. |
| Auto internal links plugin (rehype, build-time) | `src/plugins/auto-internal-links/index.mjs`; `autoAnchors: true`; `devnookUrlBuilder` required — language concept URLs use `frontmatter.language`+`frontmatter.concept`, NOT filename; 87 anchors from 42 files at session 24 |
| Use `@astrojs/sitemap@3.2.1` not custom | Custom sitemap was broken; v3.7+ incompatible with Astro 4.x. Current version generates `sitemap-0.xml` (0-indexed) — do not expect `sitemap-1.xml` |
| Publish workflows must `git add content-staging/` (session 26) | `publish.py` uses `shutil.move` which deletes staging files; without staging in `git add`, deletions never commit and every next checkout restores them. `get_staged_files()` walks the FS (not the DB), so stale files get re-picked by mtime. Always include `content-staging/` in `git add` for any workflow that moves files out of it. |

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...       # writer, qa agents + tools-team
GOOGLE_SERVICE_ACCOUNT_JSON=...    # GSC Indexing API — GitHub secret for drip-publish
```

---

## How to Run

```
Invoke subagents via Agent() tool. Pass agents/subagent-prompts/{name}.md as prompt body.

Status check:
  python -c "import sqlite3; db=sqlite3.connect('agents/content-team/registry.db');
  [print(r) for r in db.execute('SELECT status, content_type, source, COUNT(*) FROM posts GROUP BY 1,2,3')]"

Build:  npm run build
Dev:    npm run dev
```
