---
title: "Java String Formatting: String.format and printf Guide"
description: "Master java string formatting with String.format, printf, and formatted(). Format specifiers, padding, numbers, dates, and the traps to avoid."
category: "languages"
language: "java"
concept: "string-formatting"
difficulty: "intermediate"
template_id: "lang-v5"
tags: [java, string-formatting, string-format, printf, java-output]
related_posts: []
related_tools: []
linkAnchors:
  - "java string formatting"
  - "string formatting in java"
  - "java printf string formatting"
published_date: "2026-06-03"
og_image: "/og/languages/java/string-formatting.png"
word_count_target: 1900
---

String concatenation with `+` works fine for simple output. When you need consistent decimal places, padded columns in a report, or a date formatted the same way in five places, the operator falls apart fast. Java string formatting gives you a template-based approach — you write a format string with placeholders, pass values separately, and the runtime fills them in. The primary tools are `String.format()` for building a formatted string, and `System.out.printf()` for printing directly to the console.

## What Is String Formatting in Java

String formatting in Java is the process of building a string from a template and a set of values, where the template contains format specifiers that describe how each value should appear. Instead of writing:

```java
String line = "Order " + orderId + ": " + quantity + " items at $" + price + " each";
```

You write:

```java
String line = String.format("Order %d: %d items at $%.2f each", orderId, quantity, price);
```

The second form separates the structure of the string from the data. That separation makes the string easier to read, easier to localize, and easier to change when requirements shift.

Java has three main entry points for string formatting:

| Method | Returns | When to use |
|--------|---------|-------------|
| `String.format(template, args)` | a `String` | Anywhere you need a formatted string as a value |
| `System.out.printf(template, args)` | `void` | Printing directly to stdout |
| `String.formatted(args)` | a `String` | Java 15+; called on the template string itself |

All three use the same format specifier syntax, defined by the `java.util.Formatter` class.

## Format Specifiers: The Building Blocks

A format specifier starts with `%` and ends with a conversion character that tells Java what type of value to expect. The full pattern is:

```
%[argument_index$][flags][width][.precision]conversion
```

The only required parts are `%` and the conversion character. Everything else is optional. The most common conversions:

| Specifier | Type expected | Output example |
|-----------|--------------|---------------|
| `%s` | String (calls `toString()`) | `hello` |
| `%d` | Integer (int, long, Integer…) | `42` |
| `%f` | Floating-point | `3.140000` |
| `%e` | Scientific notation | `3.140000e+00` |
| `%b` | Boolean | `true` |
| `%c` | Character | `A` |
| `%n` | Platform newline | (newline) |
| `%t` | Date/time (requires a second character) | varies |

Use `%n` rather than `"\n"` inside format strings. On Windows, `%n` produces `\r\n`; on Unix it produces `\n`. Hardcoding `"\n"` can produce inconsistent line endings when your output crosses operating systems or is written to a file in text mode.

Flags and width modify how values are laid out:

- `%10d` — right-align an integer in a 10-character field
- `%-10d` — left-align in a 10-character field
- `%05d` — pad with zeros instead of spaces (`00042`)
- `%.2f` — two decimal places
- `%+.2f` — always show the sign (`+3.14` or `-3.14`)
- `%,d` — thousands separator (`1,000,000`)
- `%(f` — negative numbers in parentheses (`(3.14)` instead of `-3.14`)

The full syntax is documented in the [java.util.Formatter javadoc](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Formatter.html) — it covers every flag, every conversion, and edge cases around null handling and locale-sensitive output.

## Java String Formatting With String.format

Here is the simplest possible java string formatting call:

```java
String greeting = String.format("Hello, %s!", "Alice");
System.out.println(greeting);
// Hello, Alice!
```

`String.format()` returns the formatted string without printing it. You store it, log it, or pass it to another method — that's the key difference from `printf`.

Multiple arguments match the `%` specifiers left to right:

```java
String summary = String.format(
    "User %s placed order #%d totalling $%.2f",
    "alice@example.com", 1042, 87.5
);
System.out.println(summary);
// User alice@example.com placed order #1042 totalling $87.50
```

`%.2f` rounds `87.5` to `87.50` — the trailing zero is kept to satisfy the requested decimal count. That consistent output is the clearest illustration of why formatting beats concatenation for numeric display: no manual `Math.round()` or `DecimalFormat` plumbing required.

Java 15 added `String.formatted()` as an instance method on `String`, so you can write:

```java
String msg = "Order #%d total: $%.2f".formatted(1042, 87.5);
```

The result is identical to `String.format()`. The instance method form is slightly more readable when the template string is short and already in a variable.

## Java String Formatting With Variables: Numbers, Padding, and Dates

Formatting with variables pays off when columns need to align. Here is a simple inventory report:

