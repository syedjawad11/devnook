# DevNook Pipeline Run Log

---

## Run Template

```
## Run: YYYY-MM-DD

**Step 1 — Keyword Agent**
- Seeds used: [list of seed topics]
- Keywords discovered: X
- After deduplication: Y new keywords queued
- Duration: Xs

**Step 2 — Planner Agent**
- Items ranked: Y
- Items queued for writing: Z
- Template distribution: lang-v1: N, lang-v2: N, ...
- Duration: Xs

**Step 3 — Writer Agent**
- Items attempted: Z
- Drafts created: N
- Failures/retries: N
- Models used: Gemini Flash (N), Gemini Pro (N)
- Duration: Xs

**Step 4 — SEO Optimizer**
- Posts processed: N
- Internal links added: avg N per post
- Schema.org injected: N posts
- Duration: Xs

**Step 5 — QA Agent**
- Posts reviewed: N
- Approved: N
- Rejected: N (reasons: word count N, duplicate N, other N)
- Warnings: N
- Duration: Xs

**Step 6 — Staging**
- Files moved to /content-staging/: N
- Total in staging now: N
- Duration: Xs

**Total pipeline duration:** Xs
**Net new staged posts:** N
```

---

_Most recent runs at top._

[INGEST RUN] 2026-04-17 18:05:07 UTC processed=10 ingested=10 skipped_collision=0

[INGEST RUN] 2026-04-23 21:20:12 processed=9 ingested=9 skipped_collision=0
