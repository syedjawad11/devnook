---
title: "Java String Methods: substring, split, contains, indexOf"
description: "Master java substring, split, contains, and indexOf with working examples. Learn the exact syntax, edge cases, and when each method fits your code."
category: languages
language: java
concept: string-methods
difficulty: intermediate
template_id: lang-v2
tags: [java, string-methods, substring, split, contains]
related_posts: []
related_tools: []
linkAnchors:
  - "java substring"
  - "java string methods"
  - "java split string"
published_date: "2026-06-22"
og_image: "/og/languages/java/string-methods.png"
word_count_target: 1736
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "Java String Methods: substring, split, contains, indexOf",
    "description": "Master java substring, split, contains, and indexOf with working examples. Learn the exact syntax, edge cases, and when each method fits your code.",
    "datePublished": "2026-06-22",
    "programmingLanguage": "java",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/java/string-methods/",
    "mainEntity": [
      {"@type": "Question", "name": "What is the difference between substring(int) and substring(int, int) in Java?", "acceptedAnswer": {"@type": "Answer", "text": "substring(beginIndex) returns everything from that index to the end of the string. substring(beginIndex, endIndex) returns characters from beginIndex up to but not including endIndex. Both throw StringIndexOutOfBoundsException if any index is out of range."}},
      {"@type": "Question", "name": "Why does Java indexOf() return -1?", "acceptedAnswer": {"@type": "Answer", "text": "indexOf() returns -1 as a sentinel value meaning the substring or character was not found. Always check the return value before using it as an index — passing -1 to substring() throws StringIndexOutOfBoundsException."}},
      {"@type": "Question", "name": "When should I use contains() vs indexOf() in Java?", "acceptedAnswer": {"@type": "Answer", "text": "Use contains() when you only need a yes-or-no answer about whether a substring exists. Use indexOf() when you need the position, want to search from a specific offset using fromIndex, or want to find the last occurrence with lastIndexOf()."}}
    ]
  }
  </script>
---

Java strings arrive with a focused set of built-in methods that handle most text-processing tasks without importing anything. Four of them — `substring`, `split`, `contains`, and `indexOf` — cover extraction, splitting, and searching. Knowing how each one behaves, including where the edges are, separates clean code from a debugging session that takes longer than it should.

## Java substring: Extracting Part of a String

The java substring method comes in two forms. Which one you need depends on whether you know the endpoint.

```java
String greeting = "Hello, World!";
String fromSeven = greeting.substring(7);       // "World!"
String helloOnly = greeting.substring(0, 5);    // "Hello"
```

`substring(beginIndex)` returns every character from `beginIndex` to the end of the string. `substring(beginIndex, endIndex)` returns characters starting at `beginIndex` up to but **not including** the character at `endIndex`.

Both forms use zero-based indexing: in `"Hello"`, `H` is at index 0, `e` at index 1, and so on. The two-argument form's `endIndex` equals the number of characters you want counted from the start of the string — to get `"Hello"` (5 characters), `endIndex` is 5, not 4.

If `beginIndex` equals `endIndex`, you get an empty string. If `beginIndex` is greater than `endIndex`, or either index falls outside the string bounds, Java throws `StringIndexOutOfBoundsException`. Java does not silently clamp indices the way some other languages do, so the bounds check falls on you.

Combining `substring` with `length()` handles cases where you need to trim a known suffix:

```java
String filename = "invoice_2026.pdf";
// Remove the last 4 characters (".pdf")
String baseName = filename.substring(0, filename.length() - 4);  // "invoice_2026"
```

The `length() - 4` pattern comes up often for file extensions, suffixes, and protocol prefixes. The formula for "everything except the last N characters" is always `substring(0, s.length() - N)`.

The [Java 21 String API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html) documents all 50+ methods on `String`, including Unicode-aware behaviour for supplementary characters that sit outside the basic multilingual plane.

## split(): Turning a String into an Array

`split` takes a **regular expression** and returns a `String[]`. The regex part is what most developers trip over first.

```java
String csv = "alice,bob,charlie";
String[] names = csv.split(",");
// names[0] = "alice", names[1] = "bob", names[2] = "charlie"
```

