---
title: "Regex Cheat Sheet"
description: "The complete regex cheatsheet: character classes, anchors, quantifiers, groups, lookaheads, flags, and validation patterns for Python and JavaScript."
category: "cheatsheets"
template_id: "cheatsheet-v1"
tags: [regex, regular-expressions, pattern-matching, cheatsheet, programming]
related_posts: []
related_tools: []
published_date: "2026-06-09"
og_image: "/og/cheatsheets/regex-cheatsheet.png"
downloadable: true
content_type: editorial
---

Regular expressions are a universal pattern-matching syntax built into every major programming language, text editor, and command-line tool. This reference sheet is designed to be scanned, not read — keep it open next to your editor.

## Character Classes & Metacharacters

A character class matches exactly one character from a defined set. Metacharacters are symbols with special meaning inside a pattern.

| Pattern | Matches | Notes |
|---------|---------|-------|
| `abc` | Literal "abc" in sequence | Case-sensitive by default |
| `.` | Any character except newline | Matches newline with `re.DOTALL` / `/s` flag |
| `\d` | Any digit `[0-9]` | Unicode digits included with `re.UNICODE` |
| `\D` | Any non-digit | Inverse of `\d` |
| `\w` | Word character `[a-zA-Z0-9_]` | `re.UNICODE` expands to Unicode word chars |
| `\W` | Non-word character | Inverse of `\w` |
| `\s` | Whitespace: space, tab, `\n`, `\r`, `\f` | |
| `\S` | Non-whitespace | Inverse of `\s` |
| `[abc]` | One of: a, b, or c | Most metacharacters lose their meaning inside `[…]` |
| `[^abc]` | Any character except a, b, or c | Negated class |
| `[a-z]` | Any lowercase letter | Range syntax |
| `[A-Z]` | Any uppercase letter | |
| `[0-9]` | Any digit (same as `\d`) | |
| `[a-zA-Z0-9_]` | Any word character (same as `\w`) | |
| `\t` | Tab character | |
| `\n` | Newline character | |
| `\r` | Carriage return | |
| `\\` | Literal backslash | Must also escape in non-raw strings |

```python
import re

re.findall(r'\d+', 'Order 42, item 7')
## => ['42', '7']

re.findall(r'\w+', 'hello_world 123')
## => ['hello_world', '123']

re.findall(r'[aeiou]+', 'beautiful')
## => ['eau', 'i', 'u']

re.findall(r'[^a-zA-Z0-9]+', 'hello, world! 42')
## => [', ', '! ']
```

## Anchors & Boundaries

Anchors assert a **position** in the string — they consume no characters.

| Pattern | Position Matched | Notes |
|---------|-----------------|-------|
| `^` | Start of string | Start of each line with `re.MULTILINE` / `m` flag |
| `$` | End of string | End of each line with `re.MULTILINE` / `m` flag |
| `\b` | Word boundary | Between `\w` and `\W`, or at string edge |
| `\B` | Non-word boundary | Inside a continuous run of word characters |
| `\A` | Absolute start of string | Unaffected by `re.MULTILINE` |
| `\Z` | Absolute end of string | Unaffected by `re.MULTILINE` |

```python
text = "apple\nbanana\napricot"

re.findall(r'^a\w+', text, re.MULTILINE)
## => ['apple', 'apricot']

re.findall(r'\bcat\b', 'the cat in scatter')
## => ['cat']  — 'cat' inside 'scatter' is not matched

re.findall(r'\Aapple', text, re.MULTILINE)
## => ['apple']  — only the absolute start of the string

bool(re.fullmatch(r'\d{5}', '90210'))   ## => True
bool(re.fullmatch(r'\d{5}', 'ABC'))     ## => False
```

## Quantifiers: Greedy and Lazy

Quantifiers control **how many times** the preceding element repeats. Greedy quantifiers consume as much input as possible; lazy (non-greedy) quantifiers consume as little as possible.

| Quantifier | Meaning | Mode |
|-----------|---------|------|
| `*` | 0 or more | Greedy |
| `+` | 1 or more | Greedy |
| `?` | 0 or 1 | Greedy |
| `{n}` | Exactly n times | Greedy |
| `{n,}` | n or more times | Greedy |
| `{n,m}` | Between n and m times (inclusive) | Greedy |
| `*?` | 0 or more | Lazy |
| `+?` | 1 or more | Lazy |
| `??` | 0 or 1 | Lazy |
| `{n,m}?` | Between n and m | Lazy |

