# DevNook — Claude Session Log (Dev Workspace)

> Always read this file first at the start of a new session. Updated at end of every session.
> **Content pipeline lives in `../devnook_content_workspace/`** — no pipeline code or registry in this repo.

## Session start — do NOT auto-read these files

Unless explicitly asked, do not open:

- `archives/decisions-archive.md` (on demand only)
- Prior chat transcripts or session history

Start each session from this file + MEMORY.md only.

---

## TODO (next session #61)

1. **Run Stage 0 locally** — harvest keywords, embed via Gemini, cluster. Invoke:
   ```python
   Agent(subagent_type="general-purpose",
         prompt=open(".claude/agents/pipeline-b-stage0-harvest-cluster.md").read()
                + "\n\nWORKSPACE_DIR=C:\\Users\\Syed Jawad Hassan\\Desktop\\devnook_content_workspace")
   ```
   Requires `GOOGLE_API_KEY` env var for Gemini embeddings. Expect ~400–1000 keywords, ~20–50 clusters.
2. **Verify Stage 0 output** — run these queries in `data/keywords.db`:
   ```sql
   SELECT status, COUNT(*) FROM clusters GROUP BY status;
   SELECT category, COUNT(*) FROM clusters WHERE status='viable' GROUP BY category;
   SELECT primary_keyword, category, total_volume FROM clusters WHERE status='viable' ORDER BY total_volume DESC LIMIT 5;
   ```
   If 0 viable: lower `DISTANCE_THRESHOLD` to `0.15`, `UPDATE keyword_pool SET cluster_id=NULL`, `DELETE FROM clusters`, re-run from S0-8.
3. **Run full orchestrator** — `MAX_ARTICLES_PER_RUN=5`. Expect 5 articles published.
4. **After first article is live**: cleanup — delete `data/pipeline-b-topics.json`, update `pipelineB.md` docs, archive legacy `pipeline-b-orchestrator.md` (v1).
5. **Re-enable CCR routine** `trig_012dkTjBKiB8M9ASkKZ1c1Gk` — only after end-to-end run succeeds.

---

## Project Overview

**DevNook** (devnook.dev) — developer resource site, 1,000+ programmatic posts + 18 client-side browser tools, monetized via AdSense (deferred until 50k visitors/month).

**Stack:** Astro + Cloudflare Pages. Content is published by `../devnook_content_workspace/` via PAT.
**Repo:** `main` branch, Cloudflare Pages auto-deploy on every push.

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
| 8 — Subagent Architecture | ✅ | 2026-04-17 |
| 9 — Workspace Split | ✅ | 2026-04-25 |
| 10 — Cross-repo CI + Cleanup | ✅ | 2026-04-25 |

---

## Last Session (2026-05-27, #60)

**Status:** ✅ Pipeline B fully redesigned to keyword-first, cluster-driven 4-stage architecture. All agent files written. DB migrated. Ready to run Stage 0.

### What was done in #60

