# DevNook Architecture Decisions Log

This file records significant decisions made by agents or manually during development.
Format: Date | Decision | Reason

---

## Tools Architecture
- 2026-04-10 | All tools are client-side only — no AI-powered tools, no Cloudflare Workers | API costs uncontrollable at scale as traffic grows; client-side is faster and works offline; privacy advantage (nothing leaves the browser); zero ongoing infrastructure cost. AI-powered tools may be reconsidered post-launch once traffic and revenue justify the cost.
- 2026-04-10 | Tool count reduced from 50 to 18 | Focused on highest-value tools; all Tier 2 AI tools removed; some Tier 1 tools removed that are lower priority
- 2026-04-10 | Tier 1 / Tier 2 distinction replaced with 4 build batches | No tier concept needed when all tools are client-side; batches group by category similarity for efficient generation

## Template System
- 2024-XX-XX | Using 22 template IDs across 5 content types | Prevents duplicate structure patterns; round-robin via registry.db prevents repetition
- 2024-XX-XX | Template files stored in /templates/templates/ | Agents load them dynamically; no hardcoded structures

## Agent Architecture
- 2024-XX-XX | Plain Python scripts, no framework | No containers, no cloud scheduler; local execution is simpler and cheaper
- 2024-XX-XX | Gemini free tier as primary LLM | Cost optimization; Flash/Flash-Lite for bulk, 2.5 Pro for editorial
- 2024-XX-XX | OpenRouter (Sonnet) for dev/tools agents | Better code quality; used infrequently so cost is low

## Content Strategy
- 2024-XX-XX | No Tailwind | All styles use tokens.css custom properties; cleaner diffs, no purge complexity
- 2024-XX-XX | Safe ramp-up schedule | Google Scaled Content Abuse policy mitigation; starting at 1-2 posts/day

## Publishing
- 2024-XX-XX | GitHub Actions drip at 08:00 UTC | Consistent timing signals for Google crawlers
- 2024-XX-XX | GSC Indexing API after each publish | Speeds up crawl time for new posts

---
_Add new decisions above the line. Oldest decisions at bottom._
