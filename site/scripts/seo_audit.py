# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "python-frontmatter>=1.1.0",
#   "scikit-learn>=1.4.0",
#   "numpy>=1.26.0",
# ]
# ///
"""
SEO content audit for DevNook.

Usage:
    uv run scripts/seo_audit.py

Output:
    audits/seo_audit_YYYY-MM-DD.csv   — per-post metrics + verdict
    stdout                             — summary + top similar pairs
"""

import csv
import os
import re
import sys
from datetime import date
from pathlib import Path

import frontmatter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
CONTENT_ROOT = REPO_ROOT / "src" / "content"
AUDITS_DIR = REPO_ROOT / "audits"

COLLECTIONS = ["languages", "guides", "cheatsheets", "blog"]

# Similarity thresholds
PROSE_WARN = 0.65
PROSE_FAIL = 0.80

# Word-count fallback when no word_count_target in frontmatter
DEFAULT_TARGET = 800

# Language tokens to strip before cross-language similarity comparison
LANGUAGE_TOKENS = [
    "python", "javascript", "typescript", "java", "cpp", "c\\+\\+",
    "go", "golang", "rust", "swift", "kotlin", "php", "ruby",
    "node", "nodejs", "node\\.js",
]

# Concept synonym map — maps variant slugs → canonical slug
CONCEPT_SYNONYMS = {
    "json-decode":        "json-parse",
    "parse-json":         "json-parse",
    "json-parsing":       "json-parse",
    "json-encode":        "json-stringify",
    "stringify-json":     "json-stringify",
    "dict-comprehension": "dict-comprehension",
    "dictionary-comprehension": "dict-comprehension",
    "list-comprehension": "list-comprehension",
    "lambda":             "lambda-function",
    "arrow-function":     "lambda-function",
    "anonymous-function": "lambda-function",
    "env-variables":      "environment-variables",
    "env-vars":           "environment-variables",
    "dotenv":             "environment-variables",
    "catch-exception":    "error-handling",
    "catch-error":        "error-handling",
    "exception-handling": "error-handling",
    "handle-errors":      "error-handling",
    "try-catch":          "error-handling",
    "try-except":         "error-handling",
}

# Title filler words to ignore when computing Jaccard on title tokens
TITLE_FILLER = {
    "how", "to", "a", "an", "the", "in", "with", "using", "complete",
    "guide", "tutorial", "example", "examples", "introduction", "intro",
}

# ---------------------------------------------------------------------------
# Helpers: text normalization
# ---------------------------------------------------------------------------

_CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_HEADING_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_FRONTMATTER_RE = re.compile(r"^---[\s\S]*?---\n", re.MULTILINE)


def extract_code_blocks(body: str) -> list[str]:
    return _CODE_FENCE_RE.findall(body)


