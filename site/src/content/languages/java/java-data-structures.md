---
title: "Java Queues, Lists, Maps, and Collections Explained"
description: "Java queues, lists, and maps explained with real code. Learn when to use ArrayList, PriorityQueue, HashMap, or TreeMap in your Java projects."
category: languages
language: java
concept: data-structures
difficulty: beginner
template_id: lang-v2
tags: [java, data-structures, collections, java-queues, java-maps]
related_posts: []
related_tools: []
published_date: "2026-06-14"
og_image: "/og/languages/java/data-structures.png"
word_count_target: 2500
actual_word_count: 2717
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "Java Queues, Lists, Maps, and Collections Explained",
    "description": "Java queues, lists, and maps explained with real code. Learn when to use ArrayList, PriorityQueue, HashMap, or TreeMap in your Java projects.",
    "datePublished": "2026-06-14",
    "programmingLanguage": "java",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/java/data-structures/",
    "mainEntity": [
      {"@type": "Question", "name": "What is the difference between Java Queue and Stack?", "acceptedAnswer": {"@type": "Answer", "text": "A Queue processes elements in FIFO order while a Stack uses LIFO. Use ArrayDeque for both in modern Java."}},
      {"@type": "Question", "name": "When should I use HashMap vs TreeMap in Java?", "acceptedAnswer": {"@type": "Answer", "text": "Use HashMap by default for O(1) get and put. Choose TreeMap when you need keys in sorted order or range operations."}},
      {"@type": "Question", "name": "Is ArrayList or LinkedList faster in Java?", "acceptedAnswer": {"@type": "Answer", "text": "ArrayList is faster for most workloads due to O(1) random access and better CPU cache locality from contiguous memory."}}
    ]
  }
  </script>
---

You're writing a background job processor and need to handle tasks in the order they arrive — but some tasks are urgent and must skip the line. You reach for `ArrayList`, add your tasks, then realize you need to re-sort the entire list every time a high-priority task comes in. Java queues solve this directly. But Java gives you dozens of collection types, and picking the wrong one costs you either correctness or performance.

This guide covers the core Java data structures — queues, lists, maps, and sets — with working code for each type and clear guidance on which to reach for in each situation.

## What Are Java Data Structures?

A data structure organizes data so you can store and retrieve it efficiently. Java's **Collections Framework**, introduced in Java 2 and significantly expanded in Java 5 and Java 8, provides ready-built implementations of the most common data structures. Every collection class lives under the `java.util` package and implements either the `Collection` or `Map` interface.

At the top level, Java organizes its collections into four families:

- **List** — ordered, allows duplicates, accessible by index
- **Queue / Deque** — ordered for processing; FIFO, LIFO, or priority-based
- **Set** — no duplicate elements allowed
- **Map** — stores key-value pairs; no duplicate keys

Each family has multiple implementations that trade off insertion speed, iteration order, and thread safety. The mistake most developers make early on is defaulting to `ArrayList` for everything — it works until the moment you need priority processing, deduplication, or fast key lookup.

Before Java 5, collections stored raw `Object` references and required casts everywhere. Generics changed that: today you write `List<String>` and the compiler catches type mismatches before the JVM can throw a `ClassCastException` at runtime.