```java
String header = String.format("%-20s %8s %10s%n", "Product", "Qty", "Price");
String row1   = String.format("%-20s %8d %10.2f%n", "Wireless Keyboard", 14, 49.99);
String row2   = String.format("%-20s %8d %10.2f%n", "USB Hub", 32, 19.50);
String row3   = String.format("%-20s %8d %10.2f%n", "Monitor Stand", 7, 89.00);

System.out.print(header + row1 + row2 + row3);
```

Output:
```
Product                  Qty      Price
Wireless Keyboard         14      49.99
USB Hub                   32      19.50
Monitor Stand              7      89.00
```

`%-20s` left-aligns the product name in a 20-character field. `%8d` right-aligns the quantity in 8 characters. `%10.2f` right-aligns the price with exactly two decimal places in a 10-character field. Change the width numbers and everything snaps into a different grid — no string-padding logic scattered through the code.

**Date formatting** uses the `%t` prefix with a second character specifying which date component to extract:

```java
import java.util.Date;

Date invoiceDate = new Date();
String formatted = String.format("Invoice date: %tB %<te, %<tY", invoiceDate);
System.out.println(formatted);
// Invoice date: June 3, 2026
```

`%tB` is the full month name, `%te` is the day of the month (no leading zero), `%tY` is the four-digit year. The `<` flag reuses the previous argument — all three reference `invoiceDate` without repeating it in the argument list.

For more complex date patterns — locale-aware month names, ISO 8601 output, timezone handling — combine `java.time.LocalDate` or `ZonedDateTime` with `DateTimeFormatter`. Use `String.format` for the surrounding text and `DateTimeFormatter.format()` for the date portion.

## Using printf for Direct Console Output

When you're printing to the console and don't need the result as a string, `System.out.printf()` skips the intermediate variable:

```java
double taxRate = 0.21;
double subtotal = 342.75;
double tax = subtotal * taxRate;

System.out.printf("Subtotal: $%,.2f%n", subtotal);
System.out.printf("Tax (%.0f%%): $%,.2f%n", taxRate * 100, tax);
System.out.printf("Total:    $%,.2f%n", subtotal + tax);
```

Output:
```
Subtotal: $342.75
Tax (21%): $71.98
Total:    $414.73
```

