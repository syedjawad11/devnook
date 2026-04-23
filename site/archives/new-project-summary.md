# DevNook Project — Complete Blueprint

> **Last updated — April 10, 2026**
> This document captures all decisions, architecture, and plans discussed across sessions.
> **Status:** Site design ✅ | Agent architecture ✅ | Infrastructure ✅ | Cost model ✅ | Publishing strategy ✅ | Content templates ✅ (22 template files generated) | Domain ✅ (devnook.dev) | Skills system designed ✅ | Folder structure finalised ✅

---

## 1. Site Concept

**What we're building:** A content-first developer resource site with integrated tools.
- **Primary:** 1,000+ programming tutorials, guides, cheat sheets, and blog posts
- **Secondary:** 50+ free browser-based developer tools
- **Monetization:** Google AdSense
- **Long-term:** Potential micro-SaaS evolution

**The unifying theme:** Web formats, standards, and developer utilities. Every piece of content naturally links to a tool, and every tool page links to educational content. This creates an internal linking flywheel that Google rewards.

**Domain:** devnook.dev ✅ — registered on Cloudflare (April 2026)
- **TLD:** .dev — HTTPS enforced, developer-focused, ~$11/yr on Cloudflare at wholesale
- **Next:** Claim matching X/Twitter handle and create GitHub org under devnook

---

## 2. Content Strategy — The Concentric Rings Model

Content is organized in rings, from highest-conversion to highest-volume:

### Ring 1 — Tool-adjacent content (~80 posts)
Directly links to tools. "What is JSON", "Markdown syntax guide", "SEO meta tags explained."
Highest conversion to tool usage but lowest volume.

### Ring 2 — Web dev fundamentals (~200 posts)
"What are APIs", "HTTP status codes", "How DNS works", "What is REST."
Same audience as tools, broader topic coverage.
Template: "What is [concept]" — 40+ HTTP codes, 20+ web concepts, 30+ dev tools, etc.

### Ring 3 — Programming across languages (~600+ posts) ← Volume engine
"What is [concept] in [language]" — the programmatic SEO goldmine.
50 concepts × 12 languages = 600 posts from one template.

**Languages:** Python, JavaScript, TypeScript, Go, Rust, Java, C#, PHP, Ruby, Swift, Kotlin, C++

**Concepts:** loops, arrays, functions, classes, async/await, error handling, file I/O, HTTP requests, string methods, closures, decorators, generators, pattern matching, modules, testing, type systems, inheritance, interfaces, enums, maps/dicts, recursion, regular expressions, date/time, JSON parsing, environment variables, command line args, concurrency, database queries, unit testing, package management, and more.

### Bonus — AI + comparisons + editorial (~200 posts)
"[X] vs [Y]", "[Language] cheat sheet", "Best AI prompts for [task]"
Mix of programmatic and hand-written editorial content.

---

## 3. Site Structure & Navigation

### Top Navigation (6 items)
```
[Logo] DevToolKit    Languages | Guides | Cheat sheets | Tools | Blog    [Search /]
```

### URL Structure

```
/                              → Homepage
/languages                     → All 12 language cards with post counts
/languages/python              → Python hub (intro, 52 concept links, related tools)
/languages/python/loops        → Individual concept post
/guides                        → Filterable guide grid
/guides/what-is-json           → Individual guide
/cheatsheets                   → Visual cheat sheet gallery
/cheatsheets/python            → Individual cheat sheet
/tools                         → Tool directory with category filters
/tools/json-formatter          → Individual tool page
/blog                          → Blog feed with category filters
/blog/json-vs-yaml             → Blog post
/compare                       → Comparisons hub (optional standalone)
/compare/python-vs-go          → Comparison post
/about                         → About page
/contact                       → Contact
/privacy                       → Privacy policy
/sitemap.xml                   → Auto-generated
```

### Page Types & Layouts

**Homepage:** Hero with search → Featured tools grid → Language cards → Cheat sheet strip → Latest blog posts → Footer

**Language hub (/languages/python):** Breadcrumb → Language name + color dot → Stats (52 tutorials, 1 cheat sheet, 8 tools) → Numbered concept grid → Related tools

