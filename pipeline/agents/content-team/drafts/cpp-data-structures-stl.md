---
title: "C++ map, vector, and STL Data Structures: Complete Guide"
description: "C++ map, vector, queue, and more — learn how each STL container works, when to use it, and see working code examples for every major data structure."
category: languages
language: cpp
concept: data-structures-stl
difficulty: "beginner"
template_id: lang-v2
tags: [cpp, stl, data-structures, map, vector]
related_posts: []
related_tools: []
published_date: "2026-06-12"
og_image: "/og/languages/cpp/data-structures-stl.png"
word_count_target: 2500
actual_word_count: 2723
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "C++ map, vector, and STL Data Structures: Complete Guide",
    "description": "C++ map, vector, queue, and more — learn how each STL container works, when to use it, and see working code examples for every major data structure.",
    "datePublished": "2026-06-12",
    "programmingLanguage": "cpp",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/cpp/data-structures-stl/",
    "mainEntity": [
      {"@type": "Question", "name": "What is the difference between C++ map and unordered_map?", "acceptedAnswer": {"@type": "Answer", "text": "C++ map stores keys in sorted order using a red-black tree, giving O(log n) for all operations. unordered_map uses a hash table for average O(1) lookups but provides no ordering guarantee. Use map when you need sorted iteration or range queries; use unordered_map for raw lookup speed."}},
      {"@type": "Question", "name": "When should I use vector vs list in C++?", "acceptedAnswer": {"@type": "Answer", "text": "Use vector almost always. Its contiguous memory layout makes random access and iteration much faster than list. Only choose list when you hold iterators to positions that need O(1) insertion or deletion — a rare requirement in practice."}},
      {"@type": "Question", "name": "Is std::vector the same as an array in C++?", "acceptedAnswer": {"@type": "Answer", "text": "No. std::vector is a dynamic array that resizes automatically as elements are added. A C-style array has a fixed compile-time size. In modern C++ prefer vector over raw arrays; for fixed-size collections with the full STL interface, use std::array."}}
    ]
  }
  </script>
---

You're building a word-frequency counter and reach for an array — then realise you need to look up words by name, not by index. You switch to a raw array of structs, write linear search, and your program crawls on a 50,000-word input. There's a better way: the **C++ STL** ships a collection of data structures designed for exactly this kind of problem. The **C++ map**, `vector`, `queue`, `stack`, `set`, and `unordered_map` each solve a different access pattern, and choosing the right one often means the difference between O(n) and O(1).

This guide covers every major STL container: what it stores, how it works internally, and when to reach for it.

## What Is the C++ STL?

The Standard Template Library is a collection of generic containers and algorithms built directly into the C++ standard library — no third-party dependencies, no installation. Every STL container ships with a consistent interface: `begin()`, `end()`, `size()`, `empty()`, and `clear()`. Patterns you learn on `vector` apply immediately to `set` or `map`.

STL containers fall into four groups:

| Group | Containers | Primary Use |
|-------|-----------|-------------|
| Sequence | `vector`, `deque`, `list`, `array` | Ordered collections; position-based access |
| Associative | `map`, `set`, `multimap`, `multiset` | Key-based lookup; always sorted |
| Unordered | `unordered_map`, `unordered_set` | Hash-based lookup; no order guarantee |
| Adapters | `stack`, `queue`, `priority_queue` | Restricted interface over a sequence container |

Include only the headers you need:

```cpp
#include <vector>
#include <map>
#include <unordered_map>
#include <queue>
#include <stack>
#include <set>
```

Each header is self-contained. `<algorithm>` gives you `std::sort`, `std::find`, and the rest of the algorithm library, which works with any container that provides iterators.

## C++ map: Ordered Key-Value Storage

`std::map` stores key-value pairs where keys are always kept in sorted order. Internally, it uses a self-balancing red-black tree. Every operation — insert, lookup, erase — runs in O(log n) time. The sorted invariant is maintained automatically; you never need to sort a `map` manually.

### Basic operations