- **Pipeline B flipped to keyword-first** — root cause of Stage 1 failures (topics 5, 7) was topic-first seeding with bad seeds. New design: Stage 0 harvests a keyword pool → clusters → viable clusters become topics. Stages 2 and 3 unchanged.
- **`data/keywords.db` migrated** — added `keyword_pool` table (harvest universe) and `clusters` table (scored groups). Added `cluster_id` + `category` columns to existing `keyword_sets`. Migration is idempotent (CREATE TABLE IF NOT EXISTS + PRAGMA table_info guards).
- **`data/pipeline-b-seed-buckets.json` created** — 5 seed buckets, 3 fixed categories (`Comparisons`, `AI & Productivity`, `Tools & Workflows`), $0.50 DataForSEO cap.
- **`pipeline-b-stage0-harvest-cluster.md` created** — LOCAL ONLY. Harvest via DataForSEO MCP (`keyword_suggestions` + `related_keywords`), embed via Gemini `text-embedding-004`, cluster via `AgglomerativeClustering(metric='cosine', distance_threshold=0.18)`, score viability (`primary≥2 AND secondary≥6 AND longtail≥1`), write clusters to DB.
- **`pipeline-b-stage1-keywords.md` rewritten** — input is now `CLUSTER_ID` (not `TOPIC_ID`/seed). Reads `keyword_pool WHERE cluster_id=?`, selects 8–12 kws, synthesizes title/slug/description via Gemini Flash, writes `keyword_sets` + `keywords` rows, marks cluster `used`. No DataForSEO calls. No `topics.json` reads.
- **`pipeline-b-stage2-writer.md` minimal touch** — DB query updated to select `category` column; frontmatter now uses `subcategory` from cluster-inherited category. Body unchanged.
- **`pipeline-b-orchestrator-v2.md` rewritten** — counts viable clusters, auto-triggers Stage 0 top-up if low, selects top-N by volume, loops Stage 1→2→3 per cluster. `MAX_ARTICLES_PER_RUN` configurable (default 5). No `topics.json` reads.
- **CCR routine still disabled** (`trig_012dkTjBKiB8M9ASkKZ1c1Gk`) — do not re-enable until Stage 0 has run successfully and viable clusters exist.

### Current pipeline state

- Registry: ~74 published / 0 staged. Topics 1–4 done; topics 5–20 superseded by cluster-driven design.
- Pipeline B: **PAUSED** — all agent files ready, DB migrated, Stage 0 not yet run.
- Pipeline A: paused, cron commented out, 0 staged, redesign deferred.
- SEO rewrites: 46 language articles queued in `data/rewrite-queue.json`.

---

## Previous Session (2026-05-26, #59)

**Status:** ⚠️ Stage 1 failed for topics 5 and 7 (insufficient keywords). CCR routine DISABLED.

### What was done in #59

- **Stage 1 run for topic 5** (`ai-pair-programming-guide`, seed `"AI pair programming"`) — FAILED. Main term KD=50, longtail variants vol<140. Topic 5 marked `insufficient_keywords` (commit `97648f7`).
- **Stage 1 run for topic 7** (`ai-tools-technical-documentation`, seed `"AI documentation tools"`) — FAILED. Best candidate vol=480 (below threshold), KD=82 (unusable).
- **CCR routine disabled** (`trig_012dkTjBKiB8M9ASkKZ1c1Gk`, `enabled: false`).

---

## Older Sessions (2026-05-25, #57)

**Status:** ⚠️ Pipeline B Stage 1 keyword filtering broken — CCR routine paused pending redesign.

### What was done in #57

- **Local Stage 1 test run** — confirmed DataForSEO credentials (`admin@devnook.dev`) work locally (balance ~$50.46). CCR 403 errors in prior runs were the sandbox blocking outbound HTTP, NOT bad credentials.
- **Found 3 API bugs in `pipeline-b-stage1-keywords.md`**:
  1. `keyword_ideas/live` called with `"keyword": seed` (singular) — should be `"keywords": [seed]` (array)
  2. `keyword_ideas/live` included `filters` and `order_by` params — both rejected by current DataForSEO plan
  3. `related_keywords/live` included `filters` param — also rejected by current plan
- **Keyword relevance failure discovered** — even with API bugs fixed, Stage 1 returns off-topic keywords. Seed "prompt engineering" causes `keyword_ideas/live` to expand to root concept "engineering", returning industrial/civil engineering terms. The actual "prompt engineering" keyword has KD=99 (fails all filters). Stage 1 has no topic-relevance guard.
- **CCR routine `trig_012dkTjBKiB8M9ASkKZ1c1Gk` paused** (`enabled: false`) — do not re-enable until keyword workflow is redesigned.

### Keyword workflow redesign needed (next session)

