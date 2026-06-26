---
title: "Python for Loop and Control Flow: while, break, continue"
description: "Python for loop and while loop explained with practical examples. Master range(), break, continue, nested loops, and control flow in Python."
category: "languages"
language: "python"
concept: "loops-control-flow"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [python, loops, control-flow, for-loop, while-loop]
related_posts: []
related_tools: []
linkAnchors:
  - "python for loop"
  - "python loops"
  - "python control flow"
published_date: "2026-06-26"
og_image: "/og/languages/python/loops-control-flow.png"
word_count_target: 1592
schema_org: "<script type=\"application/ld+json\">\n{\"@context\":\"https://schema.org\",\"@type\":[\"TechArticle\",\"FAQPage\"],\"headline\":\"Python for Loop and Control Flow: while, break, continue\",\"description\":\"Python for loop and while loop explained with practical examples. Master range(), break, continue, nested loops, and control flow in Python.\",\"datePublished\":\"2026-06-26\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/languages/python/loops-control-flow/\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"What is the difference between a Python for loop and a while loop?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"A for loop iterates over a sequence a defined number of times. A while loop runs as long as a condition is True, for when you do not know the iteration count upfront. Use for for collections and ranges; use while for condition-driven repetition.\"}},{\"@type\":\"Question\",\"name\":\"How do you loop over a dictionary in Python?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Use for key in my_dict to get keys. Use for key, value in my_dict.items() for key-value pairs. Use for value in my_dict.values() for values only. All maintain insertion order in Python 3.7+.\"}},{\"@type\":\"Question\",\"name\":\"What does the else clause do in a Python for loop?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"The else block runs when the loop completes without hitting a break statement. If break fires, else is skipped. Most useful for not-found patterns where you need fallback logic when no item matched a condition.\"}}]}\n</script>"
---
Python's loops are the engine behind most useful programs. Every time you process a list of orders, scan a log file, or validate user input, you need to repeat a block of code for each item or until a condition changes. The **python for loop** covers the first case: it runs a block once for every item in a sequence. The `while` loop covers the second: it keeps running until its condition becomes false. Knowing when to use each — and how to control them with `break`, `continue`, and `else` — is the foundation of practical Python programming. This guide walks through both loop types with runnable examples.

## How the Python for Loop Works

The python for loop iterates over any *iterable* — a list, string, tuple, dictionary, or `range` object. Python assigns the loop variable to each item in the sequence in turn, runs the indented block, then moves to the next item automatically.

```python
order_ids = ["ORD-001", "ORD-002", "ORD-003"]
for order_id in order_ids:
    print(f"Processing {order_id}")
```

This prints three lines, one per order. When Python reaches the end of `order_ids`, the loop ends and execution continues on the next unindented line.

Strings are also iterable. Looping over a string gives you one character per iteration:

```python
for char in "hello":
    print(char)  # h, e, l, l, o — one per line
```

The loop variable (`order_id`, `char`) is a reference to each item, not a copy. For immutable types like strings and integers that distinction makes no practical difference. For mutable types like dicts and lists, changes made through the loop variable inside the loop body affect the original object.

## Iterating with range()

When you need to repeat something a fixed number of times, or need an index, `range()` generates the integers you need:

```python
for i in range(5):          # produces 0, 1, 2, 3, 4
    print(f"Attempt {i + 1}")

for i in range(2, 6):      # stop is exclusive; prints 2, 3, 4, 5
    print(i)

for i in range(10, 0, -2): # step of -2; prints 10, 8, 6, 4, 2
    print(i)
```

`range()` is lazy — it generates numbers on demand rather than allocating a full list in memory. `range(1_000_000)` uses negligible memory.

For index-and-value access together, `enumerate()` is cleaner than tracking a manual counter:

```python
filenames = ["report.csv", "summary.txt", "backup.csv"]
for index, filename in enumerate(filenames):
    print(f"{index}: {filename}")
```

This replaces the common pattern of `i = 0` with `i += 1` inside the loop. Python's official [control flow documentation](https://docs.python.org/3/tutorial/controlflow.html) covers `for` and `range()` in full detail, including how Python's `for` interacts with the iterator protocol internally.

## The while Loop: Running Until a Condition Changes

The `while` loop keeps executing as long as its condition evaluates to `True`:

```python
retry_count = 0
max_retries = 3

while retry_count < max_retries:
    print(f"Connecting... (attempt {retry_count + 1})")
    retry_count += 1

print("Done")
```

Use `while` when you don't know the number of iterations upfront — waiting for user input, polling a queue until it empties, retrying a network request until it succeeds or a timeout fires.

Use `for` when you're iterating over a known collection or a `range`. Python manages the iteration automatically, which removes the risk of forgetting to advance a counter and creating an infinite loop.

A `while True:` loop runs forever unless something inside it exits with `break`. This is a legitimate pattern for CLI prompts and event loops:

```python
while True:
    user_input = input("Enter a number: ")
    if user_input.isdigit():
        break
    print("Not a valid number — try again")

print(f"You entered: {user_input}")
```

Any `while True:` without a reachable `break` is a bug. Check that the exit condition can actually be reached on every code path.

## break, continue, and the Loop else Clause

### break

`break` exits the loop immediately. All remaining iterations are skipped, and Python moves to the first line after the loop block:

