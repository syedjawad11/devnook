---
title: "Python String Formatting: f-strings, format(), and %"
description: "Master python string formatting with f-strings, str.format(), and %-style. Covers float precision, padding, gotchas, and when to switch between methods."
category: "languages"
language: "python"
concept: "string-formatting"
difficulty: "intermediate"
template_id: "lang-v1"
tags: ["python", "string-formatting", "f-strings", "format-string", "python-strings"]
related_posts: []
related_tools: []
linkAnchors:
  - "python string formatting"
  - "f-string formatting python"
  - "string formatting in python"
published_date: "2026-05-30"
og_image: "/og/languages/python/string-formatting.png"
word_count_target: 1950
---

Your order-processing script is logging: `Order 4231 processed in 0.004320000000000001 seconds, total: 49.999999999999996`. Python string formatting has three methods to fix this — `%` formatting, `str.format()`, and f-strings. The choice is not just stylistic. Logging calls, SQL queries, and i18n templates each require a specific method for correctness, not preference. Each handles string formatting in Python edge cases differently, and knowing the distinctions prevents subtle bugs that appear in production but pass unit tests silently.

## Python String Formatting: Three Methods to Know

Python's formatting methods represent three different generations of the language:

| Method | Introduced | Syntax |
|--------|-----------|--------|
| `%` operator | Python 2 | `"value: %s" % val` |
| `str.format()` | Python 2.6 | `"value: {}".format(val)` |
| f-strings | Python 3.6 | `f"value: {val}"` |

**`%` formatting** treats the left-hand string as a template with `%s`, `%d`, `%f` placeholders. Multiple values require a tuple on the right side, and the specifiers read like C format strings.

**`str.format()`** introduced in Python 2.6. Positional (`{0}`, `{1}`) or keyword (`{name}`) placeholders, called via a chained `.format()`. Cleaner than `%`, still verbose for inline expressions.

**f-strings** (formatted string literals) are the default for new code in Python 3.6+. Expressions live directly inside `{curly braces}` in the string body — the interpreter evaluates each `{expr}` at runtime using the same format spec mini-language as `str.format()`.

