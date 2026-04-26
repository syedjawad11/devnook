---
title: "What is List Comprehension in Python? A Complete Guide with Examples"
description: "Learn how to use list comprehension in Python to write concise, readable loops. Includes practical examples, performance tips, and common pitfalls."
published_date: "2026-04-22"
category: "languages"
language: "python"
concept: "list-comprehension"
template_id: "lang-v1"
tags: ["python", "list-comprehension", "functional-programming", "data-processing"]
difficulty: "beginner"
related_posts:
  - /languages/python/generators
  - /languages/python/lambda-functions
  - /languages/python/dictionary-comprehension
related_tools:
  - /tools/python-repl
og_image: "/og/languages/python/list-comprehension.png"
---

Python list comprehension transforms the way developers build lists from existing iterables, replacing verbose multi-line loops with a single expressive statement that is both faster to write and faster to execute.

## What is List Comprehension in Python?

List comprehension is a syntactic construct in Python that allows developers to create new lists by applying an expression to each element of an existing iterable, optionally filtering elements with a condition — all within a single line of code. Rather than writing a traditional `for` loop that initializes an empty list, iterates over a sequence, and appends results one by one, list comprehension collapses that entire pattern into a compact, declarative expression enclosed in square brackets.

The mental model behind list comprehension is straightforward: you describe *what* you want in the resulting list rather than *how* to build it step by step. Python evaluates the expression for each element in the iterable, collects the results, and returns a fully formed list object. This approach draws inspiration from set-builder notation in mathematics, where you define a set by specifying a property that its members must satisfy.

Under the surface, Python implements list comprehensions as optimized bytecode. The interpreter recognizes the comprehension pattern and generates more efficient instructions than an equivalent `for` loop with `.append()` calls. This is not merely syntactic sugar — the CPython runtime skips the attribute lookup for the `append` method and uses an internal `LIST_APPEND` bytecode instruction, which reduces overhead per iteration. The result is code that is not only shorter and more readable, but measurably faster for list construction tasks.

List comprehensions support three forms: a simple mapping (`[expr for x in iterable]`), a filtered mapping (`[expr for x in iterable if condition]`), and nested iteration (`[expr for x in iter1 for y in iter2]`). Each form addresses a distinct pattern that Python developers encounter repeatedly when processing sequences, transforming data, or building derived collections.

## Why Python Developers Use List Comprehension

Python developers reach for list comprehensions whenever they need to transform or filter a sequence into a new list. The construct eliminates boilerplate code and communicates intent more clearly than the equivalent loop-based approach.

**Data transformation pipelines** represent one of the most common use cases. When processing a list of API responses, a developer might extract specific fields — such as pulling all user email addresses from a list of JSON objects. A list comprehension like `[user["email"] for user in response_data if user["active"]]` accomplishes in one line what would otherwise require four or five lines of loop code. This pattern appears constantly in web backends, data analysis scripts, and ETL workflows.

**File processing and text manipulation** is another scenario where list comprehensions shine. Reading lines from a log file and extracting those that match a pattern, stripping whitespace from each entry in a CSV column, or converting a list of strings to integers — these operations are natural fits for the comprehension syntax. A developer working with configuration files might write `[line.strip() for line in open("config.txt") if not line.startswith("#")]` to load non-comment lines in a single, readable expression.

**Mathematical and scientific computation** benefits as well. Generating coordinate pairs, computing element-wise transformations on numerical data, or building matrices from formulas all map cleanly onto list comprehensions. Data scientists routinely use them as lightweight alternatives to NumPy operations when working with small-to-medium datasets or when NumPy is not available in the environment.

## Basic Syntax

```python
# Basic list comprehension: square every number from 0 to 9
squares = [number ** 2 for number in range(10)]
# Result: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Filtered comprehension: keep only even squares
even_squares = [number ** 2 for number in range(10) if number % 2 == 0]
# Result: [0, 4, 16, 36, 64]

# Comprehension with transformation: convert temperatures from Celsius to Fahrenheit
celsius_temps = [0, 20, 37, 100]
fahrenheit_temps = [(temp * 9/5) + 32 for temp in celsius_temps]
# Result: [32.0, 68.0, 98.6, 212.0]

# Conditional expression inside comprehension: classify numbers
labels = ["even" if n % 2 == 0 else "odd" for n in range(6)]
# Result: ['even', 'odd', 'even', 'odd', 'even', 'odd']
```

