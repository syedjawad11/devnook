"""
Step 1: Keyword Agent
Discovers keyword opportunities using Google Autocomplete API.
Scores them heuristically and adds new ones to registry.db keywords table.

Uses asyncio + aiohttp for concurrent fetching (batches of 10, 1s between batches).
Caches fetched seed queries in a `fetched_seeds` table to skip on repeat runs.

No LLM calls needed — keyword discovery and scoring is purely heuristic.
"""

import sys
import asyncio
import aiohttp
from pathlib import Path

# Ensure project root is on path (in case script is run standalone)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.registry import get_db, get_published_slugs

# ---------------------------------------------------------------------------
# Seed topics
# ---------------------------------------------------------------------------

SEED_TOPICS = {
    # Ring 1: tool-adjacent (highest priority — matches our 17 tools)
    "tool_adjacent": [
        "json formatter online",
        "base64 encode decode",
        "regex tester online",
        "color picker hex rgb",
        "jwt decoder online",
        "markdown preview online",
        "url encoder decoder",
        "hash generator online",
        "uuid generator online",
        "cron expression parser",
        "csv to json converter",
        "diff checker online",
        "html formatter online",
        "sql formatter online",
        "sitemap generator",
        "readme generator",
        "meta tag generator",
    ],
    # Ring 2: web fundamentals guides
    "guides": [
        "what is REST API",
        "how does HTTP work",
        "what is JWT authentication",
        "difference between authentication and authorization",
        "what is Big O notation",
        "how does garbage collection work",
        "what is CORS",
        "how does DNS work",
        "what is WebSocket",
        "difference between SQL and NoSQL",
        "what is microservices architecture",
        "how does OAuth work",
    ],
    # Ring 3: language concept seeds
    "concepts": [
        "list comprehension",
        "async await",
        "decorator pattern",
        "generator function",
        "closure",
        "recursion example",
        "sorting algorithm",
        "error handling",
        "class inheritance",
        "string formatting",
        "file handling",
        "json parsing",
        "http requests",
        "regex pattern",
        "environment variables",
        "type hints",
        "dataclass",
        "context manager",
        "lambda function",
        "dictionary comprehension",
    ],
    "languages": [
        "python", "javascript", "typescript",
        "go", "rust", "java", "csharp",
        "php", "ruby", "swift", "kotlin", "cpp",
    ],
}

# Concurrency settings
BATCH_SIZE = 10       # concurrent requests per batch
BATCH_DELAY = 1.0     # seconds between batches
MAX_SUGGESTIONS = 5   # max suggestions to keep per query (ring 1)


# ---------------------------------------------------------------------------
# DB: seed cache table
# ---------------------------------------------------------------------------

def _ensure_seed_cache_table():
    """Create fetched_seeds table if it doesn't exist."""
    with get_db() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS fetched_seeds "
            "(seed TEXT PRIMARY KEY, fetched_at TEXT DEFAULT (datetime('now')))"
        )


def _get_cached_seeds() -> set:
    """Return set of seed queries already fetched."""
    with get_db() as db:
        rows = db.execute("SELECT seed FROM fetched_seeds").fetchall()
        return {r[0] for r in rows}


def _mark_seeds_fetched(seeds: list[str]):
    """Record that these seed queries have been fetched."""
    with get_db() as db:
        db.executemany(
            "INSERT OR IGNORE INTO fetched_seeds (seed) VALUES (?)",
            [(s,) for s in seeds],
        )


# ---------------------------------------------------------------------------
# Google Autocomplete (async)
# ---------------------------------------------------------------------------

async def fetch_autocomplete(session: aiohttp.ClientSession, query: str) -> tuple[str, list]:
    """Fetch Google Autocomplete suggestions. Returns (query, suggestions)."""
    url = "https://suggestqueries.google.com/complete/search"
    params = {"client": "firefox", "q": query}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                return query, data[1] if len(data) > 1 else []
    except Exception:
        pass
    return query, []


