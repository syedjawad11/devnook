---
title: "C# Collections: List, Dictionary, HashSet and Queue"
description: "Learn C# collections including dictionary in C#, List, HashSet, Queue, Stack and LINQ. Practical code examples and performance tips for every use case."
category: "languages"
language: "csharp"
concept: "collections"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [csharp, collections, dictionary, list, generics]
related_posts: []
related_tools: []
linkAnchors:
  - "dictionary in c#"
  - "c# collections"
  - "csharp dictionary"
published_date: "2026-06-28"
og_image: "/og/languages/csharp/collections.png"
word_count_target: 1940
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": [\n    \"TechArticle\",\n    \"FAQPage\"\n  ],\n  \"headline\": \"C# Collections: List, Dictionary, HashSet and Queue\",\n  \"description\": \"Learn C# collections including dictionary in C#, List, HashSet, Queue, Stack and LINQ. Practical code examples and performance tips for every use case.\",\n  \"datePublished\": \"2026-06-28\",\n  \"author\": {\n    \"@type\": \"Organization\",\n    \"name\": \"DevNook\"\n  },\n  \"publisher\": {\n    \"@type\": \"Organization\",\n    \"name\": \"DevNook\",\n    \"url\": \"https://devnook.dev\"\n  },\n  \"url\": \"https://devnook.dev/languages/csharp/collections/\",\n  \"mainEntity\": [\n    {\n      \"@type\": \"Question\",\n      \"name\": \"What is the difference between List and array in C#?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"A List<T> is dynamically resizable \\u2014 you can Add() and Remove() elements freely. An array has a fixed size set when it is created. List<T> provides methods like Sort(), IndexOf(), and FindAll(). For most application code, List<T> is the better default because it handles growth automatically.\"\n      }\n    },\n    {\n      \"@type\": \"Question\",\n      \"name\": \"How do I check if a key exists in a C# Dictionary?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"Use TryGetValue(): if (dict.TryGetValue(key, out var value)) { /* use value */ }. This checks existence and retrieves the value in one step, avoiding the KeyNotFoundException that dict[key] throws for missing keys. ContainsKey(key) works for a presence-only check.\"\n      }\n    },\n    {\n      \"@type\": \"Question\",\n      \"name\": \"When should I use HashSet instead of List in C#?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"Use HashSet<T> when you need unique elements and do not care about order or indexed access. Contains() on a HashSet runs in O(1) vs O(n) for List. HashSet also provides set operations \\u2014 UnionWith, IntersectWith, ExceptWith \\u2014 that List does not offer.\"\n      }\n    }\n  ]\n}\n</script>"
---
C# ships with five general-purpose generic collections, each designed for a different access pattern. Reaching for `List<T>` out of habit when a `HashSet<T>` or a dictionary in C# would do the job better is one of the most common sources of avoidable complexity in C# codebases. This guide walks through each collection type with runnable code, performance notes, and the mistakes that tend to catch developers off guard.

## What C# Collections Are (and Why Generics Matter)

C# arrays are fast but inflexible — the size is fixed at creation, and removing an element from the middle requires manual index juggling. The `System.Collections.Generic` namespace provides typed, resizable alternatives that handle growth and mutation without the bookkeeping.

Every generic collection implements `IEnumerable<T>`, which is what allows LINQ to work uniformly across all of them. Beyond that, more specific interfaces layer in additional capability: `ICollection<T>` adds `Count`, `Add`, and `Remove`; `IList<T>` adds indexed access via `this[int index]`; and `IDictionary<TKey, TValue>` adds the key-value contract.

The non-generic versions from `System.Collections` — `ArrayList`, `Hashtable`, `Queue`, `Stack` — still exist but require boxing for value types and provide no compile-time type safety. Unless you are maintaining legacy code that predates .NET 2.0, there is no reason to reach for them.

The five types worth learning in priority order: `List<T>`, `Dictionary<TKey, TValue>`, `HashSet<T>`, `Queue<T>`, and `Stack<T>`.

## List<T>: Ordered, Resizable, and Sequential

`List<T>` is backed by a dynamically resized array. When you add elements past the current capacity, the runtime allocates a new array roughly twice the size and copies everything over. This amortizes to O(1) per append, though you will occasionally see a short pause on resize with very large lists in tight loops.

```csharp
using System.Collections.Generic;

var cart = new List<string>();
cart.Add("laptop");
cart.Add("keyboard");
cart.Add("monitor");

cart.Remove("keyboard");    // O(n): scans and shifts remaining elements
cart.Sort();                // in-place sort

foreach (var item in cart)
    Console.WriteLine(item);
// laptop
// monitor
```

`Add` is O(1) amortized. `Remove(item)` scans linearly to find the element, then shifts everything after it — O(n). `RemoveAt(index)` is also O(n) because of the shift. If you need frequent removals from arbitrary positions, `LinkedList<T>` handles them in O(1), though its cache performance is worse for sequential reads.

The `Capacity` property exposes the internal array size. Pre-setting it with `new List<string>(expectedCount)` eliminates resizes when you know the final size upfront.