The code above demonstrates the four fundamental patterns of list comprehension. The first example applies a simple expression to every element. The second adds a filter clause using `if` at the end, which excludes elements that do not satisfy the condition. The third example shows real-world transformation — converting temperature units across an entire list. The fourth example uses a ternary expression (`x if condition else y`) within the comprehension itself, which is distinct from the filter clause and allows conditional output values.

## A Practical Example

```python
# Processing a list of student records to generate a grade report
student_records = [
    {"name": "Alice Chen", "scores": [88, 92, 78, 95]},
    {"name": "Bob Martinez", "scores": [72, 68, 81, 74]},
    {"name": "Carol Okafor", "scores": [95, 98, 92, 97]},
    {"name": "David Kim", "scores": [60, 55, 70, 65]},
    {"name": "Eva Johansson", "scores": [85, 90, 88, 91]},
]

# Calculate average score for each student
averages = [
    {"name": student["name"], "average": sum(student["scores"]) / len(student["scores"])}
    for student in student_records
]

# Filter to honor roll students (average >= 85)
honor_roll = [
    student["name"]
    for student in averages
    if student["average"] >= 85
]

# Build a formatted report for honor roll students
report_lines = [
    f"  ★ {name} — Honor Roll"
    for name in honor_roll
]

print("Honor Roll Students:")
print("\n".join(report_lines))
# Output:
#   ★ Alice Chen — Honor Roll
#   ★ Carol Okafor — Honor Roll
#   ★ Eva Johansson — Honor Roll
```

This example demonstrates how list comprehensions chain together naturally in a data processing pipeline. The first comprehension transforms raw student records into a list of dictionaries containing computed averages — notice that the expression itself can be a dictionary literal, not just a simple value. The second comprehension filters that derived list to extract only students meeting the honor roll threshold. The third comprehension formats the output strings for display. Each comprehension is self-contained and readable on its own, and together they form a pipeline that processes raw data into formatted output without a single explicit loop or temporary variable accumulator. This pattern mirrors real-world scenarios in backend development, where data flows through successive transformation and filtering stages.

## Common Mistakes

**Mistake 1: Overusing nested comprehensions for complex logic**

Developers sometimes nest multiple `for` clauses and conditions into a single comprehension, creating dense one-liners that are nearly impossible to read. A comprehension like `[cell for row in matrix for cell in row if cell > 0 if cell % 2 == 0]` is technically valid, but forces the reader to mentally unpack the iteration order and filter logic. The fix is to limit comprehensions to one or two `for` clauses. When the logic requires three or more levels of nesting, break it into a regular `for` loop or chain multiple simpler comprehensions. Readability is a core Python value — a comprehension that requires a comment to explain its structure has lost its primary advantage.

**Mistake 2: Using list comprehension purely for side effects**

Some developers write `[print(item) for item in items]` to iterate over a list and call a function on each element. This creates an unnecessary list of `None` values in memory that is immediately discarded. The construct abuses comprehension syntax for its looping behavior rather than its list-building purpose. The fix is to use a plain `for` loop: `for item in items: print(item)`. If you need a one-liner for side effects, `any(print(item) or True for item in items)` works but is equally unclear — just use the loop.

**Mistake 3: Forgetting that comprehensions create new lists, not views**

A list comprehension always creates a new list object in memory. Developers working with very large datasets sometimes write `result = [transform(x) for x in million_element_list]` without realizing that this allocates memory for the entire result list upfront. For large datasets where you only need to iterate once, a generator expression — `(transform(x) for x in million_element_list)` — is more memory-efficient because it yields values lazily. The comprehension form should be reserved for cases where you genuinely need the entire list materialized in memory.

## List Comprehension vs map() and filter()

List comprehension and the built-in `map()` and `filter()` functions solve overlapping problems — both transform and filter iterables — but they differ in readability, flexibility, and performance characteristics.

List comprehension is generally preferred in Python because it reads naturally from left to right and does not require wrapping the result in `list()`. The expression `[x ** 2 for x in numbers if x > 0]` is immediately understandable, whereas `list(map(lambda x: x ** 2, filter(lambda x: x > 0, numbers)))` nests three function calls and two lambda definitions.

