# Stage 6 — Publishing Infrastructure

**Goal:** Build the automated publishing pipeline. GitHub Actions drip-publishes 2–3 posts per day from `/content-staging/` to `/src/content/`, triggering a Cloudflare Pages deploy. Google Search Console is pinged after each publish for fast indexing.

**Depends on:** Stage 2 (Astro project must exist), Stage 5 (content-staging must have posts)  
**Unlocks:** Stage 7 (launch = first real deploy)  
**Estimated session time:** 1 focused session (~2 hours)  
**No LLM needed for this stage** — pure configuration and scripting

---

## Deliverables Checklist

- [ ] `.github/workflows/drip-publish.yml` — daily cron publisher
- [ ] `.github/workflows/on-demand-publish.yml` — manual trigger for launch day
- [ ] `agents/publish/publish.py` — the publish logic (move files + git + ping GSC)
- [ ] `agents/publish/gsc_ping.py` — Google Search Console Indexing API
- [ ] `cloudflare-pages.json` — Cloudflare Pages build config reference
- [ ] `.env.example` updated with all required secrets
- [ ] GitHub Actions secrets documented

---

## Architecture

```
GitHub Actions (daily at 08:00 UTC)
  └── drip-publish.yml
        └── python agents/publish/publish.py --count 3
              ├── Pick 3 oldest files from /content-staging/
              ├── Move them to /src/content/{category}/
              ├── Update registry.db status → published
              ├── git add + commit + push
              │     └── Triggers Cloudflare Pages auto-deploy
              └── gsc_ping.py — ping GSC Indexing API for each URL
```

---

## File: `.github/workflows/drip-publish.yml`

```yaml
name: Drip Publish

on:
  schedule:
    - cron: '0 8 * * *'  # Daily at 08:00 UTC
  workflow_dispatch:      # Allow manual trigger

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GH_PAT }}
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r agents/requirements.txt

      - name: Configure git
        run: |
          git config user.name "DevNook Publisher"
          git config user.email "publisher@devnook.dev"

      - name: Run drip publisher
        env:
          GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}
        run: |
          python agents/publish/publish.py --count 3

      - name: Check if there were any posts to publish
        id: check_changes
        run: |
          if git diff --quiet HEAD; then
            echo "has_changes=false" >> $GITHUB_OUTPUT
          else
            echo "has_changes=true" >> $GITHUB_OUTPUT
          fi

      - name: Commit and push published posts
        if: steps.check_changes.outputs.has_changes == 'true'
        run: |
          git add src/content/ agents/content-team/registry.db
          git commit -m "chore: publish $(date '+%Y-%m-%d') drip posts [skip ci]"
          git push
```

---

## File: `.github/workflows/on-demand-publish.yml`

```yaml
name: On-Demand Publish (Launch Day)

on:
  workflow_dispatch:
    inputs:
      count:
        description: 'Number of posts to publish'
        required: true
        default: '20'
        type: string
      category:
        description: 'Category filter (or "all")'
        required: false
        default: 'all'
        type: string

jobs:
  publish:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GH_PAT }}
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - run: pip install -r agents/requirements.txt

      - name: Configure git
        run: |
          git config user.name "DevNook Publisher"
          git config user.email "publisher@devnook.dev"

      - name: Publish posts
        env:
          GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}
        run: |
          python agents/publish/publish.py \
            --count ${{ github.event.inputs.count }} \
            --category ${{ github.event.inputs.category }}

      - name: Commit and push
        run: |
          git add src/content/ agents/content-team/registry.db
          git commit -m "feat: launch day publish - ${{ github.event.inputs.count }} posts" || echo "Nothing to commit"
          git push || echo "Nothing to push"
```

---

## File: `agents/publish/publish.py`

