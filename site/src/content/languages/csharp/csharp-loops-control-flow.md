---
title: "C# switch and Loops: for, foreach, while Explained"
description: "C# switch statements, for, foreach, and while loops give you precise control over program flow. Master every construct with practical examples."
category: "languages"
language: "csharp"
concept: "loops-control-flow"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [csharp, switch, loops, control-flow, pattern-matching]
related_posts: []
related_tools: []
linkAnchors:
  - "c# switch"
  - "c# loops"
  - "control flow"
published_date: "2026-06-29"
og_image: "/og/languages/csharp/loops-control-flow.png"
word_count_target: 1931
schema_org: "<script type=\"application/ld+json\">{\"@context\":\"https://schema.org\",\"@type\":[\"TechArticle\",\"FAQPage\"],\"headline\":\"C# switch and Loops: for, foreach, while Explained\",\"description\":\"C# switch statements, for, foreach, and while loops give you precise control over program flow. Master every construct with practical examples.\",\"datePublished\":\"2026-06-29\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/languages/csharp/loops-control-flow/\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"What is the difference between for and foreach in C#?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"A for loop gives you an index counter and explicit control over start, stop, and step. A foreach loop iterates over any IEnumerable without needing an index, simpler and safer for reading collections. Use for when you need the index; use foreach for straightforward traversal.\"}},{\"@type\":\"Question\",\"name\":\"What is the C# switch expression introduced in C# 8?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"The switch expression returns a value directly using arrow syntax and integrates with pattern matching. It is the preferred form in modern C# code.\"}},{\"@type\":\"Question\",\"name\":\"How does pattern matching work in C# switch?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"C# switch supports type patterns, relational patterns, property patterns, and tuple patterns. Patterns are evaluated top to bottom; the _ discard serves as the default arm.\"}}]}</script>"
---
Control flow is the skeleton of every C# program. Two mechanisms dominate: loops, which repeat a block of code, and branching statements, which route execution based on a condition. C# gives you four loop constructs — `for`, `foreach`, `while`, and `do-while` — and two forms for multi-case branching: the classic `c# switch` statement and the modern `switch` expression introduced in C# 8. This guide walks through all of them with runnable examples, from basic syntax to pattern matching.

## C# switch Statement: Syntax, Cases, and Default

The `switch` statement matches a value against a list of case labels and executes the matching block. Unlike C or Java, C# requires an explicit `break`, `return`, or `throw` at the end of each non-empty case — preventing the accidental fall-through bug that plagues older C-style switch implementations.

```csharp
string role = "admin";

switch (role)
{
    case "admin":
        Console.WriteLine("Full access granted");
        break;
    case "editor":
        Console.WriteLine("Edit access granted");
        break;
    case "viewer":
        Console.WriteLine("Read-only access");
        break;
    default:
        Console.WriteLine("Unknown role — access denied");
        break;
}
```

The `default` label catches anything that does not match a defined case. It is optional, but including it prevents silent failures when new values appear later.

Empty cases stack naturally in C#. A case with no body falls through to the next case automatically:

```csharp
switch (statusCode)
{
    case 200:
    case 201:
    case 204:
        Console.WriteLine("Success");
        break;
    case 400:
        Console.WriteLine("Bad request");
        break;
    case 404:
        Console.WriteLine("Not found");
        break;
    default:
        Console.WriteLine("Unexpected status");
        break;
}
```

Stacking 200, 201, and 204 under one handler is idiomatic C# for grouping equivalent values. Before C# 7, the `switch` statement matched only `int`, `long`, `char`, `string`, and `enum` types. Pattern matching (introduced in C# 7) removed that restriction.

## C# switch Expressions (C# 8+)

C# 8 introduced the `switch` expression — a compact, value-returning alternative to the switch statement. Instead of case labels and `break`, you write a comma-separated list of arms using `=>` arrow syntax.

```csharp
int statusCode = 404;

string message = statusCode switch
{
    200 => "OK",
    201 => "Created",
    204 => "No Content",
    400 => "Bad Request",
    404 => "Not Found",
    500 => "Internal Server Error",
    _   => "Unknown Status"
};

Console.WriteLine(message);
```

The `_` discard serves as the default arm. If no arm matches and no discard is present, the runtime throws `SwitchExpressionException`. Because the switch expression is an expression — not a statement — it fits anywhere a value is expected: in variable assignments, `return` statements, and method arguments.

```csharp
return orderStatus switch
{
    "pending"   => ProcessOrder(order),
    "shipped"   => TrackShipment(order),
    "cancelled" => RefundOrder(order),
    _           => throw new InvalidOperationException($"Unknown status: {orderStatus}")
};
```