However, `map()` has a performance edge when you are applying an existing function (not a lambda) to every element. `list(map(str, numbers))` is slightly faster than `[str(n) for n in numbers]` because `map()` avoids the overhead of evaluating a comprehension expression on each iteration — it calls the function pointer directly.

| Aspect | List Comprehension | map() / filter() |
|--------|-------------------|-------------------|
| Readability | High — declarative, left-to-right | Lower — nested, inside-out |
| Flexibility | Full — any expression, conditions | Limited — one function, separate filter |
| Performance (lambda) | Faster | Slower (lambda call overhead) |
| Performance (named function) | Slightly slower | Slightly faster |
| Memory | Returns list | Returns iterator (Python 3) |

The Python community's convention is clear: use list comprehension as the default for building lists, and reserve `map()` for cases where you are applying a single existing function with no filtering needed.

## Under the Hood: Performance & Mechanics

Python's CPython interpreter compiles list comprehensions into dedicated bytecode that is measurably faster than equivalent `for` loop constructions. When you write `[x * 2 for x in range(1000)]`, the compiler generates a `LIST_APPEND` instruction that pushes values directly onto the internal list buffer, bypassing the method lookup and function call overhead of `list.append()`.

At the memory allocation level, CPython uses an over-allocation strategy for lists. When the list grows beyond its current capacity, CPython allocates extra slots following a growth pattern roughly proportional to the current size (the exact formula is `new_size + (new_size >> 3) + 6`). This amortized resizing means that appending elements — whether via comprehension or explicit loop — achieves O(1) amortized time per insertion. However, comprehensions benefit from an additional optimization: the interpreter can sometimes pre-size the internal array when the length of the input iterable is known (for example, when iterating over a list or range object), eliminating resizing entirely.

The time complexity for a simple list comprehension is O(n) where n is the length of the input iterable — each element is visited exactly once. Adding a filter clause does not change the asymptotic complexity, though it reduces the constant factor by producing fewer output elements. Nested comprehensions with two `for` clauses produce O(n × m) iterations, which can become expensive if both iterables are large.

One hidden cost that developers often overlook is the memory footprint. A list comprehension materializes the entire result in memory before any downstream code can access it. For a comprehension producing 10 million integers, Python allocates approximately 80 MB of memory (8 bytes per pointer × 10 million, plus object overhead). Generator expressions avoid this by yielding values lazily, but they cannot be indexed or sliced — the tradeoff is between random access and memory efficiency.

Comprehensions also create their own scope in Python 3. The iteration variable does not leak into the enclosing scope, unlike a `for` loop where the variable persists after the loop completes. This scoping behavior is implemented by compiling each comprehension as an implicit nested function, which adds a small constant overhead for function creation but prevents variable name pollution.

## Advanced Edge Cases

**Edge Case 1: Variable scoping in comprehension with walrus operator**

```python
# The walrus operator (:=) inside a comprehension leaks to enclosing scope
results = [last := x ** 2 for x in range(5)]
print(last)  # Prints 16 — the last assigned value

# This is intentional behavior — PEP 572 specifies that := targets the enclosing scope
# But it creates confusing situations:
filtered = [y for x in range(10) if (y := x ** 2) > 20]
print(y)  # Prints 81 — leaks the last value of y, even filtered ones don't affect it
# y holds the LAST evaluated value, not the last value that passed the filter
```

The walrus operator (`:=`) introduced in Python 3.8 deliberately breaks the comprehension's scope isolation. While the iteration variable (`x`) stays contained within the comprehension's implicit function scope, assignment expressions using `:=` target the enclosing function or module scope. This creates a subtle trap: `y` in the example above holds value 81 (the square of 9, the last x evaluated) rather than 64 (the square of the last x whose square exceeded 20). The filter condition evaluates `y := x ** 2` for every x, but only yields the element when the condition is true. The assignment happens regardless of whether the element passes the filter.

**Edge Case 2: Comprehension with mutable default-like sharing**

```python
# Creating a list of lists using comprehension — the WRONG way
grid_wrong = [[0] * 3] * 3
grid_wrong[0][0] = 1
print(grid_wrong)
# [[1, 0, 0], [1, 0, 0], [1, 0, 0]] — all rows share the same list object!

# The correct approach using list comprehension
grid_correct = [[0] * 3 for _ in range(3)]
grid_correct[0][0] = 1
print(grid_correct)
# [[1, 0, 0], [0, 0, 0], [0, 0, 0]] — each row is an independent list
```

