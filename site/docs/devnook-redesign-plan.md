# DevNook — Content System & Repo Redesign

> **Date:** 2026-05-28
> **Purpose:** Single source of truth for the content-pipeline rebuild and repo consolidation. Supersedes the multi-pipeline planning in `project-summary`, `new-project-summary`, `new_content_plan`, and the Antigravity handoff. Built on the `devnook-audit-2026-05-28` findings + decisions taken in the redesign session.
> **Principle:** Every phase is independently executable, has its own verification, and can be reverted without unwinding later work. Do them roughly in order — later phases assume earlier ones — but none should leave the system in a broken intermediate state.

---

## 0. Locked decisions (read first)

These are settled; the phases below implement them. If one of these changes, the affected phase changes with it.

1. **One repo, one pipeline core, three profiles.** No separate codebases per content type. A single pipeline whose only per-type difference is *stage 0* (where topics come from) and which *data slice* a run touches. Profiles: `language`, `editorial`, `existing` (rewrite).
2. **Context isolation comes from data scoping, not code duplication.** A `language` run reads only language files/rows; an `editorial` run reads only editorial files/rows. One registry, every row tagged with `profile`; every query filters by it. This is what kept you wanting three repos — it's solved at the data layer.
3. **Keyword-first, always.** Discover/validate keywords → cluster → topic → outline → write → link → QA → publish. No more content seeds without keyword validation.
4. **Language = coverage play.** Per concept×language cell, run keyword research and pick the *best-available* volume/KD phrasing as canonical (drives slug + H1 + title). No hard KD/Vol gate — only a "does any demand exist at all" check. Metrics decide *build order*, not inclusion. This revives the volume engine, which currently has no producer.
5. **Editorial = gap-finding play, with primary/secondary keyword tiers.**
   - **Primary keyword** (the post is built around it — title, H1, URL, meta): `Vol 100–800, KD < 15`. Must clear this for the post to be written.
   - **Secondary keywords** (supporting terms woven into H2s/body for extra capture + topical depth): `Vol > 500, KD < 30`. Upside, not what the post bets on.
   - **Fallback:** if no primary clears KD<15, allow up to **KD < 35 (hard ceiling)**. But flag these as long-horizon, queue them *after* all KD<15 wins, and tag them so flat early performance isn't mistaken for failure — they're 6+-month bets on a low-authority domain. If nothing clears even KD<35 → drop, or send to the **zero-data → low-confidence bucket** (when DataForSEO returns *no* data, which ≠ no opportunity) for manual review.
   - Rejection still = drop; the gate is the feature. Tighten every number as DR rises.
6. **Registry is the URL authority.** Internal links come from DB queries, not from scanning other posts' bodies/titles/slugs. This fixes both the broken internal linking *and* the context-bloat worry in one move.
7. **Editorial seed sources:** DataForSEO competitor harvesting (workhorse) + GSC striking-distance queries (compounding, once impressions exist) + combinatorial entity matrices (comparisons, tool-adjacent). Community APIs (Reddit / Stack Exchange / HN Algolia / Dev.to) as an enrichment layer later.
8. **Blog/AI reframed to the developer-AI lane.** Drop the saturated, off-lane, AdSense-mismatched roundup/launch-news direction. Pillars: **Building with LLMs** (dev how-to), **AI Concepts Explained** (developer-flavored "what is X"), **AI Dev Tooling** (on-lane tools only), plus **Comparisons** (combinatorial). Skip "best AI image/video/social tools," "best courses," and "Model X launches."

---

## Phase 0 — Safety & cleanup (do this first; no dependencies)

**Goal:** stop the bleeding, merge the repos, delete the cruft. Nothing here writes new content logic — it removes risk and noise so later phases happen in a clean tree.

