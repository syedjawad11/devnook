---
actual_word_count: 1380
category: cheatsheets
concept: string-methods
description: "Python string methods reference: every built-in method with syntax and examples. Split, join, replace, strip, format, and more — organized by task."
download_png: false
language: python
og_image: /og/cheatsheets/python-string-methods.png
published_date: '2026-04-13'
related_content: []
related_posts: []
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"Article\",\n  \"headline\": \"Python String Methods Cheat Sheet:\
  \ split, join, replace, format & More\",\n  \"description\": \"Every Python string\
  \ method with syntax and examples. The only string reference you'll need — organized\
  \ by task.\",\n  \"datePublished\": \"2026-04-13\",\n  \"author\": {\"@type\": \"\
  Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\": \"Organization\"\
  , \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n  \"url\": \"https://devnook.dev/cheatsheets/\"\
  \n}\n</script>"
subject: python-string-methods
tags:
- python
- strings
- cheatsheet
- string-manipulation
template_id: cheatsheet-v2
title: 'Python String Methods Cheat Sheet: split, join, replace & More'
keyword: python string methods
slug: python-string-methods-cheatsheet
---

Every Python string method you'll reach for regularly, organized by what you're trying to do. Whether you're parsing CSV data, sanitizing user input, building formatted output, or checking string content, this reference has the method, its syntax, and a working example.

## Python String Methods for Splitting and Joining

Splitting and joining are the most frequent string operations in real code — parsing delimited data, reassembling tokens, processing file paths.

| Task | Method & Syntax |
|---|---|
| Split on whitespace | `text.split()` |
| Split on delimiter | `text.split(',')` |
| Split from right | `text.rsplit(',', 1)` |
| Split on newlines | `text.splitlines()` |
| Split into max N parts | `text.split(':', maxsplit=2)` |
| Join list into string | `', '.join(items)` |
| Join with newlines | `'\n'.join(lines)` |
| Partition into 3 parts | `text.partition(':')` |

```python
csv_row = "apple,banana,orange"
fruits = csv_row.split(',')       # ['apple', 'banana', 'orange']
rejoined = ', '.join(fruits)      # 'apple, banana, orange'

path = "/home/user/documents/file.txt"
filename = path.rsplit('/', 1)[-1]  # 'file.txt'

# partition() — handy for key:value strings
line = "Content-Type: application/json"
key, sep, value = line.partition(': ')  # ('Content-Type', ': ', 'application/json')
```

`split()` without an argument collapses consecutive whitespace and strips leading/trailing spaces — useful for normalizing messy input. `rsplit()` with a maxsplit limit is the idiomatic way to extract a file extension or the last path segment without a full `os.path` import.

When you need to build strings from a list — log lines, SQL IN clauses, comma-separated output — `','.join(items)` is always faster than string concatenation in a loop. For more on building collections efficiently, see [What is List Comprehension in Python?](/languages/python/list-comprehension).

## Searching and Checking String Content

Use these methods when you need to locate substrings, count occurrences, or validate string boundaries.

| Task | Method & Syntax |
|---|---|
| Check if contains substring | `substring in text` |
| Find first occurrence | `text.find('pattern')` |
| Find last occurrence | `text.rfind('pattern')` |
| Raise error if not found | `text.index('pattern')` |
| Count occurrences | `text.count('pattern')` |
| Check prefix | `text.startswith('prefix')` |
| Check suffix | `text.endswith('.txt')` |
| Search within a slice | `text.find('x', start, end)` |

```python
email = "user@example.com"
has_at = '@' in email          # True
domain_start = email.find('@') # 4 — returns -1 if not found

filename = "report_2026.pdf"
is_pdf = filename.endswith('.pdf')     # True
is_draft = filename.startswith('draft_')  # False

log = "ERROR: disk full. ERROR: retry failed."
error_count = log.count('ERROR')  # 2
```

