"""
Step 6: Staging
Moves approved posts from drafts/ to /content-staging/.
The drip publisher (GitHub Actions) picks up from content-staging/.

No LLM calls — pure file operations.
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Ensure project root is on path (in case script is run standalone)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.registry import get_db, update_post_status

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DRAFTS_DIR = Path(__file__).resolve().parent / "drafts"
STAGING_DIR = PROJECT_ROOT / "content-staging"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_staging_path(post: dict) -> Path:
    """
    Determine the target path in content-staging/ for a post.

    Language posts:  content-staging/languages/{lang}/{slug}.md
    All others:      content-staging/{category}/{slug}.md
    """
    category = post["category"]
    slug = post["slug"]

    if category == "languages":
        lang = post.get("language") or "misc"
        return STAGING_DIR / "languages" / lang / f"{slug}.md"
    else:
        return STAGING_DIR / category / f"{slug}.md"


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run() -> dict:
    """Move all approved posts to content-staging/. Returns pipeline result dict."""
    with get_db() as db:
        posts = db.execute(
            "SELECT * FROM posts WHERE status='approved'"
        ).fetchall()

    if not posts:
        print("  No approved posts to stage.")
        return {"processed": 0, "passed": 0, "rejected": 0}

    print(f"  Staging {len(posts)} approved posts...")

    STAGING_DIR.mkdir(exist_ok=True)

    moved = 0
    failed = 0
    now = datetime.utcnow().isoformat() + "Z"

    for row in posts:
        post = dict(row)
        slug = post["slug"]
        draft_path = DRAFTS_DIR / f"{slug}.md"

        if not draft_path.exists():
            print(f"  [MISSING] Draft not found: {slug}")
            failed += 1
            continue

        staging_path = get_staging_path(post)

        try:
            staging_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(draft_path), str(staging_path))

            update_post_status(
                slug,
                "staged",
                staged_at=now,
                file_path=str(staging_path),
            )

            print(f"  [STAGED] {slug} >> {staging_path.relative_to(PROJECT_ROOT)}")
            moved += 1

        except Exception as e:
            print(f"  [ERROR] Failed to stage '{slug}': {e}")
            failed += 1

    # Print staging tree summary
    if moved > 0:
        staged_files = list(STAGING_DIR.rglob("*.md"))
        print(f"\n  content-staging/ now has {len(staged_files)} files total")

    print(f"  Done — staged={moved}, failed={failed}")

    return {
        "processed": len(posts),
        "passed": moved,
        "rejected": failed,
    }


if __name__ == "__main__":
    result = run()
    print(f"\nResult: {result}")