def strip_prose(body: str) -> str:
    text = _FRONTMATTER_RE.sub("", body)
    text = _CODE_FENCE_RE.sub(" ", text)
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _MD_IMAGE_RE.sub(" ", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _HEADING_RE.sub(" ", text)
    return text


def neutralize_language_tokens(prose: str, extra_token: str | None = None) -> str:
    tokens = list(LANGUAGE_TOKENS)
    if extra_token and extra_token.lower() not in tokens:
        tokens.append(re.escape(extra_token.lower()))
    pattern = r"(?<![a-z0-9_])(" + "|".join(tokens) + r")(?![a-z0-9_])"
    return re.sub(pattern, " ", prose, flags=re.IGNORECASE)


def word_count(prose: str) -> int:
    return len(prose.split())


def normalize_concept(slug: str) -> str:
    s = slug.lower().strip()
    return CONCEPT_SYNONYMS.get(s, s)


def title_tokens(title: str, language: str | None = None) -> set[str]:
    raw = set(re.findall(r"[a-z0-9]+", title.lower()))
    tokens = raw - TITLE_FILLER
    if language:
        tokens.discard(language.lower())
    return tokens


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def normalize_code_lines(code_block: str) -> set[str]:
    lines = code_block.splitlines()
    return {l.strip() for l in lines if l.strip() and not l.strip().startswith("#")}


def code_jaccard(blocks_a: list[str], blocks_b: list[str]) -> float:
    if not blocks_a or not blocks_b:
        return 0.0
    lines_a: set[str] = set()
    lines_b: set[str] = set()
    for b in blocks_a:
        lines_a |= normalize_code_lines(b)
    for b in blocks_b:
        lines_b |= normalize_code_lines(b)
    return jaccard(lines_a, lines_b)


# ---------------------------------------------------------------------------
# URL builder (mirrors devnookUrlBuilder in astro.config.mjs)
# ---------------------------------------------------------------------------

def build_url(collection: str, slug: str, fm: dict) -> str:
    if collection == "languages":
        lang = fm.get("language", "").lower().strip()
        concept = fm.get("concept", "").lower().strip()
        if lang and concept:
            return f"/languages/{lang}/{concept}/"
    return f"/{collection}/{slug}/"


# ---------------------------------------------------------------------------
# Load posts
# ---------------------------------------------------------------------------

def load_posts() -> list[dict]:
    posts = []
    for coll in COLLECTIONS:
        coll_dir = CONTENT_ROOT / coll
        if not coll_dir.exists():
            continue
        for md_path in sorted(coll_dir.rglob("*.md")):
            post = frontmatter.load(str(md_path))
            fm = dict(post.metadata)
            body = post.content

            # Slug = stem of file
            slug = md_path.stem

            # Detect path_issue: language post not inside a language subfolder
            # (i.e., parent dir is the collection dir itself)
            path_issue = False
            if coll == "languages":
                rel = md_path.relative_to(coll_dir)
                path_issue = len(rel.parts) == 1  # no language subdir

            code_blocks = extract_code_blocks(body)
            prose = strip_prose(body)
            language = fm.get("language", None)
            prose_neutralized = neutralize_language_tokens(prose, language)

            posts.append({
                "path": md_path,
                "collection": coll,
                "slug": slug,
                "fm": fm,
                "body": body,
                "prose": prose,
                "prose_neutralized": prose_neutralized,
                "code_blocks": code_blocks,
                "language": (language or "").lower(),
                "concept_raw": fm.get("concept", ""),
                "concept": normalize_concept(fm.get("concept", "")),
                "title": fm.get("title", slug),
                "target": fm.get("word_count_target", DEFAULT_TARGET),
                "word_count": word_count(prose),
                "code_block_count": len(code_blocks),
                "code_chars": sum(len(b) for b in code_blocks),
                "section_count": len(re.findall(r"^## ", body, re.MULTILINE)),
                "path_issue": path_issue,
                "url": build_url(coll, slug, fm),
            })
    return posts


# ---------------------------------------------------------------------------
# Concept clustering (languages collection only)
# ---------------------------------------------------------------------------

def build_concept_clusters(posts: list[dict]) -> dict[int, str]:
    """Return a mapping of post index → cluster label for language posts."""
    lang_posts = [(i, p) for i, p in enumerate(posts) if p["collection"] == "languages"]

    # Union-Find
    parent = {i: i for i, _ in lang_posts}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    # First pass: group by normalized concept
    concept_to_indices: dict[str, list[int]] = {}
    for i, p in lang_posts:
        c = p["concept"]
        concept_to_indices.setdefault(c, []).append(i)
    for indices in concept_to_indices.values():
        for idx in indices[1:]:
            union(indices[0], idx)

    # Second pass: title-token Jaccard fallback (threshold 0.5)
    lang_list = list(lang_posts)
    for a_idx, (i, pi) in enumerate(lang_list):
        for j, pj in lang_list[a_idx + 1:]:
            if find(i) == find(j):
                continue
            ti = title_tokens(pi["title"], pi["language"])
            tj = title_tokens(pj["title"], pj["language"])
            if jaccard(ti, tj) >= 0.5:
                union(i, j)

    # Assign readable cluster labels (use the most common concept in cluster)
    clusters: dict[int, str] = {}
    root_to_posts: dict[int, list[int]] = {}
    for i, _ in lang_posts:
        r = find(i)
        root_to_posts.setdefault(r, []).append(i)

    for root, members in root_to_posts.items():
        concept_counts: dict[str, int] = {}
        for idx in members:
            c = posts[idx]["concept"]
            concept_counts[c] = concept_counts.get(c, 0) + 1
        label = max(concept_counts, key=concept_counts.__getitem__)
        for idx in members:
            clusters[idx] = label

    return clusters


# ---------------------------------------------------------------------------
# Similarity computation
# ---------------------------------------------------------------------------

def compute_similarities(posts: list[dict], clusters: dict[int, str]):
    """
    For each language post, compute max_similarity to peers in the same cluster.
    Returns dict: post_index → {max_similarity, peers_in_cluster, has_unique_examples, best_peer_idx, best_peer_code_sim}
    """
    # Group by cluster label
    cluster_members: dict[str, list[int]] = {}
    for idx, label in clusters.items():
        cluster_members.setdefault(label, []).append(idx)

    # Build TF-IDF over ALL posts' prose_neutralized (stable IDF)
    all_texts = [p["prose_neutralized"] for p in posts]
    vectorizer = TfidfVectorizer(
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
        stop_words="english",
    )
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    results: dict[int, dict] = {}

    for label, members in cluster_members.items():
        if len(members) < 2:
            # Solo post, no peers
            for idx in members:
                results[idx] = {
                    "max_similarity": 0.0,
                    "peers_in_cluster": 0,
                    "has_unique_examples": True,
                    "best_peer_idx": None,
                    "best_peer_code_sim": 0.0,
                }
            continue

        # Compute pairwise cosine on neutralized prose
        member_vectors = tfidf_matrix[members]
        sim_matrix = cosine_similarity(member_vectors)

        for local_i, idx in enumerate(members):
            sims = [
                (sim_matrix[local_i, local_j], members[local_j])
                for local_j in range(len(members))
                if local_j != local_i
            ]
            sims.sort(reverse=True)
            max_sim, best_peer = sims[0]

            # Code uniqueness: at least one code block has low Jaccard with all peers
            my_blocks = posts[idx]["code_blocks"]
            has_unique = False
            best_code_sim = 0.0

            for _, peer_idx in sims:
                peer_blocks = posts[peer_idx]["code_blocks"]
                csim = code_jaccard(my_blocks, peer_blocks)
                best_code_sim = max(best_code_sim, csim)

            if my_blocks:
                for block in my_blocks:
                    block_unique = True
                    for _, peer_idx in sims:
                        for peer_block in posts[peer_idx]["code_blocks"]:
                            peer_lines = normalize_code_lines(peer_block)
                            my_lines = normalize_code_lines(block)
                            if jaccard(my_lines, peer_lines) >= 0.5:
                                block_unique = False
                                break
                        if not block_unique:
                            break
                    if block_unique:
                        has_unique = True
                        break
            else:
                has_unique = False

            results[idx] = {
                "max_similarity": round(float(max_sim), 4),
                "peers_in_cluster": len(members) - 1,
                "has_unique_examples": has_unique,
                "best_peer_idx": best_peer,
                "best_peer_code_sim": round(best_code_sim, 4),
            }

    return results


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def assign_verdict(post: dict, sim_info: dict | None) -> tuple[str, list[str]]:
    flags = []
    wc = post["word_count"]
    target = post["target"]
    max_sim = sim_info["max_similarity"] if sim_info else 0.0
    peers = sim_info["peers_in_cluster"] if sim_info else 0
    has_unique = sim_info["has_unique_examples"] if sim_info else True

    # Fail conditions
    if wc < target // 2:
        flags.append(f"word_count_critical ({wc}<{target//2})")
    if max_sim >= PROSE_FAIL:
        flags.append(f"prose_similarity_fail ({max_sim:.2f}>={PROSE_FAIL})")
    if peers >= 1 and not has_unique:
        flags.append("no_unique_code_examples")

    fail_flags = [f for f in flags]

    # Warn conditions
    warn_flags = []
    if wc < target and wc >= target // 2:
        warn_flags.append(f"below_target ({wc}<{target})")
    if PROSE_WARN <= max_sim < PROSE_FAIL:
        warn_flags.append(f"prose_similarity_warn ({max_sim:.2f}>={PROSE_WARN})")
    if post["path_issue"]:
        warn_flags.append("path_issue_root_level")
    if post["code_block_count"] == 0:
        warn_flags.append("no_code_blocks")

    all_flags = fail_flags + warn_flags

    if fail_flags:
        verdict = "fail"
    elif warn_flags:
        verdict = "warn"
    else:
        verdict = "pass"

    return verdict, all_flags


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading posts...")
    posts = load_posts()
    print(f"  {len(posts)} posts loaded across {COLLECTIONS}")

    print("Building concept clusters (languages)...")
    clusters = build_concept_clusters(posts)
    cluster_by_idx = {i: clusters.get(i, "") for i in range(len(posts))}

    print("Computing similarities...")
    sim_results = compute_similarities(posts, clusters)

    # Build rows
    rows = []
    for i, post in enumerate(posts):
        sim_info = sim_results.get(i)
        verdict, flags = assign_verdict(post, sim_info)

        rows.append({
            "page_url": post["url"],
            "collection": post["collection"],
            "language": post["language"],
            "concept": post["concept_raw"],
            "concept_cluster": cluster_by_idx.get(i, ""),
            "word_count": post["word_count"],
            "target": post["target"],
            "code_blocks": post["code_block_count"],
            "section_count": post["section_count"],
            "max_similarity": sim_info["max_similarity"] if sim_info else 0.0,
            "peers_in_cluster": sim_info["peers_in_cluster"] if sim_info else 0,
            "has_unique_examples": sim_info["has_unique_examples"] if sim_info else True,
            "path_issue": post["path_issue"],
            "verdict": verdict,
            "flags": "; ".join(flags),
        })

    # Write CSV
    AUDITS_DIR.mkdir(exist_ok=True)
    today = date.today().isoformat()
    csv_path = AUDITS_DIR / f"seo_audit_{today}.csv"
    fieldnames = [
        "page_url", "collection", "language", "concept", "concept_cluster",
        "word_count", "target", "code_blocks", "section_count",
        "max_similarity", "peers_in_cluster", "has_unique_examples",
        "path_issue", "verdict", "flags",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCSV written -> {csv_path.relative_to(REPO_ROOT)}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    total = len(rows)
    by_verdict = {"pass": 0, "warn": 0, "fail": 0}
    for r in rows:
        by_verdict[r["verdict"]] += 1

    print("\n" + "=" * 60)
    print("SEO AUDIT SUMMARY")
    print("=" * 60)
    print(f"Total posts audited : {total}")
    print(f"  PASS  : {by_verdict['pass']}  ({by_verdict['pass']/total*100:.0f}%)")
    print(f"  WARN  : {by_verdict['warn']}  ({by_verdict['warn']/total*100:.0f}%)")
    print(f"  FAIL  : {by_verdict['fail']}  ({by_verdict['fail']/total*100:.0f}%)")

    # Structural issues
    path_issues = [r for r in rows if r["path_issue"]]
    if path_issues:
        print(f"\nStructural issues ({len(path_issues)} root-level language files):")
        for r in path_issues:
            print(f"  {r['page_url']}")

    # Urgent rewrites (below target/2)
    critical = [r for r in rows if r["word_count"] < r["target"] // 2]
    if critical:
        print(f"\nUrgent rewrites — below target/2 ({len(critical)} posts):")
        for r in sorted(critical, key=lambda x: x["word_count"]):
            print(f"  {r['page_url']}  {r['word_count']} words (target {r['target']})")

    # Top 10 most similar pairs
    pairs = []
    lang_posts_idx = [i for i, p in enumerate(posts) if p["collection"] == "languages"]
    seen_pairs: set[frozenset] = set()

    for i in lang_posts_idx:
        info = sim_results.get(i)
        if not info or info["best_peer_idx"] is None:
            continue
        j = info["best_peer_idx"]
        key = frozenset([i, j])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        pairs.append({
            "a": posts[i]["url"],
            "b": posts[j]["url"],
            "prose_sim": info["max_similarity"],
            "code_sim": info["best_peer_code_sim"],
        })

    pairs.sort(key=lambda x: x["prose_sim"], reverse=True)
    top_pairs = pairs[:10]

    if top_pairs:
        print(f"\nTop {len(top_pairs)} most similar pairs (prose similarity):")
        print(f"  {'Prose':>6}  {'Code':>6}  A  <->  B")
        for p in top_pairs:
            print(f"  {p['prose_sim']:>6.3f}  {p['code_sim']:>6.3f}  {p['a']}  <->  {p['b']}")

    print("\n" + "=" * 60)
    print(f"Full report: {csv_path}")


if __name__ == "__main__":
    main()
