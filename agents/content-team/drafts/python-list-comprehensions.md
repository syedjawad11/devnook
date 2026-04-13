---
actual_word_count: 953
category: languages
concept: list-comprehensions
description: List comprehensions let you build Python lists in a single line. Learn
  the syntax, nested patterns, filtering, and when to use them with working examples.
difficulty: intermediate
language: python
og_image: /og/languages/python/list-comprehensions.png
published_date: '2026-04-13'
related_cheatsheet: /cheatsheets/python-iterables
related_posts:
- /languages/python/lambda-functions
- /languages/python/generators
- /languages/python/filter-map-reduce
related_tools:
- /tools/python-repl
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"Python List Comprehensions:\
  \ Syntax, Examples & When to Use Them\",\n  \"description\": \"List comprehensions\
  \ let you build Python lists in a single line. Learn the syntax, nested patterns,\
  \ filtering, and when to use them with working examples.\",\n  \"datePublished\"\
  : \"2026-04-13\",\n  \"author\": {\"@type\": \"Organization\", \"name\": \"DevNook\"\
  },\n  \"publisher\": {\"@type\": \"Organization\", \"name\": \"DevNook\", \"url\"\
  : \"https://devnook.dev\"},\n  \"url\": \"https://devnook.dev/languages/\"\n}\n\
  </script>"
tags:
- python
- list-comprehension
- functional-programming
- python-syntax
- iterables
template_id: lang-v3
title: 'Python List Comprehensions: Syntax, Examples & When to Use Them'
---

Python list comprehensions let you build lists in a single line using a compact, readable syntax that combines looping and conditional logic.

## Syntax at a Glance

The basic structure packs a for-loop and optional condition into square brackets:

```python
# Basic syntax: [expression for item in iterable]
squares = [x**2 for x in range(5)]
# Result: [0, 1, 4, 9, 16]

# With condition: [expression for item in iterable if condition]
evens = [x for x in range(10) if x % 2 == 0]
# Result: [0, 2, 4, 6, 8]

# With transformation and filter
upper_vowels = [char.upper() for char in "hello" if char in "aeiou"]
# Result: ['E', 'O']
```

The expression comes first, followed by the loop logic. Any filtering condition goes at the end. The entire construct produces a new list without modifying the original iterable.

## Full Working Examples

**Example 1 — Converting Celsius to Fahrenheit**

```python
celsius = [0, 10, 20, 30, 40]
fahrenheit = [(temp * 9/5) + 32 for temp in celsius]
print(fahrenheit)
# Output: [32.0, 50.0, 68.0, 86.0, 104.0]
```

This replaces a four-line for-loop with a single expression. Each celsius value gets transformed by the formula and collected into a new list.

**Example 2 — Extracting Specific Fields from Dictionaries**

```python
users = [
    {"name": "Alice", "age": 30, "active": True},
    {"name": "Bob", "age": 25, "active": False},
    {"name": "Charlie", "age": 35, "active": True}
]

active_names = [user["name"] for user in users if user["active"]]
print(active_names)
# Output: ['Alice', 'Charlie']
```

Combining dictionary access with filtering is common when processing JSON data or database results. The condition filters users before extracting names.

**Example 3 — Nested Comprehension for Matrix Operations**

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# Flatten the matrix
flattened = [num for row in matrix for num in row]
print(flattened)
# Output: [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Transpose the matrix
transposed = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
print(transposed)
# Output: [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
```

Nested comprehensions iterate outer-to-inner, left-to-right. The flattening example processes each row, then each number in that row. The transpose builds new columns by pulling the i-th element from each row.

## Key Rules in Python

- **Left-to-right evaluation**: `[x for row in matrix for x in row]` means "for each row, then for each x in that row" — nesting goes deeper as you read right
- **Conditions filter, not transform**: The `if` clause removes items; it doesn't modify them (use a ternary expression in the output for that)
- **Creates a new list**: Original iterables remain unchanged; comprehensions build fresh lists in memory
- **Single expression output**: The first part must be a single expression — you can call functions but not use statements like `print()` or assignments
- **Equivalent to `map()` + `filter()`**: List comprehensions replace most functional programming patterns in Python with more readable syntax
- **Scope is local**: Variables defined in the comprehension (`for x in...`) don't leak into the outer scope

## Common Patterns

**Pattern: Conditional Expression in Output**

```python
# Mark odd/even numbers
labels = ["even" if x % 2 == 0 else "odd" for x in range(6)]
# Result: ['even', 'odd', 'even', 'odd', 'even', 'odd']

# Cap values at a maximum
capped = [min(x, 100) for x in [50, 150, 75, 200]]
# Result: [50, 100, 75, 100]
```

The ternary operator `(value_if_true if condition else value_if_false)` goes in the expression position. This transforms values based on conditions rather than filtering them out.

**Pattern: Calling Functions on Each Item**

```python
strings = ["  hello  ", "WORLD", "  Python  "]
cleaned = [s.strip().lower() for s in strings]
# Result: ['hello', 'world', 'python']

# Parse strings to integers, skip invalid
numbers = ["42", "invalid", "17", "3.14"]
parsed = [int(x) for x in numbers if x.isdigit()]
# Result: [42, 17]
```

Chaining method calls or function transformations keeps list comprehensions concise while handling real-world data cleaning tasks. The second example filters before conversion to avoid exceptions.

## When Not to Use List Comprehensions

Avoid list comprehensions when the logic becomes hard to read on a single line — if you need multiple conditions, complex nesting, or more than one filtering step, use a traditional for-loop. Comprehensions prioritize clarity, not cleverness. They also load the entire result into memory at once; for large datasets where you process items one at a time, use [generator expressions](/languages/python/generators) with parentheses instead of brackets.

For operations that don't build a list (like printing each item or updating a database), a standard loop is more appropriate. List comprehensions exist to create lists, not to execute side effects.

## Quick Comparison: Python vs JavaScript

JavaScript uses `map()` and `filter()` methods instead of comprehension syntax:

| Operation | Python | JavaScript |
|---|---|---|
| Transform | `[x*2 for x in nums]` | `nums.map(x => x*2)` |
| Filter | `[x for x in nums if x > 5]` | `nums.filter(x => x > 5)` |
| Both | `[x*2 for x in nums if x > 5]` | `nums.filter(x => x > 5).map(x => x*2)` |
| Nested | `[x for row in matrix for x in row]` | `matrix.flatMap(row => row)` |

Python's syntax reads more like natural language ("x squared for each x in numbers"), while JavaScript chains methods left-to-right. Python's approach often requires fewer intermediate steps for common transformations.

## Related

For functional programming alternatives to list comprehensions, see our guide to [Python's filter, map, and reduce functions](/languages/python/filter-map-reduce). When working with infinite sequences or large datasets, [generator expressions](/languages/python/generators) provide the same syntax with lazy evaluation. The [Python iterables cheat sheet](/cheatsheets/python-iterables) covers comprehension syntax for sets and dictionaries alongside lists.