```python
text = '<b>bold</b> and <i>italic</i>'

re.findall(r'<.+>', text)
## => ['<b>bold</b> and <i>italic</i>']   — greedy, one giant match

re.findall(r'<.+?>', text)
## => ['<b>', '</b>', '<i>', '</i>']   — lazy, each tag separately

re.findall(r'\b\d{2,4}\b', 'a 5 b 12 c 1234 d 99999')
## => ['12', '1234']

re.findall(r'https?://\S+', 'Visit http://a.com or https://b.com')
## => ['http://a.com', 'https://b.com']
```

## Groups, Capturing & Backreferences

Groups let you apply quantifiers to multi-character sequences, capture submatches, and refer back to earlier matches in the same pattern or in a replacement string.

| Pattern | Description |
|---------|-------------|
| `(abc)` | Capturing group — saves the matched text |
| `(?:abc)` | Non-capturing group — groups without saving |
| `(?P<name>abc)` | Named capturing group — Python/PCRE syntax |
| `(?<name>abc)` | Named capturing group — JavaScript ES2018/PCRE2 |
| `a\|b` | Alternation — match "a" or "b" |
| `\1` | Backreference to group 1 (by number) |
| `\g<1>` | Backreference to group 1 in `re.sub` replacement |
| `(?P=name)` | Named backreference — Python |
| `\k<name>` | Named backreference — JavaScript/PCRE2 |

```python
pattern = r'(?P<protocol>https?)://(?P<domain>[^/]+)(?P<path>/[^\s]*)?'
m = re.match(pattern, 'https://devnook.dev/guides/')
m.group('protocol')  ## 'https'
m.group('domain')    ## 'devnook.dev'
m.group('path')      ## '/guides/'

re.findall(r'\b(\w+)\s+\1\b', 'the the quick brown fox fox')
## => ['the', 'fox']   — repeated words

re.findall(r'colo(?:u|)r', 'colour and color')
## => ['colour', 'color']   — alternation in non-capturing group

re.sub(r'(\w+)\s+(\w+)', r'\2 \1', 'John Smith')
## => 'Smith John'   — swap groups in replacement
```

## Lookaheads & Lookbehinds

Lookarounds are **zero-width assertions** — they check what surrounds the current position without consuming any characters.

| Pattern | Type | What it asserts |
|---------|------|----------------|
| `(?=abc)` | Positive lookahead | Current position is followed by "abc" |
| `(?!abc)` | Negative lookahead | Current position is NOT followed by "abc" |
| `(?<=abc)` | Positive lookbehind | Current position is preceded by "abc" |
| `(?<!abc)` | Negative lookbehind | Current position is NOT preceded by "abc" |

```python
re.findall(r'\d+(?=px)', '12px 5em 100px 3rem')
## => ['12', '100']   — digits followed by 'px', 'px' not captured

re.findall(r'new(?!line)', 'newline and new feature')
## => ['new']   — 'new' not followed by 'line'

re.findall(r'(?<=name=)\w+', 'id=42 name=alice role=admin')
## => ['alice']

re.findall(r'(?<!no )error', 'no error here; another error exists')
## => ['error']   — only the second occurrence

re.findall(r'(?<=\$)\d+(?=\s*USD)', '$100 USD and $50 EUR')
## => ['100']   — combined lookahead + lookbehind
```

## Regex Flags

Flags (also called modifiers) alter how the engine interprets the entire pattern. Combine multiple flags with `|` in Python, or use inline `(?imsx)` syntax to embed them inside the pattern itself.

| Flag | Python constant | Python inline | JavaScript | What it changes |
|------|----------------|--------------|-----------|-----------------|
| Case-insensitive | `re.IGNORECASE` / `re.I` | `(?i)` | `i` | Letters match any case |
| Multiline | `re.MULTILINE` / `re.M` | `(?m)` | `m` | `^`/`$` match line starts and ends |
| Dot-all | `re.DOTALL` / `re.S` | `(?s)` | `s` | `.` matches `\n` too |
| Verbose | `re.VERBOSE` / `re.X` | `(?x)` | — | Whitespace and `#` comments ignored |
| Global | — | — | `g` | Find all matches, not just the first |
| Unicode | `re.UNICODE` / `re.U` | `(?u)` | `u` | Full Unicode property matching |
| ASCII | `re.ASCII` / `re.A` | `(?a)` | — | Force `\w`, `\d`, `\s` to ASCII-only |
| Sticky | — | — | `y` | Match only at `lastIndex` position |