async def fetch_batch(queries: list[str], max_per_query: int = 5) -> dict[str, list]:
    """
    Fetch autocomplete for a list of queries in batches of BATCH_SIZE.
    Returns {query: [suggestions]}.
    """
    results = {}
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(queries), BATCH_SIZE):
            batch = queries[i : i + BATCH_SIZE]
            tasks = [fetch_autocomplete(session, q) for q in batch]
            batch_results = await asyncio.gather(*tasks)
            for query, suggestions in batch_results:
                results[query] = suggestions[:max_per_query]
            # Delay between batches to avoid rate limiting
            if i + BATCH_SIZE < len(queries):
                await asyncio.sleep(BATCH_DELAY)
    return results


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_keyword(keyword: str, existing_slugs: list) -> float:
    """
    Score a keyword 0–100.
    Criteria:
      - Length sweet spot: 3–6 words = +20
      - Too short (<=2 words) = -20
      - Intent signals ("how to", "what is", etc.) = +15
      - Language-specific = +10
      - Already exists in registry = -100 (skip)
    """
    score = 50.0
    words = keyword.lower().split()

    if 3 <= len(words) <= 6:
        score += 20
    elif len(words) <= 2:
        score -= 20

    intent_signals = ["how to", "what is", "difference between", "tutorial",
                      "example", "guide", "vs ", "best way"]
    if any(sig in keyword.lower() for sig in intent_signals):
        score += 15

    lang_names = ["python", "javascript", "typescript", "go", "rust",
                  "java", "kotlin", "swift", "php", "ruby", "csharp", "c#", "c++"]
    if any(lang in keyword.lower() for lang in lang_names):
        score += 10

    # Dedup check
    candidate_slug = keyword.lower().replace(" ", "-").strip("-")
    if any(candidate_slug in existing for existing in existing_slugs):
        score -= 100

    return min(max(score, 0.0), 100.0)


# ---------------------------------------------------------------------------
# Build query list
# ---------------------------------------------------------------------------

def build_all_queries() -> dict[str, list[str]]:
    """Build all seed queries grouped by ring. Returns {ring: [queries]}."""
    queries = {
        "tool_adjacent": list(SEED_TOPICS["tool_adjacent"]),
        "guides": list(SEED_TOPICS["guides"]),
        "concepts": [],
    }
    for concept in SEED_TOPICS["concepts"]:
        for lang in SEED_TOPICS["languages"]:
            queries["concepts"].append(f"how to {concept} in {lang}")
    return queries


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run() -> dict:
    """Discover keywords and store in registry.db. Returns pipeline result dict."""
    _ensure_seed_cache_table()

    # Load cache + existing slugs
    cached_seeds = _get_cached_seeds()
    existing_slugs = get_published_slugs()

    # Build queries, filter out already-fetched seeds
    all_queries = build_all_queries()
    max_per_ring = {
        "tool_adjacent": 5,
        "guides": 4,
        "concepts": 2,
    }

    queries_to_fetch = []
    ring_map = {}  # query -> ring name (for max_per_query)
    skipped_cached = 0

    for ring, seeds in all_queries.items():
        for seed in seeds:
            if seed in cached_seeds:
                skipped_cached += 1
                continue
            queries_to_fetch.append(seed)
            ring_map[seed] = ring

    total_queries = sum(len(v) for v in all_queries.values())
    print(f"  {total_queries} total seeds, {skipped_cached} cached, {len(queries_to_fetch)} to fetch")

    if not queries_to_fetch:
        print("  All seeds already fetched. No new queries needed.")
        return {"processed": 0, "passed": 0, "rejected": 0, "notes": "all seeds cached"}

    # Fetch all in async batches
    print(f"  Fetching {len(queries_to_fetch)} queries ({BATCH_SIZE} concurrent, {BATCH_DELAY}s between batches)...")
    results = asyncio.run(fetch_batch(queries_to_fetch, max_per_query=5))

    # Mark all fetched seeds as cached
    _mark_seeds_fetched(list(results.keys()))

    # Collect unique keywords from all suggestions
    keywords_to_check: set = set()
    for query, suggestions in results.items():
        ring = ring_map.get(query, "concepts")
        limit = max_per_ring.get(ring, 2)
        keywords_to_check.update(suggestions[:limit])

    print(f"  {len(keywords_to_check)} unique suggestions. Scoring...")

    discovered = 0
    skipped = 0

    for keyword in keywords_to_check:
        keyword = keyword.strip().lower()
        if not keyword or len(keyword) < 5:
            skipped += 1
            continue

        score = score_keyword(keyword, existing_slugs)
        if score <= 0:
            skipped += 1
            continue

        try:
            with get_db() as db:
                db.execute(
                    "INSERT OR IGNORE INTO keywords (keyword, competition, status) "
                    "VALUES (?, 'unknown', 'discovered')",
                    (keyword,),
                )
                if db.execute("SELECT changes()").fetchone()[0] > 0:
                    discovered += 1
                else:
                    skipped += 1
        except Exception as e:
            print(f"  DB error for '{keyword}': {e}")
            skipped += 1

    print(f"  Stored {discovered} new keywords ({skipped} skipped/duplicate).")
    return {"processed": len(keywords_to_check), "passed": discovered, "rejected": skipped}


if __name__ == "__main__":
    result = run()
    print(f"\nResult: {result}")
