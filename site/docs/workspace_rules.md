# DevNook — Workspace Rules & Manual Run Guide

> Reference doc for working across the three workspaces. Copy this into the content
> workspace (or keep open in a tab) when running manual content jobs.

---

## The Three Workspaces

| Workspace | Path | Role |
|---|---|---|
| **Content pipeline** | `devnook_content_workspace/` | Owns Planner, Writer, Ingest, QA, Publisher. All content commands run here. |
| **Astro site (devnook)** | `devnook/` | Publish target only. Cloudflare Pages auto-deploys on every push to `main`. Don't write content here manually. |
| **Antigravity / web_content** | `web_content/output/` | Drop zone for Gemini-scraped language drafts. Source for Ingest subagent. |

**Rule of thumb:** you only ever run commands in the **content workspace**. The devnook
repo is a destination; Antigravity is a source.

---

## Post Lifecycle (registry status → physical location)

```
queued     → row in agents/content-team/registry.db
drafted    → agents/content-team/drafts/{slug}.md          (Writer / Ingest output)
approved   → still in drafts/, registry flag flipped       (after review or QA pass)
staged     → content-staging/{slug}.md                     (FIFO queue, oldest mtime first)
published  → ../devnook/src/content/{category}/{slug}.md   (committed + pushed to devnook)
```

Only `staged` posts are visible to the publisher. Anything at `drafted` or `approved`
sits forever until you act on it.

---

## Who Schedules What

- **Daily drip cron:** `.github/workflows/drip-publish.yml` in the content workspace.
  Runs **08:00 UTC daily**, calls `publish.py --count 3`.
- The cron runs forever. After the current staged queue drains, it keeps firing — just
  no-ops if `staged` is empty. New staged posts auto-publish on the next 08:00 UTC tick.
- There is **no `scheduled_for` column** today. Publishing order is FIFO by file mtime.
  "Publish on date X at time Y" is not a built-in capability.
- The devnook repo does **not** schedule anything. It only receives pushes.

---

## Scenario 1 — Generate locally, do NOT publish

Use when you want drafts to sit for review, or to build a backlog without scheduling.

**In the content workspace:**

1. Run Planner → Writer subagents (or Ingest → Antigravity QA for language posts).
2. Drafts land in `agents/content-team/drafts/{slug}.md`, status `drafted`.
3. **Stop.** Do not run `staging.py`.

Result: files stay in `drafts/`, drip cron ignores them, devnook repo untouched.
Safe to leave indefinitely.

---

## Scenario 2 — Generate 2 guide posts and publish NOW

Same path the cron uses, just triggered by hand.

**In the content workspace:**

```bash
# 1. Generate (Claude Code session, subagents)
#    Planner → 2 guide keywords queued
#    Writer  → 2 drafts written, status=drafted
#    Review → status=approved

# 2. Stage
python agents/content-team/staging.py
#    moves all approved drafts → content-staging/, status=staged

# 3. Publish immediately
python agents/publish/publish.py --count 2
```

`publish.py` in one shot:
- Moves files `content-staging/` → `../devnook/src/content/{category}/{slug}.md`
- Updates registry to `published`
- Commits + pushes to the **devnook repo** (Cloudflare auto-deploys, ~1–2 min)
- Pings Google Search Console
- Commits registry + staging deletions back to content workspace

You never touch the devnook repo manually. You never wait for cron.

### ⚠️ Caveat — FIFO queue mixing

`publish.py --count 2` publishes the **2 oldest mtime** files in `content-staging/`,
not necessarily the ones you just wrote. If other approved drafts are sitting around:

- Either generate + stage + publish in one uninterrupted sitting, **or**
- Keep unrelated approved drafts at status `drafted` until your 2 guides are through.

Current `staging.py` moves *all* approved at once — no category/count filter.

---

## Scenario 3 — Antigravity (language) post, publish now

Languages category is **owned exclusively by Antigravity**. Planner + Writer must never
queue language posts.

**Drop Gemini drafts into `../web_content/output/`** (from Antigravity), then in the
content workspace:

```bash
# In Claude Code session, subagents:
#   Ingest          → reads web_content/output/, creates drafts, status=drafted
#   Antigravity QA  → fixes structure + SEO, status=approved (never rejects)

# Same publish path as Scenario 2:
python agents/content-team/staging.py
python agents/publish/publish.py --count N
```

Publisher doesn't care about origin — programmatic, editorial, antigravity all flow
through the same `staged` → `published` gate.

---

## Workspace Responsibility Matrix

| Step | Workspace | Action |
|---|---|---|
| Plan + write | content workspace | Planner + Writer subagents |
| Ingest scraped drafts | content workspace | Ingest subagent (reads `../web_content/output/`) |
| QA antigravity | content workspace | Antigravity QA subagent |
| Stage | content workspace | `python agents/content-team/staging.py` |
| Publish manually | content workspace | `python agents/publish/publish.py --count N` |
| Publish on schedule | content workspace | `drip-publish.yml` cron (08:00 UTC daily, 3/day) |
| Site build + deploy | devnook (Cloudflare Pages) | Automatic on push |
| Drafting language posts | Antigravity / Gemini | Output to `../web_content/output/` |

---

## Quick Commands

```bash
# Status check (registry counts by status + content type)
python -c "import sqlite3; db=sqlite3.connect('agents/content-team/registry.db'); [print(r) for r in db.execute('SELECT status, content_type, COUNT(*) FROM posts GROUP BY 1,2')]"

# Stage all approved drafts
python agents/content-team/staging.py

# Publish N posts now (also pushes to devnook + pings GSC)
python agents/publish/publish.py --count N

# Manual on-demand workflow (CI alternative)
# Trigger .github/workflows/on-demand-publish.yml from GitHub Actions UI
```

---

## Hard Rules (do not violate)

- **Languages category** → Antigravity only. Never Planner/Writer.
- **Antigravity QA never rejects** → fixes only, always sets `qa_status='passed'`.
- **Meta description ≥ 120 chars** → enforced by Writer + QA.
- **Word count** → 1500–2500 for antigravity; cheatsheet target under discussion.
- **Related posts** → never write a `## Related` section. PostLayout.astro auto-derives
  at render time. `frontmatter.related_posts` stays `[]`.
- **No Python LLM calls** → all generation goes through `Agent()` subagents.
- **`content-staging/` must be in `git add`** in CI workflows — `publish.py` uses
  `shutil.move()` which deletes from staging on publish.

---

## When Something Goes Wrong

| Symptom | Where to look |
|---|---|
| Posts not publishing on schedule | content workspace → Actions tab → `drip-publish.yml` runs |
| Wrong post published first | FIFO mtime order — touch the file you want first or stage selectively |
| Devnook build fails after publish | devnook repo → Cloudflare Pages dashboard → build logs |
| GSC ping fails | non-fatal — publish still succeeds, check `gsc_ping.py` logs |
| Registry / staging out of sync | re-run `python agents/content-team/staging.py` is idempotent on `approved` |