The core problem: DataForSEO `keyword_ideas/live` is too broad for niche AI/developer topics — it expands seeds to root concepts and floods results with irrelevant high-volume terms. Stage 1 needs a fundamentally different approach. Options to consider:

- **Use `keyword_suggestions/live` as primary source** (not `keyword_ideas`) — suggestions stay closer to the original seed phrase
- **Seed with more specific phrases** — e.g. `"prompt engineering for developers"`, `"LLM prompting techniques"` instead of bare `"prompt engineering"`
- **Add topic-relevance guard** — after filtering, reject keywords that don't contain at least one word from the seed phrase (or a predefined synonym list per topic)
- **MCP-first approach** — use `mcp__dataforseo__dataforseo_labs_google_keyword_suggestions` directly in a local/manual workflow instead of CCR REST calls

**Do not re-enable the routine or run Stage 1 again until this is resolved.**

---

## Previous Session (2026-05-25, #56)

**Status:** ✅ Pipeline B redesigned to 3-stage modular architecture. New CCR routine armed for 14:00 UTC daily.

### What was done in #56

- **Pipeline B redesigned** — replaced monolithic 558-line `pipeline-b-orchestrator.md` with 3 independent stage agents + orchestrator v2:
  - `pipeline-b-stage1-keywords.md` — keyword research → `data/keywords.db` (strict: 8–12 kws, primary KD<30/vol≥500, secondary KD<40/vol≥1000; idempotent; retry with broader seeds; marks topic `insufficient_keywords` if unfillable)
  - `pipeline-b-stage2-writer.md` — reads keywords from DB, writes 2500–3500 word draft to `agents/content-team/drafts/<slug>.md`
  - `pipeline-b-stage3-qa-publish.md` — QA (2500-word hard floor + all other checks), npm build, git push, registry insert
  - `pipeline-b-orchestrator-v2.md` — coordinates stages, topic selection, B0 sandbox discovery, final verification
- **seo-writing-rules.md updated** — explicit Pipeline B 2500-word hard floor added (QA hard-fail); Pipeline A 1500-word floor documented
- **Old orchestrator deprecated** — `pipeline-b-orchestrator.md` header changed to DEPRECATED, points to v2
- **New CCR routine created** — `trig_012dkTjBKiB8M9ASkKZ1c1Gk`, cron `0 14 * * *` (14:00 UTC = 16:00 Malta CEST). Next fire: 2026-05-25T14:01Z. Manage: `https://claude.ai/code/routines/trig_012dkTjBKiB8M9ASkKZ1c1Gk`. Sources: both `syedjawad11/devnook-content` + `syedjawad11/devnook`.
- **Old routine gone** — `trig_01LD6ZaMZq3G6R5Aehz7xMHY` returned 404 (deleted or expired).

### What was done in #51–#55

- **#55**: Diagnosed CCR `auto_disabled_repo_access` (GitHub App lacked private repo access). User re-authorized both repos at `https://github.com/settings/installations`. Re-enabled routine for 16:15 UTC test fire — but old routine ID is now 404.
- **#51**: `javascript-closures` rewritten under modular-v1 system. Commit `721f748`.
- **#52**: External links gap fixed across all agents. Commit `b95c4a7`.
- **#53**: Pipeline B orchestrator v1 built. 20 topics queued in `data/pipeline-b-topics.json`. Topic 1 already done.
- **#54**: Registry cleaned, pipeline-b-orchestrator.md rewritten for REST API (no local MCP in CCR). First CCR routine created.

### Key learnings from #50–#56

