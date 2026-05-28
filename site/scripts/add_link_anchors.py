"""
Batch-add linkAnchors to language posts frontmatter.

Concepts shared across multiple languages get only language-prefixed anchors.
Unique concepts also get a bare humanized form as an additional anchor.
"""

import os
import re
import sys

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'languages')

# Concepts shared by 2+ language posts — only use language-prefixed anchor for these
SHARED_CONCEPTS = {
    'async-await',       # javascript, rust, typescript
    'closures',          # javascript, swift
    'environment-variables',  # java, php, rust
    'file-handling',     # python, java
    'format-string',     # kotlin, php
}

# Extra anchors beyond the standard language+concept pair
EXTRA_ANCHORS = {
    ('go', 'goroutines'):           ['golang goroutines'],
    ('javascript', 'promises'):     ['promises in javascript'],
    ('javascript', 'array-methods'):['array methods in javascript'],
    ('javascript', 'closures'):     ['closures in javascript'],
    ('javascript', 'async-await'):  ['async/await in javascript'],
    ('typescript', 'async-await'):  ['typescript async/await'],
    ('rust', 'pattern-matching'):   ['pattern matching in rust'],
    ('python', 'list-comprehension'):['list comprehensions'],
    ('cpp', 'http-requests'):       ['c++ http requests'],
    ('cpp', 'class-inheritance'):   ['c++ inheritance'],
    ('cpp', 'c-handle-exception'):  ['c++ exceptions'],
    ('csharp', 'exception-handling'):['c# exception handling'],
    ('java', 'lambda-functions'):   ['java lambda', 'lambda in java'],
    ('java', 'rest-api'):           ['java rest api'],
}

def humanize(concept):
    return concept.replace('-', ' ')

def generate_anchors(language, concept):
    h = humanize(concept)
    lang = language.lower()
    anchors = []

    # Primary: language + humanized concept
    anchors.append(f"{lang} {h}")

    # Bare form for unique concepts only
    if concept not in SHARED_CONCEPTS:
        anchors.append(h)

    # Extra variants
    key = (lang, concept)
    if key in EXTRA_ANCHORS:
        anchors.extend(EXTRA_ANCHORS[key])

    # Deduplicate preserving order
    seen = set()
    result = []
    for a in anchors:
        if a not in seen:
            seen.add(a)
            result.append(a)
    return result


def format_anchors_yaml(anchors, indent=0):
    """Format anchors as YAML list lines with optional indent."""
    prefix = ' ' * indent
    lines = ['linkAnchors:']
    for a in anchors:
        lines.append(f'{prefix}  - "{a}"')
    return '\n'.join(lines)


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Already has linkAnchors — skip
    if 'linkAnchors:' in content:
        return False

    # Parse frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not fm_match:
        print(f'  SKIP (no frontmatter): {filepath}')
        return False

    fm_block = fm_match.group(1)

    # Extract language and concept
    lang_m = re.search(r'^language:\s*["\']?([a-z0-9-]+)["\']?', fm_block, re.MULTILINE)
    concept_m = re.search(r'^concept:\s*["\']?([a-z0-9-]+)["\']?', fm_block, re.MULTILINE)

    if not lang_m or not concept_m:
        print(f'  SKIP (missing language/concept): {filepath}')
        return False

    language = lang_m.group(1)
    concept = concept_m.group(1)

    anchors = generate_anchors(language, concept)

    # Insert linkAnchors after the concept line
    anchor_yaml = format_anchors_yaml(anchors)

    # Insert after `concept: ...` line
    new_fm = re.sub(
        r'(^concept:\s*["\']?[a-z0-9-]+["\']?\s*$)',
        r'\1\n' + anchor_yaml,
        fm_block,
        flags=re.MULTILINE,
        count=1,
    )

    new_content = content.replace(fm_match.group(1), new_fm, 1)

    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

    rel = os.path.relpath(filepath, os.path.join(CONTENT_DIR, '..', '..', '..'))
    print(f'  Updated {rel}: {anchors}')
    return True


def main():
    updated = 0
    skipped = 0
    for root, dirs, files in os.walk(CONTENT_DIR):
        for fname in sorted(files):
            if fname.endswith('.md') or fname.endswith('.mdx'):
                fp = os.path.join(root, fname)
                if process_file(fp):
                    updated += 1
                else:
                    skipped += 1

    print(f'\nDone: {updated} updated, {skipped} skipped.')


if __name__ == '__main__':
    main()