### 0.1 Rotate the leaked DataForSEO creds (today, before anything else)
- Reset the DataForSEO password in their dashboard. Assume the committed pair is compromised.
- `git rm --cached .claude/pipeline-b-creds.env`; add `*.env` and `.claude/*.env` to `.gitignore`; commit.
- Move creds to a real secret store (GitHub Actions secret for CI; the CCR routine's own env/secret mechanism otherwise).
- Later cleanup: purge from history with `git filter-repo`. (Rotation closes the exposure; history purge is hygiene.)
- Remove `claudeCode.allowDangerouslySkipPermissions: true` from `devnook/.vscode/settings.json`.

### 0.2 Merge `devnook` + `devnook-content` into one repo
- Target layout (monorepo):
  ```
  devnook/                     ← one repo (set to PRIVATE; site is public, repo needn't be)
  ├── site/                    ← the Astro site (was devnook)
  │   └── src/ ...
  ├── pipeline/                ← content pipeline (was devnook-content)
  │   ├── core/                ← shared tail: outline, write, link, qa, publish
  │   ├── profiles/            ← language/, editorial/, existing/ (stage-0s only)
  │   ├── .claude/agents/      ← live subagents
  │   ├── data/                ← the ONE database (see Phase 0.4)
  │   └── publish.py, gsc_ping.py
  ├── docs/                    ← consolidated docs (see 0.5)
  └── CLAUDE.md                ← lean root file
  ```
- **Reconfigure Cloudflare Pages**: set the build root/working directory to `site/` and the output dir accordingly. Verify a deploy succeeds before deleting the old repo.
- **History note:** merging brings `devnook-content` history (incl. the leaked-cred commit) into the new repo. Do 0.1's rotation first; do the `filter-repo` purge after the merge so you only clean once.
- **Verify:** clean `astro build` from `site/`, successful Cloudflare deploy, both old repos archived (not deleted) until the new one is stable for a week.

### 0.3 Prune the three pipeline generations to one
Delete entirely:
- **Gen 1 (orphaned Python/Gemini):** `run-pipeline.py`, `seo_optimizer.py`, `staging.py`, `link_utility.py`, `fix_broken_links.py`, `registry.py` — nothing imports these except `publish.py → gsc_ping`. Preserve `gsc_ping` (move into `pipeline/`); delete the rest.
- **Gen 2:** the whole `agents/subagent-prompts/` folder (retired in session #49, duplicates `.claude/agents/`).
- **Dead Gen 3 agents:** the deprecated `pipeline-b-orchestrator.md` (557-line v1), both `antigravity-qa.md`, and `content-ingest.md` (all Antigravity-dependent; Antigravity is retired).
- **Keep (this becomes the core in Phase 3):** `pipeline-b-orchestrator-v2`, `stage0/1/2/3`, `stage23-runner`, `seo-optimizer`, `gsc-analyst`, `publish.py`.
- **Verify:** grep the import graph + agent references; confirm nothing live points at a deleted file before committing.

### 0.4 Consolidate the databases
- **Consolidate to one DB (decided).** Fold `data/keywords.db` tables (`clusters`, `keyword_sets`, `keyword_pool`, `keywords`) into `registry.db` so there's a single store — fewer moving parts, no hand-rolled cross-DB joins.
- Drop the now-unused `keywords` table inside `registry.db`.
- For diffability of binary-in-git: commit a `sqldump.sql` alongside the DB so daily CCR commits produce readable diffs.
- **Verify:** `PRAGMA table_info` on the surviving DB(s); one documented owner per table.

### 0.5 Kill doc sprawl + de-Antigravity the docs
- Move `SOP.md`, `auditlog.md`, `session-history.md`, `devnook-site-updates.md`, `development_stages/`, `archives/`, `skill-creator.md` into `docs/`. `.gitignore` scratch scripts (`scratch_clean.py`, `fix_frontmatter.py`, etc.).
- Rewrite both `CLAUDE.md` files into **one lean root `CLAUDE.md`** (~1.2k tokens) that points to a stable `docs/ARCHITECTURE.md`. Remove every live Antigravity reference (Workflow A2, "Languages owned by Antigravity," ingest source, "Antigravity QA never rejects") — these will mislead future sessions.
- **Verify:** `CLAUDE.md` under target token budget; no "antigravity" string in any live (non-archived) doc.

---

## Phase 1 — Standards lock (must precede rewrite & linking)

**Goal:** make the system reject junk at the wall instead of shipping it. These are the contracts everything downstream depends on.

- **Schema enum (site repo, `src/content/config.ts`):** change `language: z.string()` → `z.enum([...12 canonical slugs...])` (python, javascript, typescript, go, rust, java, csharp, php, ruby, swift, kotlin, cpp). Now the build **hard-fails** on junk like `language: "google-forms"` instead of rendering a fake hub. Lint `concept` against a known list too.
- **Lowercase enforcement:** lowercase `language`/`concept` in `getStaticPaths` (`[lang]/[concept].astro`) *or* enforce lowercase in the schema, so the page path can never diverge from the auto-link URL (latent 404 fix).
- **Slug convention (decided):** slug = the canonical keyword phrase with the **language token stripped**, kebab-cased. E.g. canonical "how to reverse a list in python" → `languages/python/how-to-reverse-a-list.md` → `/languages/python/how-to-reverse-a-list`. The language already lives in the path (`[lang]/[concept]`), so repeating it (`python-...` or `...-in-python`) is redundant and reads as keyword-stuffing. Definitional concepts use the bare noun (`list-comprehension`, `decorators`). Slug derives deterministically from the canonical keyword chosen in stage 0. Uniqueness is per-language-folder; **the registry keys on the full path**, so `reverse-a-list` can exist under multiple languages. Normalize all existing files to this; fix misleading filenames (e.g. a Go post named `...google-sheets.md`).
- **`linkAnchors` frontmatter spec:** define the field — an array of short concept phrases (e.g. `["list comprehension", "pattern matching"]`) sourced from registry concepts, never derived from filenames or titles. This is the input to Phase 2.
- **One lifecycle:** reconcile the status flow. Either route Pipeline-B posts through `drafted → ... → published` or formally document that direct-`published` insert is the path and retire unused statuses (`optimized`). Reconcile the "no API-based Python LLM calls" rule with reality (stage0/stage1 do call Gemini) — update the rule, don't pretend.
- **Verify:** `astro build` fails on a deliberately-bad `language` value; passes on clean content.

---

## Phase 2 — Internal linking rebuild (highest SEO leverage)

**Goal:** fix the root cause of "internal linking not performing" — and incidentally kill the context-bloat problem, since links now come from the DB, not from reading other posts.

- Writer emits `linkAnchors` (short concept phrases from registry) into frontmatter.
- Rewrite `devnook/src/plugins/auto-internal-links/index.mjs` to key off `linkAnchors` instead of full cleaned titles + humanized slugs (those long exact strings never appear verbatim in other posts, which is why almost nothing inserts today). Fix the inconsistent 6-char bare-language-name gate (`go`/`java`/`rust`/`swift` currently excluded).
- Stop hand-authoring `/languages/...` links in prose. The deterministic linker owns internal links. `validate_language_links()` in `publish.py` drops from primary mechanism to a belt-and-suspenders check.
- **Verify:** run `astro build` with the plugin's `dryRun: true`; count actual insertions per page before vs. after. Expect a large jump from near-zero.
- **Failure isolation:** linking is a build-time plugin + a frontmatter field; if it misbehaves, posts still render — links just don't insert. No publish blocked.

---

## Phase 3 — Pipeline core (the shared tail, built once)

**Goal:** one set of stages used by all three profiles. Each stage independently runnable and idempotent.

Shared stages (each reads a `profile`-tagged, status-filtered queue from the one registry):

| Stage | Input | Output | Notes |
|---|---|---|---|
| `outline` | topic + keyword cluster + template variant | structured outline | round-robin template variant per content type |
| `write` | outline + brief + style system | markdown + frontmatter (incl. `linkAnchors`) | fresh subagent; reads ONLY brief + 1 template + style file |
| `link` | post + registry | post with internal links | DB query for targets; never reads other post bodies |
| `qa` | post | approved / rejected(+reason) | schema enum check, word floor, link validity, dup + cluster-collision check |
| `publish` | approved post | live + sitemap + GSC ping | see GSC fix below |

- **Fix the GSC ping (audit 2.2):** set `GOOGLE_SERVICE_ACCOUNT_JSON` so `publish.py` actually submits new URLs to the Indexing API. Every run currently logs `gsc_submitted: false` — you're leaving the biggest indexing accelerant unused at exactly the stage it helps.
- **Cluster-collision guard:** QA refuses a topic whose `cluster_id` is already covered → prevents re-creating cannibalization pairs.
- **Run contract:** every stage exposes the same `run() -> dict` shape (processed / written / rejected / model / tokens / cost) so the orchestrator wires them uniformly and `--steps` can run any subset.
- **Verify:** run `outline,write,link,qa` on a single seeded topic end-to-end in a dry directory; inspect the produced markdown.
- **Failure isolation:** any stage can be re-run on its queue without re-running prior stages; status field makes it resumable.

---

## Phase 4 — Profile stage-0s (the three entry points)

Each is a thin front-end that drops `profile`-tagged briefs into the shared queue. Build 4A first (revives the dead volume engine), then 4B, then 4C.

### 4A — `language` stage-0 (revives the volume engine)
- Input: the concept×language matrix. **Keep the existing ~600 seeds** — they are your *topic universe*, not validated keywords.
- For each cell: query DataForSEO for the phrasing cluster → pick best volume/KD variant as canonical → attach opportunity score.
- **No gate.** Only a "does any demand exist at all" sanity check. Opportunity score orders the build queue (high-opportunity concepts first).
- Lift the "never queue languages" ban from planner/writer (delete the bar; it's why the engine has no producer).
- **Verify:** run `--profile language --limit 5`; expect 5 briefs with canonical keyword + opportunity score, ordered, none rejected for low KD/Vol.

### 4B — `editorial` stage-0 (gap-finding)
- **Seed harvester** (independently runnable sub-step) pulls candidates from: DataForSEO competitor domains (freecodecamp + /news, dev.to, css-tricks, smashing, LogRocket, Kinsta, Builder.io blogs), GSC striking-distance queries (pos ~5–20, once available), and locally-generated combinatorial matrices (Comparisons: language×language, tool×tool, format×format, db×db; tool-adjacent: each tool → explainer cluster). Tag each candidate with its source; dump to `keywords.db`; dedupe.
- Then: expand → **loosened gate (`Vol 100–800, KD<15`)** → cluster → one canonical topic per cluster.
- Zero-data candidates → low-confidence bucket (manual review), not auto-write.
- **Blog pillars** seeded here: Building with LLMs, AI Concepts Explained, AI Dev Tooling, Comparisons.
- **Verify:** harvester degrades gracefully — if a competitor pull 403s or an API rate-limits, the stage proceeds on whatever succeeded (no blocking). Run produces clustered topics with metrics attached.

### 4C — `existing` stage-0 (rewrite) — build LAST
- Input: a published post. Re-check its target keyword + pull GSC data → triage into **keep / merge / kill / rewrite**.
- Only `rewrite` enters the shared tail (as a "rebuild around this keyword" brief). `merge` → redirect; `kill` → delete + 301.
- **Sequenced after Phases 1 + 2** so you rewrite once against final standards, not twice.

---

## Phase 5 — Existing content triage & rewrite (~47–50 posts)

**Goal:** clean the corpus, don't blindly rewrite it.

- **Kill:** taxonomy junk (`google-forms`, Google Sheets/Colab posts masquerading as language posts). Delete + 301.
- **Merge / canonicalize:** cannibalization pairs (`cpp/c-handle-exception` vs `how-to-catch-error-in-cpp`; `python-file-handling-tutorial` vs `file-handling-in-google-colab`).
- **Rewrite:** on-topic, thin, salvageable posts → through 4C → shared tail.
- **Gate thin hubs:** don't expose a `/languages/{lang}/` hub until it has ≥5 posts (current counts: js 8, py 7, java 6, cpp 5 are fine; csharp 1, ruby 1, swift 1 are not — hold those hubs).
- **Verify:** no hub with <5 posts is linked from nav; no two live posts target the same cluster.

---

## Phase 6 — Menu & taxonomy reorg

**Goal:** fewer, fuller sections — fragmentation dilutes topical authority on a small site.

- Current: Languages · Guides · Cheatsheets · Tools · Blog(AI & Productivity, Comparisons).
- Proposed: **Languages · Guides · Tools · Blog**, with **Cheatsheets folded in as a content type** surfaced within Languages/Guides (not its own top-level hub until it has enough entries), and **Comparisons** living under the relevant language/guide hubs rather than only under Blog.
- Blog subcategories settle to the developer-AI pillars + Comparisons.
- Governing rule everywhere: a hub goes in the nav only once it clears ≥5 posts.
- *(This one is partly preference — treat the structure as a recommendation, adjust to taste, but hold the "no thin hubs in nav" rule.)*

---

## Phase 7 — Claude Code / token hygiene (cross-cutting)

Mostly delivered by earlier phases; called out so it's deliberate.

- **Biggest win is Phase 0.3** — three pipeline generations meant three mental models loaded across sessions, which bred the desyncs and firefights. Deleting them is the main token saving.
- **Lean `CLAUDE.md` → `ARCHITECTURE.md`** (Phase 0.5); per-stage subagent prompts kept under ~500 tokens each.
- **Keep research deterministic:** DataForSEO calls, clustering, harvesting are plain Python that *write to the DB*. Agents query results; they never ingest raw research into context.
- **Data scoping (decision 0.2)** means any run's context surface = one profile's slice. A language run never loads an editorial file.
- **Operating discipline:** stop sessions at ~70–75% context; route routine/deterministic work out of Claude Code; use plan mode before implementing; batch related edits.

---

## Suggested sequencing

1. **Today:** 0.1 (rotate creds) + 0.2 (repo merge).
2. **This week:** rest of Phase 0 (prune, DB, docs) → Phase 1 (standards). Everything depends on a clean tree + locked contracts.
3. **Next:** Phase 2 (internal linking) — highest SEO leverage, prerequisite for a worthwhile rewrite.
4. **Then:** Phase 3 (core) → Phase 4A (revive language engine) → 4B (editorial).
5. **Then:** Phase 5 (triage/rewrite via 4C) once standards + linking are locked.
6. **Anytime after Phase 1:** Phase 6 (menu).
7. **Continuous:** Phase 7 discipline.

---

## Out of scope / deferred

- Affiliate monetization (you're on AdSense; revisit only if the model changes).
- Community-API seed enrichment (Reddit/SO/HN/Dev.to) — add after DataForSEO + GSC seeds are solid.
- Re-adding any AI-tool-roundup / model-launch-news direction — explicitly dropped (saturated, off-lane, freshness treadmill).
- SoftwareApplication schema on tools — only once genuine reviews exist (prior decision stands).

## Resolved decisions (settled 2026-05-28)

1. **DB:** consolidate to one (`registry.db`). ✅
2. **Merged repo visibility:** private. ✅
3. **Slug convention:** canonical keyword minus language token, kebab-cased (see Phase 1). ✅
4. **Editorial thresholds:** primary `Vol 100–800, KD<15`; secondary `Vol>500, KD<30`; fallback ceiling `KD<35` (long-horizon, queued last). ✅
