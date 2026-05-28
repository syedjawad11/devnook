# DevNook — Monorepo Architecture

## Overview

This repo contains two sub-projects that work together to run devnook.dev:

| Sub-project | Path | Purpose |
|-------------|------|---------|
| Site | `site/` | Astro static site, deployed via Cloudflare Pages |
| Pipeline | `pipeline/` | Content generation pipeline (Stage 0 → QA → publish) |

## Detailed docs

- **Site architecture**: `site/docs/ARCHITECTURE.md`
- **Pipeline architecture**: `pipeline/CLAUDE.md`
- **Redesign plan**: `site/docs/devnook-redesign-stages.md`

## How they connect

`pipeline/agents/publish/publish.py` writes finished markdown to `site/src/content/`.
Cloudflare Pages auto-deploys on every push to `main`.

The pipeline runs via GitHub Actions (`.github/workflows/`), setting `DEVNOOK_PATH=site`
so publish.py knows where to write content.

## Cloudflare Pages settings

| Setting | Value |
|---------|-------|
| Build command | `npm run build` |
| Build output dir | `site/dist` |
| Root directory | `site` |