- Always verify description length with Python `len()` — agent self-reported counts are unreliable.
- Any frontmatter value containing `: ` must be wrapped in double quotes to avoid YAML parse errors at build time.
- PowerShell here-strings use `@'...'@` syntax — bash-style `cat <<'EOF'` is invalid in PowerShell.
- Local npm MCPs (`npx dataforseo-mcp-server`) cannot be remote connectors — remote CCR routines must call REST APIs directly.
- Never use `[skip ci]` in devnook commit messages — Cloudflare Pages skips the build.
- No H1 in markdown body — `PostLayout.astro` renders `frontmatter.title` as `<h1>`; duplicate H1 flagged by Ahrefs.
- **CCR routines need GitHub App access to every source repo** — private repos fail silently with `auto_disabled_repo_access`. Re-authorize at `https://github.com/settings/installations` (no CLI workaround — standard PATs return 403 on installation endpoints).
- **`gh` PAT cannot manage GitHub App installations** — endpoints under `/user/installations` require an App-issued user-to-server token, not a standard PAT.

### Current pipeline state

- Registry: **~74 published / 0 staged / 14 rejected**; topics 1–3 done, topics 4–20 pending
- Pipeline A (`drip-publish.yml`): paused — cron commented out, 0 staged, redesign deferred
- Pipeline B: **PAUSED** — CCR routine `trig_012dkTjBKiB8M9ASkKZ1c1Gk` disabled 2026-05-25. Keyword workflow redesign required before re-enabling.
- SEO rewrites: 46 language articles queued in `data/rewrite-queue.json`

### Next session priorities (#58)

1. **Pipeline B keyword workflow redesign** — Stage 1 needs a new approach for topic-relevant keyword selection. See "Keyword workflow redesign needed" note above.
2. **Re-enable CCR routine** — only after Stage 1 redesign is tested locally and produces correct keywords. Routine ID: `trig_012dkTjBKiB8M9ASkKZ1c1Gk`.
3. **Continue SEO rewrites** — `@seo-optimizer` batch from `data/rewrite-queue.json` under modular-v1 system.
4. **Pipeline A redesign** — apply same 3-stage model (Stage 1 keywords, Stage 2 writer, Stage 3 QA+publish), enforce 1500-word minimum.
5. **Deferred** — FAQPage schema validation for `meta-tag-generator`, `readme-generator`, `sitemap-generator-from-url`.

### Deferred (do not do)

- **AdSense integration** — revisit only at 50k visitors/month
- **GSC ping** — `GOOGLE_SERVICE_ACCOUNT_JSON` secret never set in content workspace repo. Non-blocking — defer.
- Blog filter chips wiring (decorative only)
- Search bar wiring (`SearchBar.astro` parked)

---

## Key Paths

