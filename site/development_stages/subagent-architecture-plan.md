# DevNook Subagent Architecture — Workflow Redesign

## Context

DevNook sessions burn through context window and tokens because the main Opus orchestrator does everything alone: reads the entire codebase, plans, implements, tests, and writes content. Each session costs too much and context fills up fast. Additionally, the current Python pipeline calls external LLM APIs (Anthropic/Gemini) which adds separate API costs on top of the Claude Code subscription.

**This plan replaces the monolithic workflow with a delegated subagent architecture** where Opus acts purely as an orchestrator, spawning specialized subagents (Haiku/Sonnet) that each run in isolated context windows. The Python scripts stay as utilities (DB ops, HTTP scraping, file moves) but all LLM intelligence flows through Claude Code subagents instead of API calls.

The previous plan in `new_content_plan.md` (Antigravity content pipeline split) is incorporated — the Ingest workflow is one of the subagent roles.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              ORCHESTRATOR (Opus)                     │
│  - Reads user requests                              │
│  - Quick registry/status checks (inline)            │
│  - Delegates to subagents                           │
│  - Reviews reports, makes decisions                 │
│  - Commits & pushes (only on user approval)         │
└─────────┬───────────┬───────────┬───────────────────┘
          │           │           │
    ┌─────▼─────┐ ┌───▼───┐ ┌────▼────┐
    │ CONTENT   │ │  DEV  │ │PUBLISH  │
    │  TEAM     │ │ TEAM  │ │  TEAM   │
    │           │ │       │ │         │
    │ Planner   │ │Builder│ │Publisher│
    │ Writer    │ │       │ │         │
    │ Ingest    │ │       │ │         │
    └───────────┘ └───────┘ └─────────┘
