# DevNook — Monorepo

> Read this first. Then navigate to the relevant sub-project.

## Structure

| Directory | Contents |
|-----------|---------|
| `site/` | Astro site (devnook.dev) — see `site/CLAUDE.md` |
| `pipeline/` | Content pipeline — see `pipeline/CLAUDE.md` |
| `docs/` | Monorepo-level architecture and planning docs |

## Quick start

```bash
# Site development
cd site && npm run dev

# Content pipeline
cd pipeline && python agents/publish/publish.py --count 2
```

## Key wiring

- **Cloudflare Pages** builds from `site/` (Root dir = `site`, output dir = `dist`). Full settings + the `site/dist` gotcha → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **GitHub Actions** workflows: `.github/workflows/` (drip-publish, on-demand-publish)
- **publish.py** reads `DEVNOOK_PATH=site` (set by CI; set it locally if running manually)
- **Registry DB**: `pipeline/data/registry.db`

## Current state

Operational state — active routines, content queue, pending one-off tasks — lives in one place: [`docs/STATUS.md`](docs/STATUS.md). The `CLAUDE.md` files hold durable instructions only.
