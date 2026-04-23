# DevNook — Archived Decisions

> Historical decisions moved out of CLAUDE.md. These are **context / rationale only** — not live guardrails. Orchestrator reads on demand ("why did we X?"), not every session.

---

| Decision | Reason | Impact |
|----------|--------|--------|
| Plain Python scripts | No containers, no cloud scheduler | Local execution, simpler debugging |
| SQLite + markdown for memory | No external memory framework | registry.db + PIPELINE_LOG.md |
| 22 templates, round-robin | Prevents spam signals | Template counters tracked in registry.db |
| Drip publish (not bulk) | Google Scaled Content Abuse mitigation | 2–3 posts/day via GitHub Actions |
| Always uninstall adapter when removing from config | Package presence kept Pages in Functions mode even with `output: 'static'` | `npm uninstall` in same commit as config removal |
| Nuclear reset beats debugging poisoned Pages state | Sessions 6–7 couldn't clear Functions-mode flags via commits or cache | Delete + recreate Pages project; preserve repo + DNS |
| Subagent architecture replaces Python LLM pipeline | Monolithic Opus session burned context and token budget | 5 subagents (Haiku/Sonnet) in isolated contexts; Opus as orchestrator only |