```

---

## Team 1: Content Team (3 subagents)

### 1.1 — Planner (Haiku)

**Purpose:** Keyword discovery + content planning. Replaces `keyword_agent.py` (LLM parts) + `planner_agent.py`.

**What it does per invocation:**
- Reads `registry.db` to understand current content coverage
- Uses WebSearch for keyword research (replaces Google Autocomplete scraping)
- Classifies keywords into categories and priorities
- Writes planned posts directly into `registry.db` via sqlite3 commands
- Reports back: keywords found, posts queued by category, coverage gaps

**Model:** Haiku — classification and structured analysis, no creative writing needed.

**Scope guard:** Never queues `languages` category posts (Antigravity owns that). Editorial rings only: tool-adjacent (Ring 1), web fundamentals (Ring 2), AI/editorial (Ring 4).

**Invocation pattern:**
```
Agent(model: "haiku", prompt: "You are DevNook's Content Planner. 
[task + registry state + editorial-only constraint]
Report: JSON with {keywords_found, posts_queued, by_category, gaps}")
```

---

### 1.2 — Writer (Sonnet)

**Purpose:** Writes article content directly using LLM capability, guided by templates. Replaces `writer_agent.py` + `seo_optimizer.py`. Also handles QA validation.

**What it does per invocation (batch of N articles):**
- Reads queued posts from `registry.db` (editorial only, batch size from orchestrator)
- Reads relevant template from `agents/skills/` (brand voice, SEO rules, content schema)
- Writes each article as a complete `.md` file with frontmatter, directly to `agents/content-team/drafts/`
- Self-validates each article (word count, heading hierarchy, frontmatter completeness, banned phrases)
- Updates `registry.db` status for each post (drafted → passed/rejected)
- Reports back: drafted count, passed count, rejected with reasons

**Model:** Sonnet — quality creative writing required.

**Key constraint:** Batch size capped at 5-10 articles per invocation to prevent subagent context overflow. Orchestrator calls Writer multiple times for large queues.

**Invocation pattern:**
```
Agent(model: "sonnet", prompt: "You are DevNook's Content Writer.
[batch details + template content pasted inline + SEO rules + QA criteria]
Write each article to agents/content-team/drafts/{slug}.md
Report: JSON with {drafted, passed, rejected, rejection_reasons}")
```

---

### 1.3 — Ingest (Haiku)

**Purpose:** Pulls Antigravity programmatic content into DevNook's pipeline. Implements the plan from `new_content_plan.md`.

**What it does per invocation:**
- Scans `../web_content/output/*.md` for new files
- Parses frontmatter, maps fields to DevNook schema (the mapping table from `new_content_plan.md`)
- Checks for slug collisions in `registry.db` — skip + log on collision
- Copies files to `agents/content-team/drafts/`
- Inserts registry rows: `content_type='programmatic'`, `source='antigravity'`, `status='drafted'`
- Moves processed files to `../web_content/output/_ingested/`
- Reports back: ingested count, collisions skipped, slugs imported

**Model:** Haiku — pure file ops + DB inserts, no creative work.

**Post-ingest:** Orchestrator chains Writer (Sonnet) with `--seo-only` flag to run SEO optimization on ingested files, then QA validation.

---

## Team 2: Dev Team (1 subagent)

### 2.1 — Builder (Sonnet)

**Purpose:** All Astro site development — new pages, components, layouts, bug fixes, tool building. Replaces `scaffold.py`, `update.py`, and `build-tool.py`.

**What it does per invocation (task from orchestrator):**
- Reads relevant source files (only what's needed for the task)
- Reads applicable skills: `astro-conventions.md`, `content-schema.md`, `tool-build-patterns.md`
- Makes targeted edits to the Astro project
- Runs `npm run build` to verify
- Reports back: files changed, build result, any issues

**Model:** Sonnet — code quality matters for frontend work.

**Embedded gotchas (always in prompt):**
- Global CSS must live in `public/styles/`, not `src/styles/`
- PostCard prop is `href`, not `slug`
- `tools/[slug].astro` uses `import.meta.glob` — never switch to dynamic import
- Never write `src/pages/tools/{slug}.astro` — route is dynamic
- Stage files by explicit path, never `git add .`

**Invocation pattern:**
```
Agent(model: "sonnet", prompt: "You are DevNook's Site Builder.
[specific task + relevant file paths + gotchas]
Run npm run build after changes.
Report: files changed, build status, issues")
```

---

## Team 3: Publish Team (1 subagent)

### 3.1 — Publisher (Haiku)

**Purpose:** Moves content through staging → publish → git push. Replaces `staging.py` + `publish.py`.

**What it does per invocation:**
- Reads approved posts from `registry.db` (`status='passed'`)
- Moves files from `agents/content-team/drafts/` → `content-staging/{category}/`
- Moves N files from `content-staging/` → `src/content/{category}/` (drip count from orchestrator)
- Updates `registry.db` status to `staged`/`published`
- Reports back: staged count, published count, file paths

**Model:** Haiku — pure file operations, no writing.

**Note:** Git commit/push is NOT done by the Publisher. The Orchestrator handles that after reviewing the Publisher's report, with user approval.

---

## Subagent Summary Table

| # | Name | Team | Model | Cost | Replaces |
|---|---|---|---|---|---|
| 1 | Planner | Content | Haiku | Low | keyword_agent.py + planner_agent.py |
| 2 | Writer | Content | Sonnet | Medium | writer_agent.py + seo_optimizer.py + qa_agent.py |
| 3 | Ingest | Content | Haiku | Low | ingest_agent.py (new, from Antigravity plan) |
| 4 | Builder | Dev | Sonnet | Medium | scaffold.py + update.py + build-tool.py |
| 5 | Publisher | Publish | Haiku | Low | staging.py + publish.py |

**5 subagents total.** Content team: 3, Dev team: 1, Publish team: 1. Orchestrator (Opus) is the 6th role but runs in the main session.

---

## Workflow Patterns

### Pattern A: Weekly Content Generation Run

```
Step 1: Planner (Haiku, background)
  → "Discover keywords and queue editorial posts"
  → Report: 47 posts queued (12 guides, 18 blog, 8 cheatsheets, 9 tools)

Step 2: Ingest (Haiku, parallel with Step 3)
  → "Check ../web_content/output/ for new Antigravity files"
  → Report: 8 files ingested, 1 collision skipped

Step 3: Writer (Sonnet, batch=5)
  → "Write next 5 queued editorial posts"
  → Report: 5 drafted, 4 passed, 1 rejected (word count low)
  → Repeat for more batches as needed

Step 4: Writer (Sonnet, seo-only)
  → "Run SEO optimization + QA on ingested programmatic drafts"
  → Report: 8 optimized, 7 passed, 1 rejected

Step 5: Publisher (Haiku)
  → "Stage all approved posts. Publish 3 to src/content/"
  → Report: 11 staged, 3 published to src/content/

Step 6: Orchestrator commits + pushes (with user approval)
```

**Context cost for Orchestrator:** ~5 short reports instead of reading/writing 13 articles.

### Pattern B: New Tool Addition

```
Step 1: Orchestrator checks spec exists (inline sqlite3/file read)

Step 2: Builder (Sonnet)
  → "Build csv-to-json tool. Read spec at tool-specs/csv-to-json.json.
     Generate component .astro + content .md. NOT the page route.
     Run npm run build."
  → Report: 2 files written, build passed

Step 3: Orchestrator reviews, commits
```

### Pattern C: Frontend Bug Fix / Feature

```
Step 1: Orchestrator describes the bug/feature clearly

Step 2: Builder (Sonnet)
  → "[Bug description + affected file paths]
     Read files, fix issue, run npm run build."
  → Report: files changed, build status

Step 3: Orchestrator reviews diff, commits
```

### Pattern D: Quick Status Check

```
Orchestrator runs inline (no subagent needed):
  sqlite3 registry.db "SELECT status, COUNT(*) FROM posts GROUP BY status"
  git status
  npm run build (if needed)
```

---

## Context Optimization Strategies

### 1. Report Format Discipline
Every subagent prompt ends with a strict report format. Example:
> "Report as compact JSON: {processed, passed, rejected, errors: [{slug, reason}]}. Do NOT quote file contents. Do NOT narrate steps."

Orchestrator receives ~200 tokens per report, not 20,000 tokens of narration.

### 2. Batch Size Controls
Writer processes 5-10 articles per invocation, never 50+. Multiple small calls > one giant call. Prevents subagent context overflow and gives orchestrator checkpoints.

### 3. Registry-First State Management
Before spawning any subagent, orchestrator runs a one-line sqlite3 query to check pipeline state. Costs a few tokens, not a full subagent invocation. Only spawn subagents for write operations.

### 4. Skills Stay on Disk
Templates and style guides live in `agents/skills/*.md`. Each subagent reads only the skills it needs. Orchestrator never loads them — it just tells the subagent which files to read.

### 5. Parallel Invocations
Independent subagents run in parallel via `run_in_background: true`:
- Planner + Ingest (different DB rows, different file paths)
- Builder + Writer (frontend vs content, no overlap)

### 6. CLAUDE.md Hygiene
Trim CLAUDE.md to essentials: current session state + architecture reference. Move historical session logs to a separate file. The orchestrator reads ~80 lines, not 600+.

### 7. Orchestrator Never Reads Source Code
For any task requiring code reading, spawn a subagent (even Haiku Explorer). The orchestrator only sees the summary. This is the single biggest context saver.

---

## What Happens to Python Scripts

| Script | Disposition |
|---|---|
| `keyword_agent.py` | **Kept as utility** — Planner subagent can call it for HTTP-based keyword scraping if WebSearch isn't sufficient |
| `planner_agent.py` | **Replaced** — Planner subagent does classification directly |
| `writer_agent.py` | **Replaced** — Writer subagent writes content directly |
| `seo_optimizer.py` | **Replaced** — Writer subagent handles SEO inline |
| `qa_agent.py` | **Kept as utility** — rule-based, no LLM. Writer subagent can call it for validation |
| `staging.py` | **Kept as utility** — file ops. Publisher subagent can call it |
| `publish.py` | **Kept as utility** — file ops + git. Publisher calls it |
| `run-pipeline.py` | **Replaced** — Orchestrator IS the pipeline now |
| `llm_router.py` | **Deprecated** — no more external API calls |
| `gemini_client.py` | **Deprecated** — no Gemini API usage |
| `scaffold.py` | **Replaced** — Builder subagent handles site generation |
| `update.py` | **Replaced** — Builder subagent handles page updates |
| `build-tool.py` | **Replaced** — Builder subagent builds tools |

**Don't delete anything yet.** Mark as deprecated. Remove after the new system is validated.

---

## Antigravity Integration (from new_content_plan.md)

The previous plan's decisions are preserved:
1. DevNook editorial only — `languages` category owned by Antigravity
2. Ingest subagent handles the `../web_content/output/` → DevNook pipeline handoff
3. Ingested files run through Writer subagent's SEO pass for uniform internal linking
4. Slug collisions → skip + log

**Schema changes still needed (from new_content_plan.md Step 1):**
- Add `content_type` + `source` columns to `posts` table in `registry.db`
- Backfill existing rows
- This is a prerequisite before Ingest subagent can work

---

## Implementation Plan (Phase Order)

### Phase 1: Foundation (Session 11)
1. **Schema migration** — Add `content_type` + `source` to registry.db (from `new_content_plan.md` Step 1)
2. **Create subagent prompt files** — Write 5 prompt templates to `agents/subagent-prompts/`:
   - `planner.md`, `writer.md`, `ingest.md`, `builder.md`, `publisher.md`
3. **Trim CLAUDE.md** — Move session history to `session-history.md`, keep CLAUDE.md lean (~100 lines)
4. **Test: Planner subagent** — Run one Planner invocation, verify registry updates

### Phase 2: Content Pipeline (Session 12)
1. **Test: Writer subagent** — Write 3 test articles, validate quality vs old pipeline
2. **Test: Ingest subagent** — Ingest Antigravity output files
3. **Test: Publisher subagent** — Stage + publish test content
4. **Full pipeline dry run** — Planner → Writer → Publisher end-to-end

### Phase 3: Dev Pipeline (Session 13)
1. **Test: Builder subagent** — Fix a known issue or add a small feature
2. **Tool building test** — Build one new tool via Builder subagent
3. **Validate parallel execution** — Run Builder + Writer simultaneously

### Phase 4: Production (Session 14+)
1. **First real content batch** — 20 editorial articles through the new pipeline
2. **Antigravity ingest** — Process the 5 waiting files from `../web_content/output/`
3. **Deprecate old scripts** — Mark replaced Python scripts as deprecated
4. **GitHub Actions** — Wire Publisher into drip-publish workflow

---

## Verification

After each phase:
1. `sqlite3 registry.db "SELECT status, content_type, source, COUNT(*) FROM posts GROUP BY 1,2,3"` — verify pipeline state
2. `npm run build` — verify site builds cleanly
3. Check `agents/content-team/drafts/` for properly formatted markdown
4. Compare article quality: new subagent output vs old pipeline output (spot check 3 articles)

---

## Key Files to Create/Modify

| File | Action | Phase |
|---|---|---|
| `agents/subagent-prompts/planner.md` | CREATE | 1 |
| `agents/subagent-prompts/writer.md` | CREATE | 1 |
| `agents/subagent-prompts/ingest.md` | CREATE | 1 |
| `agents/subagent-prompts/builder.md` | CREATE | 1 |
| `agents/subagent-prompts/publisher.md` | CREATE | 1 |
| `agents/content-team/registry.db` | MODIFY (schema migration) | 1 |
| `CLAUDE.md` | TRIM (move history out) | 1 |
| `session-history.md` | CREATE (moved from CLAUDE.md) | 1 |

---

## Token Efficiency Comparison

> **Important:** All subagents run inside Claude Code using your existing plan — there are NO separate API charges. The "cost" below refers to token consumption against your Claude Code plan limits. Subagents use cheaper models (Haiku/Sonnet) which consume fewer tokens per task than Opus.

| Workflow | Old approach | New approach | Token savings |
|---|---|---|---|
| Content: 20 articles | Opus does everything: reads templates, writes all articles, validates — fills context window | Opus sends 5 short prompts. Sonnet writes in isolated contexts. Haiku validates. | ~60% fewer Opus tokens |
| Bug fix | Opus reads entire codebase section, diagnoses, fixes, builds | Opus describes bug. Sonnet reads + fixes in its own context. Reports back. | ~50% fewer Opus tokens |
| Tool addition | Opus reads spec, reads patterns, generates code, builds | Opus delegates. Sonnet reads spec + builds in isolated context. | ~50% fewer Opus tokens |
| Status check | Opus reads CLAUDE.md + registry + git status (~5000 tokens) | Orchestrator runs inline sqlite3 query (~100 tokens) | ~95% fewer tokens |

**Key benefit:** Each subagent's context is isolated and disposable. Your main Opus session only accumulates short reports (~200 tokens each), not the full content of files read and articles written. This means you can do 3-4x more work per session before hitting context limits.

**No extra billing.** Haiku/Sonnet subagents run on your Claude Code plan. They just consume fewer tokens per task than doing the same work in the Opus orchestrator session.
