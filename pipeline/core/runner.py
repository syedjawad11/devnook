"""
runner.py — Pipeline core CLI orchestrator

Usage:
  # Run full pipeline on a queued post (real API calls)
  python -m pipeline.core.runner --slug my-slug

  # Dry run (validate only — no API calls, no file writes, no DB updates)
  python -m pipeline.core.runner --slug my-slug --dry-run

  # Resume from a specific stage (skip earlier stages)
  python -m pipeline.core.runner --slug my-slug --from-stage write

  # Run a single stage only
  python -m pipeline.core.runner --slug my-slug --stage qa

  # Seed a new post into the queue (for testing)
  python -m pipeline.core.runner --seed-post --title "My Title" --category blog \\
      --keyword "my keyword" --template blog-v5 --slug my-slug

  # Custom DB path
  python -m pipeline.core.runner --slug my-slug --db path/to/registry.db
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Resolve pipeline/ root so relative imports work when run as __main__
_PIPELINE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PIPELINE_DIR.parent))

from pipeline.core import outline, write, link, qa, publish
from pipeline.core._db import get_post

STAGE_ORDER = ["outline", "write", "link", "qa", "publish"]
STAGE_FN = {
    "outline": outline,
    "write": write,
    "link": link,
    "qa": qa,
    "publish": publish,
}
STAGE_PREREQ = {
    "outline": "queued",
    "write": "outlined",
    "link": "drafted",
    "qa": "linked",
    "publish": "approved",
}
STAGE_NEXT_STATUS = {
    "outline": "outlined",
    "write": "drafted",
    "link": "linked",
    "qa": "approved",
    "publish": "published",
}


def _default_db() -> Path:
    return _PIPELINE_DIR / "data" / "registry.db"


def seed_post(
    db_path: Path,
    slug: str,
    title: str,
    category: str,
    keyword: str,
    template_id: str,
    language: str = "",
    concept: str = "",
    content_type: str = "editorial",
) -> None:
    conn = sqlite3.connect(str(db_path))
    existing = conn.execute("SELECT status FROM posts WHERE slug=?", (slug,)).fetchone()
    if existing:
        print(f"Post '{slug}' already in registry (status={existing[0]}). Not re-inserting.")
        conn.close()
        return

    conn.execute(
        """INSERT INTO posts
           (slug, title, category, language, concept, template_id, keyword,
            status, content_type, source, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,'queued',?,'pipeline_core',datetime('now'),datetime('now'))""",
        (slug, title, category, language or None, concept or None, template_id, keyword, content_type),
    )
    conn.commit()
    conn.close()
    print(f"Seeded post '{slug}' with status='queued'.")


def run_pipeline(
    slug: str,
    db_path: Path,
    *,
    from_stage: str = "outline",
    only_stage: str | None = None,
    dry_run: bool = False,
) -> list[dict]:
    from pipeline.core._db import set_post_status

    results = []
    start_idx = STAGE_ORDER.index(from_stage)
    stages = [only_stage] if only_stage else STAGE_ORDER[start_idx:]

    post = get_post(slug, db_path)
    if not post:
        print(f"ERROR: Post '{slug}' not found in registry.")
        sys.exit(1)

    print(f"\n{'DRY RUN — ' if dry_run else ''}Pipeline for '{slug}' (current status: {post['status']})")
    print("=" * 60)

    # Status ordering for idempotency checks
    STATUS_RANK = {s: i for i, s in enumerate(
        ["queued", "outlined", "drafted", "linked", "approved", "published"]
    )}

    for stage_name in stages:
        stage_fn = STAGE_FN[stage_name]
        prereq = STAGE_PREREQ[stage_name]

        current_post = get_post(slug, db_path)
        current_status = current_post["status"] if current_post else "unknown"
        next_status = STAGE_NEXT_STATUS.get(stage_name, "")

        # Skip if already past this stage (status rank > next_status rank)
        if (current_status in STATUS_RANK and next_status in STATUS_RANK
                and STATUS_RANK[current_status] >= STATUS_RANK[next_status]):
            print(f"  [{stage_name}] SKIP — post is '{current_status}'")
            results.append({"stage": stage_name, "skipped": True, "status": current_status})
            continue

        print(f"  [{stage_name}] running...", end=" ", flush=True)
        try:
            result = stage_fn(slug, db_path, dry_run=dry_run)
        except Exception as e:
            result = {"error": str(e), "processed": 0, "written": 0, "rejected": 0}

        result["stage"] = stage_name
        results.append(result)

        if result.get("error"):
            print(f"FAILED — {result['error']}")
            print(f"\nPipeline stopped at stage '{stage_name}'.")
            break

        if result.get("rejected"):
            print(f"REJECTED — {result.get('details', {}).get('rejections', [])}")
            print(f"\nPipeline stopped at stage '{stage_name}'.")
            break

        # In dry_run mode: advance DB status so next stage can proceed
        if dry_run and not result.get("error"):
            next_status = STAGE_NEXT_STATUS.get(stage_name)
            if next_status and next_status != "published":
                set_post_status(slug, next_status, db_path)

        tokens = result.get("tokens", 0)
        cost = result.get("cost", 0.0)
        details = result.get("details", {})
        suffix = f"tokens={tokens} cost=${cost:.4f}" if tokens else ""
        if details.get("word_count"):
            suffix += f" words={details['word_count']}"
        print(f"OK {suffix}")

    print("=" * 60)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="DevNook pipeline core runner")
    parser.add_argument("--slug", help="Post slug to process")
    parser.add_argument("--db", default=None, help="Path to registry.db")
    parser.add_argument("--dry-run", action="store_true", help="Validate only — no writes/DB updates")
    parser.add_argument("--from-stage", default="outline", choices=STAGE_ORDER)
    parser.add_argument("--stage", default=None, choices=STAGE_ORDER, help="Run a single stage")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    # Profile mode — query pre-populated opportunity tables
    parser.add_argument("--profile", choices=["language", "editorial"], help="Show ordered opportunity briefs")
    parser.add_argument("--limit", type=int, default=5, help="Number of briefs for --profile output")
    # Seed mode
    parser.add_argument("--seed-post", action="store_true", help="Seed a new post into queue")
    parser.add_argument("--title", default="")
    parser.add_argument("--category", default="blog")
    parser.add_argument("--keyword", default="")
    parser.add_argument("--template", default="blog-v5")
    parser.add_argument("--language", default="")
    parser.add_argument("--concept", default="")
    parser.add_argument("--content-type", default="editorial")

    args = parser.parse_args()

    db_path = Path(args.db) if args.db else _default_db()

    if args.seed_post:
        if not args.slug or not args.title:
            print("ERROR: --slug and --title required for --seed-post")
            sys.exit(1)
        seed_post(
            db_path,
            slug=args.slug,
            title=args.title,
            category=args.category,
            keyword=args.keyword,
            template_id=args.template,
            language=args.language,
            concept=args.concept,
            content_type=args.content_type,
        )
        if not args.slug:
            return

    if args.profile == "language":
        from pipeline.core.stage0_language import list_briefs, count_status
        counts = count_status(db_path)
        total = counts.get("_total", 0)
        if total == 0:
            print("language_opportunity table is empty.")
            print("Run @pipeline-b-stage0-language agent (LOCAL session, DataForSEO MCP required).")
            sys.exit(1)
        briefs = list_briefs(db_path, limit=args.limit)
        if not briefs:
            print(
                f"No language opportunities with demand yet "
                f"({total} rows, 0 with has_demand=1).\n"
                "Re-run @pipeline-b-stage0-language to fetch volumes."
            )
            sys.exit(1)
        print(f"\nTop {len(briefs)} language opportunities (ordered by opportunity score):\n")
        for i, b in enumerate(briefs, 1):
            kd_str = f" kd={b['kd']:.0f}" if b["kd"] else ""
            print(f"  {i}. {b['language']} / {b['concept']}")
            print(
                f"     keyword: \"{b['canonical_keyword']}\""
                f"  vol={b['volume']}{kd_str}"
                f"  opp={b['opportunity_score']}"
            )
        sys.exit(0)

    if args.profile == "editorial":
        from pipeline.core.stage0_editorial import list_briefs, count_by_tier
        counts = count_by_tier(db_path)
        total = sum(counts.values())
        if total == 0:
            print("editorial_opportunity table is empty.")
            print("Run @pipeline-b-stage0-editorial agent (LOCAL session, DataForSEO MCP required).")
            sys.exit(1)
        briefs = list_briefs(db_path, limit=args.limit)
        if not briefs:
            print(
                f"No editorial opportunities with viable tier yet ({total} rows).\n"
                "Re-run @pipeline-b-stage0-editorial to fetch volumes."
            )
            sys.exit(1)
        tier_summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"\nTop {len(briefs)} editorial opportunities (tier order + score):")
        print(f"Tier counts: {tier_summary}\n")
        for i, b in enumerate(briefs, 1):
            kd_str = f" kd={b['kd']:.0f}" if b["kd"] else ""
            print(f"  {i}. [{b['tier']}] {b['cluster_label']} — \"{b['keyword']}\"")
            print(
                f"     seed: \"{b['topic_seed']}\""
                f"  vol={b['volume']}{kd_str}"
                f"  opp={b['opportunity_score']}"
            )
        sys.exit(0)

    if not args.slug:
        parser.print_help()
        sys.exit(1)

    results = run_pipeline(
        args.slug,
        db_path,
        from_stage=args.from_stage,
        only_stage=args.stage,
        dry_run=args.dry_run,
    )

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        failed = [r for r in results if r.get("error") or r.get("rejected")]
        if failed:
            sys.exit(1)


if __name__ == "__main__":
    main()
