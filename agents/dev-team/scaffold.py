#!/usr/bin/env python3
"""
DevNook Dev Team — scaffold.py
Generates the complete Astro project structure for devnook.dev.
Run once from the project root: python agents/dev-team/scaffold.py

Requires: ANTHROPIC_API_KEY environment variable
"""

import sys
import json
from pathlib import Path

from dotenv import load_dotenv

# Force UTF-8 stdout on Windows to handle Unicode characters in print statements
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load .env from project root so ANTHROPIC_API_KEY is available
_PROJECT_ROOT_FOR_ENV = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT_FOR_ENV / ".env")

# Allow imports from agents/utils/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.llm_router import route

SKILLS_DIR = Path("agents/skills")
PROJECT_ROOT = Path(".")

ASTRO_CONVENTIONS = (SKILLS_DIR / "astro-conventions.md").read_text(encoding="utf-8")
CONTENT_SCHEMA = (SKILLS_DIR / "content-schema.md").read_text(encoding="utf-8")

SYSTEM_PROMPT = f"""You are an expert Astro developer building devnook.dev — a developer resource site.
You produce complete, production-ready code with no placeholders, no TODOs, and no stub implementations.

Follow these conventions exactly:

{ASTRO_CONVENTIONS}

Additional content schema context:

{CONTENT_SCHEMA}

Rules:
- Output ONLY the raw file content. No markdown fences, no explanations, no preamble.
- Use exact CSS token names from tokens.css (--color-bg, --color-accent, etc.)
- Follow the component naming conventions (PascalCase .astro files)
- All styles via <style> blocks or tokens.css — never inline styles, never Tailwind
- TypeScript where applicable (.ts extensions, typed props in Astro frontmatter)
- All internal links are relative paths (no hardcoded domain)
"""


def generate_file(filename: str, description: str, context: str = "") -> str:
    """Call Claude to generate a single file's complete contents."""
    prompt = f"Generate the complete contents of `{filename}` for devnook.dev.\n\n{description}"
    if context:
        prompt += f"\n\nAdditional context for this file:\n{context}"
    print(f"    Calling Claude for {filename}...")
    result = route("frontend_dev", system=SYSTEM_PROMPT, prompt=prompt, max_tokens=4096)
    return result.text


def write_file(path: str, content: str):
    """Write content to file, creating parent directories as needed.

    Idempotent: skips any file that already exists, so re-running the
    scaffold only produces files that are genuinely missing. Note that
    the caller still pays for the LLM call even when we skip — use this
    to recover from partial scaffolds, not to cheaply re-run from scratch.
    """
    full_path = PROJECT_ROOT / path
    if full_path.exists():
        print(f"  · skip (exists) {path}")
        return
    import re
    # Strip markdown code fences that the LLM sometimes adds despite instructions
    content = re.sub(r"^```[a-z]*\n", "", content)
    content = re.sub(r"\n```\s*$", "", content)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"  ✓ {path}")


