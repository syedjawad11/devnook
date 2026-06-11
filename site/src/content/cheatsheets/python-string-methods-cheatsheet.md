---
title: "Python String Methods: split, join, replace, strip & More"
description: "Python string methods cheatsheet: every built-in str method with syntax, working examples, and pitfalls — split, join, replace, strip, casefold, and more."
category: "cheatsheets"
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
published_date: "2026-06-11"
og_image: /og/cheatsheets/python-string-methods.png
---

Every built-in `str` method organized by task — syntax, runnable examples, and the pitfalls that trip up even experienced developers. Python strings are immutable: every method returns a **new string** and leaves the original unchanged. Calling `s.strip()` without assigning the result is one of the most common beginner mistakes for exactly this reason. For the canonical complete list, see the [Python string methods documentation](https://docs.python.org/3/library/stdtypes.html#string-methods).

## Python String Methods Quick Reference

The table below maps every commonly used `str` method to its task area. Detailed sections with working code examples follow.

| Category | Key Methods |
|---|---|
| Splitting & joining | `split()`, `rsplit()`, `splitlines()`, `join()`, `partition()`, `rpartition()` |
| Searching & finding | `find()`, `rfind()`, `index()`, `rindex()`, `count()`, `startswith()`, `endswith()` |
| Replacing & stripping | `replace()`, `strip()`, `lstrip()`, `rstrip()`, `removeprefix()`, `removesuffix()` |
| Case conversion | `lower()`, `upper()`, `title()`, `capitalize()`, `swapcase()`, `casefold()` |
| Formatting & alignment | `format()`, `center()`, `ljust()`, `rjust()`, `zfill()` |
| Type-checking | `isalpha()`, `isdigit()`, `isdecimal()`, `isalnum()`, `isspace()`, `isidentifier()`, `isascii()` |
| Encoding & translation | `encode()`, `decode()`, `translate()`, `maketrans()`, `expandtabs()` |

All `str` methods return a new value — Python strings never mutate in place. The variable must be reassigned to keep the result: `s = s.strip()`.

## Splitting and Joining Strings

Splitting turns a string into a list; joining reassembles a list back into a string. Together they handle the vast majority of text-parsing tasks.

| Task | Method & Syntax |
|---|---|
| Split on whitespace | `text.split()` |
| Split on a delimiter | `text.split(',')` |
| Limit number of splits | `text.split(':', maxsplit=2)` |
| Split from the right | `text.rsplit('/', 1)` |
| Split on line endings | `text.splitlines()` |
| Join list with separator | `sep.join(items)` |
| Partition into exactly 3 parts | `text.partition(':')` |
| Partition from the right | `text.rpartition('/')` |

```python
csv      = "alice,bob,charlie,dana"
parts    = csv.split(',')                # ['alice', 'bob', 'charlie', 'dana']
rejoined = ' | '.join(parts)            # 'alice | bob | charlie | dana'

path                   = "/var/log/app/server.log"
dir_part, _, filename  = path.rpartition('/')     # filename = 'server.log'

log_line              = "2026-06-11T09:00:00Z INFO Server started"
timestamp, _, message = log_line.partition(' ')   # timestamp = '2026-06-11T09:00:00Z'

multiline = "line one\nline two\r\nline three\r"
lines     = multiline.splitlines()    # ['line one', 'line two', 'line three']

header        = "Content-Type: text/html; charset=utf-8"  # partition: maxsplit=1
key, _, value = header.partition(': ')   # key='Content-Type', value='text/html; charset=utf-8'
```

`split()` with no argument collapses any run of consecutive whitespace and strips leading/trailing spaces — far more robust than `split(' ')` for normalizing messy input. `splitlines()` is always preferred over `split('\n')` when processing files that may have Windows (`\r\n`) or old Mac (`\r`) line endings.

Building a string from many parts: always collect into a list and call `sep.join(items)` once — far faster than concatenation in a loop. See [What is List Comprehension in Python? A Complete Guide with Examples](/languages/python/list-comprehension) for list-building patterns that pair naturally with `join()`.

## Searching and Finding Substrings

Use these methods when you need to locate positions, count occurrences, or confirm that a string starts or ends with a known value.

| Task | Method & Syntax |
|---|---|
| Check if substring exists | `'pat' in text` |
| Find first occurrence (index) | `text.find('pat')` |
| Find last occurrence (index) | `text.rfind('pat')` |
| Raise ValueError if missing | `text.index('pat')` |
| Count non-overlapping matches | `text.count('pat')` |
| Check prefix | `text.startswith('prefix')` |
| Check suffix | `text.endswith('.json')` |
| Check multiple options at once | `text.startswith(('http://', 'https://'))` |
| Restrict search to a slice | `text.find('x', start, end)` |

```python
url      = "https://api.example.com/v2/users?page=1"
has_v2   = '/v2/' in url                              # True
qs_start = url.find('?')                              # 33; returns -1 if absent
is_https = url.startswith(('https://', 'wss://'))     # True

log        = "WARN: retry 1. WARN: retry 2. WARN: retry 3. ERROR: abort."
warn_count = log.count('WARN')     # 3
err_count  = log.count('ERROR')    # 1

filename = "data_export_2026.csv"
is_csv   = filename.endswith('.csv')                          # True
is_data  = filename.endswith(('.csv', '.tsv', '.parquet'))    # True

path    = "/home/user/projects/report.tar.gz"   # rfind scans right-to-left
dot_pos = path.rfind('.')    # index of the LAST dot
ext     = path[dot_pos:]     # '.gz'
```

**`find()` vs `index()`:** `find()` returns `-1` when the substring is absent; `index()` raises `ValueError`. Use `find()` when a missing value is a normal, expected condition; use `index()` when absence signals a bug and you want the exception to surface immediately. See [How to Handle Errors in Python? A Complete Guide](/languages/python/error-handling) for patterns that pair cleanly with both approaches.

For pattern-based searches that go beyond literal substrings — matching email addresses, IP addresses, or arbitrary formats — the [Regex Cheat Sheet](/cheatsheets/regex-cheatsheet) covers `re.search()`, `re.findall()`, and `re.sub()` with syntax you can drop straight into a project.

## Replacing and Stripping Text

`replace()` handles literal substitution throughout a string. The `strip` family removes unwanted characters from string boundaries.

| Task | Method & Syntax |
|---|---|
| Replace all occurrences | `text.replace('old', 'new')` |
| Replace first N occurrences | `text.replace('old', 'new', 2)` |
| Strip whitespace from both ends | `text.strip()` |
| Strip from left only | `text.lstrip()` |
| Strip from right only | `text.rstrip()` |
| Strip a character set | `text.strip('.,!? ')` |
| Remove exact prefix (Python 3.9+) | `text.removeprefix('https://')` |
| Remove exact suffix (Python 3.9+) | `text.removesuffix('.txt')` |

```python
msg = "ERROR: disk full. ERROR: retry failed. ERROR: gave up."
msg.replace('ERROR', 'WARN')       # replaces all 3 occurrences
msg.replace('ERROR', 'WARN', 1)    # replaces only the first

raw = "   \t hello world \n  "
raw.strip()    # 'hello world'
raw.lstrip()   # 'hello world \n  '
raw.rstrip()   # '   \t hello world'

messy = "...!!!Greetings!!!..."
messy.strip('.!')    # 'Greetings'  (strips each char in '.!' independently)

filename = "report_draft.md"
filename.removesuffix('.md')    # 'report_draft'
filename.removesuffix('.txt')   # 'report_draft.md' — no match, unchanged

url = "https://devnook.dev/blog/"
url.removeprefix('https://')    # 'devnook.dev/blog/'
url.removeprefix('http://')     # 'https://devnook.dev/blog/' — no match
```

`strip()` accepts a **character set**, not a substring. `text.strip('abc')` removes leading/trailing `a`, `b`, or `c` characters in any order — not the literal string `"abc"`. For exact prefix or suffix removal, `removeprefix()` and `removesuffix()` (Python 3.9+) are always preferred: they are unambiguous, never surprise you, and return the original string unchanged when no match is found.

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
name.capitalize()  # 'John doe'  — only the very first char is uppercased
name.swapcase()    # 'JOHN doe'

german = "Straße"
german.lower()    # 'straße'   — ß unchanged by lower()
german.casefold() # 'strasse'  — ß correctly expands to 'ss' for comparison

tags   = ["Python", "python", "PYTHON", "django", "Django"]
unique = list({t.casefold(): t for t in tags}.values())
len(unique)   # 2 — one Python variant, one Django variant

"it's a dog's life".title()   # "It'S A Dog'S Life" — apostrophe edge case
```

Always use `casefold()` — not `lower()` — when comparing strings for equality, especially with user-supplied input that may include non-ASCII characters. The difference only matters for a small set of Unicode characters (German ß, Turkish dotless ı, etc.), but using `lower()` produces silent, hard-to-reproduce comparison bugs in multilingual applications.

## String Formatting and Alignment

Python offers three formatting styles: f-strings (3.6+) for most work, `str.format()` for reusable templates, and `%` formatting in legacy codebases. For the complete format mini-language spec, see [Python String Formatting: f-strings, format(), and %](/languages/python/string-formatting).

| Task | Method & Syntax |
|---|---|
| f-string interpolation | `f"Hello, {name}!"` |
| Named placeholders | `"{name} is {age}".format(name=n, age=a)` |
| Positional placeholders | `"{} {}".format('hello', 'world')` |
| Float precision | `f"{3.14159:.2f}"` |
| Thousands separator | `f"{1_000_000:,}"` |
| Hex / binary output | `f"{255:#010x}"` / `f"{10:#b}"` |
| Center in fixed width | `text.center(20, '-')` |
| Left-justify (pad right) | `text.ljust(20, '.')` |
| Right-justify (pad left) | `text.rjust(20)` |
| Zero-pad a number | `str(42).zfill(5)` |

```python
name, score, pct = "Alice", 1842, 0.9357
f"{name:<10} {score:>8,} {pct:.1%}"   # 'Alice       1,842 93.6%'
f"{255:#010x}"                          # '0x000000ff'
f"{score:+}"                            # '+1842'

fmt = "{:<12} {:>8} {:^6}"             # fixed-width table formatting
print(fmt.format("Name", "Score", "Grade"))  # 'Name          Score  Grade '
print(fmt.format("Bob",  1750,    "B"))      # 'Bob            1750    B   '

order_id = f"order_{str(42).zfill(6)}"      # 'order_000042'

template = "User {username!r} logged in from {ip}"
template.format(username="alice", ip="192.168.1.1")
```

## Type-Checking and Validation

These predicate methods return `True` or `False` and are most useful for validating raw input before conversion or downstream processing.

| Task | Method & Syntax |
|---|---|
| All alphabetic | `text.isalpha()` |
| Strict decimal digits only | `text.isdecimal()` |
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

"alice".isalpha()       # True
"alice123".isalpha()    # False — digit present
"alice123".isalnum()    # True
"alice_123".isalnum()   # False — underscore is not alphanumeric

"123".isdecimal()   # True
"²³".isdecimal()    # False — Unicode superscripts fail isdecimal
"²³".isdigit()      # True  — superscripts pass isdigit; int("²³") still raises ValueError

"my_column".isidentifier()    # True
"2bad_name".isidentifier()    # False — starts with digit
"for".isidentifier()          # True — keyword check is separate (keyword.iskeyword())

"hello".islower()   # True
"Hello".islower()   # False
"  ".isspace()      # True
"".isspace()        # False — empty string returns False for all is* methods
```

Use `isdecimal()` — not `isdigit()` — when validating numeric input before calling `int()`. Superscript and subscript Unicode characters pass `isdigit()` but cause `int()` to raise `ValueError`. `isalnum()` excludes underscores and hyphens, so it is not a substitute for identifier validation — use `isidentifier()` for that.

## Encoding and Byte Conversion

| Task | Method & Syntax |
|---|---|
| Encode string to bytes | `text.encode('utf-8')` |
| Decode bytes to string | `b_obj.decode('utf-8')` |
| Ignore unencodable characters | `text.encode('ascii', errors='ignore')` |
| Replace unencodable characters | `text.encode('ascii', errors='replace')` |
| XML-escape unencodable chars | `text.encode('ascii', errors='xmlcharrefreplace')` |
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

rot13 = str.maketrans(
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
)
"Hello".translate(rot13)   # 'Uryyb'

"col1\tcol2\tcol3".expandtabs(12)   # 'col1        col2        col3'
```

When reading files that may have mixed or unknown encodings, always specify the `encoding` parameter in `open()` and choose an `errors` strategy (`'ignore'`, `'replace'`, or `'backslashreplace'`) to avoid hard crashes on unexpected characters. See [How to File Handling in Python + Examples](/languages/python/file-handling) for encoding-aware file patterns. The [Python string module](https://docs.python.org/3/library/string.html) also provides `string.punctuation`, `string.ascii_letters`, and `string.Template` for cases where the built-in `str` methods are not quite enough.

## Common Pitfalls and Performance Tips

These are the mistakes that appear most often in code reviews — patterns worth encoding in muscle memory.

| Pitfall | Problem | Fix |
|---|---|---|
| Discarding the return value | `text.strip()` alone changes nothing | Assign back: `text = text.strip()` |
| `text.split('')` | Raises `ValueError` | Use `list(text)` to iterate characters |
| `strip()` argument confusion | Strips individual chars, not a substring | Use `removeprefix()` / `removesuffix()` for exact removal |
| `lower()` for equality checks | Misses Unicode edge cases (German ß, etc.) | Use `casefold()` for all equality comparisons |
| String concatenation in a loop | O(n²) memory allocations | Collect into a list and call `''.join(items)` once |
| `isdigit()` for int validation | Accepts Unicode superscripts like `²` | Use `isdecimal()` instead |
| `replace()` replaces all | Unexpected mass substitution | Pass count arg: `text.replace('x', 'y', 1)` |
| `index()` on missing text | Raises `ValueError` at runtime | Use `find()` and check for `-1` |

```python
s = "  padded  "
s.strip()              # result discarded — s is still "  padded  "
s = s.strip()          # must reassign
print(s)               # 'padded'

parts  = [str(i) for i in range(10_000)]
fast   = "".join(parts)      # single allocation — O(n)
slow   = ""
for p in parts:
    slow += p                # new string object each iteration — O(n²), avoid this
```

```python
tag   = "<h1>Title</h1>"
clean = tag.removeprefix('<h1>').removesuffix('</h1>')  # 'Title'  — exact, safe
wrong = tag.strip('<h1>')    # strips CHARS '<','h','1','>' — not the literal tag string

words  = ["Café", "café", "CAFÉ"]
unique = {w.casefold() for w in words}  # 1 item — all map to 'café'
```

When you need batch string transformations over many items, [How to Do Dictionary Comprehension in Python?](/languages/python/dictionary-comprehension) shows patterns that compose cleanly with `str` method chains. The most common single fix that improves both correctness and performance: switch all string equality comparisons from `lower()` to `casefold()`, and replace any concatenation loop with a single `join()` call.