```cpp
#include <iostream>
#include <map>
#include <string>

int main() {
    std::map<std::string, int> scores;

    // Insert via operator[] — creates entry with default value if key absent
    scores["Alice"] = 95;
    scores["Bob"]   = 87;
    scores["Carol"] = 91;

    // Insert via insert() or emplace() — does NOT overwrite existing keys
    scores.insert({"Dave", 78});
    scores.emplace("Eve", 84);

    // Iterate — keys are guaranteed alphabetical order
    for (const auto& [name, score] : scores) {
        std::cout << name << ": " << score << "\n";
    }
    // Alice: 95
    // Bob: 87
    // Carol: 91
    // Dave: 78
    // Eve: 84

    return 0;
}
```

### Safe lookup: find() and at()

The `[]` operator inserts a zero-initialised entry when the key is missing — useful for counters, dangerous for lookups.

```cpp
// SAFE: find() returns end() if key absent, never modifies the map
auto it = scores.find("Frank");
if (it != scores.end()) {
    std::cout << "Found: " << it->second << "\n";
} else {
    std::cout << "Not found\n";
}

// SAFE: at() throws std::out_of_range if key absent
try {
    int val = scores.at("Frank");
} catch (const std::out_of_range& e) {
    std::cout << "Key not found\n";
}

// DANGEROUS for lookups: inserts 0 if key absent
if (scores["Frank"] > 0) { /* now "Frank" exists with value 0 */ }
```

### Range queries with lower_bound and upper_bound

Because `map` maintains sorted order, it supports efficient range queries — something `unordered_map` cannot do.

```cpp
std::map<int, std::string> events = {
    {10, "start"}, {20, "checkpoint"}, {35, "end"}
};

// All events from time 15 onwards
for (auto it = events.lower_bound(15); it != events.end(); ++it) {
    std::cout << it->first << ": " << it->second << "\n";
}
// 20: checkpoint
// 35: end
```

### When to use C++ map

- You need key-value storage **and** need keys in sorted order.
- You need `lower_bound` / `upper_bound` range queries.
- Lookup frequency is moderate and O(log n) is acceptable.
- Key collisions or hash function choice are concerns (map needs only `operator<`).

For raw lookup speed without ordering, use `unordered_map` (covered below).

## C++ vector: The Default Container

`std::vector` is the workhorse of the STL. It stores elements in a contiguous memory block — just like a C array — but manages its own allocation and resizing. When capacity fills, vector allocates a new larger block (typically doubling), moves all elements, and releases the old buffer. This growth strategy gives amortised O(1) cost per `push_back`.

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> nums = {5, 2, 8, 1, 9, 3};

    // Random access — O(1)
    std::cout << nums[0] << "\n";       // 5 — no bounds check
    std::cout << nums.at(2) << "\n";    // 8 — throws if out of range

    // Append — amortised O(1)
    nums.push_back(7);

    // Sort in place using STL algorithm
    std::sort(nums.begin(), nums.end());
    // nums: 1 2 3 5 7 8 9

    // Remove last element — O(1)
    nums.pop_back();

    // Size and capacity
    std::cout << "size: "     << nums.size()     << "\n";  // 6
    std::cout << "capacity: " << nums.capacity() << "\n";  // implementation-defined

    return 0;
}
```

### reserve() and emplace_back()

Two habits that meaningfully improve vector performance in hot paths:

```cpp
std::vector<std::string> names;
names.reserve(500);  // pre-allocate — eliminates all reallocations for <= 500 pushes

// emplace_back constructs in-place — avoids a copy/move vs push_back
names.emplace_back("Alice");
names.emplace_back("Bob");
```

`reserve()` sets capacity without changing size. Use it when you know the final element count upfront. `emplace_back` constructs directly inside the vector's buffer instead of constructing a temporary and moving it — measurable savings for non-trivial types.

### Erasing elements

```cpp
std::vector<int> v = {1, 2, 3, 4, 5};

// Erase element at index 2 (value 3) — O(n) because of shifting
v.erase(v.begin() + 2);
// v: 1 2 4 5