**`find()` vs `index()`**: `find()` returns `-1` when the substring is missing; `index()` raises `ValueError`. Use `find()` when absence is a normal case, `index()` when absence means something went wrong and you want the stack trace to say so.

For pattern-based searching beyond simple substrings, try the [Regex Tester](/tools/regex-tester) — it's useful for testing `re.search()` and `re.findall()` patterns before embedding them in code. The companion [Regex Cheat Sheet](/cheatsheets/regex-cheatsheet) covers the full syntax.

## Python String Methods for Replacing and Stripping

| Task | Method & Syntax |
|---|---|
| Replace all occurrences | `text.replace('old', 'new')` |
| Replace N times | `text.replace('old', 'new', 2)` |
| Remove whitespace (both ends) | `text.strip()` |
| Remove from left only | `text.lstrip()` |
| Remove from right only | `text.rstrip()` |
| Remove specific chars | `text.strip('.,!? ')` |
| Remove prefix (3.9+) | `text.removeprefix('https://')` |
| Remove suffix (3.9+) | `text.removesuffix('.txt')` |

```python
code = "  print('hello')  "
code.strip()  # "print('hello')"

url = "https://example.com///"
url.rstrip('/')  # 'https://example.com'

message = "!!!URGENT!!!"
message.strip('!')  # 'URGENT'

log = "ERROR: File not found"
log.replace('ERROR', 'WARNING', 1)  # 'WARNING: File not found'

# Python 3.9+ — cleaner than slicing
filename = "report.txt"
filename.removesuffix('.txt')        # 'report'
"https://devnook.dev".removeprefix('https://')  # 'devnook.dev'
```

`strip()` accepts a string of characters to remove, not a substring — `text.strip('abc')` removes any combination of `a`, `b`, or `c` from both ends, not the literal string `"abc"`. For prefix/suffix removal as a literal string, `removeprefix()` and `removesuffix()` (Python 3.9+) are exact and unambiguous.

When your replace logic involves patterns — for example, replacing multiple consecutive spaces or normalizing phone number formats — reach for `re.sub()` from the `re` module. For straightforward literal replacement, `str.replace()` is faster and clearer.

## Case Conversion Methods

| Task | Method & Syntax |
|---|---|
| Lowercase | `text.lower()` |
| Uppercase | `text.upper()` |
| Title case | `text.title()` |
| Capitalize first char | `text.capitalize()` |
| Swap case | `text.swapcase()` |
| Unicode-safe lowercase (comparisons) | `text.casefold()` |

```python
name = "john DOE"
name.lower()       # 'john doe'
name.upper()       # 'JOHN DOE'
name.title()       # 'John Doe'
name.capitalize()  # 'John doe'  (only the very first char)
name.swapcase()    # 'JOHN doe'

# casefold() handles Unicode edge cases lower() misses
german = "Straße"
german.casefold() == "strasse"  # True
german.lower() == "strasse"     # False (lower gives 'straße')
```

Always use `casefold()` — not `lower()` — when comparing strings for equality, especially with user-supplied input that may include non-ASCII characters. `lower()` is fine for ASCII-only display formatting.

## String Formatting and Alignment

| Task | Method & Syntax |
|---|---|
| f-string interpolation | `f"Hello {name}"` |
| Format method | `"Hello {}".format(name)` |
| Named format args | `"{name} is {age}".format(name=n, age=a)` |
| Center in fixed width | `text.center(20, '-')` |
| Left-pad to width | `text.ljust(20)` |
| Right-pad to width | `text.rjust(20)` |
| Zero-pad a number | `str(42).zfill(5)` |

```python
name, age = "Alice", 30

# f-strings are preferred for readability (Python 3.6+)
f"{name} is {age} years old"           # 'Alice is 30 years old'
f"{age:>10}"                           # '        30' (right-aligned in 10 chars)
f"{3.14159:.2f}"                       # '3.14'

# format() — useful when building template strings dynamically
"Hello, {name}!".format(name=name)

# Alignment for tabular output
"OK".center(10, '-')   # '----OK----'
"error".ljust(10, '.')  # 'error.....'
"42".zfill(5)           # '00042'
```