**Tool page (/tools/json-formatter):** Breadcrumb → Tool name → Tool interface (input/output/buttons) → Sidebar: "What is this" explainer + related tools + cheat sheet link

**Blog (/blog):** Category filters (All, Comparisons, AI, Tutorials, How-tos) → Featured post (full width) → Post card grid

**Individual post:** Content area + sidebar with related posts and tools

### Key Design Decisions
- Language cards use each language's official GitHub color for instant recognition
- Every tool page has SEO content below the tool (200-300 word explainer)
- Internal linking: every language post → language hub + cheat sheet + relevant tools
- Every guide → matching tool + matching cheat sheet + comparison posts

---

## 4. HTML/CSS Design Template

**File:** `devtoolkit-template.html` (attached separately)

**Design specifications:**
- **Fonts:** Outfit (body) + JetBrains Mono (code/monospace)
- **Colors:** Neutral base (#fafaf8), accent blue (#2563eb), green/amber/coral/purple for categories
- **Cards:** 1px border, 16px radius, subtle hover shadow + translateY(-1px)
- **Nav:** Sticky, 60px height, active tab with bottom border accent
- **Hero:** Gradient bg, search bar with icon, quick-access tag pills
- **Responsive:** Grid breakpoints at 768px

**Template includes 4 page mockups** (switchable via tabs):
1. Homepage — full landing experience
2. Language hub — /languages/python
3. Tool page — /tools/json-formatter
4. Blog — post listing with filters

---

## 5. Agent Architecture — 3 Local Teams, 7 Scripts

> **Architecture decision (April 2026):** Google Cloud infrastructure dropped entirely in favour of local execution + GitHub Actions. No dedicated orchestration layer — agents don't run concurrently and require no inter-agent coordination. Agent memory is handled via structured files (DECISIONS.md + SQLite registry), not a memory framework.

> **Architecture decision (April 2026 — evening):** Claude Code CLI sub-agent framework evaluated and rejected for this project. Reasons: (1) locks all agents to Anthropic API pricing, destroying the Gemini free-tier cost model; (2) designed for interactive developer workflows, not unattended weekly batch jobs; (3) no parallelism or nested delegation needed — sequential pipeline is correct. Plain Python scripts calling LLM APIs directly remain the architecture. The one exception: dev and tools agents (scaffold.py, update.py, build-tool.py) could optionally be restructured as Claude Code sub-agents in future since they already use Claude Sonnet — but this is not required and not planned.

All agents are **plain Python scripts** triggered manually or via GitHub Actions cron. No containers, no cloud scheduler, no message bus.

**API keys required:**
- `GEMINI_API_KEY` — content pipeline (all 6 steps)
- `OPENROUTER_API_KEY` — dev and tools agents (Claude Sonnet via OpenRouter)
- No direct Anthropic API key needed

---

### Team 1 — Developer Team

**Purpose:** Build and maintain the Astro website codebase.
**When triggered:** Manually. Once during initial setup, then only when site structure needs updating.
**Memory input:** `/agents/DECISIONS.md` + `/agents/skills/astro-conventions.md` injected into system prompt on every run.

#### `scaffold.py` — Run once
- Initialises the Astro project from scratch
- Creates all shared components (Nav, Footer, SearchBar, PostCard, ToolCard, LangCard, CheatSheetCard, Breadcrumb, Sidebar, AdUnit)
- Builds all 7 layouts (Base, LanguagePost, LanguageHub, Guide, CheatSheet, BlogPost, ToolPage)
- Configures sitemap plugin, SEO meta, OG image generation via Satori
- Sets up tokens.css design system and global.css
- **Model:** Claude Sonnet via OpenRouter
- **Skills loaded:** `astro-conventions.md`

#### `update.py` — Run as needed (bi-weekly or after content milestones)
- Auto-generates new language hub pages when a new language reaches 5+ posts
- Updates homepage featured sections
- Runs Lighthouse CI audit and flags regressions
- Appends any new architectural decisions to DECISIONS.md
- **Model:** Claude Sonnet via OpenRouter
- **Skills loaded:** `astro-conventions.md`

---

### Team 2 — Tools Developer Team

**Purpose:** Build and deploy client-side browser-based tools. All tools run entirely in the browser — no server, no API calls, no usage costs.
**When triggered:** Manually. During initial setup for the first batch, then on-demand for new additions.
**Memory input:** `/agents/DECISIONS.md` + `/agents/skills/tool-build-patterns.md` injected into system prompt.

#### `build-tool.py` — Run per tool
- Takes a tool spec file (name, description, inputs/outputs, category) as input
- Generates the Astro tool component with full UI
- All logic runs client-side in the browser (no Cloudflare Worker required)
- Writes SEO explainer content (200–300 words) below the tool interface
- Updates the tool registry in SQLite
- **Model:** Claude Sonnet via OpenRouter
- **Skills loaded:** `astro-conventions.md` + `tool-build-patterns.md`

> **Decision (April 2026):** All tools are client-side only. No AI-powered tools, no Cloudflare Workers for tool logic. Reasons: (1) API costs become uncontrollable at scale as traffic grows; (2) client-side tools are faster and work offline; (3) privacy advantage — nothing leaves the user's browser; (4) zero ongoing infrastructure cost. AI-powered tools may be reconsidered post-launch once traffic and revenue justify the cost.

**Tool list (18 tools — all client-side):**

*Batch 1 — Formatters & Converters (weeks 1–2):*
JSON Formatter, HTML Formatter, SQL Formatter, CSV ↔ JSON Converter, Markdown to HTML Converter

*Batch 2 — Encoders & Decoders (weeks 2–3):*
Base64 Encoder/Decoder, URL Encoder/Decoder, JWT Decoder, Hash Generator

*Batch 3 — Generators & Builders (weeks 3–4):*
UUID Generator, Meta Tag Generator, Sitemap Generator, README Generator, Cron Expression Builder

*Batch 4 — Testers & Utilities (weeks 4–5):*
Regex Tester, Diff Checker, Colour Converter

> **Decision — No language/role-based skills for dev and tools agents.** These agents do not need generic "TypeScript developer" or "full-stack developer" skill files. They are already capable of writing TypeScript, Astro, and Cloudflare Workers. What they need is project-specific knowledge — captured in `astro-conventions.md` and `tool-build-patterns.md`. Generic skills would introduce patterns that conflict with the actual project setup.

---

### Team 3 — Content Developer Team

**Purpose:** Research keywords, plan, write, QA, and stage content for publishing.
**When triggered:** Weekly manual run on your local desktop (typically Sunday). You run `python run-pipeline.py` — there is no scheduler or VPS. The script runs all 6 steps sequentially on your machine. After the run completes and you push `/content-staging/` to GitHub, your machine can be off. GitHub Actions handles the daily drip from that point automatically.
**Memory input:** SQLite registry queried before every generation step.

#### `run-pipeline.py` — Weekly batch runner
A single script that orchestrates the full content pipeline in sequence:

**Step 1 — Keyword Agent**
- Pulls from Google Autocomplete API using seed matrix (50 concepts × 12 languages + Ring 1/2 topics)
- Scores keywords by opportunity (estimated volume / difficulty + 1)
- Checks registry.db to skip already-published or already-queued topics
- Writes discovered keywords to registry.db with status `discovered`
- **Model:** Gemini 2.5 Flash (free tier)
- **Skills loaded:** none (no LLM generation — pure data processing)

**Step 2 — Planner Agent**
- Reads `discovered` keywords from registry
- Ranks by opportunity score
- Assigns content type (programmatic vs editorial) and matching template variant
- Generates content brief: target keyword, secondary keywords, template ID, title, slug, internal link targets
- Updates status to `queued`
- **Model:** Gemini 2.5 Flash (free tier)
- **Skills loaded:** `content-schema.md`

**Step 3 — Writer Agent**
Two modes based on content type:
- **Programmatic:** Load template variant → inject variables → Gemini Flash-Lite enhancement for natural language variety. Fast, cheap, consistent.
- **Editorial:** Full generation from brief (comparisons, AI posts, tutorials). Gemini 2.5 Pro.
- Output: Markdown files with complete Astro frontmatter
- Updates status to `drafted`
- **Model:** Gemini Flash-Lite (programmatic) / Gemini 2.5 Pro (editorial)
- **Skills loaded:** `content-schema.md` + `seo-writing-rules.md` + `devnook-brand-voice.md`

**Step 4 — SEO Optimizer Agent**
- Inserts 5–8 contextual internal links per post
- Validates meta descriptions (150–160 chars)
- Checks heading hierarchy (one H1, logical H2/H3 nesting)
- Validates keyword density (1–2%)
- Adds schema.org structured data (Article, HowTo, FAQPage as appropriate)
- Generates related content sidebar data
- Updates status to `optimized`
- **Model:** Gemini Flash-Lite (free tier)
- **Skills loaded:** `content-schema.md` + `seo-writing-rules.md`

**Step 5 — QA Agent**
- Duplicate detection: rejects if >85% similarity to any existing post in registry
- Code block syntax validation
- Internal link validation (slugs exist in registry)
- Frontmatter completeness check
- Minimum word count enforcement (800 words programmatic, 1,500 editorial)
- Heading structure check
- Sets status to `approved` or `needs-revision` with reason logged
- **Model:** Gemini Flash-Lite (free tier)
- **Skills loaded:** `content-schema.md` + `seo-writing-rules.md` + `qa-rejection-criteria.md`

**Step 6 — Staging**
- Moves all `approved` markdown files into `/content-staging/`
- Logs batch summary (generated, approved, rejected, rejection reasons) to `PIPELINE_LOG.md`
- No LLM needed

---

## 6. Publishing Pipeline — Stockpile + Drip Model

The content team generates in bulk weekly. GitHub Actions distributes daily at a safe pace. Your machine does not need to be on after the weekly generation run.

```
Weekly (manual — you run locally):
  content-team/run-pipeline.py
    → Generates 30–60 posts per run
    → QA filters to approved set
    → Drops .md files into /content-staging/
    → Commits /content-staging/ to staging branch

GitHub Actions — drip-publish.yml (runs daily at 08:00 UTC):
    → Picks 2–3 posts from /content-staging/
    → Moves to /src/content/ (appropriate subdirectory)
    → Commits to main
    → Cloudflare Pages auto-deploys
    → Pings Google Search Console Indexing API for each new URL
```

### Cloudflare Build Usage
- 2–3 posts batched per daily commit = 1 build/day
- ~30–35 builds/month at launch cadence
- ~90–100 builds/month at full speed
- **500 build/month limit is not a constraint at any planned publishing cadence**

---

## 7. Agent Memory — No Framework Required

No external memory system (Engram or otherwise). Memory is handled by three structured files injected as context:

### `/agents/DECISIONS.md` — For dev and tools agents
A plain text architecture log. Injected into the system prompt of every Developer Team and Tools Developer Team run.

```markdown
# Architecture Decisions

## 2026-04 — No Tailwind
All styles use tokens.css custom properties. No PostCSS pipeline.
Do not introduce Tailwind or utility class frameworks.

## 2026-04 — Tool page structure
All tools use ToolPage.astro layout. Tool iframe is sandboxed.
SEO explainer content sits below the tool, not in sidebar.

## 2026-04 — Agent framework
Plain Python scripts calling LLM APIs directly. No Claude Code CLI
sub-agent framework. No orchestration layer. Sequential execution only.

## 2026-04 — Skills architecture
Project-specific skill files in agents/skills/. No generic language
or role-based skills. Each agent loads only the skills relevant to
its task. Skills are injected into system prompts at run time.

## 2026-05 — [Add entries as decisions are made]
```

Append to this file whenever a significant decision is made — whether by you or an agent. This is the agent's institutional memory.

### `/agents/content-team/registry.db` — For content agents
SQLite database. Queried before every generation step.

```
Table: posts
  slug | title | content_type | template_id | status | published_date | keywords

Table: rejected_patterns
  pattern_description | reason | date_added

Table: template_counters
  content_type | last_variant
```

Status flow: `discovered` → `queued` → `drafted` → `optimized` → `approved` → `staged` → `published`

### `/agents/content-team/PIPELINE_LOG.md` — Weekly run log
Appended by Step 6 (Staging) after each weekly pipeline run. Gives the Writer and QA agents pattern awareness over time without changing the SQLite schema.

```markdown
## Run: 2026-05-04
- Posts generated: 48
- Posts approved: 41
- Posts rejected: 7
- Rejection reasons: word count (4), duplicate (2), broken internal link (1)
- Templates used: lang-v1 (12), lang-v3 (10), guide-v2 (8), blog-v1 (6), ...
```

---

## 8. Agent Skills System

> **Decision (April 2026 — evening):** A dedicated `agents/skills/` directory holds project-specific knowledge files. Each skill file is injected into the relevant agent's system prompt at run time. Skills are not generic role descriptions — they contain only devnook-specific conventions, schemas, and rules. This avoids agents inventing patterns that conflict with the actual project setup, and makes quality thresholds easy to tune without touching agent code.

### The 6 Skill Files

| File | Injected into | Purpose |
|------|--------------|---------|
| `astro-conventions.md` | scaffold.py, update.py, build-tool.py | Component names, layout files, tokens.css rules, Satori OG setup, no-Tailwind rule, URL structure |
| `tool-build-patterns.md` | build-tool.py | Tool spec JSON schema, Tier 1 vs Tier 2 distinction, Cloudflare Worker patterns, SEO explainer block placement |
| `content-schema.md` | Planner, Writer, SEO Optimizer, QA | All 5 frontmatter schemas, 22 template IDs, valid content types, status flow, category values, slug conventions |
| `seo-writing-rules.md` | Writer, SEO Optimizer, QA | Word count floors, heading hierarchy rules, keyword density target (1–2%), meta description length, internal link count per post |
| `devnook-brand-voice.md` | Writer only | Tone guidelines, code example framing, what to avoid, sentence style, audience level assumptions |
| `qa-rejection-criteria.md` | QA only | Exact thresholds: similarity %, minimum word counts, required frontmatter fields, link validation rules, code block requirements |

### Build order
Write skill files before writing any agent implementation code. Recommended sequence:
1. `content-schema.md` — highest leverage, used by 4 agents
2. `seo-writing-rules.md` — defines quality before a single post is written
3. `qa-rejection-criteria.md` — QA thresholds should be explicit, not buried in code
4. `devnook-brand-voice.md` — tone and style for the writer
5. `astro-conventions.md` — project setup reference for dev agents
6. `tool-build-patterns.md` — tool generation reference

---

## 9. Development Workflow

> **Decision (April 2026 — evening):** All agent implementation work is done in VS Code with the Claude extension. The project folder (`devnook/`) is opened as the workspace. This gives Claude full file context (templates, DECISIONS.md, skill files, project summary) without re-explaining the project each session. Skill files are written directly into `agents/skills/` — no copy-pasting from chat.

**Setup:**
1. Create the full folder structure on your desktop (see Section 13)
2. Open `devnook/` in VS Code
3. Install the Claude extension
4. Keep `project-summary-updated.md` and `DECISIONS.md` in the workspace root for context

---

## 10. LLM Model Routing — Three-Layer Strategy

### Layer 1: Gemini Free Tier (primary — $0/month)
| Model | RPD Limit | Used For |
|-------|-----------|----------|
| Flash-Lite | 1,000/day | Programmatic writing, SEO optimization, QA checks |
| Flash | 250/day | Planner, keyword agent |
| 2.5 Pro | 100/day | Editorial content (comparisons, tutorials) |

### Layer 2: OpenRouter Free Models (fallback — $0/month)
28+ free models available (DeepSeek R1, Llama 3.3 70B, etc.)
~20 RPM, 200 RPD limits. Catches overflow when Gemini is rate-limited.

### Layer 3: OpenRouter Paid Models (safety net — ~$0–3/month)
DeepSeek V3 at ~$0.25/MTok input. Only used if both free tiers are exhausted.

### Dev and Tools Agents (manual, infrequent — ~$3–5/month total)
Claude Sonnet via OpenRouter. Code quality justifies the cost; these run rarely.

---

## 11. Cost Breakdown

### Monthly Estimate

| Category | Cost |
|----------|------|
| LLM — content pipeline (Gemini free tier) | $0 |
| LLM — dev + tools agents (Sonnet, infrequent) | ~$3–5 |
| LLM — overflow fallback | ~$0–3 |
| Google Cloud (dropped entirely) | $0 |
| Cloudflare Pages + Workers | $0 (free tier) |
| GitHub + GitHub Actions | $0 |
| Google Autocomplete + GSC | $0 |
| Domain (.dev) | ~$1/month (~$11/year) |
| **Total** | **~$5–8/month** |

---

## 12. Image Strategy

### OG/Featured Images (every post — auto-generated)
- **Method:** Build-time generation using Satori + Resvg during `astro build`
- **Templates:** 5 designs (Language post, Guide, Tool, Blog, Cheat sheet)
- **Variables:** Title, category pill, language color bar, URL — pulled from frontmatter
- **Output:** 1200×630 PNG saved to `public/og/[slug].png`
- **Cost:** $0 (runs locally during build)

### Body Images
- **Programmatic posts:** Skip entirely. Code blocks are the visual content.
- **Editorial posts:** Occasional screenshots or diagrams only.
- **Cheat sheets:** Generate downloadable PNG/PDF version (link magnet).

### What We're NOT Using
- No stock photos
- No AI-generated illustrations
- No Unsplash/Pexels integration

---

## 13. Publishing Velocity — Safe Ramp-Up Plan

### The Core Concern
Google's Scaled Content Abuse policy targets pages produced primarily to manipulate rankings. SpamBrain detects structural repetition and thin content more than raw volume. A natural growth trajectory with genuine engagement signals is the primary protection.

### Safe Ramp-Up Schedule

| Period | Posts/month | Per day avg | Cumulative | Focus |
|--------|-------------|-------------|------------|-------|
| Launch day | 15–20 seed | Batch | 20 | Seed across all categories. 10+ tools live. Submit GSC. |
| Month 1 | ~50 | 1–2 | ~70 | Daily cadence via drip. Fill Python + JS hubs. Manual promotion. |
| Month 2 | 100–150 | 3–5 | ~200 | Increase if GSC indexing is normal. Add language hubs. |
| Month 3 | ~200 | 6–7 | ~400 | 2 months history. Fill remaining hubs. Full blog cadence. |
| Month 4–5 | 200–300 | 7–10 | ~700 | Sandbox lifting. Long-tail keywords ranking. Accelerate. |
| Month 6+ | 300+ | 10–15 | 1,000+ | Full pipeline speed. |

### Time to 1,000 posts: ~6 months

### Critical Mitigation Strategies
1. **Template variation:** 4–5 different structures per content type — the single most important spam signal mitigation
2. **Launch tools first:** Real engagement signals from day one separate you from content farms
3. **Manual promotion months 1–2:** Reddit, Dev.to, Hacker News, Twitter/X
4. **GSC as circuit breaker:** Weekly check. Pause the GitHub Actions drip immediately if manual action warnings appear
5. **Content length:** 800+ words programmatic, 1,500+ editorial
6. **E-E-A-T from day one:** About page, author bio, and at least one social profile before GSC submission

---

## 14. Repository & Folder Structure

```
devnook/                              ← root on your desktop (also the git repo)
│
├── src/                              ← Astro project (built by Developer Team)
│   ├── components/
│   │   ├── Nav.astro
│   │   ├── Footer.astro
│   │   ├── SearchBar.astro
│   │   ├── PostCard.astro
│   │   ├── ToolCard.astro
│   │   ├── LangCard.astro
│   │   ├── CheatSheetCard.astro
│   │   ├── Breadcrumb.astro
│   │   ├── Sidebar.astro
│   │   └── AdUnit.astro
│   ├── layouts/
│   │   ├── Base.astro
│   │   ├── LanguagePost.astro
│   │   ├── LanguageHub.astro
│   │   ├── Guide.astro
│   │   ├── CheatSheet.astro
│   │   ├── BlogPost.astro
│   │   └── ToolPage.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── languages/index.astro
│   │   ├── languages/[lang]/index.astro
│   │   ├── languages/[lang]/[concept].astro
│   │   ├── guides/index.astro
│   │   ├── tools/index.astro
│   │   ├── blog/index.astro
│   │   └── cheatsheets/index.astro
│   ├── content/                      ← Live content (drip publisher moves files here)
│   │   ├── languages/
│   │   ├── guides/
│   │   ├── blog/
│   │   └── tools/
│   └── styles/
│       ├── global.css
│       └── tokens.css
│
├── content-staging/                  ← Approved posts waiting to be dripped
│
├── agents/
│   ├── DECISIONS.md                  ← Shared architecture memory (all dev + tools agents)
│   │
│   ├── skills/                       ← Project-specific skill files (injected at run time)
│   │   ├── astro-conventions.md      ← scaffold.py + update.py + build-tool.py
│   │   ├── tool-build-patterns.md    ← build-tool.py
│   │   ├── content-schema.md         ← Planner, Writer, SEO Optimizer, QA
│   │   ├── seo-writing-rules.md      ← Writer, SEO Optimizer, QA
│   │   ├── devnook-brand-voice.md    ← Writer only
│   │   └── qa-rejection-criteria.md  ← QA only
│   │
│   ├── dev-team/
│   │   ├── scaffold.py
│   │   └── update.py
│   │
│   ├── tools-team/
│   │   ├── build-tool.py
│   │   └── tool-specs/               ← One JSON spec file per tool
│   │
│   └── content-team/
│       ├── run-pipeline.py
│       ├── registry.db               ← SQLite: posts, rejected_patterns, template_counters
│       ├── PIPELINE_LOG.md           ← Weekly run log (appended by Step 6)
│       └── templates/                ← 22 .md template files ✅
│           ├── language-post/
│           │   ├── lang-v1.md        ← Definition First
│           │   ├── lang-v2.md        ← Problem First
│           │   ├── lang-v3.md        ← Code First
│           │   ├── lang-v4.md        ← Concept Across Languages
│           │   └── lang-v5.md        ← Tutorial / Build-Along
│           ├── guide/
│           │   ├── guide-v1.md       ← Encyclopedia
│           │   ├── guide-v2.md       ← Quick Answer + Deep Dive
│           │   ├── guide-v3.md       ← Problem → Solution
│           │   └── guide-v4.md       ← Reference Card
│           ├── blog/
│           │   ├── blog-v1.md        ← Head-to-Head Comparison
│           │   ├── blog-v2.md        ← Use-Case Driven Comparison
│           │   ├── blog-v3.md        ← Listicle
│           │   ├── blog-v4.md        ← Deep-Dive Editorial
│           │   └── blog-v5.md        ← How-To Tutorial
│           ├── cheatsheet/
│           │   ├── cheatsheet-v1.md  ← Syntax Reference
│           │   ├── cheatsheet-v2.md  ← Task-Oriented
│           │   ├── cheatsheet-v3.md  ← Tiered Beginner→Advanced
│           │   └── cheatsheet-v4.md  ← Two-Column Comparison
│           └── tool-explainer/
│               ├── tool-exp-v1.md    ← What + Why + How
│               ├── tool-exp-v2.md    ← Problem First
│               ├── tool-exp-v3.md    ← Feature Focused
│               └── tool-exp-v4.md    ← FAQ Style
│
└── .github/
    └── workflows/
        └── drip-publish.yml          ← Daily cron: stages → content → commit → deploy
```

---

## 15. What's Still Pending

- [x] **Content templates** — frontmatter schemas defined for all 5 content types (see Section 16)
- [x] **Template variation strategy** — 4–5 structural variants per content type defined; selection via round-robin counter in `registry.db`; **22 `.md` template files generated and ready** ✅
- [x] **Domain registration** — devnook.dev registered on Cloudflare ✅
- [x] **Agent architecture** — 3 teams, 7 scripts, fully defined ✅
- [x] **Skills system** — 6 skill files designed, build order defined ✅
- [x] **Folder structure** — finalised (see Section 14) ✅
- [ ] **Skill files** — write all 6 files into `agents/skills/` (next task — in VS Code)
- [ ] **Tool spec files** — JSON spec for each of the 18 client-side tools (all tools are client-side; no AI-powered tools planned at launch)
- [ ] **Agent implementation** — actual Python code for each script
- [ ] **Astro project setup** — run scaffold.py to initialise the real project
- [ ] **drip-publish.yml** — GitHub Actions workflow for daily drip
- [ ] **Content seed list** — the first 20 pages to publish on launch day
- [ ] **Promotion strategy** — specific subreddits, communities, and outreach plan
- [ ] **AdSense integration** — placement strategy, AdUnit component

---

## 16. Content Templates — Schema & Variant Plan

> **Status:** Complete (April 2026). 22 template files generated into `agents/content-team/templates/`.

### Variant Selection Strategy

Round-robin per content type via `registry.db`. Add a `template_counters` table:

```sql
CREATE TABLE template_counters (
  content_type  TEXT PRIMARY KEY,
  last_variant  INTEGER DEFAULT 0
);
```

Before each generation call the agent reads `last_variant`, computes `next = (last_variant + 1) % variant_count`, updates the counter, and passes `template_id` into the prompt. Deterministic, even distribution, no extra LLM call needed.

---

### Frontmatter Schemas (Summary)

**Language posts** — `language`, `concept`, `difficulty`, `template_id`, `tags`, `related_tools`, `related_posts`, `related_cheatsheet`, `published_date`, `og_image`
**Guides** — `category` (web-concepts | http | dns | apis | formats | dev-tools | security), `template_id`, `tags`, `related_tools`, `related_posts`, `related_cheatsheet`, `published_date`, `og_image`
**Blog posts** — `category` (comparison | editorial | ai | tutorial | how-to), `author`, `featured`, `template_id`, `tags`, `related_tools`, `related_posts`, `published_date`, `og_image`
**Cheat sheets** — `subject`, `category` (language | web | tools | formats), `template_id`, `tags`, `related_posts`, `related_tools`, `download_png`, `published_date`, `og_image`
**Tool pages** — `tool_slug`, `category` (formatter | encoder | converter | generator | tester | analyzer | decoder), `tier` (client-side), `template_id`, `tags`, `related_tools`, `related_guides`, `related_cheatsheet`, `og_image`

Full detail: `content-template-plan.md` (planning doc)

---

## 17. Post-Launch Review Checklist — 30 Days After Launch

> **Reminder:** Schedule this review ~30 days after the first post goes live and GSC is submitted.

- [ ] **Analytics Agent — GSC feedback loop:** Assess whether it's worth wiring GSC click and impression data back into the Keyword Agent's scoring. Currently the pipeline is one-way (research → write → publish). At 30 days you'll have real performance data — topics with traction should be prioritised over estimated opportunity scores. This is the trigger to implement the Analytics Agent properly.
- [ ] **Indexing rate:** What % of submitted URLs are indexed? If below 50%, investigate crawl budget and internal linking before accelerating publishing cadence.
- [ ] **Template performance:** Any content type underperforming significantly in impressions? May indicate a structural issue with its templates — review and revise before generating more of that type.
- [ ] **QA rejection rate:** Check `PIPELINE_LOG.md`. If rejection rate is consistently above 20%, review the QA agent's thresholds in `qa-rejection-criteria.md` or the Writer agent's prompts — no code changes needed, just update the skill file.
- [ ] **Tool engagement:** Are tools getting any usage? Check Cloudflare Analytics. Tools with zero traffic after 30 days may need better internal linking from content.
- [ ] **AdSense readiness:** Google requires meaningful traffic before approval. 30 days is usually too early — but assess whether to apply or wait another 30–60 days.

---

*Document last updated — April 10, 2026*
*Session changes: All tools revised to client-side only — Code Explainer removed, Markdown Preview replaced with Markdown to HTML Converter, Tier 1/Tier 2 AI distinction removed and replaced with batch-based build order, tool frontmatter tier field updated to client-side only, build-tool.py Cloudflare Worker generation removed, decision logged.*
*Previous version: 10 Tier 1 client-side + 8 Tier 2 AI-powered tools (18 total)*
*Current version: 18 client-side tools, organised into 4 build batches, no AI tooling, no Cloudflare Workers for tools*
*Domain: devnook.dev (registered April 9, 2026)*