- Astro site: `src/`
- Layouts: `src/layouts/`
- Content: `src/content/` (written by content workspace publisher)
- Components: `src/components/`
- Global styles: `public/styles/` (NOT src/styles/)
- Tools: `src/pages/tools/[slug].astro` + `public/tools/*.html`
- Auto-internal-links plugin: `src/plugins/auto-internal-links/index.mjs`
- Related callouts plugin: `src/plugins/related-callouts/index.mjs`
- Dev subagent: `agents/subagent-prompts/builder.md`
- Dev skills: `agents/skills/astro-conventions.md`, `agents/skills/tool-build-patterns.md`
- SEO audit script: `scripts/seo_audit.py` — run with `D:\miniconda3\python.exe scripts/seo_audit.py`
- Trailing slash fixer: `scripts/fix_trailing_slashes.py` — run with `D:\miniconda3\python.exe scripts/fix_trailing_slashes.py`
- SEO audit log: `auditlog.md` — issues, verdicts, session fix plan (read before #37+)

---

## Dev Subagent

```
ORCHESTRATOR (Sonnet main session)
  └── Builder (Sonnet) — agents/subagent-prompts/builder.md
      Handles: Astro edits, new tools, npm run build verification
```

Spawn with: `Agent(prompt=open('agents/subagent-prompts/builder.md').read(), ...)`

**Workflow B** — new tool: Orchestrator → Builder → review + commit
**Workflow C** — bug fix: Orchestrator → Builder → review + commit

---

## Important Decisions Log

> Live guardrails — if you forget these, you will break something.

| Decision | Impact |
|----------|--------|
| No Tailwind | All styles in `tokens.css` custom properties |
| All tools client-side only | 18 tools, no Workers, no AI-powered tools |
| Static output (not hybrid) | `output: 'static'`, no adapter — satori crashes Workers runtime |
| Global CSS in `public/styles/` not `src/styles/` | Astro only copies `public/` to `dist/`; absolute `/styles/*` refs need public/ |
| PostCard prop is `href` not `slug` | All 5 call sites use `href`; never rename to slug/url/path |
| `tools/[slug].astro` uses `import.meta.glob` | Dynamic `await import()` crashes Vite static analysis |
| Never call `build-tool.py build_tool()` for existing tools | Writes page that collides with dynamic route — use `generate_seo_explainer()` + `write_file()` |
| Auto internal links plugin (rehype, build-time) | `src/plugins/auto-internal-links/index.mjs`; `autoAnchors: true`; `devnookUrlBuilder` required — language concept URLs use `frontmatter.language`+`frontmatter.concept`, NOT filename |
| Use `@astrojs/sitemap@3.2.1` not custom | Custom sitemap was broken; v3.7+ incompatible with Astro 4.x. Current version generates `sitemap-0.xml` (0-indexed) — do not expect `sitemap-1.xml` |
| Related posts auto-derived at render time (session 27) | `src/layouts/PostLayout.astro` builds the related list from `getCollection()` using a language/category/tags score — never from a hand-written `## Related` markdown section. `frontmatter.related_posts` is unused; leave as `[]`. |
| Linker retired (session 25) | Replaced by `src/plugins/auto-internal-links/index.mjs` (build-time rehype plugin). `link_utility.py` kept dormant in devnook root — delete after stable operation. |
| Content pipeline is external | No registry, no staging, no publish scripts in this repo. `src/content/` is written by `../devnook_content_workspace/agents/publish/publish.py` via cross-repo git push. |
| Language post URLs must use `concept`, not filename | Content pipeline agents historically guessed `/languages/{lang}/{filename-slug}` in body prose. Correct path is always `/languages/{lang}/{concept}` from registry. `publish.py` now has `validate_language_links()` guard that skips files with filename-based links at publish time. `link_utility.py._url_for_row()` is already correct — the bug is agents bypassing it. |
| Auto-internal-links plugin covers all categories | `src/plugins/auto-internal-links/index.mjs` scans the full `contentDir` via `fast-glob` — all of `guides`, `blog`, `cheatsheets`, `languages`. Not language-only. `devnookUrlBuilder` note only describes URL *generation* for language posts. |
| Related callouts plugin (session 32) | `src/plugins/related-callouts/index.mjs` — build-time rehype plugin injects up to 3 `<aside class="related-callout">` nodes at interior H2 boundaries. Scoring mirrors PostLayout.astro. CSS in `public/styles/global.css` (not scoped). Per-post opt-out: `excludeRelatedCallouts: true` in frontmatter. |
| No H1 in markdown body (session 42) | `PostLayout.astro` renders `frontmatter.title` as the page `<h1>`. Any `# Title` line in the body creates a second `<h1>` — Ahrefs flags as "Multiple H1 tags". Content pipeline files patched: `writer.md`, `antigravity-qa.md`, `seo-writing-rules.md`. Never write or instruct agents to write a body H1. |
| Never use `[skip ci]` in devnook commit messages (session 43) | Cloudflare Pages honors `[skip ci]` and skips the build — so drip-publish commits would never deploy. The `[skip ci]` in `drip-publish.yml` line 78 is intentional (content-workspace side, prevents workflow retriggering itself). The devnook-side commit in `publish.py` must NOT include it. |

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...       # Builder subagent (if needed for tool work)
```

---

## How to Run

```bash
# Dev server
npm run dev

# Production build (always verify before committing)
npm run build

# Preview production build
npm run preview
```