// Erase-remove idiom: remove all 4s efficiently
v.erase(std::remove(v.begin(), v.end(), 4), v.end());
// v: 1 2 5
```

Erasing from anywhere except the end is O(n) — all elements after the erased position must shift left. If you need frequent middle deletions, consider `std::list` or rethink your data structure.

### When to use vector

- Default choice for any ordered sequence.
- Fast random access and cache-friendly iteration (contiguous memory).
- Frequent appends at the back.
- You need STL algorithm support (`sort`, `binary_search`, `lower_bound`).

Avoid vector when you need frequent insertions or deletions in the middle of large collections.

## C++ unordered_map: Hash-Based Lookups

`std::unordered_map` provides the same key-value interface as `map` but uses a hash table internally. Average-case insert, lookup, and erase are O(1) — a significant speedup over map's O(log n) for large datasets or lookup-heavy workloads.

```cpp
#include <iostream>
#include <unordered_map>
#include <string>

int main() {
    std::unordered_map<std::string, int> word_freq;

    std::string text[] = {"apple", "banana", "apple", "cherry", "banana", "apple"};
    for (const auto& word : text) {
        word_freq[word]++;  // safe here — intentionally default-inserting 0 on first encounter
    }

    for (const auto& [word, count] : word_freq) {
        std::cout << word << ": " << count << "\n";
    }
    // Order not guaranteed — hash order, not alphabetical

    return 0;
}
```

### map vs unordered_map: choosing the right one

| Feature | `map` | `unordered_map` |
|---------|-------|-----------------|
| Internal structure | Red-black tree | Hash table |
| Lookup / insert / erase | O(log n) | O(1) average, O(n) worst |
| Key order | Always sorted | No guarantee |
| Range queries (`lower_bound`) | Supported | Not supported |
| Memory overhead | Moderate (tree nodes) | Higher (bucket array + load factor) |
| Key requirement | `operator<` or comparator | Hash function + `operator==` |

Worst-case O(n) for `unordered_map` occurs when many keys hash to the same bucket. For user-controlled input (e.g., request parameters used as hash keys), this can be exploited. In security-sensitive contexts, supply a randomised hash or use `map`.

### Custom types as keys

For custom structs, you must provide a hash specialisation:

```cpp
struct Point { int x, y; };

struct PointHash {
    std::size_t operator()(const Point& p) const {
        return std::hash<int>()(p.x) ^ (std::hash<int>()(p.y) << 16);
    }
};

struct PointEqual {
    bool operator()(const Point& a, const Point& b) const {
        return a.x == b.x && a.y == b.y;
    }
};

std::unordered_map<Point, std::string, PointHash, PointEqual> grid;
grid[{0, 0}] = "origin";
```

The technique of defining small callable structs like `PointHash` pairs naturally with [C++ lambda functions](/languages/cpp/lambda-function), which can also serve as inline comparators and hash functions for short-lived maps.

## C++ queue and deque: FIFO Data Structures

`std::queue` implements first-in, first-out (FIFO) access. Elements are pushed at the back and popped from the front — the exact semantics you need for task queues, BFS frontiers, or message buffers.

```cpp
#include <iostream>
#include <queue>
#include <string>

int main() {
    std::queue<std::string> job_queue;

    job_queue.push("render-frame-1");
    job_queue.push("render-frame-2");
    job_queue.push("render-frame-3");

    while (!job_queue.empty()) {
        std::cout << "Processing: " << job_queue.front() << "\n";
        job_queue.pop();
    }
    // Processing: render-frame-1
    // Processing: render-frame-2
    // Processing: render-frame-3

    return 0;
}
```

`queue` is a container adapter; by default it wraps `std::deque`. You cannot iterate over a `queue` — only access front and back.

### std::deque — direct double-ended access

`std::deque` (double-ended queue) is the underlying engine for `queue` but can also be used directly when you need O(1) push and pop at **both** ends, unlike `vector` which only optimises the back.

```cpp
#include <deque>

