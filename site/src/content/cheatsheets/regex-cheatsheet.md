---
title: "Regex Cheat Sheet"
description: "A complete regex cheat sheet covering pattern syntax, quantifiers, anchors, groups, lookaheads, and flags — the universal reference for regular expressions."
category: cheatsheets
template_id: cheatsheet-v1
tags: [regex, regular-expressions, pattern-matching, cheatsheet, programming]
related_posts: []
related_tools: []
published_date: "2026-04-25"
og_image: "/og/cheatsheets/regex-cheatsheet.png"
downloadable: true
content_type: editorial
---

# Regex Cheat Sheet

Regular expressions are a universal pattern-matching language supported by every major programming language and many command-line tools. This reference covers the full syntax — from basic character classes to advanced lookaheads — so you can write and read regex confidently.

## Character Classes & Literals

| Pattern | Matches |
|---------|---------|
| `abc` | Literal characters "abc" in sequence |
| `.` | Any single character except newline |
| `\d` | Any digit: `[0-9]` |
| `\D` | Any non-digit |
| `\w` | Any word character: `[a-zA-Z0-9_]` |
| `\W` | Any non-word character |
| `\s` | Any whitespace: space, tab, newline |
| `\S` | Any non-whitespace character |
| `[abc]` | Any one of: a, b, or c |
| `[^abc]` | Any character except a, b, or c |
| `[a-z]` | Any lowercase letter |
| `[A-Z]` | Any uppercase letter |
| `[0-9]` | Any digit (same as `\d`) |
| `[a-zA-Z0-9]` | Any alphanumeric character |
| `\t` | Tab character |
| `\n` | Newline character |
| `\r` | Carriage return |
| `\\` | Literal backslash |

```python
import re

# Match any digit sequence
re.findall(r'\d+', 'Order 42, item 7')
# ['42', '7']

# Match a word character sequence
re.findall(r'\w+', 'hello_world 123')
# ['hello_world', '123']
```

## Anchors & Boundaries

Anchors match a **position** in the string, not a character.

| Pattern | Matches |
|---------|---------|
| `^` | Start of string (or line in multiline mode) |
| `$` | End of string (or line in multiline mode) |
| `\b` | Word boundary (between `\w` and `\W`) |
| `\B` | Non-word boundary |
| `\A` | Absolute start of string |
| `\Z` | Absolute end of string |

```python
# Match "cat" only at the start of the string
re.match(r'^cat', 'catch')   # matches
re.match(r'^cat', 'the cat') # no match

# Word boundary: match "cat" as a whole word only
re.findall(r'\bcat\b', 'the cat scattered')
# ['cat']  — "cat" in "scattered" is not matched
```

## Quantifiers

Quantifiers specify **how many times** the preceding element must match.

| Quantifier | Meaning |
|-----------|---------|
| `*` | 0 or more (greedy) |
| `+` | 1 or more (greedy) |
| `?` | 0 or 1 (optional) |
| `{n}` | Exactly n times |
| `{n,}` | n or more times |
| `{n,m}` | Between n and m times (inclusive) |
| `*?` | 0 or more (lazy — matches as few as possible) |
| `+?` | 1 or more (lazy) |
| `??` | 0 or 1 (lazy) |
| `{n,m}?` | Between n and m (lazy) |

### Greedy vs Lazy

```python
text = '<b>bold</b> and <i>italic</i>'

# Greedy — matches as much as possible
re.findall(r'<.+>', text)
# ['<b>bold</b> and <i>italic</i>']

# Lazy — matches as little as possible
re.findall(r'<.+?>', text)
# ['<b>', '</b>', '<i>', '</i>']
```

## Groups & Alternation

| Pattern | Description |
|---------|-------------|
| `(abc)` | Capturing group — captures matched text |
| `(?:abc)` | Non-capturing group — groups without capturing |
| `(?P<name>abc)` | Named capturing group (Python/PCRE) |
| `a\|b` | Alternation — match "a" or "b" |
| `\1` | Backreference to group 1 |
| `(?P=name)` | Backreference to named group |

```python
# Extract protocol and domain from a URL
pattern = r'(?P<protocol>https?)://(?P<domain>[^/]+)'
m = re.match(pattern, 'https://devnook.dev/guides/')
m.group('protocol')  # 'https'
m.group('domain')    # 'devnook.dev'

# Alternation: match "colour" or "color"
re.findall(r'colo(?:u|)r', 'colour and color')
# ['colour', 'color']

# Backreference: find repeated words
re.findall(r'\b(\w+)\s+\1\b', 'the the fox')
# ['the']
```

## Lookaheads & Lookbehinds

