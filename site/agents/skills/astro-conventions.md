# DevNook — Astro Conventions

## Project Identity
- Framework: Astro (latest stable)
- Hosting: Cloudflare Pages
- Domain: devnook.dev
- Node version: 20+

## Styling Rules
- NO Tailwind. All styles use tokens.css custom properties.
- Global design tokens live at: `src/styles/tokens.css`
- Component-scoped styles use Astro's `<style>` blocks only.
- Fonts: Outfit (body/UI) + JetBrains Mono (code blocks), loaded via @font-face in tokens.css.
- Breakpoint: 768px (single breakpoint, mobile-first).

## Token Reference (key values)
- --color-bg: #0d0d0d
- --color-surface: #161616
- --color-border: #2a2a2a
- --color-text: #e8e8e8
- --color-text-muted: #8a8a8a
- --color-accent: #6ee7b7 (mint green)
- --color-accent-2: #7c3aed (purple)
- --font-body: 'Outfit', sans-serif
- --font-mono: 'JetBrains Mono', monospace
- --radius-sm: 4px
- --radius-md: 8px
- --radius-lg: 16px
- --space-1 through --space-8: 4px increments (4, 8, 12, 16, 24, 32, 48, 64)

## URL Structure
- `/` → Homepage
- `/languages/{lang}` → Language hub (e.g., /languages/python)
- `/languages/{lang}/{concept}` → Individual concept post
- `/guides/{slug}` → Educational guide
- `/cheatsheets/{subject}` → Cheat sheet
- `/tools/{slug}` → Browser-based tool
- `/blog/{slug}` → Blog/comparison post
- `/languages/` → Languages index
- `/guides/` → Guides index
- `/tools/` → Tools index

## Component Naming
- PascalCase filenames: `NavBar.astro`, `ToolCard.astro`, `PostCard.astro`
- Layouts in `src/layouts/`: `BaseLayout.astro`, `PostLayout.astro`, `ToolLayout.astro`
- Shared components in `src/components/`
- Page files in `src/pages/` follow URL structure

## Content Collections
- Language posts: `src/content/languages/{lang}/{concept}.md`
- Guides: `src/content/guides/{slug}.md`
- Cheat sheets: `src/content/cheatsheets/{subject}.md`
- Blog posts: `src/content/blog/{slug}.md`
- Tools: `src/content/tools/{slug}.md` (SEO explainer page)
- Tool components: `src/components/tools/{slug}.astro`

## Key Components to Know
- `NavBar.astro` — sticky top nav, 6 items: Tools, Languages, Guides, Cheatsheets, Blog, Search
- `Footer.astro` — simple 2-column footer with links + copyright
- `PostCard.astro` — card for content list pages (title, description, tags, date)
- `ToolCard.astro` — card for tools index (name, description, tier badge, icon)
- `LanguageCard.astro` — card for language hubs (logo, post count, featured topics)
- `CodeBlock.astro` — syntax-highlighted code block (JetBrains Mono, dark theme)
- `TagBadge.astro` — small pill/badge for category/tag display
- `SearchBar.astro` — client-side fuzzy search (Fuse.js)
- `OGImage.astro` — Satori-based OG image generator (used at build time)

## Important Rules
1. Never use Tailwind or utility classes.
2. Every page must include BaseLayout which handles <head>, NavBar, Footer.
3. Content is Markdown with YAML frontmatter — never JSX in content files.
4. Tool pages have TWO files: the Astro component (interactive) + the content .md (SEO text).
5. Use Astro's content collections API with `getCollection()` — not custom file reads.
6. All internal links must be relative (no hardcoded domain).
7. Images: only OG images auto-generated; no body images for programmatic posts.