f-strings support format specs directly inside the braces: `{value:.2f}` for decimal precision, `{value:>10}` for right-alignment, `{value:,}` for thousands separators. These work identically in `format()` calls but f-strings keep the value and format spec together, reducing mistakes when the variable name changes.

## Type-Checking Methods

Use these to validate input before processing — for example, before calling `int()` on a string.

| Task | Method & Syntax |
|---|---|
| All alphabetic | `text.isalpha()` |
| All digits | `text.isdigit()` |
| All alphanumeric | `text.isalnum()` |
| All lowercase | `text.islower()` |
| All uppercase | `text.isupper()` |
| All whitespace | `text.isspace()` |
| Is title case | `text.istitle()` |
| Valid Python identifier | `text.isidentifier()` |

```python
"Python".isalpha()       # True
"Python3".isalpha()      # False — digit breaks it
"Python3".isalnum()      # True
"12345".isdigit()        # True
"   ".isspace()          # True
"Hello World".istitle()  # True
"my_var".isidentifier()  # True — valid Python variable name
```

`isdigit()` returns `True` for superscripts like `²` as well as standard digits. If you need to validate that a string is a plain decimal integer, prefer `str.isdecimal()` instead, which is stricter.

When input validation logic grows complex — checking multiple conditions, raising specific errors — see [How to Handle Errors in Python](/languages/python/error-handling) for patterns that integrate cleanly with validation code.

## Encoding, Decoding, and Less Common Methods

| Task | Method & Syntax |
|---|---|
| Encode to bytes | `text.encode('utf-8')` |
| Decode from bytes | `bytes_obj.decode('utf-8')` |
| Handle encoding errors | `text.encode('ascii', errors='ignore')` |
| Expand tabs to spaces | `text.expandtabs(4)` |
| Translate characters | `text.translate(table)` |

```python
text = "Python 🐍"
encoded = text.encode('utf-8')            # b'Python \xf0\x9f\x90\x8d'
decoded = encoded.decode('utf-8')         # 'Python 🐍'

text.encode('ascii', errors='ignore')     # b'Python '
text.encode('ascii', errors='replace')    # b'Python ?'

# translate() — map or delete individual characters
remove_vowels = str.maketrans('', '', 'aeiou')
"Hello World".translate(remove_vowels)    # 'Hll Wrld'
```

## Common Options and Pitfalls

| Option | What it does |
|---|---|
| `maxsplit=N` in `split()` | Limit splits to N occurrences from the left |
| `errors='ignore'` in `encode()` | Skip characters that can't be encoded |
| `errors='replace'` in `encode()` | Substitute `?` for unencodable characters |
| `sep=None` in `split()` | Split on any whitespace run (default) |
| Second arg in `strip()` | Specify which individual characters to remove |
| `start, end` in `find()` | Restrict the search to a substring range |

**Mistakes worth avoiding:**

- **`split('')` raises ValueError** — use `list(text)` to split a string into individual characters.
- **Strings are immutable** — every method returns a new string. `text.strip()` on its own discards the result; write `text = text.strip()`.
- **Concatenation in loops is slow** — build a list and call `''.join(items)` at the end. This is one of the strongest arguments for [list comprehension in Python](/languages/python/list-comprehension) when constructing strings from transformed data.
- **`lower()` vs `casefold()` for equality checks** — always `casefold()` when comparing user input across locales.
- **`replace()` replaces all occurrences by default** — pass a third argument (count) to limit replacements: `text.replace('x', 'y', 1)`.

Building a pipeline that validates and transforms user-submitted strings? The patterns in [How to Do Dictionary Comprehension in Python](/languages/python/dictionary-comprehension) are useful for batch-processing field mappings alongside string normalization.
