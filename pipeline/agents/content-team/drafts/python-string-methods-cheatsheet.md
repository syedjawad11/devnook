---
actual_word_count: 919
category: cheatsheets
concept: string-methods
description: Every Python string method with syntax and examples. The only string
  reference you'll need — organized by task.
download_png: false
language: python
og_image: /og/cheatsheets/python-string-methods.png
published_date: '2026-04-13'
related_posts:
- /languages/python/f-strings
- /languages/python/list-comprehensions
- /guides/string-formatting-guide
related_tools:
- /tools/python-repl
- /tools/string-case-converter
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
title: 'Python String Methods Cheat Sheet: split, join, replace, format & More'
---

This Python string methods cheatsheet covers every built-in string operation you'll use regularly, organized by what you're trying to accomplish. Whether you're splitting CSV data, cleaning user input, or formatting output, the method you need is here.

## Splitting & Joining Strings

| Task | Method & Syntax |
|---|---|
| Split on whitespace | `text.split()` |
| Split on delimiter | `text.split(',')` |
| Split from right | `text.rsplit(',', 1)` |
| Split on newlines | `text.splitlines()` |
| Split into max N parts | `text.split(':', maxsplit=2)` |
| Join list into string | `', '.join(items)` |
| Join with newlines | `'\n'.join(lines)` |

```python
csv_row = "apple,banana,orange"
fruits = csv_row.split(',')  # ['apple', 'banana', 'orange']

path = "/home/user/documents/file.txt"
filename = path.rsplit('/', 1)[-1]  # 'file.txt'

words = ['Python', 'string', 'methods']
sentence = ' '.join(words)  # 'Python string methods'
```

## Searching & Checking

| Task | Method & Syntax |
|---|---|
| Check if contains substring | `substring in text` |
| Find first occurrence | `text.find('pattern')` |
| Find last occurrence | `text.rfind('pattern')` |
| Raise error if not found | `text.index('pattern')` |
| Count occurrences | `text.count('pattern')` |
| Check prefix | `text.startswith('prefix')` |
| Check suffix | `text.endswith('.txt')` |

```python
email = "user@example.com"
has_at = '@' in email  # True
domain_start = email.find('@')  # 4

filename = "report.pdf"
is_pdf = filename.endswith('.pdf')  # True
is_draft = filename.startswith('draft_')  # False
```

## Case Conversion

| Task | Method & Syntax |
|---|---|
| Lowercase | `text.lower()` |
| Uppercase | `text.upper()` |
| Title case | `text.title()` |
| Capitalize first char | `text.capitalize()` |
| Swap case | `text.swapcase()` |
| Case-insensitive compare | `text.casefold()` |

```python
name = "john DOE"
name.lower()       # 'john doe'
name.upper()       # 'JOHN DOE'
name.title()       # 'John Doe'
name.capitalize()  # 'John doe'  (only first char)

# Use casefold() for comparisons, not lower()
german = "Straße"
german.casefold() == "strasse"  # True
german.lower() == "strasse"     # False
```

## Replacing & Removing

| Task | Method & Syntax |
|---|---|
| Replace all | `text.replace('old', 'new')` |
| Replace N times | `text.replace('old', 'new', 2)` |
| Remove whitespace (both ends) | `text.strip()` |
| Remove from left | `text.lstrip()` |
| Remove from right | `text.rstrip()` |
| Remove specific chars | `text.strip('.,!? ')` |

```python
code = "  print('hello')  "
code.strip()  # "print('hello')"

url = "https://example.com///"
url.rstrip('/')  # 'https://example.com'

message = "!!!URGENT!!!"
message.strip('!')  # 'URGENT'

log = "ERROR: File not found"
log.replace('ERROR', 'WARNING')  # 'WARNING: File not found'
```

## Formatting & Alignment

| Task | Method & Syntax |
|---|---|
| f-string formatting | `f"Hello {name}"` |
| Format method | `"Hello {}".format(name)` |
| Center align | `text.center(20, '-')` |
| Left align | `text.ljust(20)` |
| Right align | `text.rjust(20)` |
| Zero-pad numbers | `str(42).zfill(5)` |

```python
name = "Alice"
age = 30

# Modern f-strings (preferred)
f"{name} is {age} years old"  # 'Alice is 30 years old'

# Format method
"{} is {} years old".format(name, age)
"{name} is {age}".format(name=name, age=age)

# Alignment
"OK".center(10, '-')  # '----OK----'
"42".zfill(5)         # '00042'
```

For more on f-strings, see our [Python f-strings guide](/languages/python/f-strings).

## Type Checking

| Task | Method & Syntax |
|---|---|
| All alphabetic | `text.isalpha()` |
| All digits | `text.isdigit()` |
| All alphanumeric | `text.isalnum()` |
| All lowercase | `text.islower()` |
| All uppercase | `text.isupper()` |
| All whitespace | `text.isspace()` |
| Is title case | `text.istitle()` |

```python
"Python".isalpha()    # True
"Python3".isalpha()   # False
"Python3".isalnum()   # True
"12345".isdigit()     # True
"   ".isspace()       # True
"Hello World".istitle()  # True
```

## Encoding & Decoding

| Task | Method & Syntax |
|---|---|
| Encode to bytes | `text.encode('utf-8')` |
| Decode from bytes | `bytes_obj.decode('utf-8')` |
| Handle errors | `text.encode('ascii', errors='ignore')` |

```python
text = "Python 🐍"
encoded = text.encode('utf-8')  # b'Python \xf0\x9f\x90\x8d'
decoded = encoded.decode('utf-8')  # 'Python 🐍'

# ASCII encoding with error handling
text.encode('ascii', errors='ignore')  # b'Python '
text.encode('ascii', errors='replace')  # b'Python ?'
```

## Less Common But Useful

| Task | Method & Syntax |
|---|---|
| Partition into 3 parts | `text.partition(':')` |
| Remove prefix (3.9+) | `text.removeprefix('https://')` |
| Remove suffix (3.9+) | `text.removesuffix('.txt')` |
| Expand tabs | `text.expandtabs(4)` |
| Translate characters | `text.translate(table)` |

```python
email = "user@example.com"
user, sep, domain = email.partition('@')  # ('user', '@', 'example.com')

url = "https://devnook.dev"
url.removeprefix('https://')  # 'devnook.dev'

filename = "report.txt"
filename.removesuffix('.txt')  # 'report'
```

## Common Options Worth Knowing

| Option | What it does |
|---|---|
| `maxsplit=N` in `split()` | Limit splits to N times |
| `errors='ignore'` in `encode()` | Skip characters that can't encode |
| `errors='replace'` in `encode()` | Replace invalid chars with `?` |
| `sep=None` in `split()` | Split on any whitespace (default) |
| Second arg in `strip()` | Specify which chars to remove |
| `start, end` in `find()` | Search within slice |

## Common Mistakes

- **Using `split()` with empty string** — `split('')` raises ValueError. Use `list(text)` to split into chars.
- **Forgetting strings are immutable** — Methods return new strings; they don't modify in place. Use `text = text.strip()`, not just `text.strip()`.
- **Using `+` for concatenation in loops** — Inefficient. Use `''.join(items)` or [list comprehensions](/languages/python/list-comprehensions) instead.
- **Using `lower()` instead of `casefold()` for comparisons** — `casefold()` handles Unicode edge cases correctly.

## Related

For string formatting specifically, check the [string formatting guide](/guides/string-formatting-guide). To practice these methods interactively, use our [Python REPL tool](/tools/python-repl). For working with case conversions online, try the [string case converter](/tools/string-case-converter).