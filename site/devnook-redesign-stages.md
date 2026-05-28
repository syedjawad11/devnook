# DevNook Redesign — Staged Execution Plan

> Source: `devnook-redesign-plan.md` (2026-05-28).
> Sequencing choice: cleanup-first, merge-later.
> Execute one stage at a time. Each stage is independently verifiable and safe to stop after.

---

## Stage 1 — Security hardening
**~30 min | Repo: devnook_content_workspace + devnook | No dependencies**

**Goal:** Close the two open security issues before any other work.

**Actions:**
1. Remove `"claudeCode.allowDangerouslySkipPermissions": true` from `devnook/.vscode/settings.json`.
2. Check if `devnook_content_workspace/.claude/pipeline-b-creds.env` is tracked by git:
   - If tracked: `git rm --cached .claude/pipeline-b-creds.env`, add `*.env` and `.claude/*.env` to `devnook_content_workspace/.gitignore`, commit with message "security: remove tracked creds file". History purge deferred to Stage 8 (merge step).
   - If untracked: confirm it is already in `.gitignore`; if not, add it.
3. User action (not Claude): rotate the DataForSEO password in the DataForSEO dashboard. Assume the committed pair is compromised.

**Done when:**
- `devnook/.vscode/settings.json` no longer contains `allowDangerouslySkipPermissions`.
- `devnook_content_workspace/.claude/pipeline-b-creds.env` not tracked by git.
- DataForSEO password rotated (user confirms).

---

## Stage 2 — Dead code purge
**~1 hour | Repo: devnook_content_workspace | No dependencies**

**Goal:** Delete three generations of dead pipeline code so later stages work in a clean tree.

**Files to delete from `devnook_content_workspace`:**

*Gen 1 Python (agents/content-team/):*
- `run-pipeline.py`, `seo_optimizer.py`, `staging.py`, `link_utility.py`, `fix_broken_links.py`, `registry.py`
- `tests/` folder (tests for deleted code)
- `registry-schema.sql`

*Scratch scripts at root:*
- `stage0_final_check.py`, `stage0_inspect.py`, `stage0_inspect2.py`, `stage0_migration.py`, `stage0_process.py`

*Gen 2 retired subagent prompts:*
- `agents/subagent-prompts/` folder (all 5 files: antigravity-qa.md, ingest.md, planner.md, publisher.md, writer.md)

*Dead Gen 3 agents (.claude/agents/):*
- `pipeline-b-orchestrator.md` (deprecated v1, 557-line)
- `antigravity-qa.md`
- `content-ingest.md`

