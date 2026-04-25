"""
Rule-based internal link inserter for DevNook pipeline.
80% deterministic string matching; no LLM calls.
"""

import re
import sys
import sqlite3
import argparse
import json
from contextlib import contextmanager
from pathlib import Path
from dataclasses import dataclass

import frontmatter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.registry import update_post_status

REGISTRY_PATH = str(Path(__file__).resolve().parent / "registry.db")
DRAFTS_DIR = Path(__file__).resolve().parent / "drafts"

MAX_LINKS = 8
THIN_THRESHOLD = 3


@dataclass
class Anchor:
    text: str
    url: str
    slug: str
    category: str
    opportunity_score: float = 0.0


def _url_for_row(row) -> str:
    cat = row["category"] or ""
    slug = row["slug"] or ""
    if cat == "languages":
        lang = (row["language"] or "").lower()
        concept = (row["concept"] or "").lower()
        return f"/languages/{lang}/{concept}"
    if cat == "guides":
        return f"/guides/{slug}"
    if cat == "blog":
        return f"/blog/{slug}"
    if cat == "cheatsheets":
        return f"/cheatsheets/{slug}"
    if cat == "tools":
        return f"/tools/{slug}"
    return f"/{cat}/{slug}"


def _humanize(slug: str) -> list[str]:
    """kebab-case slug → list of human-readable variants."""
    words = slug.replace("-", " ")
    return [words]


def _concept_variants(concept: str) -> list[str]:
    """async-await → ['async/await', 'async await']"""
    variants = []
    with_slash = concept.replace("-", "/")
    with_space = concept.replace("-", " ")
    if with_slash != concept:
        variants.append(with_slash)
    if with_space != concept and with_space not in variants:
        variants.append(with_space)
    return variants