std::deque<int> dq = {2, 3, 4};
dq.push_front(1);   // [1, 2, 3, 4]
dq.push_back(5);    // [1, 2, 3, 4, 5]
dq.pop_front();     // [2, 3, 4, 5]
dq.pop_back();      // [2, 3, 4]

// Random access still works — O(1)
std::cout << dq[1] << "\n";  // 3
```

Use `deque` over `vector` when you need fast prepend. Use `vector` otherwise — its contiguous layout is more cache-friendly than `deque`'s segmented storage.

## C++ stack and priority_queue

### stack — Last-In, First-Out

`std::stack` exposes only LIFO operations. It wraps a `deque` by default but can wrap `vector` or `list` via a template argument.

```cpp
#include <iostream>
#include <stack>

int main() {
    std::stack<int> call_stack;

    call_stack.push(100);
    call_stack.push(200);
    call_stack.push(300);

    while (!call_stack.empty()) {
        std::cout << call_stack.top() << "\n";  // 300, 200, 100
        call_stack.pop();
    }

    return 0;
}
```

`stack` is the right tool for expression evaluation (e.g. matching brackets), undo history, and depth-first graph traversal. The restricted interface enforces LIFO discipline — you cannot accidentally access elements by index.

### priority_queue — Heap-Based Ordering

`std::priority_queue` is a max-heap by default: `top()` always returns the largest element. Every `push` and `pop` runs in O(log n).

```cpp
#include <iostream>
#include <queue>
#include <vector>

int main() {
    // Max-heap (default)
    std::priority_queue<int> max_pq;
    max_pq.push(5);
    max_pq.push(1);
    max_pq.push(8);
    max_pq.push(3);

    while (!max_pq.empty()) {
        std::cout << max_pq.top() << " ";  // 8 5 3 1
        max_pq.pop();
    }
    std::cout << "\n";

    // Min-heap — swap comparator to std::greater
    std::priority_queue<int, std::vector<int>, std::greater<int>> min_pq;
    min_pq.push(5);
    min_pq.push(1);
    min_pq.push(8);

    std::cout << min_pq.top() << "\n";  // 1

    return 0;
}
```

`priority_queue` is the natural fit for Dijkstra's shortest path, A* search, and any scheduling algorithm that always needs the highest (or lowest) priority item next. For a broader view of how heap sort compares to other sorting algorithms, see the [sorting algorithms comparison](/blog/sorting-algorithms-comparison) post.

## C++ set and multiset: Unique Sorted Elements

`std::set` stores unique values in sorted order. It uses the same red-black tree as `map` — only without the value half of the pair. Lookup, insert, and erase are O(log n).

```cpp
#include <iostream>
#include <set>

