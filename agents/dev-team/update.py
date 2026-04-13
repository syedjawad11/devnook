#!/usr/bin/env python3
"""
DevNook Dev Team — update.py
Updates Astro pages based on current registry.db state.
Run after each content pipeline batch: python agents/dev-team/update.py

What it refreshes:
  - src/pages/index.astro           (post/tool counts, featured content)
  - src/pages/languages/index.astro (language list + post counts)
  - src/pages/languages/[lang]/index.astro  (creates hub pages for new languages)
  - src/pages/tools/index.astro     (tool count, featured tools)

Requires: ANTHROPIC_API_KEY environment variable
"""

import sys
import sqlite3
from pathlib import Path

# Allow imports from agents/utils/
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
from utils.llm_router import route

DB_PATH = Path("agents/content-team/registry.db")
SKILLS_DIR = Path("agents/skills")
PROJECT_ROOT = Path(".")
PAGES_DIR = PROJECT_ROOT / "src" / "pages"

ASTRO_CONVENTIONS = (SKILLS_DIR / "astro-conventions.md").read_text(encoding="utf-8")

SYSTEM_PROMPT = f"""You are an expert Astro developer maintaining devnook.dev.
You produce complete, production-ready Astro file contents — no placeholders, no TODOs.

Conventions:
{ASTRO_CONVENTIONS}

Rules:
- Output ONLY the raw file content. No markdown fences, no explanations.
- Use getCollection() from astro:content for all content queries.
- All internal links are relative paths.
- Use exact CSS token names.
"""

LANGUAGE_DISPLAY_NAMES = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "go": "Go",
    "rust": "Rust",
    "java": "Java",
    "csharp": "C#",
    "php": "PHP",
    "ruby": "Ruby",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "cpp": "C++",
}


def get_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"registry.db not found at {DB_PATH}. "
            "Run scaffold.py first and ensure Stage 1 is complete."
        )
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_stats(db: sqlite3.Connection) -> dict:
    """Pull current content stats from registry."""
    total_published = db.execute(
        "SELECT COUNT(*) FROM posts WHERE status='published'"
    ).fetchone()[0]

    total_staged = db.execute(
        "SELECT COUNT(*) FROM posts WHERE status='staged'"
    ).fetchone()[0]

    tools_count = db.execute(
        "SELECT COUNT(*) FROM posts WHERE category='tools' AND status='published'"
    ).fetchone()[0]

    lang_rows = db.execute(
        "SELECT language, COUNT(*) as count FROM posts "
        "WHERE language IS NOT NULL AND status='published' "
        "GROUP BY language ORDER BY count DESC"
    ).fetchall()
    languages = [{"language": r["language"], "count": r["count"]} for r in lang_rows]

    # Featured posts: 6 most recent published
    featured_rows = db.execute(
        "SELECT slug, title, description, category, language, published_date "
        "FROM posts WHERE status='published' "
        "ORDER BY published_date DESC LIMIT 6"
    ).fetchall()
    featured = [dict(r) for r in featured_rows]

    # Featured tools: 6 most recent published tools
    tool_rows = db.execute(
        "SELECT slug, title, description FROM posts "
        "WHERE category='tools' AND status='published' "
        "ORDER BY published_date DESC LIMIT 6"
    ).fetchall()
    featured_tools = [dict(r) for r in tool_rows]

    return {
        "total_published": total_published,
        "total_staged": total_staged,
        "tools_count": tools_count,
        "languages": languages,
        "featured": featured,
        "featured_tools": featured_tools,
    }


def write_file(path: str, content: str):
    """Write content to file, creating parent directories as needed."""
    full_path = PROJECT_ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"  >> {path}")


def generate_file(filename: str, description: str) -> str:
    print(f"    Calling Claude for {filename}...")
    result = route(
        "frontend_dev",
        system=SYSTEM_PROMPT,
        prompt=f"Generate the complete contents of `{filename}` for devnook.dev.\n\n{description}",
        max_tokens=4096,
    )
    return result.text