A simple comma delimiter works as expected. Now try a dot:

```java
String version = "2.10.4";
String[] parts = version.split(".");   // Returns []
```

That returns an empty array because `.` in regex means "any character." Splitting `"2.10.4"` on "any character" produces only empty segments between adjacent matches, and Java discards them, leaving nothing. To split on a literal dot, escape it:

```java
String[] vParts = version.split("\\.");  // ["2", "10", "4"]
```

The same problem affects `|`, `(`, `)`, `[`, `]`, `{`, `}`, `*`, `+`, and `?`. Use a [regex tester](/tools/regex-tester/) to verify any pattern before hardcoding it. For arbitrary delimiters you do not control at write-time, `Pattern.quote(delimiter)` escapes them safely without you needing to remember which characters are special.

The two-argument form of `split` gives you a ceiling on the number of pieces:

```java
String path = "usr:local:bin:node";
String[] twoMax = path.split(":", 2);
// twoMax = ["usr", "local:bin:node"]
```

A positive second argument creates at most that many tokens and puts the remainder unsplit in the last element. Passing `-1` as the limit preserves trailing empty strings that the default form discards — useful when you are parsing fixed-column formats where a missing trailing field still needs a slot in the array.

## contains() and indexOf(): Checking and Finding Substrings

These two methods answer different questions. `contains` answers "is it there?" and `indexOf` answers "where is it?"

```java
String header = "Content-Type: application/json";
boolean hasJson = header.contains("json");     // true
boolean hasXml  = header.contains("xml");      // false
```

`contains` takes a `CharSequence`, which means you can pass a `String`, `StringBuilder`, or `StringBuffer`. It returns `true` immediately on the first match and scans left to right like most string search methods.

When you need the actual position, `indexOf` is the right call. It returns the zero-based index of the first occurrence, or `-1` if the substring is not present:

```java
String log = "ERROR: connection timeout at server-a";
int errorAt  = log.indexOf("ERROR");       // 0
int serverAt = log.indexOf("server");      // 29
int warnAt   = log.indexOf("WARN");        // -1
```

Always check the return value before using it as an index into the string:

```java
int colonPos = log.indexOf(":");
if (colonPos != -1) {
    String detail = log.substring(colonPos + 2);  // "connection timeout at server-a"
    System.out.println(detail);
}
```

`indexOf` also accepts a `fromIndex` argument to start the search from a specific position, which is how you find the second or third occurrence of a pattern:

```java
String text = "cat sat on cat mat";
int first  = text.indexOf("cat");        // 0
int second = text.indexOf("cat", 1);     // 11
```

`lastIndexOf` works the same way but scans from the right end, which is useful when you need the last separator in a path or the final occurrence of a delimiter.

## A Realistic Example: Parsing a Log Entry

Log lines pull all four methods into a natural workflow. Given a line like:

```
2026-06-22T10:30:00Z ERROR /api/orders/99 timeout
```

You might want to confirm it is an error, extract the path, and pull the resource ID from the end of the path.

```java
String line = "2026-06-22T10:30:00Z ERROR /api/orders/99 timeout";

if (!line.contains("ERROR")) {
    return;   // Not an error line, skip it
}

String[] fields = line.split(" ");
String severity = fields[1];   // "ERROR"
String path     = fields[2];   // "/api/orders/99"

// Resource ID is the segment after the last "/"
int lastSlash   = path.lastIndexOf("/");
String resource = path.substring(lastSlash + 1);   // "99"

System.out.println(severity + " on resource: " + resource);
// ERROR on resource: 99
```

`contains` acts as a fast gate that avoids unnecessary work. `split` tokenises the line into fields. `lastIndexOf` locates the final path boundary. `substring` extracts the trailing segment. That four-method combination covers most log-parsing and simple text-extraction tasks you will encounter before reaching for a dedicated parsing library.

When the structure goes deeper — nested JSON from an API response, for instance — the [JSON parsing in Java guide](/languages/java/json-parse/) covers Jackson and Gson, which handle type conversion and nested access that raw string methods are not built for.

## Where These Methods Break