```python
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
from pathlib import Path
from datetime import date, datetime
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
    now = datetime.utcnow().isoformat() + "Z"
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
        print(f"  ✓ Published: {slug}")
        
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
            print(f"  ✓ GSC: {url}")
        except Exception as e:
            print(f"  ✗ GSC failed for {url}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3)
    parser.add_argument("--category", default="all")
    args = parser.parse_args()
    publish(args.count, args.category)

if __name__ == "__main__":
    main()
```

---

## File: `agents/publish/gsc_ping.py`

```python
"""
Google Search Console Indexing API
Pings Google to request immediate crawling of newly published URLs.

Setup:
1. Create a service account in Google Cloud Console
2. Enable the "Web Search Indexing API"
3. Add service account as an owner in GSC
4. Download the JSON key file
5. Set GOOGLE_SERVICE_ACCOUNT_JSON env var to the JSON content
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/indexing"]

def get_service():
    """Build authenticated GSC service."""
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON env var not set")
    
    service_account_info = json.loads(sa_json)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )
    return build("indexing", "v3", credentials=credentials)

def ping_url(url: str, notification_type: str = "URL_UPDATED"):
    """
    Ping GSC to index/update a URL.
    notification_type: URL_UPDATED or URL_DELETED
    """
    service = get_service()
    service.urlNotifications().publish(
        body={"url": url, "type": notification_type}
    ).execute()
```

---

## Cloudflare Pages Setup

Cloudflare Pages auto-deploys on every push to `main`. No configuration file needed beyond the dashboard settings:

**Build settings (set in Cloudflare Pages dashboard):**
```
Build command:      npm run build
Build output dir:   dist
Root directory:     /
Node.js version:    20
```

**Environment variables (set in Cloudflare Pages dashboard):**
```
NODE_VERSION=20
```

**Cloudflare Workers (for Tier 2 AI tools):**
Deploy each worker separately with:
```bash
cd workers/code-explainer
wrangler secret put GEMINI_API_KEY
wrangler deploy
```

---

## GitHub Repository Secrets Required

Document these in `agents/publish/SECRETS.md`:

```markdown
# Required GitHub Actions Secrets

Set these in: GitHub repo → Settings → Secrets and variables → Actions

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| GH_PAT | GitHub Personal Access Token (repo scope) | GitHub → Settings → Developer settings → PATs |
| GOOGLE_SERVICE_ACCOUNT_JSON | Google service account JSON key (full content) | Google Cloud Console → IAM → Service Accounts → Keys |

## GSC Setup Steps
1. Go to console.cloud.google.com
2. Create project or use existing
3. Enable "Web Search Indexing API"
4. Create service account: IAM & Admin → Service Accounts → Create
5. Grant it no project roles (it only needs GSC access)
6. Create JSON key: Service Account → Keys → Add Key → JSON
7. In Google Search Console (search.google.com/search-console):
   - Go to Settings → Users and permissions
   - Add service account email as Owner
8. Copy the entire JSON key content → GitHub Secret: GOOGLE_SERVICE_ACCOUNT_JSON
```

---

## Publishing Rate Schedule

The drip publisher respects the safe ramp-up schedule from the project plan:

```python
# Adjust --count in drip-publish.yml over time:
# Month 1: --count 2   (60 posts/month)
# Month 2: --count 3   (90 posts/month)
# Month 3: --count 6   (~180 posts/month)
# Month 4: --count 9   (~270 posts/month)
# Month 5+: --count 12  (360+ posts/month)
```

---

## Verification

- [ ] `python agents/publish/publish.py --count 1` moves 1 file from staging to src/content
- [ ] Moved file has valid frontmatter
- [ ] `registry.db` shows the post as `published`
- [ ] GitHub Actions YAML is valid (no syntax errors)
- [ ] After pushing workflow file + a staged post, GitHub Actions runs successfully
- [ ] Cloudflare Pages deploys after the git push (check CF dashboard)
- [ ] New post is live at `https://devnook.dev/{category}/{slug}`
- [ ] GSC ping doesn't throw errors (check GitHub Actions logs)
- [ ] Running the workflow twice doesn't re-publish the same post (idempotency)