```python
log_lines = ["INFO: start", "ERROR: disk full", "INFO: retrying"]
for line in log_lines:
    if line.startswith("ERROR"):
        print(f"Halting on error: {line}")
        break
    print(line)
```

Only `INFO: start` and the halt message print. Once the `ERROR` line is found, the loop ends.

### continue

`continue` skips the rest of the current iteration and jumps to the next one:

```python
measurements = [12.4, -1.0, 8.9, -1.0, 15.3]
for measurement in measurements:
    if measurement < 0:
        continue  # skip sentinel values
    print(f"Valid reading: {measurement}")
```

### else

A `for` or `while` loop can have an `else` block. It runs when the loop completes *without hitting `break`*:

```python
active_users = [{"id": 10, "name": "Alice"}, {"id": 11, "name": "Bob"}]
target_id = 99

for user in active_users:
    if user["id"] == target_id:
        print(f"Found: {user['name']}")
        break
else:
    print(f"User {target_id} not in the active list")
```

Without `else`, you'd need a `found = False` flag variable and a check after the loop. The `else` clause eliminates that pattern entirely.

## Iterating Over Dictionaries

Python 3 dictionaries maintain insertion order (guaranteed since Python 3.7), and their iteration API is clean:

```python
server_config = {"host": "db.prod.local", "port": 5432, "timeout": 30}

for key in server_config:               # keys only (dict's default iteration)
    print(key)

for key, value in server_config.items():  # key-value pairs
    print(f"  {key}: {value}")

for value in server_config.values():    # values only
    print(value)
```

When you need to build a new dictionary from loop logic, [dictionary comprehension in Python](/languages/python/dictionary-comprehension/) gives you a single-expression alternative to a `for` loop with explicit assignment.

When processing items that might be malformed or raise exceptions, combine your loop with [Python error handling](/languages/python/error-handling/) — a `try`/`except` block inside the loop lets you log and skip bad items without crashing the whole iteration.

## Two Loop Mistakes That Trip Beginners

### Modifying a list while iterating over it

```python
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)  # BUG: shifts indices under the iterator

print(items)  # [1, 3, 5] — item 3 was never checked
```

When `2` is removed, the list shifts left: `3` moves to index 0, but the iterator has already advanced to index 1, so `3` is never evaluated. The same bug appears with `.append()` and `.insert()` — the list changes shape while the iterator tracks a position offset.

Fix: iterate over a copy, or build a new list:

```python
items = [item for item in items if item % 2 != 0]
```

### Using the same variable name in nested loops

```python
for i in range(3):
    for i in range(3):  # shadows the outer i
        pass
print(i)  # prints 2 — the inner loop's final value, not the outer's
```

The inner `i` overwrites the outer one at every iteration. After the outer loop finishes, `i` holds the inner loop's last value. Use distinct names — `row` and `col`, `outer_idx` and `inner_idx`, or descriptive names that reflect what's being iterated.

For text processing inside loops — testing whether lines match a pattern or extracting capture groups — the [DevNook regex tester](/tools/regex-tester/) lets you validate your expressions interactively before embedding them in production code.

Python's [itertools module](https://docs.python.org/3/library/itertools.html) provides higher-level iteration building blocks — `chain`, `islice`, `product`, `groupby`, `zip_longest` — that replace many nested or conditional loop patterns with a single, readable call.

## Frequently Asked Questions

### What is the difference between a Python for loop and a while loop?

A `for` loop iterates over a sequence a defined number of times, determined by the iterable's length. A `while` loop runs as long as a condition is `True`, making it the right choice when the number of iterations isn't known upfront — polling a service, reading until EOF, retrying until success. For collections and `range` values, `for` is almost always cleaner; reserve `while` for condition-driven repetition.

### How do you loop over a dictionary in Python?

Use `for key in my_dict:` to get keys. Use `for key, value in my_dict.items():` to get key-value pairs together. Use `for value in my_dict.values():` to iterate over values only. All three patterns are O(n) and maintain insertion order in Python 3.7+.

### What does the else clause do in a Python for loop?

The `else` block runs when the loop completes without hitting a `break`. If `break` fires, the `else` is skipped entirely. The most common use case is not-found logic: loop through a collection searching for a match; if no match exists, the `else` runs your fallback code without a separate flag variable.

### Can you use a for loop without the loop variable?

Yes. Use `_` as a throwaway name when you need to repeat an action N times but don't care about the index:

```python
for _ in range(5):
    send_ping()
```

This is idiomatic Python for "repeat N times."

## What to Learn Next

With the python for loop and `while` covered, two topics deepen your iteration skills directly:

[Python list comprehensions](/languages/python/list-comprehension/) replace the common `result = []; for x in items: result.append(...)` pattern with a single readable line. Start here — it's the most immediately practical next step after mastering loop basics.

[Python recursive functions](/languages/python/write-recursive-functions/) handle problems that don't map cleanly to iteration — tree traversal, divide-and-conquer algorithms, problems with naturally nested structure. Understanding loops first makes the transition to recursion much easier.

For loops become more interesting as the data structures you're iterating over grow more complex — see [Python data structures: deque, set, stack](/languages/python/data-structures/) for working with collections beyond plain lists.
