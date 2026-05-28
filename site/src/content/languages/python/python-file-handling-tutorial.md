---
related_content: []
actual_word_count: 1880
category: languages
concept: file-handling
linkAnchors:
  - "python file handling"
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
- open-scenario
- core-how-it-works
- code-walkthrough
- prac-gotchas
- prac-production-patterns
- close-next
tags:
- python
- file-handling
- io-operations
- file-management
- read-write
template_id: modular-v1
title: How to File Handling in Python + Examples
voice: tutorial-guide
---

You're automating a deployment monitoring script — it reads a folder of log files produced by your CI/CD system, extracts error counts, and writes a daily summary. You write a loop: open each file, parse the lines, close when done. It works in development with the four files in your test directory. You point it at the production logs — 600 files, three months of build history — and within seconds it crashes: `OSError: [Errno 24] Too many open files`. You check the code. You do have `close()` calls. But one of your parsing functions raises an exception on an unexpected format, and when it does, the `close()` never runs. Python's file-handling doesn't fail loudly when you leak a file handle — the OS keeps the descriptor open until the garbage collector reclaims it or the process limit is hit. That's the first thing to understand about file-handling in Python: the language gives you the tools to do this correctly, but it doesn't force you to use them. The `with` statement is what makes file lifecycle automatic and reliable, and everything else — modes, encoding, iteration — builds on that foundation.

## How Python Represents an Open File

When you call `open('access.log', 'r')`, Python asks the operating system to open a file descriptor — a small integer that represents an open file entry in the kernel's table. Every Python file object wraps one of these descriptors. Each process gets a limited pool: on Linux, the default is 1,024 descriptors per process (`ulimit -n`). That's the quota you exhaust when a loop opens files without closing them.

The file object Python hands back is a layered stack. For text mode (`'r'`, `'w'`, `'a'`), you get a `TextIOWrapper` on top of a `BufferedReader` or `BufferedWriter`, which sits above a `FileIO` object that communicates directly with the OS descriptor. Reading text doesn't touch the disk on every call — the buffered layer pulls data in 8KB chunks and serves lines from that in-memory buffer. Writing works the same way: a `write()` call writes to the buffer first, and the data reaches disk when the buffer fills or the file is closed. This matters in practice. If your process crashes before `close()` runs, the last buffer's worth of data is gone.

The `with open(path, mode) as f:` pattern calls `f.__exit__()` when the block exits — whether normally, through a `ValueError`, or via a `KeyboardInterrupt`. That method calls `f.close()`, which flushes the write buffer and releases the file descriptor before any exception propagates upward. Your handle is cleaned up regardless of what happens inside the block. There's no reason to manage this manually.

```python
with open('requests.log', 'r', encoding='utf-8') as f:
    for line in f:
        process(line.rstrip('\n'))
```

This is the shape you'll use for nearly every read operation. Iterate the file object directly — one line at a time, constant memory no matter how large the file.

## File Modes and Read/Write Patterns

Start with reading. Iterating a file object directly is the right default — it reads one line at a time using the internal buffer, so your memory usage stays flat whether the file is 1KB or 10GB.

```python
with open('access.log', 'r', encoding='utf-8') as f:
    for line in f:
        process(line.rstrip('\n'))
```

If you call `f.read()` instead, Python loads the entire file into a single string. That's fine for small config files you want to parse all at once. It's a problem when the file is a 2GB server log and you've just allocated 2GB of RAM.

For writing, the `'w'` mode creates the file if it doesn't exist and erases it entirely if it does — at open time, not at write time:

```python
with open('report.txt', 'w', encoding='utf-8') as f:
    f.write('Processed: 847 records\n')
    f.write(f'Errors: {error_count}\n')
```

The truncation happens the moment `open()` runs. Open a file with `'w'`, throw an exception before writing anything, and you've already erased the original content. Keep that in mind any time existing data needs to survive a failed run.

Appending is the mode for logs and any data that accumulates over time:

```python
with open('events.log', 'a', encoding='utf-8') as f:
    f.write(f'{timestamp}: {event_type}\n')
```

`'a'` positions the file pointer at the end on open and never truncates. Every `write()` adds to what's already there. If the file doesn't exist yet, Python creates it.

Here's the mode reference you'll come back to:

| Mode | If file exists | If file missing | Truncates |
|------|---------------|-----------------|-----------|
| `'r'` | opens it | raises `FileNotFoundError` | no |
| `'w'` | opens it | creates it | yes, at open time |
| `'a'` | opens it | creates it | no |
| `'r+'` | opens it | raises `FileNotFoundError` | no |
| `'x'` | raises `FileExistsError` | creates it | no |