The Python 3.x [formatted string literals documentation](https://docs.python.org/3/reference/lexical_analysis.html#formatted-string-literals) covers the grammar in full. The [Format String Syntax reference](https://docs.python.org/3/library/string.html#format-string-syntax) covers the format spec mini-language shared by both f-strings and `str.format()`.

## f-string Formatting in Python: From Simple to Production-Ready

### Step 1: Basic substitution

Any Python expression works inside `{}` — variable reference, attribute access, method call, arithmetic. The expression is evaluated at the point the string is created:

```python
order_id = 4231
user_email = "chen@example.com"
total = 49.99

message = f"Order {order_id} for {user_email}: ${total}"
print(message)  # "Order 4231 for chen@example.com: $49.99"
```

### Step 2: Format specifiers

The colon (`:`) inside `{}` starts a format specifier that controls precision, padding, and number formatting:

```python
processing_time = 0.004320000000000001
total = 49.999999999999996
count = 1_234_567
label, value = "Status", "active"
price = 1_249_999.50

print(f"Time: {processing_time:.4f}s")   # "Time: 0.0043s"
print(f"Total: ${total:.2f}")            # "Total: $50.00"
print(f"Records: {count:,}")             # "Records: 1,234,567"
print(f"{label:<12}{value:>10}")         # "Status           active"
print(f"${price:,.2f}")                  # "$1,249,999.50"
```

The spec follows `[fill][align][sign][width][grouping][.precision][type]`. For most cases, `:.2f` and `:,` are sufficient.

### Step 3: Python string formatting float specifiers

The type code at the end of a specifier selects the representation:

```python
pi = 3.141592653589793

print(f"{pi:.2f}")   # "3.14" — fixed decimal places
print(f"{pi:.4f}")   # "3.1416" — four decimal places
print(f"{pi:.2e}")   # "3.14e+00" — scientific notation
print(f"{pi:.2g}")   # "3.1" — general (strips trailing zeros)
print(f"{pi:.0%}")   # "314%" — percentage
```

One subtlety: Python uses banker's rounding (round half to even), not the "always round half up" rule:

```python
print(f"{2.5:.0f}")   # "2", not "3"
print(f"{3.5:.0f}")   # "4"
```

For currency or financial contexts where 0.5 must always round up, use the `decimal` module with `ROUND_HALF_UP` — the float representation itself is approximate, and the format specifier can't fix that.

### Step 4: Realistic log formatter

Adjacent string literals join at compile time, letting you split a long f-string across lines without backslash continuation:

```python
from datetime import datetime

def format_order_log(order_id: int, user_email: str, total: float, duration_s: float) -> str:
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"[{ts}] order={order_id} "
        f"user={user_email} "
        f"total=${total:.2f} "
        f"duration={duration_s:.3f}s"
    )

print(format_order_log(4231, "chen@example.com", 49.99, 0.004320))
```

Output: `[2026-05-30T12:00:00Z] order=4231 user=chen@example.com total=$49.99 duration=0.004s`

This pattern appears throughout Django's ORM logging and Celery task runners — long format strings split across lines, each segment an f-string where it contains expressions.

## str.format() and %-Style: Where They Still Appear

f-strings require Python 3.6+ and evaluate immediately in place. Two situations call for the older methods.

**Templates stored outside source code.** If the format string comes from a database, config file, or translation catalog, it cannot be an f-string — f-strings need the expression at definition time. `str.format()` handles this correctly because the template is data, not code:

```python
ALERT_TEMPLATE = "Alert: {level} in module {module} at line {line}"

def make_alert(level: str, module: str, line: int) -> str:
    return ALERT_TEMPLATE.format(level=level, module=module, line=line)

print(make_alert("WARNING", "payments", 87))
```

Output: `Alert: WARNING in module payments at line 87`

The template string can come from a YAML config, a database column, or a translation lookup. You call `.format()` after retrieval — something an f-string fundamentally cannot do.

**Logging calls.** The `logging` module uses `%`-style placeholders internally and delays substitution until it confirms the message will be emitted. The `%d` version skips string construction entirely if the log level is filtered out:

```python
import logging

logging.warning("Failed to process order %d after %d retries", order_id, retry_count)
```

Compare to the f-string version, which always evaluates:

```python
logging.warning(f"Failed to process order {order_id} after {retry_count} retries")
```

The f-string constructs the full string on every call, even when `WARNING` is suppressed. In high-throughput services with `DEBUG` and `INFO` disabled, this overhead compounds.

## Traps That Catch Developers Off-Guard

**Trap 1: Backslashes inside f-string expressions (pre-3.12)**

Before Python 3.12, the parser rejects backslashes inside f-string `{}` expressions. The workaround is to assign the escape string to a variable first:

```python
names = ["Alice", "Bob", "Charlie"]

separator = "\n"
print(f"Names:\n{separator.join(names)}")
```

Python 3.12 lifted this restriction — backslashes are now valid inside f-string expressions, so `f"{'\\n'.join(names)}"` works directly on 3.12+.

**Trap 2: Quote conflicts inside `{}`**

On Python versions below 3.12, you cannot use the same quote type inside an f-string expression as the f-string delimiter itself:

```python
data = {"status": "active"}

print(f"Status: {data['status']}")   # outer double, inner single — works on all versions

key = "status"
print(f"Status: {data[key]}")        # variable lookup avoids the issue entirely
```

Python 3.12+ supports proper quote nesting, so `f"Status: {data["status"]}"` is valid there. For code targeting earlier versions, use mismatched quote types or a helper variable.

**Trap 3: KeyError from external templates**

`str.format()` raises `KeyError` when a template references a placeholder not supplied as a keyword argument. This surfaces at runtime, not at import time:

```python
def build_report(count: int, template: str = "Found {count} results") -> str:
    try:
        return template.format(count=count)
    except KeyError as exc:
        raise ValueError(f"Template references unknown placeholder: {exc}") from exc

print(build_report(42))                                            # "Found 42 results"
print(build_report(42, "Found {count} results, total: {total}"))   # raises ValueError
```

Wrap external templates in try/except, or validate them against the expected placeholders before substitution. For broader [Python error handling](/languages/python/error-handling) patterns that cover runtime format errors, the error handling guide walks through the relevant exception hierarchy.

## When f-strings Are the Wrong Tool

**Logging calls.** Pre-format with an f-string and you remove the deferred substitution that makes `logging` efficient at scale. Pass the format string and arguments separately every time.

**SQL queries.** Injecting user input with an f-string hands control of the query structure to whoever supplies the value:

```python
user_id = request.args.get("id")

cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")    # SQL injection risk

cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))  # correct: parameterized
```

Parameterized queries send SQL and data separately; the database driver handles escaping. An f-string collapses them, making the query structure malleable from outside.

**Internationalization (i18n).** Translation libraries like `gettext` work with format strings stored in message catalogs. An f-string evaluates immediately — you cannot translate a string that has already been built:

```python
from gettext import gettext as _

template = _("Welcome, {username}!")
msg = template.format(username=username)
```

The template string is what the catalog looks up. You translate first, substitute second. f-strings make that order impossible.

## Frequently Asked Questions

### What is the difference between f-strings and str.format() in Python?

f-strings evaluate expressions inline at the point where the string is written — the expression is in the source code and runs when the interpreter reaches that line. `str.format()` takes a template string, which can be a variable or come from external storage, and fills placeholders at call time. For hardcoded strings in Python 3.6+, f-strings are shorter and faster. For templates that live outside source code — config files, databases, translation catalogs — `str.format()` is the correct choice because you can defer the substitution.

### How do you format a float to 2 decimal places in Python?

Use the `:.2f` format specifier: `f"{value:.2f}"` or `"{:.2f}".format(value)`. Both produce a string with exactly two decimal places using banker's rounding. For currency with a thousands separator: `f"${value:,.2f}"`. If you need "round half up" semantics — common in financial contexts — use `decimal.Decimal` with `ROUND_HALF_UP` rather than float arithmetic, since floats are inherently approximate.

### What does %s mean in Python string formatting?

`%s` is a conversion placeholder in the `%` operator formatting style. It converts the argument to a string using `str()`. `%d` expects an integer, `%f` a float. Multiple values: `"Order %d for %s" % (order_id, username)`. This style appears mainly in `logging` calls and legacy code — `str.format()` and f-strings replaced it for general use in Python 2.6 and 3.6 respectively.

### Can you use an if/else expression inside an f-string?

Yes — conditional expressions (ternary form) work inside `{}`:

```python
count = 5
print(f"Found {count} {'result' if count == 1 else 'results'}")  # "Found 5 results"
```

Full `if`/`elif`/`else` blocks are not allowed inside the braces. For complex logic, compute the value in a variable first, then reference that variable in the f-string.

### Why does f"{2.5:.0f}" print 2 instead of 3?

Python uses IEEE 754 banker's rounding (round half to even), not the "always round 0.5 up" rule. `2.5` rounded to 0 decimal places gives `2` (even), while `3.5` gives `4` (even). This matches the behavior of Python's built-in `round()` function. It's statistically unbiased over many operations — the standard in numeric computing — but surprises developers expecting "always round up."

## What to Read Next

The [Python String Methods Cheat Sheet](/cheatsheets/python-string-methods-cheatsheet) covers the full `str` method set — `split()`, `join()`, `replace()`, `strip()`, and the rest — giving you a fast reference for the operations you'll combine with string formatting day to day.

If your formatted strings end up written to disk, [Python file handling](/languages/python/file-handling) covers `open()` with context managers, encoding arguments, and writing text versus binary files. The `write()` call expects a string, so formatting and file I/O pair naturally.

For building a list of formatted strings programmatically — one formatted message per row in a collection — [Python list comprehensions](/languages/python/list-comprehension) covers the pattern you'll reach for most often: `[f"{item['id']}: {item['name']}" for item in records]`. Combining list comprehensions with format specifiers handles most data-to-display transformations cleanly.

String formatting in Python is stable across 3.6+, but the edge cases — logging optimization, SQL injection risk, i18n template ordering, and the 3.12 backslash and quote-nesting relaxations — repay a careful read before you're tracing a production bug at 2 a.m.
