#!/usr/bin/env python3
"""
DevNook Drip Publisher
Moves posts from /content-staging/ to /src/content/ and pings GSC.

Usage:
  python agents/publish/publish.py --count 3
  python agents/publish/publish.py --count 20 --category languages
"""

import argparse
import re
import shutil
import sqlite3
import subprocess
import sys
import os
from pathlib import Path
from datetime import date, datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agents.publish.gsc_ping import ping_url

STAGING_DIR = Path("content-staging")
DEVNOOK_DIR = Path(os.environ.get("DEVNOOK_PATH", "../devnook"))
CONTENT_DIR = DEVNOOK_DIR / "src/content"
DB_PATH = Path("agents/content-team/registry.db")
BASE_URL = "https://devnook.dev"

def get_category_url_prefix(category: str, slug: str, language: str = None) -> str:
    """Generate the live URL for a post."""
    if category == "languages" and language:
        return f"{BASE_URL}/languages/{language}/{slug}"
    return f"{BASE_URL}/{category}/{slug}"

def get_staged_files(count: int, category_filter: str = "all") -> list:
    """Get the oldest staged files from content-staging."""
    all_files = []
    
    # Walk content-staging directory
    for path in STAGING_DIR.rglob("*.md"):
        all_files.append(path)
    
    # Sort by modification time (oldest first = FIFO queue)
    all_files.sort(key=lambda p: p.stat().st_mtime)
    
    if category_filter != "all":
        all_files = [f for f in all_files if category_filter in str(f)]
    
    return all_files[:count]

_RELATED_SECTION_RE = re.compile(
    r"\n[ \t]*##[ \t]+Related\b[^\n]*\n.*?(?=\n##[ \t]|\Z)",
    re.DOTALL | re.IGNORECASE,
)


def strip_related_section(file_path: Path) -> bool:
    """Remove any hand-written `## Related` section from the post body.

    Why: PostLayout.astro auto-derives the Related list from frontmatter at render
    time. LLM-written `## Related` markdown sections produce broken /languages/{lang}/{concept}
    links because agents have no visibility into what is published. This is the
    safety net described in CLAUDE.md.

    Returns True if the file was modified.
    """
    text = file_path.read_text(encoding="utf-8")
    cleaned = _RELATED_SECTION_RE.sub("", text)
    if cleaned != text:
        cleaned = cleaned.rstrip() + "\n"
        file_path.write_text(cleaned, encoding="utf-8")
        return True
    return False


def validate_language_links(staging_path: Path) -> list:
    """
    Scan body prose for /languages/{lang}/{segment} links and verify each
    segment is a valid concept in the registry (not a filename-based slug).
    Returns a list of problem descriptions; empty list means clean.
    """
    text = staging_path.read_text(encoding="utf-8")
    link_re = re.compile(r'\]\((/languages/([^/\s"]+)/([^/\s")]+))')
    problems = []

    conn = sqlite3.connect(DB_PATH)
    for m in link_re.finditer(text):
        full_path, lang, segment = m.group(1), m.group(2), m.group(3).rstrip("/")
        is_concept = conn.execute(
            "SELECT 1 FROM posts WHERE language = ? AND concept = ?",
            (lang, segment),
        ).fetchone()
        if is_concept:
            continue
        slug_row = conn.execute(
            "SELECT concept FROM posts WHERE language = ? AND slug = ?",
            (lang, segment),
        ).fetchone()
        if slug_row:
            problems.append(
                f"{full_path} uses filename slug — correct URL is /languages/{lang}/{slug_row[0]}"
            )
        else:
            problems.append(f"{full_path} not found in registry (broken link)")
    conn.close()
    return problems


def move_to_content(staging_path: Path) -> Path:
    """Move a file from content-staging to src/content, preserving directory structure."""
    # staging_path: content-staging/languages/python/python-list-comprehensions.md
    # dest_path:    src/content/languages/python/python-list-comprehensions.md
    relative = staging_path.relative_to(STAGING_DIR)
    dest_path = CONTENT_DIR / relative
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staging_path), str(dest_path))
    return dest_path

def update_registry(slug: str, file_path: str):
    """Mark post as published in registry.db"""
    from datetime import timezone
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        UPDATE posts SET status='published', published_at=?, published_date=?, file_path=?
        WHERE slug=?
    """, (now, date.today().isoformat(), file_path, slug))
    conn.commit()
    conn.close()

def get_post_meta(staging_path: Path) -> dict:
    """Extract slug, category, language from file path and frontmatter."""
    import frontmatter
    post = frontmatter.load(str(staging_path))
    return {
        "slug": staging_path.stem,
        "category": post.metadata.get("category", ""),
        "language": post.metadata.get("language", ""),
    }

def publish(count: int, category_filter: str = "all"):
    files = get_staged_files(count, category_filter)
    
    if not files:
        print("No staged posts found. Run the content pipeline first.")
        return
    
    print(f"Publishing {len(files)} posts...")
    published_urls = []
    
    for staging_path in files:
        meta = get_post_meta(staging_path)
        slug = meta["slug"]

        # Guard: reject files with filename-based or broken /languages/ links
        link_problems = validate_language_links(staging_path)
        if link_problems:
            print(f"  [SKIP] {slug}: invalid /languages/ links — fix before publishing:")
            for p in link_problems:
                print(f"         {p}")
            continue

        # Move file to src/content
        dest_path = move_to_content(staging_path)
        if strip_related_section(dest_path):
            print(f"  -- Stripped hand-written ## Related section from {slug}")
        print(f"  >> Published: {slug}")
        
        # Update registry
        update_registry(slug, str(dest_path))
        
        # Build URL for GSC ping
        url = get_category_url_prefix(meta["category"], slug, meta.get("language"))
        published_urls.append(url)
    
    # Ping GSC for all published URLs (skipped if GOOGLE_SERVICE_ACCOUNT_JSON not set)
    if not os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
        print("\nSkipping GSC ping — GOOGLE_SERVICE_ACCOUNT_JSON not configured.")
    else:
        print(f"\nPinging Google Search Console ({len(published_urls)} URLs)...")
        for url in published_urls:
            try:
                ping_url(url)
                print(f"  >> GSC: {url}")
            except Exception as e:
                print(f"  [X] GSC failed for {url}: {e}")

    # Commit and push new posts to the devnook repo
    devnook = str(DEVNOOK_DIR)
    today = date.today().isoformat()
    subprocess.run(["git", "add", "src/content/"], cwd=devnook)
    result = subprocess.run(
        ["git", "commit", "-m", f"chore: publish {today} drip posts [skip ci]"],
        cwd=devnook,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        subprocess.run(["git", "push"], cwd=devnook)
        print(f"\ndevnook: committed and pushed {len(files)} posts.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--category", default="all")
    args = parser.parse_args()
    publish(args.count, args.category)

if __name__ == "__main__":
    main()
