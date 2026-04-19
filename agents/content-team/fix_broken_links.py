"""
One-shot audit+fix script for broken internal links in src/content/.

Usage:
  python agents/content-team/fix_broken_links.py --dry-run   # audit only
  python agents/content-team/fix_broken_links.py             # apply fixes
"""

import os
import re
import sys
from pathlib import Path

CONTENT_DIR = Path("src/content")

# Known typo rewrites in body prose (old_path -> new_path)
KNOWN_REWRITES = {
    "/tools/json-formatter-validator": "/tools/json-formatter",
}

STATIC_ROUTES = {
    "/", "/languages", "/guides", "/blog", "/cheatsheets",
    "/tools", "/about", "/cookie-policy",
    # Language index pages (one per language subfolder)
    "/languages/javascript", "/languages/python", "/languages/typescript",
    "/languages/rust", "/languages/go", "/languages/java", "/languages/cpp",
    "/languages/kotlin", "/languages/swift", "/languages/php",
}

DRY_RUN = "--dry-run" in sys.argv


def parse_frontmatter(text: str) -> tuple[dict, str, str]:
    """Return (fields_dict, raw_frontmatter_block, body). fields_dict is shallow."""
    if not text.startswith("---"):
        return {}, "", text
    end = text.index("---", 3)
    raw = text[3:end]
    body = text[end + 3:].lstrip("\n")
    fields: dict = {}
    current_key = None
    current_list = None
    for line in raw.splitlines():
        list_match = re.match(r"^(\w[\w_-]*):\s*$", line)
        scalar_match = re.match(r"^(\w[\w_-]*):\s+(.+)$", line)
        item_match = re.match(r"^- (.+)$", line)
        if list_match:
            current_key = list_match.group(1)
            current_list = []
            fields[current_key] = current_list
        elif scalar_match:
            current_key = scalar_match.group(1)
            current_list = None
            fields[current_key] = scalar_match.group(2).strip("'\"")
        elif item_match and current_list is not None:
            current_list.append(item_match.group(1).strip())
    return fields, raw, body


def build_url_set() -> set[str]:
    urls: set[str] = set(STATIC_ROUTES)

    for md in CONTENT_DIR.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        fields, _, _ = parse_frontmatter(text)
        parts = md.relative_to(CONTENT_DIR).parts
        collection = parts[0]
        file_slug = md.stem

        if collection == "languages":
            lang = fields.get("language", "")
            concept = fields.get("concept", "")
            if lang and concept:
                urls.add(f"/languages/{lang}/{concept}")
        elif collection == "tools":
            slug = fields.get("tool_slug") or file_slug
            urls.add(f"/tools/{slug}")
        elif collection in ("guides", "blog", "cheatsheets"):
            urls.add(f"/{collection}/{file_slug}")

    return urls


def fix_related_section(body: str, url_set: set[str]) -> tuple[str, list[str]]:
    """Drop broken list items from the in-body ## Related section."""
    # Allow optional blank line between heading and list items
    pattern = re.compile(
        r"^## Related\n(\n?)((?:- .+\n?)*)",
        re.MULTILINE,
    )
    dropped = []

    def replace(m: re.Match) -> str:
        blank = m.group(1)
        items_block = m.group(2)
        kept = []
        for line in items_block.splitlines(keepends=True):
            link_match = re.search(r"\((/[^)]+)\)", line)
            if link_match:
                path = link_match.group(1).split("#")[0]
                if path not in url_set:
                    dropped.append(f"  Dropped Related item: {line.strip()}")
                    continue
            kept.append(line)
        if not kept:
            dropped.append("  Dropped empty ## Related heading")
            return ""
        return "## Related\n" + blank + "".join(kept)

    new_body = pattern.sub(replace, body)
    return new_body, dropped


