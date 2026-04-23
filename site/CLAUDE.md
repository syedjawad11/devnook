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

## Last Session (2026-04-23, #25)

**Status:** ✅ Linker retirement finalized + 9 orphan antigravity posts recovered and queued for drip.

### What was done

- **Orphan batch recovery (Workflow A2)**: 9 antigravity articles had bypassed Ingest and were sitting in `../web_content/output/_ingested/2026-04-22/`. Moved back to `../web_content/output/` root, ran Ingest → Antigravity QA (batch=9, all passed) → Publisher stage. All 9 now in `content-staging/languages/` with `status='staged'`
- One QA correction: `how-to-do-file-handling-in-google-colab.md` — language frontmatter corrected `go` → `python`, 9 code blocks retagged
- **Drip ordering**: 16 total staged (7 older editorial from 2026-04-17 + 9 new antigravity from 2026-04-23). All have `opportunity_score=NULL` so order falls to `created_at ASC` — older 7 publish first (2026-04-24 through 2026-04-26), new 9 interleave after (2026-04-27 through 2026-04-29). User chose Option A (accept ordering)
- **Registry binary merge conflict**: remote `e52faa1` touched registry.db; reconciled by extracting remote DB via Python subprocess (Windows bash redirect corrupts binaries) and copying 3 `published_at` values for editorial posts into local DB. Committed as `758683e`
- **Linker retirement** (from session 24 plan):
  - Production HTML verified to contain `auto-internal-link` class
  - `agents/subagent-prompts/publisher.md` staging query already updated to `status IN ('drafted','linked')`
  - Linker removed from workflow patterns A/A2 in this file
  - `link_utility.py` + `linker.md` + tests kept dormant (committed as reference)
- **Cleanup commits**:
  - `d0cac56` — Linker retirement (CLAUDE.md + dormant linker files)
  - `4881d65` — antigravity-qa subagent prompt added
  - `ab2cb7a` — .gitignore `.claude/`, archives, docs/content-strategy.md, devnook-site-updates.md
- Removed duplicate folders: `templates/templates/templates/`, empty `{braces}` dir, `devnook_plugin/` (superseded by `src/plugins/auto-internal-links/`)

### Next session priorities (#26)

1. **Monitor drip runs** — confirm 2026-04-24/25/26 publish the 3 older editorial posts correctly; 2026-04-27/28/29 publish the 9 antigravity posts. Watch for any QA-flagged issues on the `colab` language correction
2. **Verify sitemap in GSC** — resubmit `https://devnook.dev/sitemap-index.xml` and confirm no errors (carryover from #24)
3. **Next antigravity batch** — after current 9 finish draining, ingest + QA the next wave
4. **Optional**: delete `link_utility.py` + `linker.md` + `agents/content-team/tests/` after a few weeks of stable auto-internal-links plugin operation

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
