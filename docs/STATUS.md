# DevNook — Operational Status

> Single home for **ephemeral** state: active routines, content queue, and pending
> one-off tasks. The `CLAUDE.md` files hold durable instructions only and point here.
> Keep this file current; when an item is done, remove it (git history is the record).

**Last updated:** 2026-05-31

---

## Active routines

All routines run as remote CCR agents (`claude-sonnet-4-6`, source `syedjawad11/devnook`)
and publish via `git push origin HEAD`. Times in UTC; Malta is CEST (UTC+2).

| Routine | Trigger ID | Cron | Status | Notes |
|---------|-----------|------|--------|-------|
| Editorial publisher (`/blog/`, `/guides/`) | `trig_01Xc9GuTZmzJAQXXAD7KZXUs` | `0 23 * * *` (01:00 Malta) | ✅ Healthy | ER-9 `git push` bug fixed 2026-05-30 |
| Language publisher (`/languages/`) | `trig_015wteVF9kPq2mNxR7sT4wXz` | `0 3 * * *` (05:00 Malta) | ✅ Active | URL = frontmatter `concept`, not filename |
| Rewrite routine (thin `/languages/` posts) | `trig_01VJJqhYwLmK3nP8rT5vX2zQ` | `0 1 * * *` (03:00 Malta) | ✅ Active | Overwrites in place; never changes slug/concept |
| Pipeline B (keyword-first cluster) | `trig_012dkTjBKiB8M9ASkKZ1c1Gk` | `0 14 * * *` (16:00 Malta) | ⛔ Disabled | Re-enable only after a `keyword_sets` row is `status='ready'` |

Routine "how it works" / gotchas are documented in memory
(`project_editorial_routine`, `project_language_routine`, `project_rewrite_routine`).

---

## Content queue

| Section | Queued | Notes |
|---------|--------|-------|
| Editorial | 4 posts (ids 95–98) | Next 23:00 UTC run picks id 95 `api-rate-limiting-guide`. Top up from `editorial_opportunity` primary tier (252 keywords) when low. |
| Language | 5 posts (ids 99–103) | — |
| Rewrite | 5 thinnest posts seeded | From `language_rewrite_queue`. |

Verify against the DB (from `pipeline/`):
`python -c "import sqlite3; print(sqlite3.connect('data/registry.db').execute(\"SELECT status, content_type, COUNT(*) FROM posts GROUP BY 1,2\").fetchall())"`

---

## Pending one-off tasks

- [ ] **Resolve Pipeline B cluster conflict** — `keyword_set_id=6`
  (`git-commands-cheat-sheet-developers`) collides with the existing
  `/cheatsheets/git-commands-cheatsheet`. Decide: (a) update the existing cheatsheet,
  (b) repurpose the cluster, or (c) delete id=6 and re-seed. Re-enable the Pipeline B
  routine once a `keyword_sets` row is `status='ready'`.
- [ ] **Remove `DEVNOOK_REPO_PAT` secret** from `syedjawad11/devnook` — no longer needed
  in the monorepo.

---

## Recently completed (rolling — prune freely)

- 2026-05-31 — Archived legacy repo `syedjawad11/devnook-content` and removed the local
  `devnook_content_workspace/` folder (superseded by `pipeline/`).
- 2026-05-30 — Editorial routine ER-9 `git push origin HEAD` fix verified
  (`websockets-vs-http` published, live 200).
- 2026-05-30 — GSC Indexing API decommissioned (unsupported on `sc-domain:` properties).
- 2026-05-29 — Redesign stages 1–13 complete (see `site/docs/devnook-redesign-stages.md`).
