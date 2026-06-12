---
title: "Python String Methods: split, join, replace, strip & More"
description: "Python string methods cheat sheet: every built-in str method with syntax and working examples — split, join, replace, strip, format, encode, and more."
category: cheatsheets
language: python
template_id: cheatsheet-v2
tags:
  - python
  - strings
  - cheatsheet
  - string-manipulation
  - string-methods
related_posts: []
related_tools: []
published_date: '2026-06-10'
og_image: /og/cheatsheets/python-string-methods.png
---

Every Python string method you need, organized by what you are trying to accomplish. Whether you are cleaning user input, parsing log files, building formatted output, or validating field values, this reference covers the method, its exact syntax, and a runnable example. For the authoritative complete list, see the [Python official string methods documentation](https://docs.python.org/3/library/stdtypes.html#string-methods).

## Python String Methods Quick Reference

The table below maps every commonly used `str` method to its purpose. Detailed breakdowns with working code follow in each section.

| Category | Key Methods |
|---|---|
| Splitting & joining | `split()`, `rsplit()`, `splitlines()`, `join()`, `partition()`, `rpartition()` |
| Searching & finding | `find()`, `rfind()`, `index()`, `rindex()`, `count()`, `startswith()`, `endswith()` |
| Replacing & stripping | `replace()`, `strip()`, `lstrip()`, `rstrip()`, `removeprefix()`, `removesuffix()` |
| Case conversion | `lower()`, `upper()`, `title()`, `capitalize()`, `swapcase()`, `casefold()` |
| Formatting & alignment | `format()`, `center()`, `ljust()`, `rjust()`, `zfill()` |
| Type-checking | `isalpha()`, `isdigit()`, `isdecimal()`, `isalnum()`, `isspace()`, `isidentifier()`, `isascii()` |
| Encoding & translation | `encode()`, `decode()`, `translate()`, `maketrans()`, `expandtabs()` |

All `str` methods return a **new string** — Python strings are immutable. Assigning back to the same variable is always intentional: `s = s.strip()`. Calling `s.strip()` alone and discarding the result is one of the most common beginner mistakes.

## Splitting and Joining Strings

Splitting and joining are the workhorses of text parsing. `split()` breaks a string into a list; `join()` reassembles a list back into a string. They are two sides of the same operation.

| Task | Method & Syntax |
|---|---|
| Split on whitespace | `text.split()` |
| Split on a delimiter | `text.split(',')` |
| Split from right | `text.rsplit(',', 1)` |
| Limit number of splits | `text.split(':', maxsplit=2)` |
| Split on newlines | `text.splitlines()` |
| Join list into string | `', '.join(items)` |
| Join with newlines | `'\n'.join(lines)` |
| Partition into exactly 3 parts | `text.partition(':')` |
| Partition from right | `text.rpartition('/')` |

```python
csv_row  = "apple,banana,orange,grape"
fruits   = csv_row.split(',')           # ['apple', 'banana', 'orange', 'grape']
rejoined = ' | '.join(fruits)           # 'apple | banana | orange | grape'

path                    = "/home/user/projects/report.tar.gz"
dir_part, _, filename   = path.rpartition('/')    # filename = 'report.tar.gz'

data  = "line one\nline two\r\nline three\r"
lines = data.splitlines()   # ['line one', 'line two', 'line three']

log             = "2026-06-10T08:30:00Z INFO Application started"
ts, sep, msg    = log.partition(' ')    # ts='2026-06-10T08:30:00Z', msg='INFO...'
```

`split()` with no argument collapses any run of consecutive whitespace and strips leading/trailing spaces — far more robust than `split(' ')` for normalizing messy input. `splitlines()` is safer than `split('\n')` when processing files with mixed Windows/Unix line endings.

Building strings by joining a list is always faster than concatenation in a loop. See [What is List Comprehension in Python?](/languages/python/list-comprehension/) for list-building patterns that pair naturally with `join()`.

## Searching and Finding Substrings

Use these methods when you need to locate text positions, count occurrences, or confirm that a string starts or ends with a known value.

| Task | Method & Syntax |
|---|---|
| Check if substring exists | `substring in text` |
| Find first occurrence (index) | `text.find('pat')` |
| Find last occurrence (index) | `text.rfind('pat')` |
| Raise if not found | `text.index('pat')` |
| Count non-overlapping occurrences | `text.count('pat')` |
| Check prefix | `text.startswith('prefix')` |
| Check suffix | `text.endswith('.json')` |
| Check multiple prefixes/suffixes | `text.startswith(('http://', 'https://'))` |
| Restrict search to a slice | `text.find('x', start, end)` |

```python
url          = "https://api.example.com/v2/users?page=1"
has_v2       = '/v2/' in url                              # True
query_start  = url.find('?')                              # 33; -1 if absent
is_secure    = url.startswith(('https://', 'wss://'))     # True

filename  = "data_export_2026.csv"
is_csv    = filename.endswith('.csv')                     # True
is_backup = filename.endswith(('.bak', '.old', '.backup'))# False

log         = "WARN: retry 1. WARN: retry 2. WARN: retry 3. ERROR: abort."
warn_count  = log.count('WARN')     # 3
error_count = log.count('ERROR')    # 1
```

**`find()` vs `index()`:** `find()` returns `-1` when the substring is absent; `index()` raises `ValueError`. Use `find()` when missing text is a normal condition; use `index()` when absence means something is wrong and you want the exception to say so.

For pattern-based searches beyond literal substrings — matching any email format, any run of digits, or conditional patterns — the [Regex Cheat Sheet](/cheatsheets/regex-cheatsheet/) covers `re.search()`, `re.findall()`, and `re.sub()` syntax.

## Replacing and Stripping Text

`replace()` handles literal substitution throughout a string. The `strip` family trims unwanted characters from the boundaries of a string.

| Task | Method & Syntax |
|---|---|
| Replace all occurrences | `text.replace('old', 'new')` |
| Replace first N occurrences | `text.replace('old', 'new', 2)` |
| Strip whitespace from both ends | `text.strip()` |
| Strip from left only | `text.lstrip()` |
| Strip from right only | `text.rstrip()` |
| Strip a set of characters | `text.strip('.,!? ')` |
| Remove exact prefix (Python 3.9+) | `text.removeprefix('https://')` |
| Remove exact suffix (Python 3.9+) | `text.removesuffix('.txt')` |

```python
log = "ERROR: disk full. ERROR: retry failed. ERROR: gave up."
log.replace('ERROR', 'WARN')       # replaces all three occurrences
log.replace('ERROR', 'WARN', 1)    # replaces first match only

raw = "   \t hello world \n  "
raw.strip()   # 'hello world'
raw.lstrip()  # 'hello world \n  '
raw.rstrip()  # '   \t hello world'

messy = "...!!!Hello, World!!!..."
messy.strip('.!')   # 'Hello, World'  (each char in '.!' stripped independently)

filename = "report_draft.md"
filename.removesuffix('.md')   # 'report_draft'
filename.removesuffix('.txt')  # 'report_draft.md' — no match, unchanged

url = "https://devnook.dev/blog/"
url.removeprefix('https://')   # 'devnook.dev/blog/'
url.removeprefix('http://')    # 'https://devnook.dev/blog/' — no match, unchanged
```

`strip()` accepts a **character set**, not a substring. `text.strip('abc')` removes leading/trailing `a`, `b`, or `c` in any order — not the literal string `"abc"`. For exact prefix/suffix removal, `removeprefix()` and `removesuffix()` (Python 3.9+) are unambiguous and always preferred. When replacement logic involves patterns, use `re.sub()` from the `re` module rather than chaining multiple `str.replace()` calls.

## Case Conversion and Normalization

| Task | Method & Syntax |
|---|---|
| Lowercase | `text.lower()` |
| Uppercase | `text.upper()` |
| Title case | `text.title()` |
| Capitalize only first character | `text.capitalize()` |
| Swap each character's case | `text.swapcase()` |
| Unicode-safe folded lowercase | `text.casefold()` |

```python
name = "john DOE"
name.lower()       # 'john doe'
name.upper()       # 'JOHN DOE'
name.title()       # 'John Doe'
name.capitalize()  # 'John doe'  (only first character uppercased)
name.swapcase()    # 'JOHN doe'

german = "Straße"
german.casefold() == "strasse"   # True  — correct Unicode fold
german.lower() == "strasse"      # False — lower() gives 'straße', not 'strasse'

tags   = ["Python", "python", "PYTHON", "django", "Django"]
unique = list({t.casefold(): t for t in tags}.values())
len(unique) == 2   # True: ['Python', 'django'] after deduplication

"it's a dog's life".title()   # "It'S A Dog'S Life" — apostrophe edge case
```

Always use `casefold()` — not `lower()` — when comparing strings for equality, especially with user-supplied input that may include non-ASCII characters. The difference only matters for a small set of Unicode characters, but getting it wrong produces subtle, hard-to-reproduce bugs.

## String Formatting and Alignment

Python provides three string formatting approaches. f-strings (Python 3.6+) are the preferred style for clarity. See [Python String Formatting: f-strings, format(), and %](/languages/python/string-formatting/) for the complete format spec reference.

| Task | Method & Syntax |
|---|---|
| f-string interpolation | `f"Hello {name}"` |
| Named placeholders | `"{name} is {age}".format(name=n, age=a)` |
| Positional placeholders | `"{} {}".format('hello', 'world')` |
| Center in fixed width | `text.center(20, '-')` |
| Left-justify (pad right) | `text.ljust(20, '.')` |
| Right-justify (pad left) | `text.rjust(20)` |
| Zero-pad a number string | `str(42).zfill(5)` |
| Float precision | `f"{3.14159:.2f}"` |
| Thousands separator | `f"{1_000_000:,}"` |
| Hex / binary output | `f"{255:#010x}"` / `f"{10:#b}"` |

```python
name, score, pct = "Alice", 1842, 0.9357

f"{name:<10} {score:>8,} {pct:.1%}"   # 'Alice       1,842 93.6%'
f"{255:#010x}"                          # '0x000000ff'
f"{score:+}"                            # '+1842'

template   = "User {username!r} logged in from {ip}"
result     = template.format(username="alice", ip="192.168.1.1")
len(result) > 0   # True: "User 'alice' logged in from 192.168.1.1"

fmt = "{:<12} {:>8} {:^6}"
print(fmt.format("Name", "Score", "Grade"))   # 'Name          Score  Grade '
print(fmt.format("Bob",  1750,    "B"))       # 'Bob            1750    B   '

order_id = f"order_{str(42).zfill(6)}"       # 'order_000042'
```

## Type-Checking and Validation

These predicate methods return `True` or `False` and are most useful for validating input before conversion or processing.

| Task | Method & Syntax |
|---|---|
| All alphabetic | `text.isalpha()` |
| Strict decimal digits | `text.isdecimal()` |
| Broad digit characters | `text.isdigit()` |
| All alphanumeric | `text.isalnum()` |
| All lowercase | `text.islower()` |
| All uppercase | `text.isupper()` |
| All whitespace | `text.isspace()` |
| Title-cased | `text.istitle()` |
| Valid Python identifier | `text.isidentifier()` |
| ASCII characters only | `text.isascii()` |

```python
raw_age = "25"
age = int(raw_age) if raw_age.isdecimal() else None

"alice".isalpha()        # True
"alice123".isalpha()     # False — digit present
"alice123".isalnum()     # True
"alice_123".isalnum()    # False — underscore excluded

"123".isdecimal()   # True
"²³".isdecimal()    # False — superscripts fail isdecimal
"²³".isdigit()      # True  — superscripts pass isdigit (use isdecimal for int validation)

"my_column".isidentifier()    # True
"2bad_name".isidentifier()    # False — starts with digit
```

Use `isdecimal()` — not `isdigit()` — when validating numeric input before calling `int()`, because superscripts and other Unicode "digits" pass `isdigit()` but cause `int()` to raise `ValueError`. When validation logic grows complex, see [How to Handle Errors in Python?](/languages/python/error-handling/) for patterns that integrate cleanly with input validation.

## Encoding and Byte Conversion

| Task | Method & Syntax |
|---|---|
| Encode string to bytes | `text.encode('utf-8')` |
| Decode bytes to string | `b_obj.decode('utf-8')` |
| Ignore unencodable characters | `text.encode('ascii', errors='ignore')` |
| Replace unencodable characters | `text.encode('ascii', errors='replace')` |
| XML-escape unencodable characters | `text.encode('ascii', errors='xmlcharrefreplace')` |
| Map or delete characters | `text.translate(table)` |
| Build a translation table | `str.maketrans('abc', 'ABC')` |
| Delete a set of characters | `str.maketrans('', '', chars_to_delete)` |
| Expand tab stops to spaces | `text.expandtabs(4)` |

```python
text     = "Python 🐍 rocks"
as_bytes = text.encode('utf-8')          # b'Python \xf0\x9f\x90\x8d rocks'
back_str = as_bytes.decode('utf-8')      # 'Python 🐍 rocks'

text.encode('ascii', errors='ignore')   # b'Python  rocks'  — emoji stripped
text.encode('ascii', errors='replace')  # b'Python ? rocks' — emoji replaced

no_punct = str.maketrans('', '', '.,!?;:')
"Hello, World!".translate(no_punct)    # 'Hello World'

"col1\tcol2\tcol3".expandtabs(12)    # 'col1        col2        col3'
```

When reading files that may have mixed or unknown encodings, always pass the `encoding` parameter to `open()` and choose an `errors` strategy. See [How to File Handling in Python + Examples](/languages/python/file-handling/) for patterns that prevent `UnicodeDecodeError` at file read time.

## Common Pitfalls and Performance Tips

These are the mistakes that appear repeatedly in code reviews — patterns worth encoding in muscle memory.

| Pitfall | Problem | Fix |
|---|---|---|
| `text.split('')` | Raises `ValueError` | Use `list(text)` to split into characters |
| Discarding the return value | `text.strip()` does nothing on its own | Assign back: `text = text.strip()` |
| `strip()` argument confusion | Removes individual chars, not a substring | Use `removeprefix()` / `removesuffix()` for exact removal |
| `lower()` for equality checks | Misses Unicode edge cases (German ß, etc.) | Use `casefold()` for all equality comparisons |
| String concat in a loop | O(n²) memory allocations | Build a list and call `''.join(items)` once |
| `isdigit()` for int validation | Accepts Unicode superscripts like `²` | Use `isdecimal()` instead |
| `replace()` replaces all | Unexpected mass substitution | Pass count: `text.replace('x', 'y', 1)` |
| `index()` on missing text | Raises `ValueError` at runtime | Use `find()` and check for `-1` |

```python
items = ["a", "b", "c"]
result = "".join(process(item) for item in items)   # O(n) — join once
bad    = ""
for item in items:
    bad += process(item)    # O(n²) — avoidable; don't do this in production loops

s = "  hello  "
s = s.strip()   # must reassign: str methods return new strings, never mutate in place
print(s)        # 'hello'

tag    = "<h1>title</h1>"
clean  = tag.removeprefix('<h1>').removesuffix('</h1>')  # 'title' — exact, unambiguous
wrong  = tag.strip('<h1>')    # strips CHARS '<','h','1','>' not the literal tag string
```

For batch string transformations across a collection of items, [How to Do Dictionary Comprehension in Python?](/languages/python/dictionary-comprehension/) shows patterns that compose well with `str` method chains. The [Python string module documentation](https://docs.python.org/3/library/string.html) also provides `string.punctuation`, `string.ascii_letters`, and `string.Template` for cases where the built-in `str` methods are not quite enough.
