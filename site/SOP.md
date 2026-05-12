# DevNook — Standard Operating Procedure (SOP)

> **Single source of truth** for the DevNook two-repo system: the Astro site (this repo) and the content pipeline (`../devnook_content_workspace/`).
> **Audience:** Future Claude sessions + the human operator (Syed Jawad).
> **Last full audit:** 2026-05-11 (session #43)
> **Companion docs:** `CLAUDE.md` (session log), `auditlog.md` (SEO issues), `workspace_rules.md` (manual workflow refs).

---

## Table of Contents

1. [Quick Reference Card](#1-quick-reference-card)
2. [Architecture Overview](#2-architecture-overview)
3. [Repo Map: DevNook (site)](#3-repo-map-devnook-site)
4. [Repo Map: Content Workspace](#4-repo-map-content-workspace)
5. [Agents Inventory — Active (6)](#5-agents-inventory--active-6)
6. [Skills Inventory — Active (6)](#6-skills-inventory--active-6)
7. [Scripts Inventory — Active](#7-scripts-inventory--active)
8. [Scripts & Agents — Deprecated / Dormant / Retired](#8-scripts--agents--deprecated--dormant--retired)
9. [Astro Build Plugins](#9-astro-build-plugins)
10. [Cross-Repo Publishing Mechanics](#10-cross-repo-publishing-mechanics)
11. [Registry Schema & Data Flow](#11-registry-schema--data-flow)
12. [CI Workflows (GitHub Actions)](#12-ci-workflows-github-actions)
13. [Environment Variables](#13-environment-variables)
14. [Memory System Inventory](#14-memory-system-inventory)
15. [Important Decisions Log (Guardrails)](#15-important-decisions-log-guardrails)
16. [Stage Progression History](#16-stage-progression-history)
17. [Playbooks (with commands)](#17-playbooks-with-commands)
18. [Verification Checklist](#18-verification-checklist)
19. [Glossary](#19-glossary)

---

## 1. Quick Reference Card

| Resource | Value |
|----------|-------|
| Live site | https://devnook.dev |
| Site repo | https://github.com/syedjawad11/devnook.git (branch: `main`) |
| Content repo | https://github.com/syedjawad11/devnook-content.git (branch: `master`) |
| Hosting | Cloudflare Pages, auto-deploy on push to `main` |
| Site framework | Astro 4.16.18, static output |
| Site local path | `c:\Users\Syed Jawad Hassan\Desktop\devnook` |
| Content workspace path | `C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace` |
| Antigravity source | `C:\Users\Syed Jawad Hassan\Desktop\web_content\output\` |
| Total posts | ~1,000+ programmatic + guides + blog + cheatsheets |
| Total client-side tools | 18 |
| Monetization | AdSense (deferred until 50k monthly visitors) |
| Drip cadence | 2 posts/day, 08:00 UTC, via GitHub Actions cron |
| Python | `D:\miniconda3\python.exe` |
| Node | npm scripts: `dev`, `build`, `preview` |

**Two commands you will need most:**

```powershell
# Local site dev (this repo)
npm run dev

# Verify build before commit (this repo)
npm run build
```

---

## 2. Architecture Overview

### 2.1 The two-repo split

DevNook is intentionally split into two independent repositories that talk to each other only through a single cross-repo Git push.

```
┌─────────────────────────────────────────┐
│  devnook_content_workspace (separate)   │
│  ─────────────────────────────────────  │
│  • Registry (SQLite)                    │
│  • Planner / Writer / Ingest / QA /     │
│    Publisher subagents                  │
│  • Drafts / Staging / Archive           │
│  • GitHub Actions: drip-publish cron    │
│                                         │
│           pushes via PAT ↓              │
└─────────────────────────────────────────┘
                  │
                  │  git push (DEVNOOK_REPO_PAT)
                  │  writes to src/content/
                  ▼
┌─────────────────────────────────────────┐
│  devnook (this repo)                    │
│  ─────────────────────────────────────  │
│  • Astro site                           │
│  • src/content/ (read-only target)      │
│  • Layouts, components, tools           │
│  • Build-time rehype plugins            │
│  • Builder subagent (for site work)     │
│                                         │
│           pushes to main ↓              │
└─────────────────────────────────────────┘
                  │
                  ▼
            Cloudflare Pages
            (auto-deploy)
```

### 2.2 Why the split?

- **Separation of concerns.** Content pipeline state (registry, drafts, run logs) should not pollute the deployable site repo.
- **Cloudflare deploys per push.** A noisy content workspace would trigger excessive rebuilds. The publisher batches writes (e.g., 2 posts/day) so Cloudflare deploys ~1×/day at most.
- **Independent iteration.** Pipeline refactors (e.g., swapping out the Writer) don't risk breaking the site build.
- **Single integration seam.** The only contract is "push markdown files into `src/content/*` in the correct frontmatter shape."

### 2.3 The integration contract

The content workspace must produce markdown files conforming to one of 22 frontmatter templates (see Section 11 and `agents/skills/content-schema.md` in the content workspace). The site repo treats `src/content/` as **read-only output** of the pipeline — it must never be edited by hand except for emergency fixes (e.g., the duplicate-H1 cleanup in session #42).

### 2.4 Tech stack

**Site (this repo):**
- Astro 4.16.18, static output (`output: 'static'`, no adapter)
- No Tailwind — all styles via CSS custom properties in `tokens.css`
- All 18 tools are client-side only (no Workers, no AI tools)
- Sitemap: `@astrojs/sitemap@3.2.1`
- Build plugins: `auto-internal-links`, `related-callouts` (custom rehype)

**Content pipeline:**
- Python 3 (miniconda at `D:\miniconda3\python.exe`)
- SQLite registry
- Claude Agent SDK via subagent spawning (no direct Anthropic API calls in scripts)
- Google Search Console API (Indexing API ping)

---

## 3. Repo Map: DevNook (site)

```
c:\Users\Syed Jawad Hassan\Desktop\devnook\
├── CLAUDE.md                          ← Session log; read at start of every session
├── SOP.md                             ← This file
├── auditlog.md                        ← SEO audit issues + verdicts (read before #37+)
├── update_plan.md                     ← Workspace split plan snapshot (2026-04-25)
├── workspace_rules.md                 ← Manual workflow reference
├── astro.config.mjs                   ← Astro config (plugins registered here)
├── package.json
├── tsconfig.json
├── wrangler.toml                      ← Cloudflare config
│
├── Sheet1.csv                         ← Ahrefs crawl export (308 redirects, untracked)
├── audits/                            ← SEO audit CSVs (untracked)
│   ├── seo_audit_2026-05-03.csv
│   ├── seo_audit_2026-05-04.csv
│   └── .gitkeep
│
├── agents/                            ← Site-side subagent prompts + skills
│   ├── subagent-prompts/
│   │   └── builder.md                 ← Builder subagent prompt
│   └── skills/
│       ├── astro-conventions.md       ← Astro/CSS/no-Tailwind conventions
│       └── tool-build-patterns.md     ← 4-batch tool architecture
│
├── scripts/
│   ├── seo_audit.py                   ← ACTIVE: word count + readability + similarity
│   └── fix_trailing_slashes.py        ← ACTIVE: internal-link trailing slash fixer
│
├── public/
│   ├── styles/
│   │   ├── tokens.css                 ← CSS custom properties (design tokens)
│   │   └── global.css                 ← Global styles incl. .related-callout
│   ├── tools/*.html                   ← 18 client-side tool pages
│   ├── robots.txt
│   └── _redirects                     ← Cloudflare redirects
│
├── src/
│   ├── content/                       ← WRITTEN BY CONTENT WORKSPACE (do not edit)
│   │   ├── blog/
│   │   ├── guides/
│   │   ├── cheatsheets/
│   │   └── languages/{language}/      ← e.g., languages/python/, languages/rust/
│   ├── content/config.ts              ← Astro collections schema (frontmatter validation)
│   ├── layouts/
│   │   └── PostLayout.astro           ← Renders frontmatter.title as <h1>; auto-derives related posts
│   ├── components/
│   │   ├── PostCard.astro             ← prop is `href`, NEVER rename to slug/url/path
│   │   ├── SearchBar.astro            ← Parked (not wired)
│   │   └── ...
│   ├── pages/
│   │   ├── index.astro
│   │   ├── blog/...
│   │   ├── guides/...
│   │   ├── languages/[language]/[concept].astro
│   │   └── tools/[slug].astro         ← Uses import.meta.glob (NOT await import)
│   ├── plugins/
│   │   ├── auto-internal-links/index.mjs
│   │   └── related-callouts/index.mjs
│   └── styles/                        ← (mostly empty — global CSS lives in public/styles/)
│
├── fix_frontmatter.py                 ← DORMANT (one-shot frontmatter normalizer)
└── scratch_clean.py                   ← DORMANT (one-shot cleanup utility)
```

### 3.1 Critical site-side file conventions

- **PostCard.astro prop = `href`** — never `slug`, `url`, or `path`. Five call sites depend on it.
- **Static output only** — never switch to `hybrid`. Satori (used in og-image generation) crashes Workers runtime.
- **Global CSS in `public/styles/`** — Astro only copies `public/` into `dist/`. Absolute references like `/styles/global.css` only resolve from `public/`.
- **Tools route uses `import.meta.glob`** — `await import()` crashes Vite static analysis.
- **`src/content/` is the publish target** — anything you change there will be overwritten on next pipeline publish unless you also update the upstream draft/registry.

---

## 4. Repo Map: Content Workspace

```
C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace\
├── README.md
├── CLAUDE.md                          ← Pipeline session log
│
├── agents/
│   ├── subagent-prompts/
│   │   ├── planner.md                 ← Keyword discovery + queueing (Haiku)
│   │   ├── writer.md                  ← Batch markdown writer (Sonnet)
│   │   ├── ingest.md                  ← Antigravity draft ingestion (Haiku)
│   │   ├── antigravity-qa.md          ← Fix+approve language posts (Sonnet)
│   │   └── publisher.md               ← File ops for publish (Haiku)
│   │
│   ├── skills/
│   │   ├── seo-writing-rules.md       ← Word counts, headings, keyword placement
│   │   ├── content-schema.md          ← 22 frontmatter template specs
│   │   ├── qa-rejection-criteria.md   ← TF-IDF, duplicate detection thresholds
│   │   └── devnook-brand-voice.md     ← Banned phrases, code style
│   │
│   ├── content-team/
│   │   ├── registry.py                ← SQLite helpers (active)
│   │   ├── staging.py                 ← Approved → staging FIFO move
│   │   ├── fix_broken_links.py        ← Maintenance utility (active)
│   │   ├── run-pipeline.py            ← DEPRECATED (replaced by subagents)
│   │   ├── seo_optimizer.py           ← DEPRECATED
│   │   ├── link_utility.py            ← DEPRECATED (logic inlined into subagents)
│   │   └── tests/
│   │       └── test_link_utility.py   ← INACTIVE
│   │
│   └── publish/
│       ├── publish.py                 ← Drip publisher + GSC ping + cross-repo push
│       ├── gsc_ping.py                ← Google Search Console Indexing API client
│       └── seed.py                    ← DEPRECATED (one-shot 30-post seed)
│
├── registry.db                        ← SQLite content registry
├── drafts/                            ← Writer/QA output (markdown)
├── content-staging/                   ← FIFO publish queue (ordered by registry id)
├── archive/                           ← Post-publish archive
├── logs/                              ← Pipeline run logs
│
└── .github/workflows/
    ├── drip-publish.yml               ← Cron: 08:00 UTC daily, 2 posts
    └── on-demand-publish.yml          ← Manual trigger, count + category inputs
```

### 4.1 External Antigravity source

Antigravity = Gemini-scraped language drafts. Source location:
`C:\Users\Syed Jawad Hassan\Desktop\web_content\output\`

The Ingest subagent pulls from here into `drafts/` for QA review. After processing, drafts are archived to `C:\Users\Syed Jawad Hassan\Desktop\web_content\output\_ingested\YYYY-MM-DD\`.

---

## 5. Agents Inventory — Active (6)

Two distinct kinds of "agents" exist:
1. **Subagents** — prompt files invoked via the `Agent()` tool from a Claude main session.
2. **Skills** — reference docs loaded into agent context (see Section 6).

This section documents the **6 active subagents** (1 in this repo + 5 in the content workspace).

### 5.1 Builder (site repo)

| Field | Value |
|-------|-------|
| Prompt path | `agents/subagent-prompts/builder.md` (devnook repo) |
| Model | Sonnet |
| Purpose | Astro site edits, new tool creation, build verification |
| Spawned by | Main session orchestrator (Claude in devnook context) |
| Inputs | Task description; relevant file paths; build constraints from skills |
| Outputs | File edits in `src/`, `public/`, `agents/`; verified `npm run build` |
| Constraints | Must run `npm run build` before reporting done; follows astro-conventions.md and tool-build-patterns.md |
| Loaded skills | `astro-conventions.md`, `tool-build-patterns.md` |
| Invocation pattern | `Agent(prompt=open('agents/subagent-prompts/builder.md').read() + "\n\nTask: ...", subagent_type="general-purpose")` |
| Used in workflows | **Workflow B** (new tool), **Workflow C** (bug fix) |

**When to spawn Builder:**
- Adding a new client-side tool (HTML + Astro slug page).
- Bug fix in any `.astro` file, layout, or component.
- Style/token changes across components.
- Plugin tuning (auto-internal-links, related-callouts).

**When NOT to spawn Builder:**
- Editing content files in `src/content/` — those are pipeline output; fix at source.
- Pipeline scripts (those live in `../devnook_content_workspace/`).

---

### 5.2 Planner (content workspace)

| Field | Value |
|-------|-------|
| Prompt path | `agents/subagent-prompts/planner.md` (content workspace) |
| Model | Haiku |
| Purpose | Keyword discovery + queue posts into the SQLite registry |
| Inputs | `DB_PATH`, `BATCH_SIZE`, `RING_FILTER` (priority ring), `CATEGORY_FILTER` (excluding `languages`) |
| Outputs | New rows in `posts` registry table with `status='queued'` |
| Constraints | **Never queues `category='languages'`** (those are seeded from Antigravity via Ingest). Skips slugs that already exist (`slug_exists()`). |
| Loaded skills | `seo-writing-rules.md`, `content-schema.md` |
| Typical batch | 10–30 posts per invocation |

**Categories Planner handles:** `blog`, `guides`, `cheatsheets`, `tools` (explainer pages).

---

### 5.3 Writer (content workspace)

| Field | Value |
|-------|-------|
| Prompt path | `agents/subagent-prompts/writer.md` (content workspace) |
| Model | Sonnet |
| Purpose | Batch-generate markdown drafts from queued registry rows |
| Inputs | `DB_PATH`, `DRAFTS_DIR`, `MAX_POSTS` (≤10/invocation), `MODE` (`full` or `seo-only`) |
| Outputs | Markdown files in `drafts/{category}/{slug}.md` with full frontmatter; registry row → `status='drafted'` |
| Constraints | **Skips `category='languages'`**. Enforces no body H1 (Decision #16). Banned phrases per brand voice. Word count floors per template. |
| Loaded skills | `seo-writing-rules.md`, `content-schema.md`, `devnook-brand-voice.md` |
| Templates produced | 5 lang-vN, 4 guide-vN, 5 blog-vN, 4 cheatsheet-vN, 4 tool-exp-vN (22 total) |

---

### 5.4 Ingest (content workspace)

| Field | Value |
|-------|-------|
| Prompt path | `agents/subagent-prompts/ingest.md` (content workspace) |
| Model | Haiku |
| Purpose | Move Antigravity (Gemini-scraped) language drafts from `web_content/output/` into pipeline `drafts/languages/` |
| Inputs | `SOURCE_DIR` (`web_content/output/`), `ARCHIVE_DIR`, `LOG_PATH`, `DB_PATH` |
| Outputs | Files copied to `drafts/languages/{language}/{concept}.md`; registry rows inserted with `status='drafted'` and `source='antigravity'`; source archived |
| Constraints | Does not modify content — passes through raw to QA. Registers `concept` + `language` fields exactly as parsed. |
| Loaded skills | `content-schema.md` |
| Note | This is the ONLY way `languages/` content enters the pipeline. Planner cannot queue languages. |

---

### 5.5 Antigravity QA (content workspace)

| Field | Value |
|-------|-------|
| Prompt path | `agents/subagent-prompts/antigravity-qa.md` (content workspace) |
| Model | Sonnet |
| Purpose | Fix + approve language drafts pulled in by Ingest |
| Inputs | `DRAFTS_DIR/languages/`, registry rows where `status='drafted' AND source='antigravity'` |
| Outputs | Cleaned markdown files; registry rows → `status='approved'`. **Never rejects** — always fixes and approves. |
| Constraints | Word range 1500–2500. **Removes any body H1** (Decision #16, patched session #42). Strips `## Related` sections (auto-derived by site layout). Enforces correct `/languages/{lang}/{concept}` URL form, NOT `/languages/{lang}/{filename}`. |
| Loaded skills | `seo-writing-rules.md`, `qa-rejection-criteria.md`, `devnook-brand-voice.md` |
| Why "never rejects"? | Antigravity output is human-curated upstream; rejecting it would orphan good content. QA's job is repair, not gatekeeping. |

---

### 5.6 Publisher (content workspace)

| Field | Value |
|-------|-------|
| Prompt path | `agents/subagent-prompts/publisher.md` (content workspace) |
| Model | Haiku |
| Purpose | Pure file operations during publish — move staging → site repo working tree |
| Inputs | `ACTION` (`stage` / `publish` / `both`), `COUNT`, `CATEGORY` (optional) |
| Outputs | Files moved from `content-staging/` into `<devnook>/src/content/`; archived locally; registry rows → `status='published'` |
| Constraints | **No git commands** — actual commit + push handled by `publish.py` script. **No content edits.** Strict FIFO by registry `id`, not mtime (mtime is unreliable under GitHub Actions checkout). |
| Loaded skills | None (pure file ops) |
| Why a subagent at all? | Encapsulates the file-move logic so `publish.py` stays small and the rules (FIFO, language-link validation, archival) are documented as a prompt. |

---

### 5.7 Subagent orchestration diagram

```
Editorial flow (Workflow A):
  Orchestrator → Planner → Writer → (human review) → manual approve → staging.py → cron publishes

Antigravity flow (Workflow D):
  Orchestrator → Ingest → Antigravity QA → staging.py → cron publishes

Site work flows:
  Workflow B (new tool):   Orchestrator → Builder → review + commit
  Workflow C (bug fix):    Orchestrator → Builder → review + commit
```

---

## 6. Skills Inventory — Active (6)

Skills are reference markdown files that subagents load into their context window. They encode rules and conventions that would otherwise rot if embedded into prompts.

### 6.1 Site-side skills (this repo)

| Skill | Path | Consumed by | Purpose |
|-------|------|-------------|---------|
| `astro-conventions.md` | `agents/skills/astro-conventions.md` | Builder | Astro framework conventions, no-Tailwind rule, tokens.css usage, static output requirement |
| `tool-build-patterns.md` | `agents/skills/tool-build-patterns.md` | Builder | 4-batch tool architecture (Formatters, Encoders, Generators, Testers); HTML+Astro pairing rules |

### 6.2 Content-workspace skills

| Skill | Path | Consumed by | Purpose |
|-------|------|-------------|---------|
| `seo-writing-rules.md` | `agents/skills/seo-writing-rules.md` | Writer, Antigravity QA | Word count floors per template, heading hierarchy (no body H1 — patched #42), keyword placement, meta description 120–160 chars |
| `content-schema.md` | `agents/skills/content-schema.md` | Planner, Writer, Ingest | 22 frontmatter templates: 5 lang-vN, 4 guide-vN, 5 blog-vN, 4 cheatsheet-vN, 4 tool-exp-vN |
| `qa-rejection-criteria.md` | `agents/skills/qa-rejection-criteria.md` | Antigravity QA | TF-IDF >70% duplicate threshold, >40% sentence-overlap rule, word floor enforcement |
| `devnook-brand-voice.md` | `agents/skills/devnook-brand-voice.md` | Writer, Antigravity QA | Banned phrases ("Let's dive in", "Buckle up", etc.); preferred code style; tone guidelines |

---

## 7. Scripts Inventory — Active

### 7.1 Site repo scripts

#### `scripts/seo_audit.py`

| Field | Value |
|-------|-------|
| Status | ACTIVE |
| Purpose | Crawl `src/content/`, score word count + readability + keyword density + cross-post similarity |
| Inputs | None (defaults to `src/content/`) |
| Outputs | `audits/seo_audit_YYYY-MM-DD.csv` |
| Invocation | `D:\miniconda3\python.exe scripts/seo_audit.py` |
| When to run | Before any "batch fix" session; after large content drops; before reporting site health |
| Notes | Output CSVs are git-ignored — they live in `audits/` for local review only. |

#### `scripts/fix_trailing_slashes.py`

| Field | Value |
|-------|-------|
| Status | ACTIVE |
| Purpose | Walks `src/content/` markdown files and ensures all internal links (`/blog/`, `/guides/`, `/languages/`, `/cheatsheets/`, `/tools/`) end with `/` |
| Inputs | None |
| Outputs | In-place edits; prints summary of fixes |
| Invocation | `D:\miniconda3\python.exe scripts/fix_trailing_slashes.py` |
| When to run | After bulk content imports; after any redirect cleanup (e.g., the 308 Ahrefs flag from session #41) |

### 7.2 Content workspace scripts

#### `agents/content-team/registry.py`

| Field | Value |
|-------|-------|
| Status | ACTIVE — library module (imported, not invoked directly) |
| Purpose | SQLite helpers for the content registry |
| Key functions | `get_db()`, `slug_exists(slug)`, `get_queued_posts(limit, category)`, `add_post(...)`, `update_post_status(id, status)`, `log_pipeline_run(...)` |
| Schema owner | This file is the source of truth for `registry.db` schema (`posts`, `pipeline_runs` tables) |
| Imported by | Planner (via subagent tool calls), Writer, Ingest, Antigravity QA, Publisher, `staging.py`, `publish.py` |

#### `agents/content-team/staging.py`

| Field | Value |
|-------|-------|
| Status | ACTIVE |
| Purpose | Move approved drafts → `content-staging/` in strict FIFO order by registry `id` |
| Inputs | `--count <N>`, `--category <cat>` (optional) |
| Outputs | Files moved; registry rows → `status='staged'` |
| Invocation | `python agents/content-team/staging.py --count 5` |
| Why FIFO by id, not mtime | GitHub Actions checkout resets mtime — `id` is the only stable order |

#### `agents/content-team/fix_broken_links.py`

| Field | Value |
|-------|-------|
| Status | ACTIVE (maintenance utility, run on demand) |
| Purpose | Scan registry + filesystem for broken internal links; report or fix |
| Inputs | `--mode {report,fix}` |
| Outputs | Console report, or in-place edits when `--mode fix` |
| Invocation | `python agents/content-team/fix_broken_links.py --mode report` |
| When to run | After Ahrefs/audit flags 404s on internal links |

#### `agents/publish/publish.py`

| Field | Value |
|-------|-------|
| Status | ACTIVE — **the drip publisher** |
| Purpose | Move staged posts → `<devnook>/src/content/`, commit, push, ping GSC, update registry |
| Inputs | `--count <N>`, `--dry-run`, env: `DEVNOOK_REPO_PAT`, `DEVNOOK_PATH`, `GOOGLE_SERVICE_ACCOUNT_JSON` |
| Outputs | Git commit + push to `devnook:main`; GSC Indexing API pings; registry rows → `status='published'`; local archive |
| Key functions | `get_staged_files()`, `validate_language_links()`, `move_to_content()`, `strip_related_section()`, `update_registry()`, `git_commit_and_push()` |
| Invocation | `python agents/publish/publish.py --count 2` |
| Critical guard | `validate_language_links()` — skips any file whose body links use `/languages/{lang}/{filename-slug}` instead of `/languages/{lang}/{concept}` (Decision #13 enforcement) |
| Notes | This is the **only** script in the entire system that runs `git push` to the site repo. |

#### `agents/publish/gsc_ping.py`

| Field | Value |
|-------|-------|
| Status | ACTIVE — library, called from `publish.py` |
| Purpose | Google Search Console Indexing API client |
| Key functions | `get_service()`, `ping_url(url, notification_type='URL_UPDATED')` |
| Inputs | env: `GOOGLE_SERVICE_ACCOUNT_JSON` (path to service account JSON) |
| Called per published URL | Yes — one ping per file in the publish batch |

---

## 8. Scripts & Agents — Deprecated / Dormant / Retired

### 8.1 Deprecated (replaced by subagents)

| Item | Path | Replaced by | Reason |
|------|------|-------------|--------|
| `run-pipeline.py` | `agents/content-team/run-pipeline.py` | Subagent orchestration via `Agent()` tool | Direct Anthropic API calls removed; orchestrator now spawns subagents |
| `seo_optimizer.py` | `agents/content-team/seo_optimizer.py` | Writer + Antigravity QA validation | SEO checks moved into subagent prompts + skills |
| `link_utility.py` | `agents/content-team/link_utility.py` | `auto-internal-links` rehype plugin (build-time) | Build-time injection is faster and avoids draft drift |

### 8.2 Retired (one-shot, kept for archaeology)

| Item | Path | Reason kept |
|------|------|-------------|
| `seed.py` | `agents/publish/seed.py` | One-shot 30-post seed used at launch — documents initial data load |
| `fix_frontmatter.py` | `<devnook>/fix_frontmatter.py` | One-shot frontmatter normalizer — record of historical schema drift |
| `scratch_clean.py` | `<devnook>/scratch_clean.py` | One-shot cleanup utility |
| `tests/test_link_utility.py` | `agents/content-team/tests/test_link_utility.py` | Test of retired module |

### 8.3 Parked (UI not wired)

| Item | Path | Reason parked |
|------|------|---------------|
| `SearchBar.astro` | `src/components/SearchBar.astro` | Component exists but not wired to any data source |
| Blog filter chips | (in blog index pages) | Decorative only; clicking does nothing |

### 8.4 Deferred features

| Feature | Trigger to revisit |
|---------|-------------------|
| AdSense integration | Site reaches 50k monthly visitors |
| Search bar wiring | Post-launch UX improvement priority |
| Filter chip wiring | After search bar |

### 8.5 Retired during Stage 9–10 (workspace split)

The Stage 9 workspace split moved ALL content-pipeline code out of this repo. Anything pre-split in `<devnook>/agents/content-team/` or `<devnook>/agents/publish/` is gone — those paths only exist in the **content workspace** now.

---

## 9. Astro Build Plugins

Both plugins are **build-time rehype plugins** registered in `astro.config.mjs`. They run during `astro build` and rewrite the rendered HTML tree.

### 9.1 `src/plugins/auto-internal-links/index.mjs`

| Field | Value |
|-------|-------|
| Type | Rehype plugin |
| Stage | Build-time |
| Purpose | Inject up to N contextual internal links into each post body |
| Key config | `autoAnchors: true`, `maxLinksPerPage: 8`, `contentDir: 'src/content'` |
| Scope | **All categories** — guides, blog, cheatsheets, languages (not language-only — see Decision #15) |
| Critical hook | `devnookUrlBuilder` — for `languages/` rows, builds URL from `frontmatter.language` + `frontmatter.concept`, NEVER from filename (Decision #13) |
| Library | `fast-glob` for scanning |

### 9.2 `src/plugins/related-callouts/index.mjs`

| Field | Value |
|-------|-------|
| Type | Rehype plugin |
| Stage | Build-time |
| Purpose | Inject up to 3 `<aside class="related-callout">` blocks at interior H2 boundaries |
| Key config | `wordThreshold: 500`, `maxCallouts: 3` |
| Scoring | Mirrors `PostLayout.astro` (language + category + tags) |
| Per-post opt-out | Set `excludeRelatedCallouts: true` in frontmatter |
| CSS | `public/styles/global.css` — `.related-callout` (NOT scoped) |

### 9.3 Why build-time, not runtime?

- Static output target — no runtime to inject from.
- Cached forever per build — zero per-request cost.
- Failures surface during `npm run build`, before deploy.

---

## 10. Cross-Repo Publishing Mechanics

### 10.1 The single integration seam

The entire pipeline-to-site interface boils down to **one git push** executed from `publish.py`:

```python
# Pseudocode from publish.py
subprocess.run(["git", "add", "src/content/"], cwd=DEVNOOK_PATH)
subprocess.run(["git", "commit", "-m", f"feat: publish {N} posts"], cwd=DEVNOOK_PATH)
subprocess.run(["git", "push", remote_with_pat, "main"], cwd=DEVNOOK_PATH)
```

The remote URL is built using `DEVNOOK_REPO_PAT`:
```
https://x-access-token:<DEVNOOK_REPO_PAT>@github.com/syedjawad11/devnook.git
```

### 10.2 What the publisher does in order

1. `get_staged_files(count, category)` — FIFO by registry id from `content-staging/`.
2. `validate_language_links(file)` — gate; skip if any `/languages/{lang}/{filename-slug}` pattern is found.
3. `strip_related_section(file)` — remove any `## Related` markdown sections (site auto-derives related posts).
4. `move_to_content(file)` — copy into `<DEVNOOK_PATH>/src/content/{category}/...`.
5. Git add + commit + push to `devnook:main` (using PAT).
6. `gsc_ping.ping_url(url)` per published file.
7. `update_registry(id, 'published')` per file.
8. Archive originals to `archive/YYYY-MM-DD/`.

### 10.3 Why `DEVNOOK_PATH` is optional

If unset, `publish.py` defaults to `../devnook` relative to the content workspace. On the local machine (where workspaces are siblings on the Desktop), this works without env.

On GitHub Actions, `DEVNOOK_PATH` is set explicitly during the checkout step.

---

## 11. Registry Schema & Data Flow

### 11.1 SQLite registry: `registry.db`

Located at the content workspace root. Two tables:

**`posts`** — one row per content piece, lifecycle tracked via `status`:

```
id              INTEGER PRIMARY KEY AUTOINCREMENT
slug            TEXT UNIQUE
title           TEXT
category        TEXT       -- 'blog' | 'guides' | 'cheatsheets' | 'languages' | 'tools'
language        TEXT       -- only set when category='languages'
concept         TEXT       -- only set when category='languages'
template        TEXT       -- e.g., 'lang-v2', 'guide-v3'
ring            INTEGER    -- priority tier
status          TEXT       -- queued | drafted | approved | staged | published
source          TEXT       -- 'planner' | 'antigravity' (default 'planner')
draft_path      TEXT
published_url   TEXT
created_at      TEXT
updated_at      TEXT
```

**`pipeline_runs`** — audit log of subagent invocations.

### 11.2 Status lifecycle

```
            Planner             Writer            Manual            staging.py        publish.py
[absent] ──────────► queued ──────────► drafted ──────► approved ──────► staged ──────► published
                                                          ▲
                                                          │ (Ingest + Antigravity QA flow)
                                                          │
            [absent] ──Ingest──► drafted ──Antigravity QA──┘  (auto-approved, never rejected)
```

### 11.3 Key invariants

- A `slug` is unique forever (no reuse, no recycling).
- `category='languages'` rows always have non-null `language` AND `concept`. URL is **always** `/languages/{language}/{concept}/` — never derived from filename.
- `source='antigravity'` rows skip Planner and Writer entirely.
- A row in `status='published'` is immutable — re-publishing means a new row.

---

## 12. CI Workflows (GitHub Actions)

Both workflows live in the **content workspace** repo (`devnook-content`), not this one.

### 12.1 `.github/workflows/drip-publish.yml`

| Field | Value |
|-------|-------|
| Trigger | `schedule: cron '0 8 * * *'` (08:00 UTC daily) |
| Default count | 2 posts/run |
| Secrets used | `GH_PAT`, `DEVNOOK_REPO_PAT`, `GOOGLE_SERVICE_ACCOUNT_JSON` |
| Steps | (a) checkout content workspace, (b) checkout devnook repo to `./devnook/`, (c) set `DEVNOOK_PATH`, (d) install deps, (e) `python agents/publish/publish.py --count 2` |

### 12.2 `.github/workflows/on-demand-publish.yml`

| Field | Value |
|-------|-------|
| Trigger | `workflow_dispatch` (manual) |
| Inputs | `count` (default 2), `category` (optional) |
| Use case | Catch up after a backlog; rush a specific category |
| Same secrets as drip |

### 12.3 Why two PATs?

- `GH_PAT` — generic access for the workflow itself (clone, push back to content repo if needed).
- `DEVNOOK_REPO_PAT` — narrow-scope PAT used only for the cross-repo push to `devnook`. Separated so it can be rotated independently.

---

## 13. Environment Variables

### 13.1 Required (content workspace)

| Var | Purpose | Where used |
|-----|---------|------------|
| `ANTHROPIC_API_KEY` | Claude API access for subagents | All subagent runs (when invoked outside Claude Code main session) |
| `DEVNOOK_REPO_PAT` | GitHub PAT, push access to `syedjawad11/devnook` | `publish.py` |
| `GH_PAT` | General GitHub access | CI workflows |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Path to GSC service account JSON | `gsc_ping.py` |

### 13.2 Optional

| Var | Default | Purpose |
|-----|---------|---------|
| `DEVNOOK_PATH` | `../devnook` (relative to content workspace) | Where the site repo working tree lives locally |

### 13.3 Site repo

| Var | Purpose |
|-----|---------|
| `ANTHROPIC_API_KEY` | Builder subagent invocations (when run outside Claude Code) |

---

## 14. Memory System Inventory

Claude Code persists memories in `C:\Users\Syed Jawad Hassan\.claude\projects\c--Users-Syed-Jawad-Hassan-Desktop-devnook\memory\`. Index lives at `MEMORY.md`.

### 14.1 DevNook-scoped memories (loaded for this repo)

| File | Type | Summary |
|------|------|---------|
| `project_devnook.md` | project | Active project devnook.dev, 7-stage plan, always check CLAUDE.md first |
| `project_subagent_architecture.md` | project | 5-subagent design replacing Python pipeline |
| `feedback_adsense_deferral.md` | feedback | Never suggest AdSense until 50k visitors/month — user's explicit decision |
| `project_broken_links_plan.md` | project | 75/89 related links 404 — two causes + Option A fix |

### 14.2 Claude-workspace memories (separate project, NOT auto-loaded here)

Lives in `C:\Users\Syed Jawad Hassan\.claude\projects\c--Users-Syed-Jawad-Hassan-Desktop-claude-workspace\memory\`. Eight memories covering user profile, infrastructure, business ideas, outreach agent, Tuesday plan, local setup, C-drive cleanup, white taskbar icon. **Do not cross-load into DevNook sessions unless explicitly relevant.**

---

## 15. Important Decisions Log (Guardrails)

> Replicated from `CLAUDE.md`. If you forget these, you will break something.

| # | Decision | Impact |
|---|----------|--------|
| 1 | No Tailwind | All styles in `tokens.css` custom properties |
| 2 | All tools client-side only | 18 tools, no Workers, no AI-powered tools |
| 3 | Static output (not hybrid) | `output: 'static'`, no adapter — satori crashes Workers runtime |
| 4 | Global CSS in `public/styles/` not `src/styles/` | Astro only copies `public/` to `dist/` |
| 5 | PostCard prop is `href` not `slug` | All 5 call sites use `href` |
| 6 | `tools/[slug].astro` uses `import.meta.glob` | Dynamic `await import()` crashes Vite static analysis |
| 7 | Never call `build-tool.py build_tool()` for existing tools | Writes page that collides with dynamic route |
| 8 | Auto internal links plugin (rehype, build-time) | `devnookUrlBuilder` required for language posts |
| 9 | Use `@astrojs/sitemap@3.2.1` not custom | Custom sitemap was broken; v3.7+ incompatible with Astro 4.x |
| 10 | Related posts auto-derived at render time (session 27) | `PostLayout.astro` builds related list from `getCollection()`; `frontmatter.related_posts` unused |
| 11 | Linker retired (session 25) | Replaced by `auto-internal-links` plugin |
| 12 | Content pipeline is external | No registry/staging/publish in this repo |
| 13 | Language post URLs must use `concept`, not filename | `publish.py.validate_language_links()` enforces; `link_utility.py._url_for_row()` was correct — bug was agents bypassing |
| 14 | Auto-internal-links plugin covers all categories | Not language-only — scans full `contentDir` |
| 15 | Related callouts plugin (session 32) | Build-time rehype; max 3 callouts; opt-out via frontmatter |
| 16 | No H1 in markdown body (session 42) | `PostLayout.astro` renders `frontmatter.title` as `<h1>`. Body H1 → "Multiple H1" Ahrefs flag. Pipeline patched. |

---

## 16. Stage Progression History

| Stage | Description | Status | Completed |
|-------|-------------|--------|-----------|
| 1 | Skills (foundational reference docs) | ✅ | 2026-04-10 |
| 2 | Dev Team (Builder subagent) | ✅ | 2026-04-10 |
| 3 | Tools Team (18 client-side tools) | ✅ | 2026-04-11 |
| 4 | Content Pipeline Core (registry, schema) | ✅ | 2026-04-12 |
| 5 | Content Pipeline Write (Writer subagent) | ✅ | 2026-04-12 |
| 6 | Publishing (publish.py + GSC ping) | ✅ | 2026-04-13 |
| 7 | Launch (live at devnook.dev) | ✅ | 2026-04-15 |
| 8 | Subagent Architecture (5-subagent design replaces Python LLM calls) | ✅ | 2026-04-17 |
| 9 | Workspace Split (pipeline moved to `devnook_content_workspace/`) | ✅ | 2026-04-25 |
| 10 | Cross-repo CI + Cleanup (drip-publish.yml, dormant scripts) | ✅ | 2026-04-25 |

**Recent session highlights:**

- **#41 (2026-05-04)** — Fixed all 308 redirects from Ahrefs audit. 172 link replacements across 60 content files.
- **#42 (2026-05-06)** — Removed duplicate H1 from 7 posts + patched content pipeline (writer.md, antigravity-qa.md, seo-writing-rules.md) so it can never recur.

---

## 17. Playbooks (with commands)

> Every command in this section is copy-paste runnable. PowerShell syntax (use `;` not `&&`).

### Playbook A — Daily drip publish (automatic)

**Trigger:** GitHub Actions cron `08:00 UTC` daily.

**What happens automatically:**
1. Action checks out content workspace and devnook into `./devnook/`.
2. Runs `python agents/publish/publish.py --count 2`.
3. Publisher moves 2 oldest staged posts → `devnook/src/content/`.
4. Commits + pushes to `devnook:main`.
5. Cloudflare Pages deploys within ~60s.
6. GSC Indexing API pinged per URL.

**Staging cutoff:** Stage approved posts before 08:00 UTC. If you stage later than that, the next cron tick is tomorrow — that day's slot is missed and cannot be recovered without a manual on-demand publish (Playbook B).

**Manual override:**
```powershell
# Run drip locally (if you have the env set up)
cd C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace
$env:DEVNOOK_PATH = "C:\Users\Syed Jawad Hassan\Desktop\devnook"
python agents/publish/publish.py --count 2
```

### Playbook B — On-demand publish burst

**Use case:** Catch up after a backlog or push a specific category.

**Via GitHub Actions UI:**
1. Open `devnook-content` → Actions → "On-demand publish".
2. Run workflow with `count=5`, optional `category=blog`.

**Locally:**
```powershell
cd C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace
python agents/publish/publish.py --count 5 --category blog
```

**Dry-run first:**
```powershell
python agents/publish/publish.py --count 5 --dry-run
```

### Playbook C — Generate a new content batch (editorial flow)

This is the **Planner → Writer → manual approve → staging** loop.

```powershell
# Step 1: Open Claude Code in content workspace
cd C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace
# (open Claude Code session here)
```

In Claude:
```
Spawn Planner subagent with BATCH_SIZE=10, RING_FILTER=1, CATEGORY_FILTER=blog
→ inserts 10 queued rows

Spawn Writer subagent with MAX_POSTS=10, MODE=full
→ produces 10 markdown drafts in drafts/blog/

Review drafts manually (read each in editor)
```

Then approve + stage:
```powershell
# Manually flip status to approved in registry (or via helper)
# Then stage:
python agents/content-team/staging.py --count 10 --category blog
```

The next cron tick will start publishing them 2/day.

### Playbook D — Ingest Antigravity language batch

**Setup:** Drop Gemini-scraped markdown into `C:\Users\Syed Jawad Hassan\Desktop\web_content\output\`.

```powershell
cd C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace
# (open Claude Code session)
```

In Claude:
```
Spawn Ingest subagent with SOURCE_DIR=web_content/output, DB_PATH=registry.db
→ files moved to drafts/languages/{lang}/{concept}.md, registry rows inserted with source='antigravity'

Spawn Antigravity QA subagent
→ cleans each draft (removes body H1, strips ## Related, validates URLs)
→ flips status to 'approved'
```

Stage + publish:
```powershell
python agents/content-team/staging.py --count 20 --category languages
# Wait for cron, OR push manually:
python agents/publish/publish.py --count 5 --category languages
```

### Playbook E — Add a new client-side tool

```powershell
cd c:\Users\Syed Jawad Hassan\Desktop\devnook
# (open Claude Code session)
```

In Claude:
```
Spawn Builder subagent with task:
  "Create new tool: <tool-name>. Batch: <Formatter|Encoder|Generator|Tester>.
   Inputs: <description>. Outputs: <description>.
   Follow tool-build-patterns.md exactly:
     - HTML at public/tools/<slug>.html (client-side only)
     - Astro slug page already exists at src/pages/tools/[slug].astro
     - Register in tools index if needed
   Verify: npm run build clean, 0 errors."
```

After Builder reports done:
```powershell
npm run build         # final verification
git status
git add public/tools/<slug>.html src/...
git commit -m "feat: add <tool-name> tool"
git push origin main
```

### Playbook F — Bug fix in Astro/component/layout

```powershell
cd c:\Users\Syed Jawad Hassan\Desktop\devnook
# (open Claude Code session)
```

In Claude:
```
Spawn Builder subagent with task description + file paths + reproduction steps.
Builder runs npm run build before reporting done.
```

### Playbook G — Run SEO audit

```powershell
cd c:\Users\Syed Jawad Hassan\Desktop\devnook
D:\miniconda3\python.exe scripts/seo_audit.py
# Output: audits/seo_audit_YYYY-MM-DD.csv
```

Review the CSV: word counts, readability scores, keyword density, similarity matches. Add issues to `auditlog.md` if action needed.

### Playbook H — Fix trailing slashes after a content drop

```powershell
cd c:\Users\Syed Jawad Hassan\Desktop\devnook
D:\miniconda3\python.exe scripts/fix_trailing_slashes.py
# In-place edits across src/content/
git diff --stat
git add src/content/
git commit -m "seo: ensure trailing slashes on internal links"
git push origin main
```

### Playbook I — Investigate broken internal links

```powershell
cd C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace
python agents/content-team/fix_broken_links.py --mode report
# Review console output
# If safe to auto-fix:
python agents/content-team/fix_broken_links.py --mode fix
```

### Playbook J — Re-run Ahrefs / external crawler

1. Trigger crawl in Ahrefs UI for `devnook.dev`.
2. Export issues as CSV.
3. Drop CSV in `<devnook>/` (e.g., `Sheet1.csv`).
4. In Claude session, ask: "Analyze Sheet1.csv and propose fix plan grouped by issue type."
5. Execute fixes via Builder or content-pipeline subagents per category.

### Playbook K — Local site dev

```powershell
cd c:\Users\Syed Jawad Hassan\Desktop\devnook
npm install            # first time only
npm run dev            # localhost:4321
```

To verify production build before pushing:
```powershell
npm run build
npm run preview        # serves dist/ on local port
```

### Playbook L — Cloudflare deploy verification

After `git push origin main`:
1. Open Cloudflare Pages dashboard → `devnook` project.
2. Watch latest deployment turn green (~60–90s).
3. Spot-check live URL of the changed file.

If deploy fails:
- Check the build log for the failing step (almost always `astro build` errors).
- Reproduce locally with `npm run build`.
- Common culprits: stale `node_modules` cache, missing frontmatter field, plugin error.

### Playbook M — Emergency content rollback

```powershell
cd c:\Users\Syed Jawad Hassan\Desktop\devnook
git log --oneline -20            # find the bad commit
git revert <commit-sha>           # safer than reset
git push origin main
# Cloudflare auto-deploys the revert
```

Then sync registry on content workspace side:
```powershell
cd C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace
# Manually mark the rolled-back posts back to 'staged' (or 'approved') in registry.db
# (use sqlite3 CLI or a helper)
```

### Playbook N — Rotate `DEVNOOK_REPO_PAT`

1. Generate new fine-grained PAT on GitHub: scope = `Contents: read+write` on `syedjawad11/devnook` only.
2. Update GitHub Actions secret in `devnook-content` repo settings.
3. Update local `.env` if you run `publish.py` locally.
4. Revoke old PAT.

### Playbook O — Adding a new frontmatter template

1. Define the template ID (e.g., `blog-v6`) and shape in `agents/skills/content-schema.md`.
2. Update Writer prompt at `agents/subagent-prompts/writer.md` to reference it.
3. Add validation rules in `qa-rejection-criteria.md` if rejection criteria differ.
4. Update `src/content/config.ts` in the site repo if any new frontmatter fields need schema validation.
5. Test: queue 1 post with new template → run Writer → verify draft → publish to staging in dry-run.

### Playbook P — Pause/resume the drip

**Pause:**
- GitHub → `devnook-content` → Settings → Actions → Disable workflows
- OR comment out the `schedule:` line in `drip-publish.yml` and commit

**Resume:**
- Re-enable in UI or restore the cron line.

### Playbook Q — Diagnose "post published but not on site"

1. Confirm registry status: should be `published`.
2. Check the cross-repo push: in the devnook repo run `git fetch origin main && git log origin/main -5 --oneline` — was the publish commit pushed? Do not rely on local `HEAD`; the publisher pushes from CI, so your local clone is always potentially behind.
3. Check Cloudflare deploy logs — did the build succeed?
4. Confirm the file actually exists at `src/content/{category}/{slug}.md` on the deployed commit.
5. If file missing: `validate_language_links()` likely skipped it. Re-run with `--dry-run` and inspect logs.

### Playbook R — Start a new Claude session correctly

**This repo:**
1. Open Claude Code in `c:\Users\Syed Jawad Hassan\Desktop\devnook`.
2. Claude auto-reads `CLAUDE.md`.
3. Do NOT auto-read `archives/decisions-archive.md` or prior transcripts.
4. Begin with: "Next session priorities" from CLAUDE.md.

**Content workspace:**
1. Open Claude Code in `C:\Users\Syed Jawad Hassan\Desktop\devnook_content_workspace`.
2. Read its `CLAUDE.md` (separate from this one).
3. Verify `registry.db` is present and last-modified date matches expectations.

---

## 18. Verification Checklist

Use this whenever you suspect drift from the documented state.

### 18.1 Site repo invariants

- [ ] `npm run build` clean, 0 errors, 95+ pages emitted
- [ ] `src/content/` contains `blog/`, `guides/`, `cheatsheets/`, `languages/{lang}/`
- [ ] No file in `src/content/` has a body `# Title` H1 (Decision #16)
- [ ] `public/styles/tokens.css` exists; no Tailwind in `package.json`
- [ ] `astro.config.mjs` registers both `auto-internal-links` and `related-callouts`
- [ ] Sitemap generated as `dist/sitemap-0.xml` (not `sitemap-1.xml`)
- [ ] `PostCard.astro` uses `href` prop (grep all call sites)
- [ ] `tools/[slug].astro` uses `import.meta.glob`, not `await import()`

### 18.2 Content pipeline invariants

- [ ] `registry.db` accessible; `posts` and `pipeline_runs` tables exist
- [ ] All 5 subagent prompts exist in `agents/subagent-prompts/`
- [ ] All 4 content skills exist in `agents/skills/`
- [ ] `publish.py` is the only script that runs `git push` to devnook
- [ ] `.github/workflows/drip-publish.yml` cron is `0 8 * * *`
- [ ] Secrets configured: `GH_PAT`, `DEVNOOK_REPO_PAT`, `GOOGLE_SERVICE_ACCOUNT_JSON`

### 18.3 Cross-repo seam

- [ ] `DEVNOOK_REPO_PAT` push works (test with empty commit if needed)
- [ ] Cloudflare deploys on push to `main`
- [ ] GSC service account JSON is valid

### 18.4 Deprecated items not accidentally re-active

- [ ] `run-pipeline.py` NOT imported anywhere
- [ ] `seo_optimizer.py` NOT imported anywhere
- [ ] `link_utility.py` NOT imported by `publish.py` or subagents
- [ ] `seed.py` NOT in any cron or workflow

---

## 19. Glossary

| Term | Definition |
|------|------------|
| **Antigravity** | Gemini-scraped language drafts pulled from `web_content/output/` into the pipeline via the Ingest subagent. |
| **Builder** | Site-side subagent (Sonnet) that handles all Astro/component/tool work. |
| **Concept** | The canonical slug for a language post (e.g., `async-await`). Distinct from filename. URL is always `/languages/{language}/{concept}/`. |
| **Cross-repo push** | The single git push from `publish.py` (content workspace) → `devnook:main`, authenticated by `DEVNOOK_REPO_PAT`. |
| **Drip publish** | Cron-driven 2-posts/day publish via `drip-publish.yml`. |
| **FIFO by id** | Strict ordering of staged posts by `registry.posts.id` ASC. Used because mtime is unreliable under GitHub Actions checkout. |
| **GSC ping** | Google Search Console Indexing API call (`URL_UPDATED`) for each newly-published URL. |
| **Plan mode** | Claude Code mode where edits are restricted to a single plan file; ExitPlanMode required to begin execution. |
| **Programmatic posts** | Auto-generated language posts (e.g., "how to async await in python", "how to async await in javascript"). The bulk of the 1,000+ post count. |
| **Registry** | The SQLite database at content-workspace-root `/registry.db` tracking every post's lifecycle. |
| **Rehype plugin** | Astro/unified build-time HTML AST transformer. Used for auto-internal-links + related-callouts. |
| **Ring** | Priority tier on a queued post — Planner uses `RING_FILTER` to pick high-priority topics first. |
| **Skill** | A reference markdown file loaded into a subagent's context (not invokable on its own). |
| **Staging** | The `content-staging/` directory — FIFO queue between "approved by QA" and "published to site". |
| **Subagent** | A prompt file invoked via the `Agent()` tool; isolated context window, returns a single message to the orchestrator. |
| **Template** | One of 22 frontmatter shapes (e.g., `lang-v2`, `guide-v3`, `blog-v4`, `cheatsheet-v2`, `tool-exp-v1`). Defines required fields + word floor. |
| **Workflow A / B / C / D** | A = editorial content batch; B = new tool; C = bug fix; D = Antigravity language batch. |

---

## Appendix — Where to find more detail

- **Per-session changes:** `CLAUDE.md` (this repo) + `CLAUDE.md` in content workspace.
- **SEO issues + fix plans:** `auditlog.md`.
- **Manual workflow reference:** `workspace_rules.md`.
- **Historical workspace split plan:** `update_plan.md`.
- **Decision archaeology:** `archives/decisions-archive.md` (open on demand only).

---

*End of SOP. Update this file whenever an agent, skill, script, or workflow changes. The CLAUDE.md log captures per-session deltas; this SOP captures the steady state.*
