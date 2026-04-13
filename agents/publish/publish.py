#!/usr/bin/env python3
"""
DevNook Drip Publisher
Moves posts from /content-staging/ to /src/content/ and pings GSC.

Usage:
  python agents/publish/publish.py --count 3
  python agents/publish/publish.py --count 20 --category languages
"""

import argparse
import shutil
import sqlite3
import sys
import os
from pathlib import Path
from datetime import date, datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agents.publish.gsc_ping import ping_url

STAGING_DIR = Path("content-staging")
CONTENT_DIR = Path("src/content")
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
        
        # Move file to src/content
        dest_path = move_to_content(staging_path)
        print(f"  >> Published: {slug}")
        
        # Update registry
        update_registry(slug, str(dest_path))
        
        # Build URL for GSC ping
        url = get_category_url_prefix(meta["category"], slug, meta.get("language"))
        published_urls.append(url)
    
    # Ping GSC for all published URLs
    print(f"\nPinging Google Search Console ({len(published_urls)} URLs)...")
    for url in published_urls:
        try:
            ping_url(url)
            print(f"  >> GSC: {url}")
        except Exception as e:
            print(f"  [X] GSC failed for {url}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--category", default="all")
    args = parser.parse_args()
    publish(args.count, args.category)

if __name__ == "__main__":
    main()