**Gotcha 1: substring's endIndex is exclusive**

The most common `substring` mistake is off-by-one. To extract `"Invoice"` (7 characters) from `"Invoice.pdf"`, use `substring(0, 7)` — not `substring(0, 8)`:

```java
String doc = "Invoice.pdf";
String name = doc.substring(0, 7);   // "Invoice"
String ext  = doc.substring(8);      // "pdf"
```

The `endIndex` marks the first character you do not want included. If you want a segment of length `n` starting at position `i`, the formula is always `substring(i, i + n)`. Memorising that formula eliminates most off-by-one errors.

**Gotcha 2: split() treats its argument as a regular expression**

Any regex metacharacter in your delimiter produces unexpected output. Splitting on a pipe `|` is a very common trap in TSV and log-format parsing:

```java
String row = "alice|30|engineer";
String[] wrong   = row.split("|");           // splits on every character boundary
String[] correct = row.split("\\|");         // ["alice", "30", "engineer"]
```

Use `Pattern.quote(delimiter)` to handle arbitrary delimiters safely, so you do not have to remember which specific characters need escaping.

**Gotcha 3: using the indexOf result without checking -1**

Passing an unchecked `indexOf` return value directly to `substring` throws `StringIndexOutOfBoundsException` when the substring is absent. The guard is one `if` check, but skipping it is easy when you are certain the pattern is always present — until production data proves otherwise:

```java
String input = "username=alice";
int eq = input.indexOf("=");

// Unsafe: if "=" is absent, substring(-1) throws
String valueUnsafe = input.substring(eq + 1);

// Safe
if (eq != -1) {
    String value = input.substring(eq + 1);  // "alice"
}
```

## Frequently Asked Questions

### What is the difference between substring(int) and substring(int, int) in Java?

`substring(beginIndex)` returns everything from `beginIndex` to the end of the string. `substring(beginIndex, endIndex)` returns characters starting at `beginIndex` up to but not including the character at `endIndex`. To get a segment of exactly `n` characters starting at position `i`, use `substring(i, i + n)`. Both forms throw `StringIndexOutOfBoundsException` if any index is negative or greater than the string's length — Java does not silently clamp out-of-range indices.

### Why does Java indexOf() return -1?

`indexOf` uses `-1` as its "not found" sentinel, which is consistent with `List.indexOf`, `Arrays.binarySearch`, and most Java search APIs. The value `-1` cannot be a valid character position, so it unambiguously signals absence. Always guard with `if (pos != -1)` before passing the result to `substring` or using it as an array index. Skipping that check is one of the more common sources of `StringIndexOutOfBoundsException` in Java code.

### When should I use contains() vs indexOf() in Java?

Use `contains` when the answer is strictly a yes or no — it reads more clearly in conditionals and signals intent without noise. Use `indexOf` when you need the actual character position, when you want to find a later occurrence by passing a `fromIndex`, or when you want to search backwards with `lastIndexOf`. For code that runs the same pattern search many thousands of times, precompile the query with `Pattern.compile` from the [java.util.regex package](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/regex/package-summary.html) to avoid recompiling the pattern on every call.

## Conclusion

The four java string methods covered here — `substring`, `split`, `contains`, and `indexOf` — handle the text-parsing patterns you will encounter in almost every Java project. Knowing that `endIndex` is exclusive, that `split` treats its argument as a regular expression, and that `indexOf` signals absence with `-1` prevents the most common traps from slowing you down.

Two directions are worth following from here. If you need to process collections of extracted strings — filtering lists, building maps from key-value pairs, counting occurrences — the [Java Data Structures guide](/languages/java/data-structures/) covers `ArrayList`, `HashMap`, and `LinkedList` with the patterns teams reach for in practice. When the goal shifts to building formatted output strings rather than parsing input, the [Java String Formatting guide](/languages/java/string-formatting/) covers `String.format` and the `printf`-style methods that complement these four. And when string operations run inside loops or conditionals, [Java Loops and Control Flow](/languages/java/loops-control-flow/) covers the iteration patterns that combine naturally with `split`, `indexOf`, and the rest of the `String` API.