```python
re.findall(r'(?i)hello', 'Hello HELLO hello')
## => ['Hello', 'HELLO', 'hello']   — inline case-insensitive flag

text = "Error: disk full\nerror: timeout\nWARN: retrying"
re.findall(r'^error:.+$', text, re.IGNORECASE | re.MULTILINE)
## => ['Error: disk full', 'error: timeout']

date_re = re.compile(r"""
    (?P<year>\d{4})            (?# 4-digit year)
    -
    (?P<month>0[1-9]|1[0-2])  (?# month 01-12)
    -
    (?P<day>0[1-9]|[12]\d|3[01])  (?# day 01-31)
""", re.VERBOSE)

date_re.match('2026-06-09').groupdict()
## => {'year': '2026', 'month': '06', 'day': '09'}
```

```javascript
'Hello HELLO hello'.match(/hello/gi);
// => ['Hello', 'HELLO', 'hello']

const { groups: { year, month, day } } =
  '2026-06-09'.match(/(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/);
// year='2026', month='06', day='09'

const sticky = /\d+/y;
sticky.lastIndex = 7;
sticky.exec('Order: 42');
// => ['42']  — matched exactly at index 7
```

## Common Regex Patterns

Production-ready patterns for frequent validation and extraction tasks. Paste them into the [Java Regex Tester — Free Online Tool](/tools/regex-tester/) to verify matches before shipping.

| Use Case | Pattern |
|----------|---------|
| Email address | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` |
| URL (HTTP/HTTPS) | `https?://[^\s/$.?#].[^\s]*` |
| IPv4 address | `\b(?:\d{1,3}\.){3}\d{1,3}\b` |
| IPv6 (simplified) | `(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}` |
| Date YYYY-MM-DD | `\d{4}-(?:0[1-9]\|1[0-2])-(?:0[1-9]\|[12]\d\|3[01])` |
| US phone number | `\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}` |
| Hex colour | `#(?:[0-9a-fA-F]{3}){1,2}\b` |
| Slug (URL-safe) | `^[a-z0-9]+(?:-[a-z0-9]+)*$` |
| Positive integer | `^[1-9]\d*$` |
| HTML tag (basic) | `<([a-z][a-z0-9]*)\b[^>]*>.*?</\1>` |
| UUID v4 | `[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}` |
| Semantic version | `\bv?\d+\.\d+\.\d+\b` |
| JWT token | `^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$` |
| Whitespace-only string | `^\s*$` |
| C-style block comment | `/\*[\s\S]*?\*/` |

```python
import re

email_re = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
email_re.match('user@example.com')  ## => Match object
email_re.match('not-an-email')      ## => None

css = "color: #fff; background: #1a2b3c; border: 1px solid #aabbcc;"
re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', css)
## => ['#fff', '#1a2b3c', '#aabbcc']

changelog = "Released v1.2.3; fixed bug from v1.2.1; target is v2.0.0"
re.findall(r'\bv?\d+\.\d+\.\d+\b', changelog)
## => ['v1.2.3', 'v1.2.1', 'v2.0.0']
```

## Regex in Python: re Module Reference