## Dictionary in C#: Key-Value Pairs with O(1) Lookups

A dictionary in C# maps unique keys to values using a hash table. Lookups, inserts, and deletes are O(1) on average — a significant advantage when you need to find items by identifier rather than position.

```csharp
var wordCount = new Dictionary<string, int>();

string[] words = { "apple", "banana", "apple", "cherry", "banana", "apple" };

foreach (var word in words)
{
    if (wordCount.TryGetValue(word, out int count))
        wordCount[word] = count + 1;
    else
        wordCount[word] = 1;
}

foreach (var entry in wordCount)
    Console.WriteLine($"{entry.Key}: {entry.Value}");
// apple: 3
// banana: 2
// cherry: 1
```

`TryGetValue` is the idiomatic way to read a value that might not exist. It returns `false` without throwing, and sets the `out` parameter to the found value if present. The alternative — `wordCount["bob"]` when `"bob"` is not a key — throws `KeyNotFoundException`. Experienced C# developers treat unguarded index access on a dictionary as a code smell outside of contexts where the key is guaranteed to exist.

The `Keys` and `Values` properties return collections you can iterate or convert to lists. The dictionary itself iterates as `KeyValuePair<TKey, TValue>` pairs. Enumeration order is not guaranteed and should never be relied upon.

You can find the full interface hierarchy and all collection types in the [Microsoft .NET collections documentation](https://learn.microsoft.com/en-us/dotnet/standard/collections/).

## HashSet<T>: When Uniqueness Matters More Than Order

`HashSet<T>` stores distinct elements with no ordering guarantee. Its `Contains()` check is O(1), compared to O(n) for `List<T>`. If you are using a list solely to track whether something has been seen before, swap it for a `HashSet<T>`.

```csharp
var activeUsers = new HashSet<string> { "alice", "bob", "charlie" };
var premiumUsers = new HashSet<string> { "bob", "diana", "charlie" };

// Keep only users who are both active and premium
activeUsers.IntersectWith(premiumUsers);
Console.WriteLine(string.Join(", ", activeUsers));
// bob, charlie
```

`HashSet<T>` provides proper set algebra: `UnionWith` (combine without duplicates), `IntersectWith` (common elements only), `ExceptWith` (elements in first but not second), and `IsSubsetOf`/`IsSupersetOf` for relationship checks. These are genuinely useful when working with access control lists, tag sets, feature flags, or any domain where membership and overlap matter.

One trade-off: `HashSet<T>` has no indexer. You cannot access elements by position. If you need both uniqueness and ordered access, `SortedSet<T>` maintains elements in sorted order while still guaranteeing uniqueness.

## Queue<T> and Stack<T>: Ordering by Access Pattern

These two collections encode specific access patterns that neither `List` nor `Dictionary` handles idiomatically.

`Queue<T>` is FIFO — the first item enqueued is the first dequeued. Background job systems, event processing loops, and breadth-first graph traversal all map naturally to a queue.

`Stack<T>` is LIFO — the last item pushed is the first popped. Undo/redo systems, expression parsers, and depth-first traversal use stacks.

```csharp
// Queue: processing jobs in submission order
var jobQueue = new Queue<string>();
jobQueue.Enqueue("resize-image");
jobQueue.Enqueue("send-email");
jobQueue.Enqueue("generate-report");

while (jobQueue.Count > 0)
{
    var job = jobQueue.Dequeue();
    Console.WriteLine($"Processing: {job}");
}
// Processing: resize-image
// Processing: send-email
// Processing: generate-report

// Stack: tracking undo operations
var undoStack = new Stack<string>();
undoStack.Push("draw circle");
undoStack.Push("fill blue");
undoStack.Push("resize 200px");

string lastAction = undoStack.Pop();
Console.WriteLine($"Undo: {lastAction}");
// Undo: resize 200px
```

Both types have `Peek()` to inspect the next item without removing it. For concurrent scenarios, `ConcurrentQueue<T>` and `ConcurrentStack<T>` from `System.Collections.Concurrent` are thread-safe equivalents.

The FIFO/LIFO distinction is a recurring concept across languages. Python developers use `collections.deque` for both patterns — the [Python data structures guide](/languages/python/data-structures/) covers deque, set, and stack in depth. Java developers will recognize the pattern from the [Java data structures guide](/languages/java/data-structures/) where `LinkedList` and `ArrayDeque` fill both roles. C++ takes the same approach with STL containers — [C++ STL containers](/languages/cpp/data-structures-stl/) covers `std::queue`, `std::stack`, and `std::unordered_map`.

## LINQ Queries Across C# Collections

LINQ works uniformly across any `IEnumerable<T>`, which means all five collection types support method-chain queries. Method syntax is generally cleaner than query syntax for filtering and projection.

```csharp
var products = new List<(string Name, decimal Price, string Category)>
{
    ("Laptop", 999.99m, "Electronics"),
    ("Phone", 699.99m, "Electronics"),
    ("Desk", 299.99m, "Furniture"),
    ("Chair", 199.99m, "Furniture"),
};

// Filter, sort, and project in one pipeline
var electronicNames = products
    .Where(p => p.Category == "Electronics")
    .OrderBy(p => p.Price)
    .Select(p => p.Name)
    .ToList();

Console.WriteLine(string.Join(", ", electronicNames));
// Phone, Laptop

// Convert any collection to a dictionary for fast lookup
var priceByName = products.ToDictionary(p => p.Name, p => p.Price);
```

`ToDictionary` is particularly useful for converting query results into a fast lookup structure. `GroupBy` creates an `IGrouping<TKey, TElement>` sequence — effectively a dictionary of lists. `ToLookup` creates a persistent grouped structure you can query multiple times efficiently without re-running the grouping.

LINQ queries are lazy by default: they do not execute until enumerated. Calling `ToList()`, `ToArray()`, or `ToDictionary()` materializes the result. Be careful if you iterate the source multiple times or if the source changes between iterations — you may get different results each time without realizing it.

The full LINQ method reference is in the [Microsoft LINQ documentation](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/). When inspecting collection data that gets serialized to JSON, the [JSON formatter tool](/tools/json-formatter/) is helpful for reading nested structures clearly.

## Common Mistakes with C# Collections

**Modifying a collection during `foreach`**

The enumerator tracks a version counter on the underlying collection. Any modification — `Add`, `Remove`, `Clear` — increments that counter, and the enumerator throws `InvalidOperationException` on the next iteration step.

```csharp
var items = new List<string> { "a", "b", "c" };

// Wrong: throws InvalidOperationException
foreach (var item in items)
{
    if (item == "b")
        items.Remove(item);
}

// Correct: iterate over a snapshot
foreach (var item in items.ToList())
{
    if (item == "b")
        items.Remove(item);
}
```

For simple cases, `items.RemoveAll(item => item == "b")` is the most direct fix — it handles removal in a single pass without an extra copy. For production code dealing with this exception, see how [C# exception handling](/languages/csharp/exception-handling/) helps structure proper error boundaries around collection operations.

**Direct Dictionary index access on possibly-absent keys**

```csharp
var scores = new Dictionary<string, int> { ["alice"] = 100 };

// Wrong: throws KeyNotFoundException when "bob" is absent
var bobScore = scores["bob"];

// Correct: TryGetValue returns false without throwing
if (scores.TryGetValue("bob", out int value))
    Console.WriteLine(value);
else
    Console.WriteLine("Player not found.");
```

**Ignoring thread safety**

`List<T>` and `Dictionary<TKey, TValue>` are not thread-safe. Concurrent reads are fine, but any concurrent write alongside a read causes data corruption with no exception to alert you. For shared state across threads — ASP.NET Core services, background workers — use `ConcurrentDictionary<TKey, TValue>` or synchronize with `lock`.

**Using `List<T>` for membership checks at scale**

`list.Contains(item)` is O(n). At 10 items the difference is invisible. At 100,000 items called thousands of times, it becomes the dominant cost. Switch to a `HashSet<T>` for membership tracking and keep the list only if ordering matters.

## Frequently Asked Questions

### What is the difference between List and array in C#?

A `List<T>` is dynamically resizable — you can `Add()` and `Remove()` elements freely, and the list grows as needed. An array has a fixed size set when it is created; to add elements, you need to allocate a new array and copy. `List<T>` provides methods like `Sort()`, `IndexOf()`, `FindAll()`, and `Contains()`. For most application code, `List<T>` is the better default. Arrays are preferable when size is fixed and you need the lowest possible memory overhead.

### How do I check if a key exists in a C# Dictionary?

Use `TryGetValue()`: `if (dict.TryGetValue(key, out var value)) { /* use value */ }`. This combines the existence check and value retrieval into one operation, avoiding the `KeyNotFoundException` that `dict[key]` throws for absent keys. If you only need the presence check without retrieving the value, `ContainsKey(key)` returns a bool. Both are O(1).

### When should I use HashSet instead of List in C#?

Use `HashSet<T>` when you need unique elements and do not need indexed access or a specific ordering. `Contains()` on a `HashSet<T>` runs in O(1) vs O(n) for `List<T>`. `HashSet<T>` also provides set operations — `UnionWith`, `IntersectWith`, `ExceptWith` — that have no equivalent on `List`. The trade-off is that you cannot retrieve elements by position.

## Conclusion

C# collections are not interchangeable defaults — each type solves a specific problem. A dictionary in C# gives you O(1) key-based lookups that a list cannot match. `HashSet<T>` enforces uniqueness and enables set algebra with one method call. `Queue<T>` and `Stack<T>` encode FIFO and LIFO semantics directly into the type, eliminating the index-management bugs that come from simulating those patterns with a list.

Start with `List<T>` and `Dictionary<TKey, TValue>` for general use. Reach for `HashSet<T>` when membership matters, and for `Queue<T>` or `Stack<T>` when access order is the defining constraint. When thread safety or immutability requirements enter the picture, `System.Collections.Concurrent` and `System.Collections.Immutable` extend the toolkit further.
