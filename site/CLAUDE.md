# DevNook — Dev Workspace

> Always read this file first at the start of a new session.
> Content pipeline lives in `../devnook_content_workspace/` — no pipeline code or registry here.
> Detailed pipeline architecture → `docs/ARCHITECTURE.md`

## Session start

Do not auto-read: `docs/archives/`, `docs/session-history.md`. Start from this file + MEMORY.md only.

---

## TODO (session #61)

1. **Day 1 routine PAUSED** — `trig_01E8rdMC6qNREuvBY8shLUfg` disabled. `keyword_set_id=5` (`git-commands-cheat-sheet-developers`) conflicts with existing `/cheatsheets/git-commands-cheatsheet`. Decide: (a) update existing, (b) repurpose cluster, or (c) delete id=5 and run Stage 0 on fresh cluster.
2. **Verify Day 2 run** (2026-05-29 ~14:00 UTC) — check `data/pipeline-b-runs.log` for `slug=react-vs-angular-vs-vue-comparison`; visit `https://devnook.dev/blog/react-vs-angular-vs-vue-comparison`. Routine: `trig_013SxsubDU4oN2FcJr7SYAyP`.
3. **Redesign stages in progress** — `docs/devnook-redesign-stages.md`. Stages 1–4 complete; Stage 5 done this session.

---

## Project Overview

**DevNook** (devnook.dev) — developer resource site. ~91 posts + 18 client-side browser tools.
**Stack:** Astro + Cloudflare Pages. `main` branch auto-deploys on every push.
**Content:** Published by `../devnook_content_workspace/` via PAT — no pipeline code lives here.

---

## Key Paths

| Path | Purpose |
|------|---------|
| `src/` | Astro site source |
| `src/layouts/` | Layouts (PostLayout.astro, etc.) |
| `src/content/` | Published markdown content (written by content workspace) |
| `src/components/` | Astro components |
| `public/styles/` | Global CSS (NOT src/styles/) |
| `src/pages/tools/[slug].astro` | Tools dynamic route |
| `public/tools/*.html` | Tool HTML files |
| `src/plugins/auto-internal-links/index.mjs` | Build-time internal link insertion |
| `src/plugins/related-callouts/index.mjs` | Build-time related post callouts |
| `agents/subagent-prompts/builder.md` | Dev subagent prompt |
| `agents/skills/astro-conventions.md` | Astro coding conventions |
| `scripts/seo_audit.py` | SEO audit — `D:\miniconda3\python.exe scripts/seo_audit.py` |
| `scripts/fix_trailing_slashes.py` | Trailing slash fixer |
| `docs/` | Architecture docs, session history, planning docs |

---

## Dev Subagent

```
ORCHESTRATOR (Sonnet main session)
  └── Builder (Sonnet) — agents/subagent-prompts/builder.md
      Handles: Astro edits, new tools, npm run build verification
```

Spawn with: `Agent(prompt=open('agents/subagent-prompts/builder.md').read(), ...)`

**Workflow B** — new tool: Orchestrator → Builder → review + commit
**Workflow C** — bug fix: Orchestrator → Builder → review + commit

---

## Important Decisions

> Live guardrails — forgetting these will break something.

| Decision | Impact |
|----------|--------|
| No Tailwind | All styles in `tokens.css` custom properties |
| All tools client-side only | 18 tools, no Workers, no AI-powered tools |
| Static output (not hybrid) | `output: 'static'`, no adapter — satori crashes Workers runtime |
| Global CSS in `public/styles/` not `src/styles/` | Astro only copies `public/` to `dist/`; absolute `/styles/*` refs need public/ |
| PostCard prop is `href` not `slug` | All 5 call sites use `href`; never rename to slug/url/path |
| `tools/[slug].astro` uses `import.meta.glob` | Dynamic `await import()` crashes Vite static analysis |
| Never call `build-tool.py build_tool()` for existing tools | Writes page that collides with dynamic route |
| Auto internal links plugin (rehype, build-time) | `src/plugins/auto-internal-links/index.mjs`; language concept URLs use `frontmatter.language`+`frontmatter.concept`, NOT filename |
| Use `@astrojs/sitemap@3.2.1` not custom | v3.7+ incompatible with Astro 4.x; generates `sitemap-0.xml` (0-indexed) |
| Related posts auto-derived at render time | `PostLayout.astro` builds related list from `getCollection()` — never from hand-written `## Related` sections. `frontmatter.related_posts` unused; leave as `[]`. |
| Content pipeline is external | No registry, staging, or publish scripts here. `src/content/` written by `../devnook_content_workspace/agents/publish/publish.py`. |
| Language post URLs use `concept`, not filename | Correct path: `/languages/{lang}/{concept}`. `publish.py` has `validate_language_links()` guard. |
| Auto-internal-links covers all categories | Scans full `contentDir` — guides, blog, cheatsheets, languages. Not language-only. |
| Related callouts plugin (session 32) | Injects up to 3 `<aside class="related-callout">` nodes at interior H2s. Per-post opt-out: `excludeRelatedCallouts: true`. |
| No H1 in markdown body | `PostLayout.astro` renders title as `<h1>`. Body `# Title` = duplicate H1, Ahrefs flags it. |
| Never use `[skip ci]` in devnook commits | Cloudflare Pages skips build. The `[skip ci]` in `drip-publish.yml` is intentional (content-workspace side only). |

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Builder subagent (if needed)
```

---

## How to Run

```bash
npm run dev        # Dev server
npm run build      # Production build (always verify before committing)
npm run preview    # Preview production build
```