def update_homepage(stats: dict):
    """Regenerate homepage with current stats."""
    stats_context = (
        f"Current site stats:\n"
        f"- Published posts: {stats['total_published']}\n"
        f"- Published tools: {stats['tools_count']}\n"
        f"- Languages with content: {len(stats['languages'])}\n"
        f"- Staged (upcoming): {stats['total_staged']}\n"
    )

    if stats["featured"]:
        stats_context += "\nRecent published posts (use for featured grid):\n"
        for p in stats["featured"]:
            stats_context += f"  - [{p['category']}] {p['title']} → /{p['category']}/{p['slug']}\n"

    if stats["featured_tools"]:
        stats_context += "\nRecent tools (use for featured tools section):\n"
        for t in stats["featured_tools"]:
            stats_context += f"  - {t['title']} → /tools/{t['slug']}\n"

    content = generate_file(
        "src/pages/index.astro",
        "Homepage for devnook.dev. Uses BaseLayout. "
        "Sections:\n"
        "1. Hero: headline 'Developer Resources, Fast.' + subtext. CTA: 'Browse Tools' → /tools/, 'Explore Languages' → /languages/.\n"
        "2. Featured Tools: grid using getCollection('tools') for real tool data (fallback to empty state if none).\n"
        "3. Languages: LanguageCard grid from getCollection('languages') grouped by language.\n"
        "4. Recent Posts: grid of PostCard from all collections sorted by published_date desc, limit 6.\n"
        "5. Stats bar: show total post count and tool count.\n\n"
        + stats_context,
    )
    write_file("src/pages/index.astro", content)


def update_languages_index(stats: dict):
    """Regenerate languages index with current post counts."""
    lang_context = "Languages with published post counts:\n"
    if stats["languages"]:
        for lang in stats["languages"]:
            display = LANGUAGE_DISPLAY_NAMES.get(lang["language"], lang["language"].title())
            lang_context += f"  - {display} ({lang['language']}): {lang['count']} posts\n"
    else:
        lang_context += "  (No published posts yet — show all 12 languages as 'Coming soon')\n"

    content = generate_file(
        "src/pages/languages/index.astro",
        "Languages index page. Uses BaseLayout. Title: 'Programming Languages — DevNook'. "
        "Show a LanguageCard grid for all 12 supported languages: "
        "python, javascript, typescript, go, rust, java, csharp, php, ruby, swift, kotlin, cpp. "
        "Use getCollection('languages') to compute per-language post counts. "
        "If a language has 0 posts, still show the card with 'Coming soon' label.\n\n"
        + lang_context,
    )
    write_file("src/pages/languages/index.astro", content)


def update_tools_index(stats: dict):
    """Regenerate tools index."""
    content = generate_file(
        "src/pages/tools/index.astro",
        "Tools index page. Uses BaseLayout. Title: 'Free Developer Tools — DevNook'. "
        "Uses getCollection('tools') for all tool data. "
        "Grid of ToolCard components. Category filter buttons via client-side JS. "
        f"Current tool count: {stats['tools_count']}. "
        "If tools_count is 0, show 'Tools coming soon' friendly message.",
    )
    write_file("src/pages/tools/index.astro", content)


def ensure_language_hubs(db: sqlite3.Connection):
    """
    Create hub pages for any language that has published posts
    but whose hub page doesn't exist yet.
    """
    lang_rows = db.execute(
        "SELECT DISTINCT language FROM posts "
        "WHERE language IS NOT NULL AND status='published'"
    ).fetchall()

    created = 0
    for row in lang_rows:
        lang = row["language"]
        hub_path = PAGES_DIR / "languages" / lang / "index.astro"
        if not hub_path.exists():
            display = LANGUAGE_DISPLAY_NAMES.get(lang, lang.title())
            print(f"  Creating missing hub for: {lang}")
            content = generate_file(
                f"src/pages/languages/{lang}/index.astro",
                f"Language hub for {display}. Uses BaseLayout. "
                f"Title: '{display} — DevNook'. "
                f"Shows all posts in the '{lang}' language collection as PostCard grid, "
                "sorted by published_date desc. "
                f"Breadcrumb: Home / Languages / {display}. "
                "Use getStaticPaths() pattern but hard-code the language slug since this is a static page.",
            )
            write_file(f"src/pages/languages/{lang}/index.astro", content)
            created += 1

    if created == 0:
        print("  No new language hubs needed.")
    else:
        print(f"  Created {created} new language hub(s).")


def update():
    print("=== DevNook Update — Starting ===\n")

    if not PAGES_DIR.exists():
        print("ERROR: src/pages/ does not exist. Run scaffold.py first.")
        sys.exit(1)

    with get_db() as db:
        stats = get_stats(db)

        print(
            f"Registry stats: {stats['total_published']} published, "
            f"{stats['tools_count']} tools, "
            f"{len(stats['languages'])} languages\n"
        )

        print(">> Updating homepage...")
        update_homepage(stats)

        print(">> Updating languages index...")
        update_languages_index(stats)

        print(">> Updating tools index...")
        update_tools_index(stats)

        print(">> Checking for new language hubs...")
        ensure_language_hubs(db)

    print("\n=== Update Complete ===")
    print(f"  Published posts: {stats['total_published']}")
    print(f"  Tools: {stats['tools_count']}")
    print(f"  Languages: {len(stats['languages'])}")
    print("\nRun 'npm run build' to verify no errors.")


if __name__ == "__main__":
    update()