Lookarounds are **zero-width assertions** — they check context without consuming characters.

| Pattern | Type | Description |
|---------|------|-------------|
| `(?=abc)` | Positive lookahead | Match if followed by "abc" |
| `(?!abc)` | Negative lookahead | Match if NOT followed by "abc" |
| `(?<=abc)` | Positive lookbehind | Match if preceded by "abc" |
| `(?<!abc)` | Negative lookbehind | Match if NOT preceded by "abc" |

```python
# Find numbers followed by "px"
re.findall(r'\d+(?=px)', '12px 5em 100px')
# ['12', '100']

# Find "foo" not preceded by "no"
re.findall(r'(?<!no)foo', 'foobar nofoo')
# ['foo']  — only the first match

# Extract values inside quotes
re.findall(r'(?<=")[^"]+(?=")', '"hello" "world"')
# ['hello', 'world']
```

## Regex Flags

Flags modify how the entire pattern is applied.

| Flag | Python | JS | Description |
|------|--------|----|-------------|
| Case-insensitive | `re.IGNORECASE` / `re.I` | `i` | Match regardless of case |
| Multiline | `re.MULTILINE` / `re.M` | `m` | `^`/`$` match line boundaries |
| Dot-all | `re.DOTALL` / `re.S` | `s` | `.` matches newline too |
| Verbose | `re.VERBOSE` / `re.X` | — | Allow whitespace and comments |
| Global | — | `g` | Find all matches (not just first) |
| Unicode | `re.UNICODE` / `re.U` | `u` | Full Unicode matching |

```python
# Multiline: ^ matches each line start
text = "line1\nline2\nline3"
re.findall(r'^\w+', text, re.MULTILINE)
# ['line1', 'line2', 'line3']

# Verbose mode: readable complex patterns
pattern = re.compile(r"""
    (?P<year>\d{4})    # 4-digit year
    -
    (?P<month>\d{2})   # 2-digit month
    -
    (?P<day>\d{2})     # 2-digit day
""", re.VERBOSE)
```

```javascript
// JavaScript flags
const email = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/i;
email.test('User@Example.COM'); // true

// Global flag: find all matches
'one two three'.match(/\w+/g); // ['one', 'two', 'three']
```

## Common Regex Patterns

Ready-to-use patterns for frequent validation tasks.

| Use Case | Pattern |
|----------|---------|
| Email address | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` |
| URL | `https?://[^\s/$.?#].[^\s]*` |
| IPv4 address | `\b(?:\d{1,3}\.){3}\d{1,3}\b` |
| Date (YYYY-MM-DD) | `\d{4}-(?:0[1-9]\|1[0-2])-(?:0[1-9]\|[12]\d\|3[01])` |
| US phone number | `\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}` |
| Hex colour | `#(?:[0-9a-fA-F]{3}){1,2}\b` |
| Slug (URL-safe) | `^[a-z0-9]+(?:-[a-z0-9]+)*$` |
| Positive integer | `^[1-9]\d*$` |
| HTML tag | `<([a-z]+)(?:\s[^>]*)?>.*?</\1>` |
| Whitespace-only | `^\s*$` |

```python
import re

# Validate an email
email_re = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
email_re.match('user@example.com')  # Match object
email_re.match('not-an-email')      # None

# Extract all hex colours from CSS
css = "color: #fff; background: #1a2b3c; border: 1px solid #aabbcc;"
re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', css)
# ['#fff', '#1a2b3c', '#aabbcc']
```

## Special Characters: Escaping Reference

| Character | Escaped | Notes |
|-----------|---------|-------|
| `.` | `\.` | Literal dot |
| `*` | `\*` | Literal asterisk |
| `+` | `\+` | Literal plus |
| `?` | `\?` | Literal question mark |
| `(` `)` | `\(` `\)` | Literal parentheses |
| `[` `]` | `\[` `\]` | Literal brackets |
| `{` `}` | `\{` `\}` | Literal braces |
| `^` | `\^` | Literal caret (outside character class) |
| `$` | `\$` | Literal dollar sign |
| `\|` | `\\\|` | Literal pipe |
| `\\` | `\\\\` | Literal backslash |

This cheat sheet covers the full regex syntax you'll encounter in any language or tool. For scripting scenarios where regex is combined with file operations, see the [Linux Commands Cheat Sheet](/cheatsheets/linux-commands-cheatsheet) — `grep`, `sed`, and `awk` all support regex. Explore more quick references on the [DevNook cheatsheets hub](/cheatsheets/), or visit the [guides hub](/guides/) for in-depth tutorials. The [DevNook tools hub](/tools/) also has utilities for testing and debugging your patterns interactively.
