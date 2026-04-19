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

## Last Session (2026-04-19, #21)

**Status:** ✅ Linker subagent fully implemented + 45 internal links retrofitted into 21 live posts. Details in [session-history.md](session-history.md).

### What was done

- Built `agents/content-team/link_utility.py` — rule-based internal link inserter (no LLM, 8 links max/post)
- Built `agents/subagent-prompts/linker.md` — Haiku subagent for batch + retrofit modes
- 8 pytest cases passing (`agents/content-team/tests/`)
- Updated `publisher.md` staging query to `status='linked'`
- Retired Gemini Flash link-insertion branch from `seo_optimizer.py`
- Retrofitted 21 published posts (45 links) + 11 staged posts (14 links) — pushed live

### Next session priorities (#22)

1. **Investigate missing staging file** — `python-file-handling-tutorial` is in registry as `staged` but file not found on disk; check if ingest failed or file is in wrong location, clean up registry if needed
2. **Scale Writer** — run on 2 queued editorial posts (CSS/HTML minification)
3. **Fix 2–3 minor website UI issues** (user will specify)
4. **Verify GSC** — sitemap submission + indexing
5. **Next antigravity batch** — ingest + QA + stage more languages articles

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
  │   ├── Antigravity QA (Sonnet) — fixes + approves antigravity drafts
  │   └── Linker   (Haiku)  — inserts in-body links via link_utility.py (status=linked)
  ├── Dev Team
  │   └── Builder  (Sonnet) — Astro edits + npm run build
  └── Publish Team
      └── Publisher (Haiku) — linked drafts → staging → src/content
```

Orchestrator spawns subagents, reviews JSON reports (~200 tok each), commits + pushes only on user approval. Python scripts retained as non-LLM utilities.

**Workflow patterns:**
- A — weekly content: Planner → Ingest (parallel) → Writer (batch=5) → Linker → Publisher
- A2 — antigravity: Ingest → Antigravity QA (batch=10) → Linker → Publisher
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
| Linker runs between QA/Writer and Publisher | Rule-based match first (`link_utility.py`), Haiku fill-in only if <3 links; Publisher staging query reads `status='linked'` |
| Use `@astrojs/sitemap@3.2.1` not custom | Custom sitemap was broken; v3.7+ incompatible with Astro 4.x |

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