Throwing inside a switch expression arm is valid and is the standard way to surface unhandled cases at runtime rather than silently returning null. The [Microsoft documentation on C# selection statements](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/selection-statements) covers the full switch statement specification, including `when` guard clauses for additional filtering within a case.

## Pattern Matching in C# switch

Pattern matching turns the `switch` into a dispatch tool for structured data, not just primitive values. C# 7 added type patterns; C# 9 added relational patterns; C# 10 added property patterns and logical combinators (`and`, `or`, `not`).

**Type pattern** — match by runtime type:

```csharp
object shape = GetShape();

string description = shape switch
{
    Circle c    => $"Circle with radius {c.Radius}",
    Rectangle r => $"Rectangle {r.Width}x{r.Height}",
    Triangle t  => $"Triangle with base {t.Base}",
    _           => "Unknown shape"
};
```

**Relational pattern** (C# 9) — match by value range:

```csharp
double score = 87.5;

string grade = score switch
{
    >= 90 => "A",
    >= 80 => "B",
    >= 70 => "C",
    >= 60 => "D",
    _     => "F"
};
```

**Property pattern** — match on object properties:

```csharp
var discount = customer switch
{
    { Tier: "Gold", OrderCount: > 10 } => 0.20,
    { Tier: "Silver" }                  => 0.10,
    { IsNewCustomer: true }             => 0.05,
    _                                   => 0.0
};
```

Property patterns remove long `if`-`else if` chains when branching on object state. The [Microsoft documentation on C# patterns](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/patterns) covers all pattern types including list patterns (C# 11) and slice patterns. For testing string-based patterns interactively before embedding them in code, the DevNook [regex tester](/tools/regex-tester/) is a useful companion — though C# type and property patterns operate at the compiler level, not the regex engine level.

## for Loop in C#

The `for` loop is the right choice when you know the number of iterations in advance, or when you need the index to access or modify elements by position.

```csharp
int[] temperatures = { 22, 18, 25, 30, 17 };

for (int i = 0; i < temperatures.Length; i++)
{
    Console.WriteLine($"Day {i + 1}: {temperatures[i]}°C");
}
```

The loop header has three parts: initializer (`int i = 0`), condition (`i < temperatures.Length`), and iterator (`i++`). All three are optional — `for (;;)` loops forever until an explicit `break`.

Iterate backwards by reversing the initializer and condition:

```csharp
for (int i = temperatures.Length - 1; i >= 0; i--)
{
    Console.WriteLine($"Day {i + 1}: {temperatures[i]}°C (reversed)");
}
```

Use `for` over `foreach` when you need the index for random access, when you modify the array in place, or when you want to step by more than one element at a time (`i += 2`). The official [C# iteration statements reference](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/iteration-statements) documents all loop forms with their full grammar and edge cases.

## foreach Loop in C#

The `foreach` loop iterates over any type implementing `IEnumerable` or `IEnumerable<T>` — arrays, `List<T>`, `Dictionary<TKey,TValue>`, LINQ results, and more. It is the idiomatic C# choice for read-only collection traversal.

```csharp
var products = new List<string> { "Keyboard", "Monitor", "Mouse" };

foreach (string product in products)
{
    Console.WriteLine($"Product: {product}");
}
```

Because `foreach` hides the index, it eliminates off-by-one errors at the cost of positional access. It also works on LINQ query results, file line enumerators, and any custom `IEnumerable<T>` implementation you write.

When working with [C# Collections: List, Dictionary, HashSet, Queue](/languages/csharp/collections/), `foreach` is almost always the right choice for traversal. Switch to a `for` loop only when you need to track position, remove items, or read two elements at once.

**Iterating a dictionary with deconstruction:**

```csharp
var config = new Dictionary<string, string>
{
    { "host", "localhost" },
    { "port", "5432" },
    { "database", "orders" }
};

foreach (var (key, value) in config)
{
    Console.WriteLine($"{key} = {value}");
}
```

Deconstruction syntax (`var (key, value)`) unpacks `KeyValuePair<TKey, TValue>` directly into named variables, avoiding the verbose `.Key` and `.Value` property accesses.

## while and do-while Loops in C#

The `while` loop checks its condition before each iteration. Use it when the number of iterations is not known at the start — polling, retrying network calls, or reading from a stream.

```csharp
int retryCount = 0;
bool success = false;

while (!success && retryCount < 3)
{
    success = TryConnectToDatabase();
    retryCount++;
    if (!success) Thread.Sleep(1000);
}

Console.WriteLine(success ? "Connected" : "Failed after 3 retries");
```

The `do-while` loop executes the body at least once, then checks the condition. Use it when the loop body must run before the condition is meaningful — for example, prompting for input until valid data arrives.

```csharp
string? input;
do
{
    Console.Write("Enter a number greater than 0: ");
    input = Console.ReadLine();
} while (!int.TryParse(input, out int n) || n <= 0);

Console.WriteLine($"You entered: {n}");
```

The distinction between `while` and `do-while` matters when the initial state of the condition is unpredictable or when the first iteration initialises the data you then test against.

## Loop Control: break, continue, and goto

C# gives you three keywords to alter loop flow mid-iteration:

| Keyword | Effect |
|---------|--------|
| `break` | Exits the innermost loop or switch immediately |
| `continue` | Skips the remainder of the current iteration and moves to the next |
| `goto case` | Jumps to a different named case inside a `switch` statement |

```csharp
foreach (int number in Enumerable.Range(1, 20))
{
    if (number % 2 == 0) continue;   // skip even numbers
    if (number > 10) break;           // stop once past 10
    Console.Write($"{number} ");
}
// Output: 1 3 5 7 9
```

`goto case` enables explicit fall-through between named switch cases. It is one of the few justified uses of `goto` in modern C#:

```csharp
switch (command)
{
    case "quit":
    case "exit":
        goto case "shutdown";
    case "shutdown":
        Console.WriteLine("Shutting down...");
        break;
}
```

Avoid `goto` outside of switch fall-through — it creates control flow that is hard to reason about, debug, or test.

## Common Pitfalls

**Trap 1: Missing the `_` discard in switch expressions.**

A switch expression that does not match any arm throws `SwitchExpressionException` at runtime — not a compile error. Always include a `_` arm unless the compiler can verify exhaustiveness (for example, switching on a `bool` with both `true` and `false` cases covered).

**Trap 2: Modifying a collection during `foreach`.**

```csharp
// Throws InvalidOperationException: Collection was modified
foreach (var item in items)
{
    if (item.IsExpired) items.Remove(item);
}

// Fix: iterate a snapshot
foreach (var item in items.ToList())
{
    if (item.IsExpired) items.Remove(item);
}
```

Calling `.Remove()` or `.Add()` on a `List<T>` while iterating it throws at runtime. Either iterate a copy (`items.ToList()`) or use a `for` loop with backward index-based removal. For robust [exception handling in C#](/languages/csharp/exception-handling/), wrap these patterns appropriately.

**Trap 3: Off-by-one in `for` loop bounds.**

```csharp
// Wrong — silently skips the last element
for (int i = 0; i < items.Length - 1; i++) { ... }

// Correct
for (int i = 0; i < items.Length; i++) { ... }
```

Arrays are zero-indexed: valid indices run from 0 to `Length - 1`. Writing `i < items.Length - 1` silently skips the last element — a frequent bug when the length is also used elsewhere in arithmetic on the same line.

## Frequently Asked Questions

### What is the difference between `for` and `foreach` in C#?

`for` gives you an index counter and explicit control over start, stop, and step. `foreach` iterates over any `IEnumerable<T>` without an index — simpler and less error-prone for collection traversal. Use `for` when you need positional access; use `foreach` for clean, read-oriented iteration. Developers coming from [Java loops and control flow](/languages/java/loops-control-flow/) will find C#'s `foreach` semantically similar to Java's enhanced `for` loop.

### What is the C# switch expression introduced in C# 8?

The `switch` expression returns a value directly using `=>` arrow syntax — it is an expression, not a statement. The traditional `switch` statement uses `case` labels and `break`. The expression form is more compact, composes cleanly in return statements and assignments, and is the preferred form in modern C#. Both forms support pattern matching.

### How does pattern matching work in C# switch?

C# switch supports type patterns (`Circle c`), relational patterns (`>= 90`), property patterns (`{ Tier: "Gold" }`), and tuple patterns. All work inside both switch expressions and switch statements. Patterns are evaluated top to bottom; the first matching arm executes. Include a `_` discard arm to handle unmatched values.

### Can I use `switch` on strings in C#?

Yes. Unlike C and C++, C# switch works natively on `string` values. Matching is case-sensitive by default. For case-insensitive matching, apply `.ToLowerInvariant()` to the switched value, or use an `if`-`else` chain with `string.Equals(..., StringComparison.OrdinalIgnoreCase)`.

## Conclusion

C# loops and the `c# switch` statement and expression cover the full range of control flow needs. Reach for `for` when you need an index, `foreach` for clean collection traversal, `while` for condition-driven repetition, and `do-while` when the body must run at least once. For multi-case branching, prefer the `switch` expression in modern C# — it is concise, composable, and forces you to handle all cases explicitly with a `_` discard arm. Once control flow is solid, the natural next step is [C# Collections: List, Dictionary, HashSet, Queue](/languages/csharp/collections/), since loops and switch expressions are most useful when operating over the structured data that collections provide.