Two details worth noting: `%,` adds the locale-default thousands separator, and `%%` is the escape sequence for a literal percent sign. A bare `%` with no following conversion character throws `MissingFormatArgumentException` at runtime. See the [String.format() API documentation](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html#format(java.lang.String,java.lang.Object...)) for the complete list of conversion characters and valid escape sequences.

`System.err.printf()` follows the same signature and writes to stderr — useful for formatting error output separately from normal output without mixing streams.

## Three Bugs You Will Write First

**Trap 1: Wrong argument count.**

```java
// Throws MissingFormatArgumentException at runtime
String bad = String.format("Value: %d and %d", 42);
```

Two `%d` specifiers, one argument. Java doesn't catch this at compile time — the exception surfaces at runtime, often in a call path that's difficult to trace. Always count specifiers against arguments when you write or modify a format string.

**Trap 2: Type mismatch.**

```java
// Throws IllegalFormatConversionException
String bad = String.format("%d", 3.14);
```

`%d` expects an integer type (`int`, `long`, `Integer`, `Long`). Passing a `double` or `float` throws `IllegalFormatConversionException`. The conversion characters are strict: use `%d` for integer types, `%f` or `%e` for floating-point, and `%s` when you need `toString()` fallback for any object.

**Trap 3: Locale-sensitive decimal separators.**

```java
System.out.printf("Price: %.2f%n", 1234.56);
// Prints "Price: 1234,56" on a German-locale JVM
```

`%f` uses the JVM's default locale for the decimal separator. On a German-locale machine, the separator is `,` rather than `.`. When consistent output matters — log files, machine-readable reports, CSV exports — pass a `Locale` explicitly:

```java
String price = String.format(Locale.US, "Price: %.2f", 1234.56);
// Always prints "Price: 1234.56" regardless of system locale
```

`Locale.US` fixes the decimal separator at `.` and the thousands separator at `,` across all platforms.

## When String.format Is the Wrong Tool

**Inside a logging framework.** Don't construct the message eagerly:

```java
// Avoid: builds the string even when INFO is suppressed
logger.info(String.format("Processing order %d for user %s", orderId, userId));
```

SLF4J and Log4j 2 both accept parameterized messages that are only interpolated when the log level is active:

```java
logger.info("Processing order {} for user {}", orderId, userId);
```

This avoids creating a `String` object on every call when the log level means the message won't be printed — relevant in high-throughput services where `logger.debug(...)` calls sit in hot paths.

**Building large strings in a loop.** Calling `String.format()` on each iteration and concatenating results creates a new object per iteration. Use a `StringBuilder` with `append()` calls, or `String.join()` if the pieces are already in a list.

**Single-variable substitution with no formatting.** `"Hello, " + userName + "!"` is clearer than `String.format("Hello, %s!", userName)` when there's only one substitution and no width, alignment, or numeric precision involved. The format overhead adds nothing.

## How Java Compares to Python, C, and JavaScript

Java's `%s`/`%d`/`%f` syntax is directly inherited from C's `printf`. The two are nearly interchangeable:

**C:**
```c
printf("Order %d: $%.2f\n", order_id, total);
```

**Java:**
```java
System.out.printf("Order %d: $%.2f%n", orderId, total);
```

The only surface difference is `%n` versus `\n`. If you know C's printf, Java's printf is immediately readable.

**Python** moved from `%`-style formatting to two newer options — f-strings (Python 3.6+) and the `.format()` method:

```python
line = f"Order {order_id}: ${total:.2f}"           # f-string
line = "Order {}: ${:.2f}".format(order_id, total) # .format()
```

Python's f-strings embed expressions directly in the template. Java's `String.format()` keeps arguments separate — which is easier to scan when templates are long or when the same template string is reused with different argument sets.

**JavaScript** uses template literals with a similar inline approach:

```javascript
const line = `Order ${orderId}: $${total.toFixed(2)}`;
```

Java 21 added text blocks for multiline strings but doesn't support inline expression interpolation like `${variable}`. String formatting in Java stays explicitly template-plus-arguments — you can't put a `toFixed(2)` call inside the format string itself.

For a broader look at how Java approaches familiar problems compared to other languages, [sorting algorithms explained across Python, JavaScript, Go, and Java](/blog/sorting-algorithms-comparison/) shows the same comparative pattern for another core topic.

## Frequently Asked Questions

### What is the difference between String.format and printf in Java?

`String.format()` returns a formatted `String` you can store, pass to another method, or log. `System.out.printf()` prints directly to standard output and returns nothing — it's equivalent to `System.out.print(String.format(...))`. Both use identical format specifier syntax. Reach for `String.format()` when the result needs to be a value; reach for `printf` when printing to the console is the only goal and you don't need the string afterward.

### How do I format a string in Java with variables?

Pass each variable as an argument after the format template, in the same left-to-right order as the `%` specifiers:

```java
String productName = "Widget";
int stockCount = 250;
double unitPrice = 4.99;

String report = String.format(
    "%-15s | %5d units | $%.2f each",
    productName, stockCount, unitPrice
);
// Widget          |   250 units | $4.99 each
```

The specifier type must match the variable type. `%s` for strings and objects, `%d` for integers, `%f` for floats. Mismatches throw `IllegalFormatConversionException` at runtime.

### What does %n mean in Java string formatting?

`%n` is a platform-appropriate newline. On Windows it produces `\r\n`; on macOS and Linux it produces `\n`. Using `%n` keeps format strings portable across operating systems. When you write formatted output to a [Java file with BufferedWriter](/languages/java/file-handling/), `%n` produces the correct line ending for the target platform automatically, without you having to detect the OS or hardcode `System.lineSeparator()`.

### Can I use String.format to build JSON output?

You can, but it's the wrong tool. `String.format` has no awareness of JSON structure — it won't escape quotes within string values, handle null correctly, or validate nesting depth. For [JSON handling in Java](/languages/java/json-parse/), use Jackson or Gson. Those libraries serialize objects safely and handle all the escaping rules. Reserve `String.format` for human-readable output: log lines, console reports, and display strings.

### Why does String.format output different decimal separators on different machines?

`%f` is locale-sensitive by default. On a JVM running with a European locale, the decimal separator is `,` rather than `.`. The fix is to pass a `Locale` explicitly:

```java
// Locale-sensitive — unsafe for machine-readable output
String a = String.format("%.2f", 1234.56);       // "1234,56" on DE locale

// Explicit locale — always consistent
String b = String.format(Locale.US, "%.2f", 1234.56); // always "1234.56"
```

Use `Locale.US` for any output that will be parsed by another system, written to a file, or compared across environments.

## What to Learn Next

String formatting handles how data looks on its way out. The next useful step is how it comes in: [JSON parsing in Java](/languages/java/json-parse/) covers Jackson's `ObjectMapper`, which is the standard way to deserialize API responses into Java objects that you then format for display or logs.

If you're building HTTP services, [Java REST APIs](/languages/java/rest-api/) shows how response bodies are constructed and where string formatting fits into the output pipeline. For writing formatted output directly to disk, [Java file I/O](/languages/java/file-handling/) covers `BufferedWriter` and `PrintWriter` — including when each is the better fit for formatted text files.

When your format strings involve patterns you want to test before committing — date patterns, order ID formats, postal codes — the [Java Regex Tester](/tools/regex-tester/) lets you verify patterns against sample data interactively.

Java string formatting with `String.format` and `printf` covers the majority of output needs. Knowing the format specifier syntax, the locale trap, and when a logging framework or `StringBuilder` serves better puts you past the rough edges that trip up developers new to the API.