This edge case trips even experienced Python developers. The multiplication operator `*` for lists creates references, not copies. When `[[0] * 3] * 3` executes, it creates one inner list and replicates three references to that same object. Modifying any "row" mutates all of them because they point to the same memory address. The list comprehension form `[[0] * 3 for _ in range(3)]` evaluates `[0] * 3` on each iteration, producing three distinct list objects. This distinction is fundamental to Python's object model — the comprehension creates new objects per iteration, while multiplication replicates references.

## Testing List Comprehension in Python

Testing code that uses list comprehensions follows the same principles as testing any pure transformation — you verify that given specific inputs, the output matches expected results. Python's built-in `unittest` framework provides everything needed for thorough validation.

```python
import unittest


def get_passing_scores(student_scores, threshold=70):
    """Extract scores that meet or exceed the passing threshold."""
    return [score for score in student_scores if score >= threshold]


def normalize_emails(raw_emails):
    """Clean and lowercase a list of email addresses, removing empty entries."""
    return [
        email.strip().lower()
        for email in raw_emails
        if email.strip()
    ]


class TestListComprehensions(unittest.TestCase):

    def test_passing_scores_filters_correctly(self):
        scores = [85, 42, 70, 95, 60, 78]
        result = get_passing_scores(scores)
        self.assertEqual(result, [85, 70, 95, 78])

    def test_passing_scores_with_custom_threshold(self):
        scores = [85, 42, 70, 95, 60, 78]
        result = get_passing_scores(scores, threshold=80)
        self.assertEqual(result, [85, 95])

    def test_passing_scores_empty_input(self):
        self.assertEqual(get_passing_scores([]), [])

    def test_passing_scores_all_fail(self):
        self.assertEqual(get_passing_scores([10, 20, 30]), [])

    def test_normalize_emails_strips_and_lowercases(self):
        raw = ["  Alice@Example.COM ", "bob@test.org", "  ", "CAROL@Dev.IO"]
        result = normalize_emails(raw)
        self.assertEqual(result, ["alice@example.com", "bob@test.org", "carol@dev.io"])

    def test_normalize_emails_removes_blank_entries(self):
        raw = ["", "   ", "valid@email.com"]
        result = normalize_emails(raw)
        self.assertEqual(result, ["valid@email.com"])


if __name__ == "__main__":
    unittest.main()
```

The test suite above validates two functions that use list comprehensions internally. The key testing strategy is to isolate the comprehension logic inside named functions rather than testing inline comprehensions directly. This approach gives each comprehension a clear contract (inputs → outputs) and makes tests self-documenting. The `get_passing_scores` tests cover the filter clause behavior — standard threshold, custom threshold, empty input, and all-fail scenarios. The `normalize_emails` tests verify both the transformation expression (strip and lowercase) and the filter condition (removing blank entries). Edge cases like empty lists, all-filtered results, and whitespace-only strings exercise boundary conditions where comprehensions might silently return unexpected empty lists.

## Quick Reference

- List comprehension syntax: `[expression for item in iterable if condition]`
- Filter clause (`if`) goes at the end and excludes elements; ternary expression (`x if cond else y`) goes in the expression position and transforms output
- Comprehensions always create a new list in memory — use generator expressions `()` for lazy evaluation
- Iteration variables in comprehensions do not leak into the enclosing scope (Python 3)
- Prefer comprehensions over `map()`/`filter()` for readability; use `map()` only when applying a single named function
- Nested comprehensions read left-to-right: `[x for row in matrix for x in row]` means "for each row, for each x in that row"
- CPython compiles comprehensions to optimized `LIST_APPEND` bytecode — typically 10-30% faster than equivalent `.append()` loops
- Maximum recommended complexity: two `for` clauses; beyond that, use explicit loops

## Next Steps

- **Generator expressions** extend the comprehension concept with lazy evaluation — essential for processing large datasets without memory pressure. Use `()` instead of `[]` to create a generator instead of a list.
- **Dictionary and set comprehensions** use the same syntax principles but produce `dict` and `set` objects. Learn how in [dictionary comprehension in Python](/languages/python/dictionary-comprehension).
- **Lambda functions** pair naturally with `map()` and `filter()` when comprehensions are not the right fit. Explore the tradeoffs between comprehensions and lambda with `map()` and `filter()`.
- Visit the [Python language hub](/languages/python) for more concept guides.