The [Python re module](https://docs.python.org/3/library/re.html) is the standard library's full regex API. Always use raw strings (`r'…'`) for patterns to avoid double-escaping backslashes.

| Function / Method | What it returns | Notes |
|------------------|----------------|-------|
| `re.search(pat, s)` | First match anywhere | Returns `None` if no match |
| `re.match(pat, s)` | Match at start of string only | Does not scan the whole string |
| `re.fullmatch(pat, s)` | Match spanning entire string | Strictest option for validation |
| `re.findall(pat, s)` | List of all non-overlapping matches | Returns list of strings or tuples |
| `re.finditer(pat, s)` | Iterator of Match objects | Use when you need `.start()` / `.end()` |
| `re.sub(pat, repl, s)` | String with substitutions | `repl` can be a string or callable |
| `re.subn(pat, repl, s)` | `(new_string, count)` tuple | Count = number of replacements made |
| `re.split(pat, s)` | List of substrings | Capturing groups appear in the result |
| `re.compile(pat, flags)` | Compiled Pattern object | Reuse for performance-critical loops |
| `m.group(n)` | Captured group n (0 = full match) | `None` if group did not participate |
| `m.groups()` | All captured groups as tuple | |
| `m.groupdict()` | Named groups as `{name: value}` dict | |
| `m.start()` / `m.end()` | Start / end position in string | Integer index |
| `m.span()` | `(start, end)` tuple | Equivalent to `(m.start(), m.end())` |

```python
import re

text = "2026-06-09: Released version 2.1.4"

for m in re.finditer(r'\d+', text):
    print(f"'{m.group()}' at {m.span()}")
## '2026' at (0, 4)
## '06' at (5, 7)  ... etc.

def bump(m):
    return str(int(m.group()) + 1)

re.sub(r'\b\d+\b', bump, 'a=1 b=2 c=3')
## => 'a=2 b=3 c=4'

re.split(r'[,;\s]+', 'one, two;three  four')
## => ['one', 'two', 'three', 'four']

slug_re = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
[s for s in ['hello-world', 'Bad Slug', 'ok-123'] if slug_re.match(s)]
## => ['hello-world', 'ok-123']
```

For more Python string operations that complement regex, see [Python String Methods Cheat Sheet: split, join, replace & More](/cheatsheets/python-string-methods-cheatsheet/).

## Regex in JavaScript

JavaScript regex uses literal syntax `/pattern/flags` or `new RegExp('pattern', 'flags')`. The [MDN Regular Expressions guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions) covers every detail of the spec.

| Method | Called on | What it does |
|--------|-----------|-------------|
| `str.match(re)` | String | First match (or all with `/g`), returns array or `null` |
| `str.matchAll(re)` | String | Iterator of all Match objects — requires `/g` flag |
| `str.search(re)` | String | Index of first match, or `-1` |
| `str.replace(re, sub)` | String | Replaces first match (or all with `/g`) |
| `str.replaceAll(re, sub)` | String | Replaces all matches — requires `/g` or a string |
| `str.split(re)` | String | Splits on each match, returns array |
| `re.test(str)` | RegExp | `true` if the pattern matches anywhere |
| `re.exec(str)` | RegExp | Next match object (stateful with `/g` or `/y`) |

```javascript
// Named groups (ES2018+) with destructuring
const dateRe = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/;
const { groups: { year, month, day } } = '2026-06-09'.match(dateRe);
// year='2026', month='06', day='09'

// replaceAll with a transform function (requires /g)
const result = 'a=1, b=2, c=3'.replace(/(\w+)=(\d+)/g, (_, k, v) => `${k}=${+v * 10}`);
// => 'a=10, b=20, c=30'

// matchAll: iterate all matches and extract groups
const str = 'cat bat hat mat';
const matches = [...str.matchAll(/(?<word>[cbhm]at)/g)];
matches.map(m => m.groups.word);
// => ['cat', 'bat', 'hat', 'mat']

// test() for fast boolean validation
const emailRe = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
emailRe.test('user@example.com');  // true
emailRe.test('not-an-email');      // false
```

For a deeper look at JavaScript's native regex capabilities, see [What is Regex Pattern Checking in JavaScript?](/languages/javascript/check-regex-pattern/). If you use regex in shell scripts or with CLI tools like `grep`, `sed`, and `awk`, the [Linux Commands Cheat Sheet](/cheatsheets/linux-commands-cheatsheet/) has the flags and syntax for POSIX and extended regex modes.

## Escaping Special Characters

These characters carry special meaning in regex syntax and must be escaped with a backslash when you want to match them literally.

| Character | Escaped Form | Normal Meaning in Regex |
|-----------|-------------|------------------------|
| `.` | `\.` | Match any character |
| `*` | `\*` | 0-or-more quantifier |
| `+` | `\+` | 1-or-more quantifier |
| `?` | `\?` | 0-or-1 quantifier / lazy modifier |
| `(` | `\(` | Open capturing group |
| `)` | `\)` | Close capturing group |
| `[` | `\[` | Open character class |
| `]` | `\]` | Close character class |
| `{` | `\{` | Open repetition count |
| `}` | `\}` | Close repetition count |
| `^` | `\^` | Start anchor / negation inside `[…]` |
| `$` | `\$` | End anchor |
| `\|` | `\\\|` | Alternation operator |
| `\\` | `\\\\` | Backslash itself |
| `/` | `\/` | Pattern delimiter in JavaScript literals |

```python
import re

re.escape('3.14 * x^2')
## => '3\\.14\\ \\*\\ x\\^2'

pattern = re.compile(re.escape('3.14 * x^2'))
pattern.search("result: 3.14 * x^2 + 1")
## => Match object — safe to use with user-supplied text

def is_valid_regex(s):
    try:
        re.compile(s)
        return True
    except re.error:
        return False

is_valid_regex(r'\d+')       ## => True
is_valid_regex(r'[unclosed') ## => False
```
