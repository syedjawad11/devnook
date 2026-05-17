---
related_content: []
actual_word_count: 1080
category: languages
concept: file-handling
description: Learn how to perform file handling in Python, including reading, writing,
  and appending to files with practical code examples. Master I/O operations.
difficulty: beginner
language: python
og_image: og-default
published_date: '2026-04-12'
related_cheatsheet: ''
related_posts: []
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"How to File Handling in Python\
  \ + Examples\",\n  \"description\": \"Learn how to perform file handling in Python,\
  \ including reading, writing, and appending to files with practical code examples.\
  \ Master I/O operations.\",\n  \"datePublished\": \"2026-04-12\",\n  \"author\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\"\
  : \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n\
  \  \"url\": \"https://devnook.dev/languages/\"\n}\n</script>"
sections_used:
- open-quick
- core-syntax-detail
- code-before-after
- code-realistic
- prac-common-mistakes
- close-checklist
tags:
- python
- file-handling
- io-operations
- file-management
- read-write
template_id: modular-v1
title: How to File Handling in Python + Examples
voice: terse-senior
---

Use `with open(path, mode) as f:` for all file operations. It closes the file automatically — on normal exit and on exceptions.

```python
with open('requests.log', 'r', encoding='utf-8') as f:
    for line in f:
        process(line.strip())
```

Three modes cover most work: `'r'` reads, `'w'` writes and erases first, `'a'` appends. Iterate the file object directly — one line at a time, constant memory use regardless of file size.

## The open() Call, Parameter by Parameter

```python
open(file, mode='r', encoding=None, errors='strict', newline=None)
```

**`file`** — path to the file. String or `pathlib.Path`. Relative to the current working directory unless absolute.

**`mode`** — what operations are allowed and how the file opens:

| Mode | If file exists | If missing | Truncates | Position |
|------|----------------|------------|-----------|----------|
| `'r'` | opens it | raises `FileNotFoundError` | no | start |
| `'w'` | opens it | creates it | yes, at open time | start |
| `'a'` | opens it | creates it | no | end |
| `'r+'` | opens it | raises `FileNotFoundError` | no | start |
| `'x'` | raises `FileExistsError` | creates it | — | start |

Add `'b'` to any mode for binary I/O: `'rb'`, `'wb'`, `'ab'`. Required for images, archives, pickled data, or anything that isn't plain text.

**`encoding`** — don't rely on the default. Python uses the OS locale encoding, which is UTF-8 on most Linux systems but differs on Windows. Specify `'utf-8'` explicitly whenever the file might be read on a different machine.

**`errors`** — what to do with bytes that can't be decoded. `'strict'` (the default) raises `UnicodeDecodeError`. `'replace'` substitutes `�`. Use `'replace'` when processing files you didn't generate and can't guarantee are clean.

The non-obvious one in the table: `'w'` truncates at open time, not at write time. Open a file with `'w'`, throw an exception before writing a single byte, and you've still erased whatever was there.

## The Context Manager vs Manual Close

**Before — the manual pattern:**

```python
f = open('deployments.txt', 'r')
records = f.readlines()
process_records(records)
f.close()
```

If `process_records()` raises, `f.close()` never runs. On Linux the garbage collector eventually reclaims the handle. On Windows, the file stays locked — other code trying to open or rename it will fail.

**After — context manager:**

```python
with open('deployments.txt', 'r', encoding='utf-8') as f:
    records = f.readlines()
    process_records(records)
```

The `with` block calls `f.__exit__()` on both normal exit and on exceptions. No manual close. No leaks. This is the only pattern worth using.

## Working with a Config File

Here's a shape that shows up in CLI tools and background services:

```python
import json
from pathlib import Path

CONFIG_PATH = Path.home() / '.config' / 'deployer' / 'settings.json'

def load_settings() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)

def save_settings(settings: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open('w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

settings = load_settings()
settings['deploy_target'] = 'production'
settings['max_retries'] = 3
save_settings(settings)
```

`Path.home()` resolves to the actual home directory on any OS — no hardcoded paths. The `mkdir(parents=True, exist_ok=True)` call creates the full directory tree before writing; skip it and the write fails if the directory doesn't exist yet. `json.dump` with `indent=2` writes human-readable JSON — worth doing for a config file a person might edit directly.

`CONFIG_PATH.open()` works the same as the built-in `open()` but reads more naturally when the path is already a `Path` object. Both forms accept the same arguments.

## Mistakes That Happen on First Projects

**Mistake 1: no encoding specified**

```python
# Works locally, may break on a different server
with open('invoice.txt', 'w') as f:
    f.write('Total: €1,299')
```

```python
# Same behavior everywhere
with open('invoice.txt', 'w', encoding='utf-8') as f:
    f.write('Total: €1,299')
```

The first version uses the OS default. On a Linux server with a non-UTF-8 locale, it writes garbled bytes or raises `UnicodeEncodeError`. Always specify encoding.

**Mistake 2: `'w'` instead of `'a'` for logs**

```python
# Intended to append — actually erases the file on every call
with open('events.log', 'w') as f:
    f.write(f'{timestamp}: user logged in\n')
```

```python
# Correct — appends without touching existing content
with open('events.log', 'a', encoding='utf-8') as f:
    f.write(f'{timestamp}: user logged in\n')
```

`'w'` truncates before your code runs. Every call to this function wipes the log. Use `'a'` for anything that accumulates content over time.

**Mistake 3: `read()` on large files**

```python
# 1GB log file = 1GB in RAM
with open('access.log', 'r') as f:
    lines = f.read().splitlines()
```

```python
# Constant memory regardless of file size
with open('access.log', 'r', encoding='utf-8') as f:
    for line in f:
        handle(line.rstrip('\n'))
```

`f.read()` loads the entire file into a string. Fine for small config files. Not for logs or datasets. Iterate the file object directly — it yields one line at a time.

## Quick Reference

- Use `with open(...) as f:` — never `f.close()` manually
- `'w'` truncates at open time — use `'a'` to keep existing content
- Always specify `encoding='utf-8'` — OS default varies
- Iterate the file object (`for line in f:`) for memory-constant line reading
- `'rb'`/`'wb'` for binary files
- Check `path.exists()` before opening in `'r'` mode
- `pathlib.Path` for cross-platform paths; `.open()` works like built-in `open()`