The official [Java Collections Framework overview](https://docs.oracle.com/javase/tutorial/collections/intro/index.html) documents the full interface hierarchy for reference.

## Java Queues: PriorityQueue and Deque

A **queue** processes elements in a defined order. Java's `Queue` interface extends `Collection` and adds a second set of methods designed around processing semantics rather than pure storage.

The `Queue` interface provides two methods for each core operation — one that throws an exception on failure, and one that returns a sentinel value:

| Operation | Throws on failure | Returns null/false |
|-----------|------------------|--------------------|
| Insert | `add(e)` | `offer(e)` |
| Remove head | `remove()` | `poll()` |
| Inspect head | `element()` | `peek()` |

Prefer `offer()` and `poll()` for most code. They return `false` or `null` instead of throwing, which makes error handling more predictable. The [Java Queue API documentation](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Queue.html) lists every implementing class and the full contract.

### PriorityQueue

`PriorityQueue` is the most-used `Queue` implementation. It uses a binary min-heap internally, so `poll()` always removes the smallest element in O(log n) time — by natural ordering or by a `Comparator` you supply.

```java
import java.util.PriorityQueue;

PriorityQueue<Integer> taskPriorities = new PriorityQueue<>();
taskPriorities.offer(5);
taskPriorities.offer(1);
taskPriorities.offer(3);

while (!taskPriorities.isEmpty()) {
    System.out.println(taskPriorities.poll());
}
// Output: 1, 3, 5
```

Iterating over a `PriorityQueue` with a for-each loop does not produce elements in priority order — only `poll()` guarantees that. The heap stores elements in positions that satisfy the heap invariant internally, not in sorted sequence.

For a max-heap that processes the largest element first, pass `Comparator.reverseOrder()`:

```java
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
maxHeap.offer(5);
maxHeap.offer(1);
maxHeap.offer(3);
System.out.println(maxHeap.poll()); // 5
```

### ArrayDeque

`ArrayDeque` is the fastest general-purpose queue in Java. It uses a circular array and adds or removes from either end in amortized O(1) time. Use it as a FIFO queue by adding to the back and removing from the front, or as a stack by adding and removing from the front.

```java
import java.util.ArrayDeque;
import java.util.Deque;

Deque<String> jobQueue = new ArrayDeque<>();
jobQueue.offer("render-thumbnail");   // add to back
jobQueue.offer("send-confirmation");  // add to back
jobQueue.offer("update-inventory");   // add to back

String nextJob = jobQueue.poll();     // removes from front: "render-thumbnail"
```

`ArrayDeque` outperforms `LinkedList` as a queue because its contiguous memory layout is more cache-friendly. It also replaces the legacy `Stack` class: calling `push()` and `pop()` on an `ArrayDeque` gives LIFO behavior without the synchronization overhead the old `Stack` class carries on every method call.

### LinkedList as a Queue

`LinkedList` implements both `List` and `Deque`, so you can use it as a FIFO queue when `ArrayDeque` isn't available to you for some reason:

```java
import java.util.LinkedList;
import java.util.Queue;

Queue<String> notificationQueue = new LinkedList<>();
notificationQueue.offer("password-reset");
notificationQueue.offer("order-shipped");
String next = notificationQueue.poll(); // "password-reset"
```

In practice, prefer `ArrayDeque`. `LinkedList` allocates a node object per element, adding memory overhead that `ArrayDeque`'s resizable array avoids entirely.

## Java Lists: ArrayList vs LinkedList

`List` is the most-used collection type in Java. It preserves insertion order, allows duplicate elements, and supports index-based access. The two main implementations handle different access patterns.

### ArrayList

`ArrayList` backs its list with a resizable array. Random access by index runs in O(1). Insertions at the end are amortized O(1) — the internal array doubles when it hits capacity. Insertions or deletions in the middle run in O(n) because all subsequent elements must shift.

```java
import java.util.ArrayList;
import java.util.List;

List<String> products = new ArrayList<>();
products.add("keyboard");
products.add("monitor");
products.add("mouse");

String second = products.get(1);  // "monitor" — O(1)
products.add(1, "webcam");        // inserts at index 1, shifts "monitor" right — O(n)
products.remove(0);               // removes "keyboard", shifts remaining items — O(n)

System.out.println(products);     // [webcam, monitor, mouse]
```

If you know the approximate number of elements upfront, pass an initial capacity to avoid repeated internal resizes:

```java
List<String> orderIds = new ArrayList<>(10_000);
```

This avoids the default growth pattern of doubling from 10 → 20 → 40 → ... until the array is large enough.

### LinkedList

`LinkedList` stores each element in a doubly-linked node. Adding or removing at either end runs in O(1). Access by index requires traversal from the head and runs in O(n).

```java
import java.util.LinkedList;

LinkedList<String> recentSearches = new LinkedList<>();
recentSearches.addFirst("java queue tutorial");
recentSearches.addLast("hashmap vs treemap");

String latest = recentSearches.removeFirst(); // O(1)
String byIndex = recentSearches.get(0);        // O(n) traversal from head
```

### Choosing Between ArrayList and LinkedList

| Operation | ArrayList | LinkedList |
|-----------|-----------|------------|
| `get(index)` | O(1) | O(n) |
| `add(end)` | O(1) amortized | O(1) |
| `add(middle)` | O(n) | O(1)* |
| `remove(middle)` | O(n) | O(1)* |
| Memory per element | No overhead | ~40 bytes per node |

*O(1) only once you hold the node reference; finding the position by index is O(n) first.

Default to `ArrayList`. Switch to `LinkedList` only when you need frequent insertions and deletions at both ends and never need index access. For context on how these structures interact with sorting, the [sorting algorithms comparison](/blog/sorting-algorithms-comparison) covers how different algorithm choices favor different backing structures.

## Java Maps: HashMap, TreeMap, and LinkedHashMap

A `Map` stores key-value pairs where each key is unique. Maps don't extend `Collection`, but they appear in almost every Java application — caches, configuration stores, lookup tables, and grouping operations all depend on them.

### HashMap

`HashMap` is the default choice for key-value storage. It hashes each key to a bucket in an internal array, giving O(1) average time for both `get()` and `put()`. Insertion order is not preserved.

```java
import java.util.HashMap;
import java.util.Map;

Map<String, Integer> wordCount = new HashMap<>();
wordCount.put("java", 10);
wordCount.put("collections", 7);
wordCount.put("queue", 5);

int count = wordCount.getOrDefault("queue", 0);     // 5
wordCount.merge("java", 1, Integer::sum);           // wordCount.get("java") == 11
wordCount.computeIfAbsent("streams", k -> 0);       // initializes key only if absent
```

`HashMap` allows one `null` key and multiple `null` values. Under Java 8+, buckets with many collisions — more than 8 entries per bucket — convert from a linked list to a balanced tree, keeping worst-case lookup at O(log n) instead of O(n).

A common production pattern is caching compiled `Pattern` objects in a `HashMap<String, Pattern>` to avoid recompilation on each request. Use the [online Java regex tester](/tools/regex-tester-online-java) to validate your patterns before adding them to the cache.

Working with maps is where [Java lambda functions](/languages/java/lambda-function/) pay off most clearly — `merge()`, `computeIfAbsent()`, and `forEach()` all accept lambda expressions and replace verbose for-loop patterns with single readable calls.

### TreeMap

`TreeMap` stores entries in sorted key order using a red-black tree. All operations run in O(log n), and you get range query methods not available in `HashMap`:

```java
import java.util.TreeMap;

TreeMap<String, Integer> leaderboard = new TreeMap<>();
leaderboard.put("alice", 95);
leaderboard.put("bob", 82);
leaderboard.put("carol", 91);
leaderboard.put("diana", 88);

// All entries from "bob" to "carol" inclusive
System.out.println(leaderboard.subMap("bob", true, "carol", true));
// {bob=82, carol=91}

System.out.println(leaderboard.firstKey()); // "alice"
System.out.println(leaderboard.lastKey());  // "diana"
```

Use `TreeMap` when you need entries sorted alphabetically or numerically, or when you need `headMap()`, `tailMap()`, or `subMap()` range operations that `HashMap` cannot provide.

### LinkedHashMap

`LinkedHashMap` extends `HashMap` with a doubly-linked list that preserves insertion order. It gives you `HashMap`'s O(1) lookup while iterating entries in the order they were added.

```java
import java.util.LinkedHashMap;

LinkedHashMap<String, String> requestHeaders = new LinkedHashMap<>();
requestHeaders.put("Content-Type", "application/json");
requestHeaders.put("Authorization", "Bearer abc123");
requestHeaders.put("Accept", "application/json");

// Iterates in insertion order — predictable output for debugging
requestHeaders.forEach((key, value) -> System.out.println(key + ": " + value));
```

`LinkedHashMap` constructed with `accessOrder = true` becomes an LRU-cache skeleton. Accessing an entry moves it to the tail, so the entry at the head is always the least-recently-used one — you can evict it when the cache exceeds a maximum size.

## Java Sets: HashSet and TreeSet

A `Set` holds no duplicate elements. Use it when uniqueness matters: deduplication, membership testing, and set operations like union, intersection, and difference.

### HashSet

`HashSet` is backed by a `HashMap` where your values become the map's keys (a dummy object serves as the value). It gives O(1) `contains()`, `add()`, and `remove()`. Order is not preserved.

```java
import java.util.HashSet;
import java.util.Set;

Set<String> activeSessionIds = new HashSet<>();
activeSessionIds.add("session-abc");
activeSessionIds.add("session-xyz");
activeSessionIds.add("session-abc"); // duplicate — silently ignored

System.out.println(activeSessionIds.size());                   // 2
System.out.println(activeSessionIds.contains("session-xyz")); // true
```

Use `HashSet` when fast membership checks are the primary requirement and iteration order doesn't matter. Checking whether a string appears in a `HashSet` of ten million entries takes the same time as checking a set of ten.

### TreeSet

`TreeSet` maintains elements in sorted order using a red-black tree. All operations run in O(log n), and you get the same range operations available in `TreeMap`:

```java
import java.util.TreeSet;

TreeSet<Integer> availablePorts = new TreeSet<>();
availablePorts.add(8080);
availablePorts.add(3000);
availablePorts.add(5432);
availablePorts.add(9000);

System.out.println(availablePorts.first());        // 3000
System.out.println(availablePorts.last());         // 9000
System.out.println(availablePorts.headSet(8080));  // [3000, 5432]
System.out.println(availablePorts.tailSet(5432));  // [5432, 8080, 9000]
```

`LinkedHashSet` (not shown) combines `HashSet` performance with insertion-order iteration — use it when you need unique elements in the exact order they were first seen.

## Choosing the Right Java Collection

| Need | Use |
|------|-----|
| Ordered list with index access | `ArrayList` |
| Frequent add/remove at both ends | `ArrayDeque` |
| Process elements by priority | `PriorityQueue` |
| FIFO task processing | `ArrayDeque` (as `Queue`) |
| Fast key-value lookup, no ordering | `HashMap` |
| Key-value pairs sorted by key | `TreeMap` |
| Key-value pairs in insertion order | `LinkedHashMap` |
| Fast membership check, no duplicates | `HashSet` |
| Sorted unique values | `TreeSet` |
| Thread-safe bounded queue | `ArrayBlockingQueue` |

A few defaults worth internalizing:

- **`ArrayList` for lists** unless you need frequent insertions and deletions at both ends without index access.
- **`HashMap` for maps** unless you need sorted keys or range queries.
- **`ArrayDeque` over `LinkedList` as a queue** — it is faster and uses less memory per element.
- **Avoid `Vector` and `Stack`** — both synchronize on every call even when you don't need thread safety. Use `ArrayList` and `ArrayDeque` instead.
- **Avoid `Hashtable`** — superseded by `HashMap` and `ConcurrentHashMap` for thread-safe use cases.

## Common Pitfalls with Java Collections

### Trap 1: Modifying a collection during iteration

Modifying a list with a for-each loop in progress throws `ConcurrentModificationException`:

```java
List<String> pendingJobs = new ArrayList<>(List.of("job-1", "job-2", "job-3"));

// Throws ConcurrentModificationException at runtime
for (String job : pendingJobs) {
    if (job.equals("job-2")) {
        pendingJobs.remove(job); // modifying the list while iterating it
    }
}
```

Use an explicit `Iterator` and call `iterator.remove()`:

```java
Iterator<String> it = pendingJobs.iterator();
while (it.hasNext()) {
    if (it.next().equals("job-2")) {
        it.remove(); // safe — removes through the iterator
    }
}
```

For a one-liner, `removeIf()` handles this more cleanly: `pendingJobs.removeIf(job -> job.equals("job-2"))`.

### Trap 2: Iterating a PriorityQueue expecting sorted output

Iterating a `PriorityQueue` with a for-each loop does not produce elements in priority order. The heap structure satisfies the heap invariant internally but does not maintain a fully sorted sequence.

```java
PriorityQueue<Integer> scores = new PriorityQueue<>(List.of(10, 3, 7, 1));

// Heap storage order — iteration output is implementation-defined
for (int score : scores) {
    System.out.print(score + " "); // might print "1 3 7 10" or "1 10 7 3"
}

// Use poll() for guaranteed sorted removal
while (!scores.isEmpty()) {
    System.out.print(scores.poll() + " "); // always: 1 3 7 10
}
```

### Trap 3: Mutable objects as HashMap keys

`HashMap` locates values by the hash of the key at insertion time. If the key object mutates after insertion, its hash code changes and the map loses the entry:

```java
List<String> accountIds = new ArrayList<>(List.of("user-001"));
Map<List<String>, String> tierCache = new HashMap<>();
tierCache.put(accountIds, "premium");

accountIds.add("user-002"); // mutates the key after insertion

// Map computes a new hash, finds no matching bucket
System.out.println(tierCache.get(accountIds)); // null — entry is lost
```

Always use immutable objects as map keys — `String`, `Integer`, `Long`, `UUID`, or Java record types all work correctly.

## Frequently Asked Questions

### What is the difference between Java Queue and Stack?

A `Queue` processes elements in first-in, first-out (FIFO) order — the first element added is the first one removed. A `Stack` uses last-in, first-out (LIFO) order — the most recently added element is removed first. In modern Java, `ArrayDeque` handles both roles: calling `offer()` and `poll()` gives FIFO queue behavior, while calling `push()` and `pop()` (which delegate to `addFirst()` and `removeFirst()`) gives stack behavior. Avoid the legacy `Stack` class — it extends `Vector` and synchronizes every method call even when thread safety is not needed, adding overhead that `ArrayDeque` never incurs.

### When should I use HashMap vs TreeMap in Java?

Use `HashMap` by default. It runs `get()` and `put()` in O(1) average time, versus `TreeMap`'s O(log n). Choose `TreeMap` when you need entries sorted by key — a leaderboard in alphabetical order, a frequency report, or any structure requiring `firstKey()`, `lastKey()`, `subMap()`, `headMap()`, or `tailMap()` range operations. If you need insertion-order iteration rather than key-sorted order, `LinkedHashMap` gives you `HashMap` performance with predictable iteration sequence.

### Is ArrayList or LinkedList faster in Java?

`ArrayList` is faster for the vast majority of real-world workloads. Random access by index runs in O(1) versus `LinkedList`'s O(n) traversal. `ArrayList` also uses less memory per element — `LinkedList` allocates a node object with two pointer fields for every element, adding roughly 40 bytes of overhead per entry on a 64-bit JVM. Contiguous memory means `ArrayList` benefits from CPU cache locality, making sequential iteration measurably faster in practice. `LinkedList` has an advantage only when you need frequent insertions and deletions at both ends without index access — and `ArrayDeque` covers that same pattern with less overhead.

## Conclusion

Java queues, lists, maps, and sets each solve a distinct problem. Picking `PriorityQueue` for ordered task processing, `ArrayList` for indexed sequences, and `HashMap` for fast lookups is not premature optimization — it is choosing the right data structure from the start. The Collections Framework provides all of them; the cost is learning when each fits.

For functional operations across these collections — filtering, grouping, and reducing — the [Java lambda functions guide](/languages/java/lambda-function/) covers `stream()`, `filter()`, `collect()`, and the utility methods that make collection transformations concise.