int main() {
    std::set<int> unique_ids = {42, 7, 19, 42, 7, 100};
    // Duplicates silently dropped — contents: {7, 19, 42, 100}

    for (int id : unique_ids) {
        std::cout << id << " ";  // 7 19 42 100
    }
    std::cout << "\n";

    // O(log n) membership test
    if (unique_ids.count(19)) {
        std::cout << "19 is in the set\n";
    }

    // Remove an element
    unique_ids.erase(7);

    // Range: all IDs between 10 and 50
    auto lo = unique_ids.lower_bound(10);
    auto hi = unique_ids.upper_bound(50);
    for (auto it = lo; it != hi; ++it) {
        std::cout << *it << " ";  // 19 42
    }

    return 0;
}
```

`std::multiset` allows duplicate values while maintaining sorted order. `std::unordered_set` gives average O(1) membership tests without sorted order — the same hash/tree trade-off as `unordered_map` vs `map`.

Use `set` when you need a deduplicated, sorted collection and you care about membership or range queries. Use `unordered_set` when you only need fast membership checks and order is irrelevant.

## Choosing the Right STL Container

The right container comes down to three questions: **How do you access elements?** **How often do you insert and delete?** **Does order matter?**

| Access Pattern | Recommended Container | Complexity |
|---|---|---|
| Random access by index, frequent appends | `vector` | O(1) access, amortised O(1) push_back |
| Key → value lookup, sorted keys needed | `map` | O(log n) all ops |
| Key → value lookup, max speed | `unordered_map` | O(1) average |
| FIFO processing (queue, BFS) | `queue` | O(1) push/pop |
| LIFO access (undo, DFS) | `stack` | O(1) push/pop |
| Always-available max or min element | `priority_queue` | O(log n) push/pop |
| Unique sorted values | `set` | O(log n) all ops |
| Unique values, fast membership only | `unordered_set` | O(1) average |
| Fast insert at both ends | `deque` | O(1) both ends |
| Frequent O(1) middle insert/delete | `list` | O(1) insert at iterator |

When uncertain, start with `vector`. It is cache-friendly, has the widest algorithm support, and its O(n) insertion cost is only a problem once profiling confirms it.

Understanding how these containers allocate memory is also relevant to performance. For a clear look at where heap-allocated containers live at runtime, see the [stack vs heap memory](/blog/stack-vs-heap-memory) explainer. When these containers hold class instances — particularly polymorphic ones — patterns from [C++ class inheritance](/languages/cpp/class-inheritance) become directly relevant.

The complete API for every standard container is documented at [cppreference.com/w/cpp/container](https://en.cppreference.com/w/cpp/container).

## Frequently Asked Questions

### What is the difference between C++ map and unordered_map?

`map` uses a red-black tree and stores keys in sorted order. Every operation — lookup, insert, erase — is O(log n). `unordered_map` uses a hash table for average-case O(1) operations but provides no ordering guarantee and has a higher memory footprint due to the bucket array. Choose `map` when you need sorted iteration or `lower_bound`/`upper_bound` range queries; choose `unordered_map` when you only need fast point lookups and key order is irrelevant.

### When should I use vector vs list in C++?

Use `vector` almost always. Contiguous memory makes cache performance significantly better than `list`'s scattered node allocations — the speed difference often exceeds a factor of 10 on modern hardware, even for operations where `list` has better algorithmic complexity. Use `std::list` only when you hold stable iterators into the container and need O(1) insertion or deletion at those iterator positions — a narrow use case that rarely arises in practice.

### Is std::vector the same as an array in C++?

No. `std::vector` is a dynamically resizing array: it allocates on the heap and grows automatically. A C-style array (`int arr[100]`) has a fixed compile-time size, lives on the stack (for local arrays), and carries none of the STL interface. In modern C++, prefer `vector` over raw arrays. For a fixed-size collection with the full STL iterator and algorithm interface, use `std::array<int, N>` — it has zero overhead compared to a raw array.

### Can I use a struct as a C++ map key?

Yes. `map` requires the key type to support `operator<` (or a custom comparator supplied as a template argument). `unordered_map` requires a hash function and `operator==`. For simple structs, you can define these as member functions or standalone free functions. The [cppreference documentation](https://en.cppreference.com/w/cpp/container/map) includes examples for custom key types.

### What happens to iterators when a vector resizes?

All iterators, pointers, and references to elements are **invalidated** after a `vector` reallocation. This is a common source of bugs: if you hold a pointer or iterator into a vector and then call `push_back`, you may be pointing at freed memory after the resize. The safe pattern is to store indices rather than raw pointers. Calling `reserve()` upfront prevents reallocation entirely for the reserved range.

## Conclusion

The C++ STL gives you a battle-tested toolkit: reach for `vector` by default, use `map` or `unordered_map` for key-value lookups (sorted vs fast), and use the container adapters — `stack`, `queue`, `priority_queue` — when an algorithm demands a specific access discipline. The C++ map and its unordered counterpart cover the majority of real-world associative data needs. For a full API reference including every member function and iterator guarantee, the authoritative source is [cppreference.com](https://en.cppreference.com/w/cpp/container). Continue building your C++ toolkit with [C++ lambda functions](/languages/cpp/lambda-function) and [C++ class inheritance](/languages/cpp/class-inheritance).