def fix_prose_links(body: str, url_set: set[str]) -> tuple[str, list[str]]:
    """Apply known typo rewrites; strip remaining broken prose links (keep link text)."""
    log = []

    # Apply known rewrites
    new_body = body
    for old, new in KNOWN_REWRITES.items():
        if old in new_body:
            new_body = new_body.replace(old, new)
            log.append(f"  Rewrote prose link: {old} → {new}")

    # Strip broken prose links outside ## Related — keep link text, drop href
    # Process in reverse so offsets stay valid after substitution
    def strip_broken(text: str) -> tuple[str, list[str]]:
        # Isolate ## Related block so we don't touch it
        related_re = re.compile(r"^## Related\n(\n?)((?:- .+\n?)*)", re.MULTILINE)
        related_spans = [(m.start(), m.end()) for m in related_re.finditer(text)]

        link_re = re.compile(r"\[([^\]]+)\]\((/[^)]+)\)")
        replacements = []
        for m in link_re.finditer(text):
            path = m.group(2).split("#")[0]
            if path in url_set:
                continue
            # Skip if inside a ## Related block
            in_related = any(s <= m.start() < e for s, e in related_spans)
            if in_related:
                continue
            replacements.append((m.start(), m.end(), m.group(1), m.group(0)))

        stripped_log = []
        result = text
        for start, end, link_text, full_match in reversed(replacements):
            result = result[:start] + link_text + result[end:]
            stripped_log.append(f"  Stripped broken prose link: {full_match} → {link_text}")

        return result, stripped_log

    new_body, stripped_log = strip_broken(new_body)
    log.extend(stripped_log)

    return new_body, log


def fix_frontmatter_arrays(raw_fm: str, fields: dict, url_set: set[str]) -> tuple[str, list[str]]:
    """Filter related_posts and related_tools arrays; clear broken related_cheatsheet."""
    log = []
    new_fm = raw_fm

    for field in ("related_posts", "related_tools"):
        items = fields.get(field)
        if not isinstance(items, list):
            continue
        for item in items:
            path = item.strip()
            if path.startswith("/") and path not in url_set:
                # Remove the list item line from frontmatter
                pattern = re.compile(r"^- " + re.escape(path) + r"\s*$", re.MULTILINE)
                if pattern.search(new_fm):
                    new_fm = pattern.sub("", new_fm)
                    log.append(f"  Dropped {field} entry: {path}")

    cheatsheet = fields.get("related_cheatsheet", "")
    if cheatsheet and cheatsheet.startswith("/") and cheatsheet not in url_set:
        new_fm = re.sub(
            r"^related_cheatsheet: .+$",
            "related_cheatsheet: ''",
            new_fm,
            flags=re.MULTILINE,
        )
        log.append(f"  Cleared related_cheatsheet: {cheatsheet}")

    return new_fm, log


def process_file(md: Path, url_set: set[str]) -> list[str]:
    text = md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return []

    fields, raw_fm, body = parse_frontmatter(text)
    rel_path = md.relative_to(Path("."))
    changes: list[str] = []

    new_fm, fm_log = fix_frontmatter_arrays(raw_fm, fields, url_set)
    new_body, related_log = fix_related_section(body, url_set)
    new_body, prose_log = fix_prose_links(new_body, url_set)

    all_log = fm_log + related_log + prose_log
    if not all_log:
        return []

    changes.append(str(rel_path))
    changes.extend(all_log)

    if not DRY_RUN:
        new_text = f"---{new_fm}---\n\n{new_body}"
        md.write_text(new_text, encoding="utf-8")

    return changes


def main():
    os.chdir(Path(__file__).parent.parent.parent)  # repo root
    url_set = build_url_set()
    print(f"Built URL set: {len(url_set)} routes")

    all_changes = []
    for md in sorted(CONTENT_DIR.rglob("*.md")):
        changes = process_file(md, url_set)
        if changes:
            all_changes.extend(changes)
            all_changes.append("")

    if not all_changes:
        print("No broken links found.")
        return

    mode = "DRY RUN" if DRY_RUN else "APPLIED"
    print(f"\n=== {mode} ===")
    for line in all_changes:
        print(line)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    main()