@contextmanager
def _open_db(registry_path: str):
    conn = sqlite3.connect(registry_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def build_anchor_map(registry_path: str, exclude_slug: str | None = None) -> list[Anchor]:
    anchors: list[Anchor] = []
    seen_urls: set[str] = set()

    with _open_db(registry_path) as db:
        rows = db.execute(
            "SELECT slug, title, category, language, concept, opportunity_score "
            "FROM posts WHERE status IN ('staged', 'published', 'linked')"
        ).fetchall()

    for row in rows:
        if exclude_slug and row["slug"] == exclude_slug:
            continue
        url = _url_for_row(row)
        if url in seen_urls:
            continue
        seen_urls.add(url)

        opp = row["opportunity_score"] or 0.0
        cat = row["category"] or ""
        slug = row["slug"] or ""

        def _anchor(text: str) -> Anchor:
            return Anchor(text=text.lower(), url=url, slug=slug, category=cat, opportunity_score=opp)

        # Title
        title = row["title"] or ""
        if title:
            anchors.append(_anchor(title))

        # Slug humanized
        for v in _humanize(slug):
            if v and v.lower() != title.lower():
                anchors.append(_anchor(v))

        # Concept variants (languages only)
        concept = row["concept"] or ""
        if concept and cat == "languages":
            for v in _concept_variants(concept):
                anchors.append(_anchor(v))

        # Language — yields only the language index URL
        language = row["language"] or ""
        if language and cat == "languages":
            lang_url = f"/languages/{language.lower()}"
            if lang_url not in seen_urls:
                seen_urls.add(lang_url)
                anchors.append(Anchor(text=language.lower(), url=lang_url, slug=slug,
                                      category=cat, opportunity_score=opp))

    # Longest match first so "JSON parser" wins over "JSON"
    anchors.sort(key=lambda a: len(a.text), reverse=True)
    return anchors


# Patterns for skip regions
_FENCED_CODE = re.compile(r"^```")
_HEADING = re.compile(r"^\s*#{1,6}\s")
_EXISTING_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_INLINE_CODE = re.compile(r"`[^`]+`")
_FRONTMATTER_SEP = re.compile(r"^---\s*$")


def _insert_links(body: str, anchors: list[Anchor], self_url: str) -> tuple[str, list[str]]:
    """Walk body and insert up to MAX_LINKS anchor links. Returns (new_body, anchors_used)."""
    lines = body.split("\n")
    used_texts: set[str] = set()
    used_urls: set[str] = set()
    anchors_used: list[str] = []
    link_count = 0
    in_fence = False

    result_lines = []
    for line in lines:
        # Track fenced code blocks
        if _FENCED_CODE.match(line):
            in_fence = not in_fence
            result_lines.append(line)
            continue

        # Skip inside fenced code or headings
        if in_fence or _HEADING.match(line):
            result_lines.append(line)
            continue

        if link_count >= MAX_LINKS:
            result_lines.append(line)
            continue

        # Build mask of spans that must not be re-linked:
        # existing markdown links and inline code
        skip_spans: list[tuple[int, int]] = []
        for m in _EXISTING_LINK.finditer(line):
            skip_spans.append((m.start(), m.end()))
        for m in _INLINE_CODE.finditer(line):
            skip_spans.append((m.start(), m.end()))
        skip_spans.sort()

        for anchor in anchors:
            if link_count >= MAX_LINKS:
                break
            if anchor.text in used_texts:
                continue
            if anchor.url in used_urls:
                continue
            if anchor.url == self_url:
                continue

            pattern = re.compile(
                r"(?<!\[)(?<!\()\b(" + re.escape(anchor.text) + r")\b(?!\])",
                re.IGNORECASE,
            )

            match = pattern.search(line)
            if not match:
                continue

            # Check it's not in a skip span
            ms, me = match.start(1), match.end(1)
            in_skip = any(ss <= ms and me <= se for ss, se in skip_spans)
            if in_skip:
                continue

            # Replace first occurrence only, preserving original casing
            original = match.group(1)
            replacement = f"[{original}]({anchor.url})"
            line = line[:ms] + replacement + line[me:]

            # Shift subsequent skip spans by the added characters
            delta = len(replacement) - len(original)
            skip_spans = [
                (ss if se <= ms else (ss + delta, se + delta))
                for ss, se in skip_spans
            ]

            used_texts.add(anchor.text)
            used_urls.add(anchor.url)
            anchors_used.append(anchor.text)
            link_count += 1
            break  # one anchor per pass through the line

        result_lines.append(line)

    return "\n".join(result_lines), anchors_used


def _count_existing_links(body: str) -> int:
    return len(_EXISTING_LINK.findall(body))


def _candidates_for_llm(slug: str, registry_path: str, n: int = 10) -> list[dict]:
    """Top N posts ranked: same-category first, then opportunity_score DESC."""
    with _open_db(registry_path) as db:
        row = db.execute(
            "SELECT category FROM posts WHERE slug=?", (slug,)
        ).fetchone()
        if not row:
            return []
        my_cat = row["category"] or ""

        candidates = db.execute(
            "SELECT slug, category, language, concept, opportunity_score FROM posts "
            "WHERE status IN ('staged', 'published', 'linked') AND slug != ?",
            (slug,)
        ).fetchall()

    def rank(c):
        same_cat = 1 if c["category"] == my_cat else 0
        return (same_cat, c["opportunity_score"] or 0.0)

    sorted_c = sorted(candidates, key=rank, reverse=True)[:n]
    return [
        {"slug": c["slug"], "url": _url_for_row(c), "category": c["category"]}
        for c in sorted_c
    ]


def link_post(draft_path: str, registry_path: str) -> dict:
    path = Path(draft_path)
    if not path.exists():
        return {"slug": path.stem, "links_inserted": 0, "anchors_used": [],
                "status": "error", "error": "file_not_found"}
    try:
        post = frontmatter.load(str(path))
    except Exception as e:
        return {"slug": path.stem, "links_inserted": 0, "anchors_used": [],
                "status": "error", "error": str(e)}

    slug = post.metadata.get("slug", path.stem)
    category = post.metadata.get("category", "")
    language = post.metadata.get("language", "")
    concept = post.metadata.get("concept", "")

    # Derive self URL
    if category == "languages" and language and concept:
        self_url = f"/languages/{language.lower()}/{concept.lower()}"
    elif category:
        self_url = f"/{category}/{slug}"
    else:
        self_url = f"/{slug}"

    existing = _count_existing_links(post.content)
    anchors = build_anchor_map(registry_path, exclude_slug=slug)
    new_body, anchors_used = _insert_links(post.content, anchors, self_url)
    links_inserted = len(anchors_used)
    total_links = existing + links_inserted

    new_post = frontmatter.Post(new_body, **post.metadata)
    path.write_text(frontmatter.dumps(new_post), encoding="utf-8")

    status = "linked" if total_links >= THIN_THRESHOLD else "thin"
    result: dict = {
        "slug": slug,
        "links_inserted": links_inserted,
        "anchors_used": anchors_used,
        "status": status,
    }
    if status == "thin":
        result["candidates_for_llm"] = _candidates_for_llm(slug, registry_path)

    return result


def link_retrofit(content_path: str, registry_path: str) -> dict:
    """Link a published file in place. Does NOT update registry."""
    return link_post(content_path, registry_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli_draft(draft_path: str) -> None:
    result = link_post(draft_path, REGISTRY_PATH)
    if result["status"] != "error":
        update_post_status(result["slug"], "linked")
    print(json.dumps(result, indent=2))


def _cli_batch_status(status_filter: str) -> None:
    with _open_db(REGISTRY_PATH) as db:
        rows = db.execute(
            "SELECT slug, file_path FROM posts WHERE status=?", (status_filter,)
        ).fetchall()

    results = []
    for row in rows:
        fp = row["file_path"] or str(DRAFTS_DIR / f"{row['slug']}.md")
        result = link_post(fp, REGISTRY_PATH)
        if result["status"] in ("linked", "thin"):
            update_post_status(row["slug"], "linked")
        results.append(result)

    print(json.dumps(results, indent=2))


def _cli_retrofit(content_path: str) -> None:
    result = link_retrofit(content_path, REGISTRY_PATH)
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="DevNook internal link inserter")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--draft", metavar="PATH", help="Link one draft file in place")
    group.add_argument("--batch-status", metavar="STATUS",
                       help="Link all registry rows with given status")
    group.add_argument("--retrofit", metavar="PATH",
                       help="Link a published file in place (no registry update)")
    args = parser.parse_args()

    if args.draft:
        _cli_draft(args.draft)
    elif args.batch_status:
        _cli_batch_status(args.batch_status)
    elif args.retrofit:
        _cli_retrofit(args.retrofit)


if __name__ == "__main__":
    main()