Add `'b'` to any mode for binary I/O: `'rb'`, `'wb'`, `'ab'`. Use binary mode for images, archives, pickle files, or anything that isn't plain text with a known encoding. Binary mode skips the text decoding layer entirely and gives you raw bytes.

Always pass `encoding='utf-8'` when working with text files. Python's default encoding comes from the OS locale — UTF-8 on most Linux systems, but `cp1252` or `mbcs` on some Windows configurations. A file written without an explicit encoding on your development machine may not decode on the deployment server. One non-ASCII character — a currency symbol, an accented name, a Unicode quote mark — is all it takes to expose the mismatch. Specify the encoding explicitly every time.

## Things That Will Trip You Up

**Trap 1: `'w'` erasing data before your code runs.**

```python
with open('config.json', 'w') as f:
    settings = compute_settings()   # raises an exception here
    json.dump(settings, f)          # never executes
# config.json is now empty
```

The file is truncated when `open()` runs, not when `json.dump()` runs. If `compute_settings()` raises, your original config is gone. The fix is the atomic write pattern — write to a temporary file, then rename:

```python
import os

tmp_path = 'config.json.tmp'
with open(tmp_path, 'w', encoding='utf-8') as f:
    json.dump(compute_settings(), f, indent=2)
os.replace(tmp_path, 'config.json')
```

`os.replace()` is atomic on POSIX systems — either the rename completes or the original file is untouched. There's no window where both files are absent. Python 3.3+ gives you the same guarantee on Windows.

**Trap 2: encoding mismatch between write and read.**

```python
# Written on Windows with default encoding (cp1252)
with open('invoice.txt', 'w') as f:
    f.write('Total: €1,299')

# Read later on Linux with UTF-8 expectation
with open('invoice.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80 in position 8
```

The file was written with one encoding and read assuming another. ASCII-only content hides the bug until the first non-ASCII byte surfaces. Match the encoding in every `open()` call that touches the same file, and default to `'utf-8'` throughout your project.

**Trap 3: opening in `'r'` mode when the file might not exist.**

```python
with open('user_prefs.json', 'r', encoding='utf-8') as f:
    prefs = json.load(f)
# FileNotFoundError on first run — file doesn't exist yet
```

For files that are legitimately absent on a first run, check before opening:

```python
from pathlib import Path

prefs_path = Path('user_prefs.json')
if prefs_path.exists():
    with prefs_path.open('r', encoding='utf-8') as f:
        prefs = json.load(f)
else:
    prefs = {}
```

`Path.exists()` expresses the intent more clearly than catching `FileNotFoundError` for something that's expected to be missing.

## In Production Code

Production Python code almost always uses `pathlib.Path` instead of bare path strings. A `Path` object handles OS-specific separators, exposes the existence checks you need before opening, and has an `.open()` method that behaves identically to the built-in `open()`:

```python
from pathlib import Path
import json

class SettingsStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> dict:
        if not self.path.exists():
            return {}
        with self.path.open('r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, settings: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix('.tmp')
        with tmp.open('w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        tmp.replace(self.path)
```

`self.path.parent.mkdir(parents=True, exist_ok=True)` creates the full directory tree if it doesn't exist. Call `save()` on a path inside a directory that hasn't been created yet, and it won't crash. The atomic write pattern protects the settings file — a crash during `json.dump()` leaves the `.tmp` file incomplete and the original `config.json` untouched.

For append-only data like event logs, production code often holds the file handle open for the lifetime of the process rather than reopening on every write:

```python
import atexit

_log_file = None

def setup_log(path: str) -> None:
    global _log_file
    _log_file = open(path, 'a', encoding='utf-8')
    atexit.register(_log_file.close)

def log_event(event: str) -> None:
    if _log_file:
        _log_file.write(f'{event}\n')
        _log_file.flush()
```

`atexit.register()` ensures the handle closes cleanly on normal process exit. The explicit `flush()` after each write pushes data to disk immediately rather than waiting for the buffer to fill — necessary if another process is reading the log file in real time.

## Where to Go Next

Once you're comfortable with basic file operations, `pathlib` is the next topic worth understanding in depth. Start with `Path.glob()` for working with directories of files, `Path.stat()` for file metadata like size and modification time, and `Path.read_text()` / `Path.write_text()` for the shorthand when you don't need streaming. They wrap the same primitives you've been using, but cut boilerplate for common one-shot reads and writes. After that, look at how the standard library structured-file modules — `csv`, `json`, `tomllib` (added in Python 3.11) — accept a file object from `open()` rather than a path. Everything you've learned about modes, encoding, and context managers transfers directly to working with those formats.