*Superseded data files:*
- `data/pipeline-b-topics.json` (superseded by cluster design, per CLAUDE.md TODO #4)

**Pre-delete verification:** Grep for any live file that imports or references each target before deleting.

**Done when:**
- Deleted files gone; `git status` clean after commit.
- `grep -r "antigravity" .claude/agents/` → zero results.
- `grep -r "from agents.content-team" .` → zero results.

---

## Stage 3 — Database housekeeping
**~1-2 hours | Repo: devnook_content_workspace | No dependencies**

**Goal:** One database, correct row statuses, readable diffs.

**Actions:**
1. **Fix keyword_set_id=4 bug**: `UPDATE keyword_sets SET status='used' WHERE id=4` in `data/keywords.db`.
2. **Consolidate to one DB:** Migrate all tables from `data/keywords.db` (`keyword_pool`, `clusters`, `keyword_sets`, `keywords`) into `agents/content-team/registry.db`. Then move the unified DB to `data/registry.db`.
3. Drop the now-unused `keywords` table inside the old `registry.db` if it exists separately.
4. Update all agent .md files that reference `data/keywords.db` or `agents/content-team/registry.db` to point to `data/registry.db`.
5. Commit `data/sqldump.sql` (schema + data dump) alongside the DB for readable git diffs.
6. Update `.gitignore` if the DB itself should be excluded.

**Agent files needing DB path update:**
- `.claude/agents/pipeline-b-stage0-harvest-cluster.md`
- `.claude/agents/pipeline-b-stage1-keywords.md`
- `.claude/agents/pipeline-b-stage2-writer.md`
- `.claude/agents/pipeline-b-stage3-qa-publish.md`
- `.claude/agents/pipeline-b-orchestrator-v2.md`
- `agents/publish/publish.py`

**Done when:**
- Single DB at `data/registry.db`.
- `PRAGMA table_info` shows all expected tables.
- All agent file references point to the new path.
- `keyword_set_id=4` has `status='used'`.

---

## Stage 4 — Doc cleanup
**~1 hour | Repo: devnook | No dependencies**

**Goal:** Clear the devnook root of noise; every doc in its right place.

**Create `devnook/docs/` and move into it:**
- `SOP.md`, `auditlog.md`, `session-history.md`, `devnook-site-updates.md`, `skill-creator.md`
- `development_stages/` (whole folder)
- `archives/` (whole folder)
- `devnook-redesign-plan.md` (source doc)
- `pipelineB.md`, `devnook_content_pipeline.md`, `pipeline-b-keyword-first-prompt.md`, `handoff.md`, `workspace_rules.md`

**Add to `devnook/.gitignore`:**
- `fix_frontmatter.py`
- `scratch_clean.py`

**Devnook root after cleanup:** `CLAUDE.md`, `astro.config.mjs`, `tsconfig.json`, `package.json`, `package-lock.json`, `README.md`, `.gitignore`, `.env.example`, `.mcp.json`, `src/`, `public/`, `agents/`, `docs/`, `scripts/`.

**Done when:** Root is clean; `docs/` contains the archive; build still passes.

---

## Stage 5 — CLAUDE.md rewrite
**~1-2 hours | Repo: devnook + devnook_content_workspace | Depends on: Stage 4**

**Goal:** One lean `CLAUDE.md` per repo (~1.2k tokens each); zero Antigravity references in live docs.

**Actions:**
1. Rewrite `devnook/CLAUDE.md`: keep key paths, decisions table, how-to-run, env vars, subagent pattern. Remove full session history, per-session blocks, all Antigravity mentions. Point to `docs/ARCHITECTURE.md`.
2. Write `devnook/docs/ARCHITECTURE.md` with detailed stable content (pipeline overview, stage flow, registry schema, profile system).
3. Rewrite `devnook_content_workspace/CLAUDE.md` similarly: lean operational guide, no Antigravity references.

**Done when:**
- Both `CLAUDE.md` files under ~1.2k tokens each.
- `grep -ri "antigravity" .` in live files → 0 results.

---

## Stage 6 — Standards lock
**~1-2 hours | Repo: devnook | Depends on: Stage 4**

**Goal:** Build fails fast on bad content; slug/language conventions locked.

**Files:** `devnook/src/content/config.ts`, `devnook/src/pages/languages/[lang]/[concept].astro`

**Actions:**
1. Change `language: z.string()` → `z.enum(['python','javascript','typescript','go','rust','java','csharp','php','ruby','swift','kotlin','cpp'])` in `config.ts`.
2. Add `concept: z.string()` validation (lowercase-only check).
3. Add `linkAnchors: z.array(z.string()).optional()` to `languagesCollection`, `guidesCollection`, `blogCollection` schemas.
4. Enforce lowercase on `lang` and `concept` params in `getStaticPaths`.
5. Add slug convention to `docs/ARCHITECTURE.md`.

**Verification:** Temporarily add a test file with `language: "google-forms"` → `astro build` must fail. Revert; build must pass.

**Done when:** Build hard-fails on bad `language` value; `linkAnchors` field accepted in schema.

---

## Stage 7 — Internal linking rebuild
**~half day | Repo: devnook | Depends on: Stage 6 (linkAnchors in schema)**

**Goal:** Fix near-zero internal link insertions; links from frontmatter, not fuzzy title matching.

**File:** `devnook/src/plugins/auto-internal-links/index.mjs`

**Actions:**
1. Rewrite plugin to key off `linkAnchors` frontmatter field instead of derived-from-title/slug strings.
2. Fix 6-char bare-language exclusion bug blocking `go`/`java`/`rust`/`swift`.
3. Add `linkAnchors` to existing language posts via automated frontmatter batch update.
4. Test with `dryRun: true`: count insertions before vs. after.

**Done when:**
- `dryRun` log shows meaningful link insertions (not near-zero).
- `go`/`java`/`rust`/`swift` anchors no longer excluded.
- Full `astro build` passes.

---

## Stage 8 — Repo merge (monorepo)
**~half day | Both repos | Depends on: Stages 1–7**

**Goal:** One private repo; Cloudflare Pages building from `site/` subdirectory; leaked cred purged from history.

**Target structure:**
```
devnook/  (private, one repo)
├── site/          ← former devnook Astro site
├── pipeline/      ← former devnook_content_workspace
├── docs/          ← consolidated docs
└── CLAUDE.md
```

**Actions:**
1. Merge `devnook-content` history into `devnook` via `git subtree` or `git filter-repo`.
2. Move devnook files into `site/`; content workspace files into `pipeline/`.
3. Consolidate `docs/` from both repos.
4. Write one root `CLAUDE.md`.
5. Reconfigure Cloudflare Pages: build root = `site/`, output dir = `site/dist`.
6. Run `git filter-repo` to purge `.claude/pipeline-b-creds.env` from history.
7. Archive (do not delete) both old repos for one week minimum.

**Done when:**
- Clean Cloudflare deploy from `site/` subdirectory.
- `git log --all --full-history -- "*.env"` → no cred file in history.
- Both old repos archived.

---

## Stage 9 — Pipeline core rebuild
**~1-2 days | Repo: pipeline/ | Depends on: Stage 8 + Stage 3**

**Goal:** One shared pipeline tail (outline → write → link → qa → publish); every stage idempotent.

**Each stage in `pipeline/core/` exposes `run() -> dict`** with keys: `processed`, `written`, `rejected`, `model`, `tokens`, `cost`.

**QA requirements:** schema enum check, word floor (2500 editorial / 1500 language), link validity, dup check, cluster-collision guard.

**Fix GSC ping:** set `GOOGLE_SERVICE_ACCOUNT_JSON` secret (currently logs `gsc_submitted: false` every run).

**Status lifecycle:** `queued → outlined → drafted → linked → approved → published` (or `rejected`).

**Done when:** End-to-end dry run on one seeded topic produces a valid markdown file; no stage blocked by prior stage failure.

---

## Stage 10 — Language stage-0 (revive volume engine)
**~1 day | Repo: pipeline/ | Depends on: Stage 9**

**Goal:** Keyword-validate ~600 concept×language seeds, build ordered queue.

**Actions:**
1. Query DataForSEO `keyword_suggestions/live` per concept×language cell.
2. No hard KD/Vol gate — only "any demand at all" sanity check.
3. Attach opportunity score; order queue high-opportunity-first.
4. Remove "never queue languages" ban from planner/writer agents.

**Done when:** `--profile language --limit 5` produces 5 ordered briefs with canonical keyword + opportunity score.

---

## Stage 11 — Editorial stage-0 (gap-finding)
**~1-2 days | Repo: pipeline/ | Depends on: Stage 9**

**Goal:** Harvest editorial keyword candidates from competitors + combinatorial matrices.

**Seed sources:** freecodecamp, dev.to, css-tricks, smashing, LogRocket, Kinsta, Builder.io; GSC striking-distance queries; language×language / tool×tool / format×format matrices.

**Keyword gates:**
- Primary: `Vol 100–800, KD < 15`
- Secondary: `Vol > 500, KD < 30`
- Fallback ceiling: `KD < 35` (queued last, tagged)
- Zero-data → low-confidence bucket (manual review)

**Done when:** Harvester degrades gracefully on rate-limit; produces clustered topics with metrics.

---

## Stage 12 — Content triage
**~ongoing | Repo: site/ | Depends on: Stages 6 + 7**

**Goal:** Clean the corpus; don't blindly rewrite.

**Categories:**
- **Kill:** taxonomy junk (`google-forms`, Sheets/Colab masquerading as language posts). Delete + 301 redirect.
- **Merge:** cannibalization pairs. Keep stronger URL; redirect weaker.
- **Rewrite:** on-topic, thin, salvageable → pipeline tail.
- **Gate thin hubs:** `/languages/{lang}/` hidden from nav until ≥5 posts.

**Done when:** No hub <5 posts in nav; no two posts targeting same cluster; all 301 redirects tested.

---

## Stage 13 — Menu & taxonomy reorg
**~1 hour | Repo: site/ | Depends on: Stage 12**

**Goal:** Fewer, fuller nav sections. No thin hubs.

**Proposed nav:** Languages · Guides · Tools · Blog

**Rules:**
- Cheatsheets folded into Languages/Guides (not top-level until ≥5 entries).
- Comparisons under relevant hubs + Blog.
- Blog subcategories: Building with LLMs, AI Concepts Explained, AI Dev Tooling, Comparisons.
- Hub appears in nav only once it clears ≥5 posts.

**Done when:** Clean build; no thin hubs in nav; Astro sitemap reflects new structure.

---

## Execution order summary

| Stage | Name | Repo | Est. time |
|---|---|---|---|
| 1 | Security hardening | both | 30 min |
| 2 | Dead code purge | content_workspace | 1 hr |
| 3 | Database housekeeping | content_workspace | 1–2 hr |
| 4 | Doc cleanup | devnook | 1 hr |
| 5 | CLAUDE.md rewrite | both | 1–2 hr |
| 6 | Standards lock | devnook | 1–2 hr |
| 7 | Internal linking rebuild | devnook | half day |
| 8 | Repo merge | both | half day |
| 9 | Pipeline core rebuild | pipeline/ | 1–2 days |
| 10 | Language stage-0 | pipeline/ | 1 day |
| 11 | Editorial stage-0 | pipeline/ | 1–2 days |
| 12 | Content triage | site/ | ongoing |
| 13 | Menu & taxonomy reorg | site/ | 1 hr |

**Stages 1–7:** Work in existing two-repo layout. Safe to do in any order within each repo.
**Stage 8:** Repo merge — after Stages 1–7 so you migrate a clean tree.
**Stages 9–13:** Build on merged monorepo and locked standards.