def scaffold():
    print("=== DevNook Scaffold — Starting ===\n")
    print("This will call Claude ~37 times via OpenRouter (~$0.30–0.50 estimated).\n")

    # ── 1. Config files ────────────────────────────────────────────────────────
    print("→ [1/8] Config files...")

    write_file("package.json", generate_file(
        "package.json",
        "Astro project package.json. Dependencies: astro (latest), @astrojs/cloudflare, "
        "@astrojs/sitemap, @astrojs/check, sharp, fuse.js, @resvg/resvg-js, satori. "
        "Scripts: dev, build, preview, check. Node engine: >=20."
    ))

    write_file("astro.config.mjs", generate_file(
        "astro.config.mjs",
        "Astro config for devnook.dev. Adapter: @astrojs/cloudflare (output: 'hybrid'). "
        "Integrations: sitemap (with filter to exclude /og/**), image optimization (sharp). "
        "Site: 'https://devnook.dev'. Content collections enabled."
    ))

    write_file("tsconfig.json", generate_file(
        "tsconfig.json",
        "TypeScript config for Astro project. Extend astro/tsconfigs/strict. "
        "Paths: @components/* → src/components/*, @layouts/* → src/layouts/*, "
        "@styles/* → src/styles/*, @utils/* → src/utils/*."
    ))

    # ── 2. Styles ──────────────────────────────────────────────────────────────
    print("→ [2/8] Styles...")

    write_file("src/styles/tokens.css", generate_file(
        "src/styles/tokens.css",
        "All CSS custom properties for devnook.dev. Must include:\n"
        "Colors: --color-bg (#0d0d0d), --color-surface (#161616), --color-border (#2a2a2a), "
        "--color-text (#e8e8e8), --color-text-muted (#8a8a8a), --color-accent (#6ee7b7), "
        "--color-accent-2 (#7c3aed), --color-error (#f87171), --color-success (#34d399).\n"
        "Fonts: @font-face for Outfit (body) and JetBrains Mono (code) loaded from Google Fonts CDN. "
        "--font-body: 'Outfit', sans-serif. --font-mono: 'JetBrains Mono', monospace.\n"
        "Spacing: --space-1 through --space-8 (4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px).\n"
        "Border radius: --radius-sm (4px), --radius-md (8px), --radius-lg (16px).\n"
        "Shadows: --shadow-sm, --shadow-md.\n"
        "Transitions: --transition-fast (150ms ease), --transition-base (250ms ease).\n"
        "Max widths: --max-w-content (720px), --max-w-site (1200px)."
    ))

    write_file("src/styles/global.css", generate_file(
        "src/styles/global.css",
        "Global CSS for devnook.dev. Import tokens.css first. "
        "Include: CSS reset (*, box-sizing: border-box, margin: 0), "
        "body base styles (background: var(--color-bg), color: var(--color-text), font: var(--font-body)), "
        "base link styles (color: var(--color-accent), underline on hover), "
        "base code/pre styles (font: var(--font-mono), background: var(--color-surface)), "
        "prose styles for article content (.prose h1-h4, p, ul, ol, blockquote, table, code), "
        "utility classes: .container (max-w-site + horizontal padding + centered), "
        ".sr-only (screen-reader only), .visually-hidden."
    ))

    # ── 3. Content collections config ──────────────────────────────────────────
    print("→ [3/8] Content config...")

    write_file("src/content/config.ts", generate_file(
        "src/content/config.ts",
        "Astro content collections config using zod. Define 5 collections:\n"
        "1. languages — fields: title, description, category ('languages'), language (string), "
        "concept (string), template_id, tags (string[]), related_posts (string[]), "
        "related_tools (string[]), published_date (string), og_image (string), word_count_target (number optional).\n"
        "2. guides — fields: title, description, category ('guides'), template_id, tags, "
        "related_posts, related_tools, published_date, og_image, word_count_target.\n"
        "3. cheatsheets — fields: title, description, category ('cheatsheets'), language (optional), "
        "template_id, tags, related_posts, related_tools, published_date, og_image, downloadable (boolean optional).\n"
        "4. blog — fields: title, description, category ('blog'), template_id, tags, "
        "related_posts, related_tools, published_date, og_image, word_count_target.\n"
        "5. tools — fields: title, description, category ('tools'), tool_slug, template_id, "
        "tags, related_tools, related_content, published_date, og_image, word_count_target.\n"
        "Export as: export const collections = { languages, guides, cheatsheets, blog, tools }."
    ))

    # ── 4. Layouts ─────────────────────────────────────────────────────────────
    print("→ [4/8] Layouts...")

    write_file("src/layouts/BaseLayout.astro", generate_file(
        "src/layouts/BaseLayout.astro",
        "Base layout for all pages. Props: title (string), description (string), "
        "ogImage (string, default '/og/default.png'), canonicalUrl (string optional), noindex (boolean optional). "
        "Includes: <head> with charset, viewport, title, meta description, OG tags (og:title, og:description, "
        "og:image, og:type, og:url), Twitter card, canonical link, sitemap link, "
        "link to tokens.css + global.css. "
        "Body structure: <NavBar />, <main><slot /></main>, <Footer />. "
        "Import and use NavBar.astro and Footer.astro components."
    ))

    write_file("src/layouts/PostLayout.astro", generate_file(
        "src/layouts/PostLayout.astro",
        "Layout for all content posts (language posts, guides, blog, cheatsheets). "
        "Extends BaseLayout. Props: frontmatter (the content collection entry data). "
        "Structure: article with class='prose', header section (h1 title, meta bar with date + tags), "
        "two-column layout on desktop: main content slot (left, wider) + sidebar (right, narrower) "
        "with table of contents (static, populated via JS from h2/h3 elements) + related posts widget. "
        "Mobile: single column, sidebar below content. "
        "Include Breadcrumb.astro above the title. "
        "Include RelatedPosts.astro below content if related_posts is non-empty."
    ))

    write_file("src/layouts/ToolLayout.astro", generate_file(
        "src/layouts/ToolLayout.astro",
        "Layout for tool pages. Extends BaseLayout. Props: frontmatter (tools collection entry). "
        "Structure: tool component slot at top (full-width), then below it the SEO explainer content "
        "from the .md file (rendered as prose). The tool component slot must be above the fold. "
        "Include Breadcrumb.astro. Below the tool: Related Tools section if related_tools non-empty."
    ))

    # ── 5. Components ──────────────────────────────────────────────────────────
    print("→ [5/8] Components...")

    write_file("src/components/NavBar.astro", generate_file(
        "src/components/NavBar.astro",
        "Sticky top navigation bar. Dark background (--color-surface), 1px bottom border (--color-border). "
        "Left: DevNook logo/wordmark (text, links to /). "
        "Right: nav links — Tools (/tools/), Languages (/languages/), Guides (/guides/), "
        "Cheatsheets (/cheatsheets/), Blog (/blog/). Plus a search icon button that opens SearchBar. "
        "Mobile: hamburger menu toggling a slide-down nav. "
        "Active link detection using Astro.url.pathname. "
        "Accent color on active/hover links."
    ))

    write_file("src/components/Footer.astro", generate_file(
        "src/components/Footer.astro",
        "Simple footer. Dark background (--color-surface), top border. "
        "Two columns: left — DevNook logo + tagline ('Developer resources, fast.') + copyright. "
        "Right — two link groups: Resources (Tools, Languages, Guides, Cheatsheets, Blog) "
        "and Legal (Privacy Policy /privacy/, Terms /terms/). "
        "Mobile: stacks to single column."
    ))

    write_file("src/components/PostCard.astro", generate_file(
        "src/components/PostCard.astro",
        "Card component for content list pages. Props: title, description, slug, tags (string[]), "
        "date (string), category. "
        "Renders as a card with: --color-surface background, --color-border border, --radius-md, "
        "hover effect (border becomes --color-accent). "
        "Title as h2 (linked to the post slug), description as p, tags as TagBadge components below. "
        "Date formatted as human-readable (e.g. 'Apr 2025'). Import TagBadge.astro."
    ))

    write_file("src/components/ToolCard.astro", generate_file(
        "src/components/ToolCard.astro",
        "Card for tools index. Props: name, description, slug, category, tier (1 or 2), icon (string). "
        "Renders a card with tool name as h3 (linked to /tools/{slug}), description, "
        "a tier badge (Tier 1: 'Client-side', Tier 2: 'AI-Powered') in --color-accent color, "
        "and the icon name displayed as a small label. "
        "Hover: lift effect (transform: translateY(-2px)), accent border."
    ))

    write_file("src/components/LanguageCard.astro", generate_file(
        "src/components/LanguageCard.astro",
        "Card for the languages index. Props: language (string slug, e.g. 'python'), "
        "displayName (string, e.g. 'Python'), postCount (number), featuredTopics (string[]). "
        "Shows language display name as h3 (linked to /languages/{language}/), "
        "post count ('X posts'), and up to 4 featured topics as small badges. "
        "Clean card style matching PostCard."
    ))

    write_file("src/components/CodeBlock.astro", generate_file(
        "src/components/CodeBlock.astro",
        "Syntax-highlighted code block. Props: code (string), lang (string, default 'text'), "
        "filename (string optional). "
        "Uses --font-mono, dark background (--color-surface), 1px border, --radius-md. "
        "Show filename in a top bar if provided. "
        "Include a copy-to-clipboard button (top right corner) using navigator.clipboard API. "
        "Note: in Markdown content, use standard fenced code blocks (rendered by Astro's Shiki); "
        "this component is for programmatic use in .astro files."
    ))

    write_file("src/components/TagBadge.astro", generate_file(
        "src/components/TagBadge.astro",
        "Small pill/badge for tags and categories. Props: tag (string), href (string optional). "
        "Style: small font size, --color-surface background, --color-accent border, --radius-sm, "
        "horizontal padding. If href is provided, renders as <a>; otherwise renders as <span>. "
        "Hover: background becomes --color-accent with dark text."
    ))

    write_file("src/components/SearchBar.astro", generate_file(
        "src/components/SearchBar.astro",
        "Client-side fuzzy search component using Fuse.js. "
        "Fetches /api/search-index.json at runtime. "
        "UI: modal overlay triggered by the search button in NavBar. "
        "Input field with autofocus. Results show as a list of PostCard-style items (title + description). "
        "Keyboard navigation (arrow keys + enter + escape to close). "
        "Search across title and description fields. "
        "All logic in a <script> block — no framework. Import Fuse.js from npm."
    ))

    write_file("src/components/Breadcrumb.astro", generate_file(
        "src/components/Breadcrumb.astro",
        "Breadcrumb navigation. Props: crumbs — array of {label: string, href: string | null}. "
        "Last item has href=null (current page, not linked). "
        "Renders as <nav aria-label='Breadcrumb'> with separator '/' between crumbs. "
        "Uses schema.org BreadcrumbList in JSON-LD. "
        "Small font size, --color-text-muted color."
    ))

    write_file("src/components/RelatedPosts.astro", generate_file(
        "src/components/RelatedPosts.astro",
        "Related posts widget for post sidebar/footer. Props: posts — array of {title, slug, category}. "
        "Renders as a section with heading 'Related Posts' and a list of linked titles. "
        "Simple, minimal design — just linked titles with category labels."
    ))

    # ── 6. Pages ───────────────────────────────────────────────────────────────
    print("→ [6/8] Pages...")

    write_file("src/pages/index.astro", generate_file(
        "src/pages/index.astro",
        "Homepage for devnook.dev. Uses BaseLayout. "
        "Sections:\n"
        "1. Hero: headline 'Developer Resources, Fast.' + subtext explaining the site. CTA buttons: 'Browse Tools' → /tools/, 'Explore Languages' → /languages/.\n"
        "2. Featured Tools: grid of 6 ToolCard components (static placeholder data until tools are built).\n"
        "3. Languages: row of LanguageCard components for the 12 supported languages.\n"
        "4. Recent Posts: grid of 6 PostCard components pulled from content collections (getCollection, sorted by published_date desc).\n"
        "5. Footer CTA: 'More guides and references coming daily.' banner.\n"
        "All content collections imports use getCollection() from astro:content."
    ))

    write_file("src/pages/tools/index.astro", generate_file(
        "src/pages/tools/index.astro",
        "Tools index page. Uses BaseLayout. Title: 'Free Developer Tools — DevNook'. "
        "Pulls all tools from getCollection('tools'). "
        "Grid of ToolCard components. Category filter buttons (data, encoding, formatting, etc.) "
        "using client-side JS to filter visible cards. "
        "If no tools exist yet, show a friendly 'Tools coming soon' message."
    ))

    write_file("src/pages/tools/[slug].astro", generate_file(
        "src/pages/tools/[slug].astro",
        "Dynamic tool page. Uses ToolLayout. "
        "getStaticPaths() from getCollection('tools'). "
        "Renders the tool's SEO explainer .md content as prose below the tool component slot. "
        "The tool component itself is imported dynamically by slug: "
        "import(`../../components/tools/${slug}.astro`). "
        "Breadcrumb: Home / Tools / {Tool Name}."
    ))

    write_file("src/pages/languages/index.astro", generate_file(
        "src/pages/languages/index.astro",
        "Languages index page. Uses BaseLayout. Title: 'Programming Languages — DevNook'. "
        "Shows a grid of LanguageCard for each of the 12 supported languages: "
        "python, javascript, typescript, go, rust, java, csharp, php, ruby, swift, kotlin, cpp. "
        "Pull post counts from getCollection('languages') grouped by language frontmatter. "
        "Display names: Python, JavaScript, TypeScript, Go, Rust, Java, C#, PHP, Ruby, Swift, Kotlin, C++."
    ))

    write_file("src/pages/languages/[lang]/index.astro", generate_file(
        "src/pages/languages/[lang]/index.astro",
        "Language hub page. Uses BaseLayout. Dynamic route for each language. "
        "getStaticPaths() derives paths from unique language values in getCollection('languages'). "
        "Shows: language display name as H1, post count, "
        "grid of PostCard for all posts in that language sorted by published_date desc. "
        "Breadcrumb: Home / Languages / {Language}."
    ))

    write_file("src/pages/languages/[lang]/[concept].astro", generate_file(
        "src/pages/languages/[lang]/[concept].astro",
        "Individual language concept post page. Uses PostLayout. "
        "getStaticPaths() from getCollection('languages'), filtering by language and concept frontmatter. "
        "Pass entry.data as frontmatter prop to PostLayout. "
        "Render <Content /> (from entry.render()) inside the layout slot. "
        "Breadcrumb: Home / Languages / {Language} / {Concept}."
    ))

    write_file("src/pages/guides/index.astro", generate_file(
        "src/pages/guides/index.astro",
        "Guides index. Uses BaseLayout. Title: 'Developer Guides — DevNook'. "
        "Grid of PostCard from getCollection('guides') sorted by date. "
        "Simple grid layout matching the tools index style."
    ))

    write_file("src/pages/guides/[slug].astro", generate_file(
        "src/pages/guides/[slug].astro",
        "Individual guide page. Uses PostLayout. "
        "getStaticPaths() from getCollection('guides'). "
        "Render <Content /> inside PostLayout. "
        "Breadcrumb: Home / Guides / {Title}."
    ))

    write_file("src/pages/cheatsheets/index.astro", generate_file(
        "src/pages/cheatsheets/index.astro",
        "Cheatsheets index. Uses BaseLayout. Title: 'Developer Cheat Sheets — DevNook'. "
        "Grid of PostCard from getCollection('cheatsheets') sorted by date."
    ))

    write_file("src/pages/cheatsheets/[subject].astro", generate_file(
        "src/pages/cheatsheets/[subject].astro",
        "Individual cheatsheet page. Uses PostLayout. "
        "getStaticPaths() from getCollection('cheatsheets'). "
        "Render <Content />. Breadcrumb: Home / Cheatsheets / {Title}."
    ))

    write_file("src/pages/blog/index.astro", generate_file(
        "src/pages/blog/index.astro",
        "Blog index. Uses BaseLayout. Title: 'Blog — DevNook'. "
        "Grid of PostCard from getCollection('blog') sorted by date."
    ))

    write_file("src/pages/blog/[slug].astro", generate_file(
        "src/pages/blog/[slug].astro",
        "Individual blog post page. Uses PostLayout. "
        "getStaticPaths() from getCollection('blog'). "
        "Render <Content />. Breadcrumb: Home / Blog / {Title}."
    ))

    write_file("src/pages/404.astro", generate_file(
        "src/pages/404.astro",
        "404 page. Uses BaseLayout. "
        "Shows: large '404' heading, message 'Page not found', "
        "brief helpful text, and link back to homepage. "
        "Centered layout, uses accent color for the 404 number."
    ))

    write_file("src/pages/sitemap-index.xml.ts", generate_file(
        "src/pages/sitemap-index.xml.ts",
        "Sitemap index endpoint. Re-exports Astro's built-in sitemap integration output. "
        "This file just needs to be a valid Astro endpoint that defers to @astrojs/sitemap. "
        "If @astrojs/sitemap handles this automatically, make this a minimal passthrough."
    ))

    # ── 7. OG Image pages ──────────────────────────────────────────────────────
    print("→ [7/8] OG image endpoints...")

    og_shared_context = (
        "Uses Satori + @resvg/resvg-js to generate PNG images at build time. "
        "Design: dark background (#0d0d0d), DevNook logo top-left, large title text in white, "
        "description text in muted gray (#8a8a8a), category badge in --color-accent (#6ee7b7). "
        "Size: 1200x630px. Font: Outfit loaded via ArrayBuffer from Google Fonts. "
        "Export GET handler. Response: new Response(png, { headers: { 'Content-Type': 'image/png' } })."
    )

    write_file("src/pages/og/languages/[...slug].png.ts", generate_file(
        "src/pages/og/languages/[...slug].png.ts",
        "OG image generator for language concept posts. " + og_shared_context +
        " getStaticPaths() from getCollection('languages'). "
        "Params include lang + concept. Title from entry.data.title."
    ))

    write_file("src/pages/og/guides/[slug].png.ts", generate_file(
        "src/pages/og/guides/[slug].png.ts",
        "OG image generator for guide posts. " + og_shared_context +
        " getStaticPaths() from getCollection('guides')."
    ))

    write_file("src/pages/og/tools/[slug].png.ts", generate_file(
        "src/pages/og/tools/[slug].png.ts",
        "OG image generator for tool pages. " + og_shared_context +
        " getStaticPaths() from getCollection('tools')."
    ))

    write_file("src/pages/og/blog/[slug].png.ts", generate_file(
        "src/pages/og/blog/[slug].png.ts",
        "OG image generator for blog posts. " + og_shared_context +
        " getStaticPaths() from getCollection('blog')."
    ))

    write_file("src/pages/og/cheatsheets/[slug].png.ts", generate_file(
        "src/pages/og/cheatsheets/[slug].png.ts",
        "OG image generator for cheatsheets. " + og_shared_context +
        " getStaticPaths() from getCollection('cheatsheets')."
    ))

    # ── 8. Search index ────────────────────────────────────────────────────────
    print("→ [8/8] Search index API...")

    write_file("src/pages/api/search-index.json.ts", generate_file(
        "src/pages/api/search-index.json.ts",
        "Static JSON endpoint that generates the Fuse.js search index at build time. "
        "Collects all entries from all 5 content collections (languages, guides, cheatsheets, blog, tools). "
        "Output format: JSON array of { title, description, slug, category, url } objects. "
        "url is the full path (e.g., /languages/python/list-comprehensions). "
        "Export GET handler returning new Response(JSON.stringify(items), "
        "{ headers: { 'Content-Type': 'application/json' } })."
    ))

    # ── Done ───────────────────────────────────────────────────────────────────
    print("\n=== Scaffold Complete ===")
    print(f"\nFiles written to: {PROJECT_ROOT.resolve()}")
    print("\nNext steps:")
    print("  1. npm install")
    print("  2. npm run dev  →  http://localhost:4321/")
    print("  3. npm run build  (verify no errors)")
    print("\nRun update.py after populating content to refresh homepage stats.")


if __name__ == "__main__":
    scaffold()
