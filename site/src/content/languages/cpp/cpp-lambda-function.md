---
title: "C++ Lambda Functions: Syntax, Captures, and Patterns"
description: "Learn c++ lambda function syntax, capture modes, and real-world patterns. Covers by-value, by-reference, and init captures with working code examples."
category: "languages"
language: "cpp"
concept: "lambda-function"
difficulty: "intermediate"
template_id: "lang-v3"
tags: [cpp, lambda-function, closures, functional-programming, stl]
related_posts: []
related_tools: []
linkAnchors:
  - "c++ lambda function"
  - "c++ lambda expression"
  - "c++ lambda capture"
published_date: "2026-06-01"
og_image: "/og/languages/cpp/lambda-function.png"
word_count_target: 2000
---

You have a vector of `Order` objects and need to sort them by price, descending. The options without lambdas: write a comparator struct, add a static member function, or declare a free function. Any of those works, but each adds a named declaration somewhere else in the file for behavior that's only used once. A c++ lambda function solves this by letting you define the comparator exactly where you use it — inline, at the call site, with no extra names polluting the surrounding scope.

C++11 added lambda expressions to the language, and they've become the default for inline callables in modern C++ code. You'll find them in STL algorithm calls, event callbacks, initialization expressions, and anywhere a short callable makes the code more readable than a standalone function declaration. The c++ lambda expression syntax looks unusual at first, but every part has a clear purpose.

## C++ Lambda Expression Syntax, Explained

The general form of a C++ lambda expression:

```cpp
[capture-list](parameters) -> return-type { body }
```

Each part serves a distinct role:

**`[capture-list]`** — controls which variables from the enclosing scope the lambda can access. The brackets are mandatory even when the list is empty. An empty `[]` means the lambda captures nothing; trying to use an outer local variable inside will produce a compile error.

**`(parameters)`** — works like a regular function parameter list. You can omit the parentheses entirely in C++14 and later if the lambda takes no arguments: `[] { return 42; }` is valid. C++11 requires the parentheses even for no-argument lambdas: `[]() { return 42; }`.

**`-> return-type`** — the trailing return type is optional. The compiler deduces the return type from the return statement in most cases. Specify it explicitly when you need to enforce a type or when the body has multiple return paths that return different-but-convertible types.

**`{ body }`** — the function body, same rules as any other C++ function.

The non-obvious detail: the square brackets are not optional syntax — they distinguish a lambda from a brace-initializer. Omitting them produces a compilation error or an unintended interpretation.

By-value captures are `const` inside the lambda by default. If you need to modify a captured copy, add `mutable` after the parameter list:

```cpp
int retry_count = 3;
auto attempt = [retry_count]() mutable {
    retry_count--;
    return retry_count > 0;
};
// The outer retry_count is unchanged; only the lambda's copy changes.
```

The c++ lambda return type is deduced here automatically. C++11 supports deduction for single-return-statement bodies; C++14 extended this to multi-return bodies.

## Your First Lambda: Minimal Working Example

Here's the smallest self-contained c++ lambda function that does something useful:

```cpp
#include <iostream>

int main() {
    auto add = [](int a, int b) { return a + b; };
    std::cout << add(3, 7) << "\n"; // 10
    return 0;
}
```

The compiler generates an anonymous class — the closure type — with an `operator()` member. `auto add` deduces that closure type at compile time. Calling `add(3, 7)` calls `operator()(3, 7)` on that object.

You can also invoke a lambda immediately without assigning it to a variable:

```cpp
int result = [](int x, int y) { return x * y; }(6, 8);
// result == 48
```

The trailing `(6, 8)` calls the lambda immediately after it's defined. This pattern appears in complex initialization expressions where you need scoped computation to produce a `const` value.

A lambda with no capture list `[]` and no non-`const` member state behaves exactly like a free function. Importantly, a no-capture lambda can implicitly convert to a function pointer, which matters when interfacing with C APIs.

## C++ Lambda Capture Modes, Step by Step

Capture semantics is where most lambda bugs originate. Work through each mode before combining them.

**No capture:**

```cpp
auto square = [](int n) { return n * n; };
square(9); // 81
```

No outer variables. The lambda is a pure function — stateless and trivially convertible to a function pointer.

**Capture all by value (`[=]`):**

```cpp
int tax_rate = 8;
double base_price = 99.00;

auto total_cost = [=](int quantity) {
    return base_price * quantity * (1.0 + tax_rate / 100.0);
};

tax_rate = 20; // doesn't affect total_cost — it already captured 8
std::cout << total_cost(3) << "\n"; // uses base_price=99, tax_rate=8
```

The lambda copies `tax_rate` and `base_price` at the point of capture. Later modifications to those variables have no effect inside the lambda.

**Capture all by reference (`[&]`):**

```cpp
std::vector<std::string> log_entries;

auto record = [&](const std::string& message) {
    log_entries.push_back(message);
};

record("Request received");
record("Processing complete");
// log_entries now contains both strings
```

The lambda holds a reference to `log_entries`. Every call modifies the original vector. Using `[&]` is appropriate here because `log_entries` outlives the lambda.

**Selective capture — the clearest form:**

```cpp
int base_price = 100;
int discount = 15;

auto apply_discount = [base_price, &discount](int quantity) {
    discount = std::min(discount, 20); // modifies the outer discount
    return (base_price - discount) * quantity;
};
```

`base_price` is captured by value; `discount` is captured by reference. Mixing modes in the capture list documents intent precisely — you can tell at a glance which variables the lambda reads and which it modifies.

**C++14 init captures (c++ lambda init capture):**

Init captures let you create new variables inside the capture list, rather than just naming existing ones:

```cpp
auto ptr = std::make_unique<int>(42);

auto use_ptr = [moved_ptr = std::move(ptr)]() -> int {
    return *moved_ptr;
};

// ptr is now null; moved_ptr owns the value inside the lambda
use_ptr(); // returns 42
```

Without init captures, you couldn't move a non-copyable type like `unique_ptr` into a lambda — capturing by value would try to copy it (a compile error) and capturing by reference would leave ownership ambiguous. Init captures solve this directly.

You can also use init captures to rename a captured variable:

```cpp
auto handler = [timeout_ms = config.network.timeout_ms]() {
    // cleaner name inside the lambda body
    do_request(timeout_ms);
};
```

## Passing a Lambda as a Function Parameter

The most frequent use of a c++ lambda as function parameter is with STL algorithms. Here's `std::sort` with a descending integer comparator:

```cpp
#include <algorithm>
#include <vector>
#include <iostream>

int main() {
    std::vector<int> prices = {430, 129, 780, 55, 340};

    std::sort(prices.begin(), prices.end(), [](int a, int b) {
        return a > b; // descending
    });

    for (int p : prices) std::cout << p << " ";
    // Output: 780 430 340 129 55
    return 0;
}
```

STL algorithms accept comparators as template parameters. The lambda's `operator()` gets inlined into the sort loop at compile time — no virtual dispatch, no indirection. The [sorting algorithms comparison](/blog/sorting-algorithms-comparison/) shows how this pattern compares to equivalent sort idioms in Python, Go, and Java.

When writing your own function that accepts a callable, you have two options:

**Template parameter (zero overhead, inlineable):**

```cpp
template<typename Predicate>
void filter_print(const std::vector<int>& nums, Predicate pred) {
    for (int n : nums) {
        if (pred(n)) std::cout << n << " ";
    }
}

filter_print(prices, [](int p) { return p > 200; });
// Output: 430 780 340
```

**`std::function` (type-erased, adds indirection):**

```cpp
void filter_print(
    const std::vector<int>& nums,
    std::function<bool(int)> pred
);
```

Use `std::function` when you need to store the callable in a member variable, put it in a container, or return it from a function. For short-lived algorithm predicates in performance-critical code, the template approach is preferable — `std::function` typically adds a heap allocation and a virtual-function-equivalent dispatch per call.

## Generic Lambdas and C++14 Onwards

C++14 introduced generic lambdas, where parameters are typed `auto`:

```cpp
auto multiply = [](auto a, auto b) { return a * b; };

multiply(3, 4);       // int × int → 12
multiply(2.5, 1.5);   // double × double → 3.75
multiply(3L, 7L);     // long × long → 21
```

The compiler generates a templated `operator()` inside the closure type. Each distinct set of argument types becomes a separate template instantiation — the same behavior as a function template, in a more compact form. A c++ generic lambda avoids having to write a full class or function template for simple multi-type callables.

C++20 extended this with explicit template parameters in the lambda:

```cpp
auto get_first = []<typename T>(const std::vector<T>& v) -> T {
    return v.front();
};
```

This is more expressive when you need to name the type explicitly, constrain it with a concept, or use it in multiple parameter positions.

### Comparison: lambda vs named function template

| Scenario | Lambda | Named function |
|---|---|---|
| Single call site | Preferred | Overkill |
| Multiple call sites | Duplicate or extract | Preferred |
| Recursive behavior | Workaround required | Natural |
| Storing in a container | `std::function` wrapper | Direct function pointer |
| C API compatibility | Only if no captures | Always possible |

## Capture Bugs That Will Trip You Up

**Bug 1: Dangling reference from a returned lambda**

```cpp
std::function<int()> make_counter(int start) {
    // DANGER: start lives on make_counter's stack frame
    return [&start]() { return ++start; };
} // start is destroyed here

auto counter = make_counter(0);
counter(); // undefined behavior — dangling reference to start
```

When a lambda outlives the scope where its reference captures live, those references are dangling. Fix: capture by value instead.

```cpp
return [start]() mutable { return ++start; };
```

**Bug 2: Capturing `this` in member functions**

```cpp
class RequestHandler {
    int timeout_ms = 5000;
    void schedule() {
        auto task = [=]() { do_request(timeout_ms); };
        queue_task(task);
    }
};
```

In a member function, `[=]` captures `this` by pointer — it doesn't copy the members themselves. `timeout_ms` inside the lambda resolves to `this->timeout_ms`. If the `RequestHandler` is destroyed before `task` runs, the behavior is undefined.

Fix with a C++14 init capture:

```cpp
auto task = [timeout = this->timeout_ms]() { do_request(timeout); };
```

Now the lambda holds a copy of the integer, with no dependency on `this`.

**Bug 3: Forgetting `mutable` on a value-captured variable**

```cpp
int page = 1;
auto next_page = [page]() {
    page++; // compile error: assignment of read-only variable
    return page;
};
```

By-value captures are `const` by default inside the lambda body. Adding `mutable` allows modification of the lambda's internal copy — but doesn't affect the outer variable.

```cpp
auto next_page = [page]() mutable { return ++page; };
```

If you need to modify the outer variable, use reference capture instead.

## When a Lambda Is the Wrong Tool

Lambdas aren't the right choice in every situation. Three cases where alternatives are cleaner:

**Reuse across multiple call sites.** When the same predicate or comparator appears in three different locations, a named free function is easier to test and modify. A lambda is a local tool; behavior needed in multiple places deserves a name.

**Complex logic that benefits from a name.** A 25-line lambda with three branches and early returns is harder to follow than a named function like `validate_payment_details()`. When the body is long enough to warrant explanation, the name is part of the documentation.

**Recursive algorithms.** A lambda can't refer to itself by name without a workaround. Capturing a `std::function<...>` by reference and calling through it works but adds overhead. The c++ lambda vs function pointer tradeoff matters here too: lambdas with captures don't convert to function pointers, which is a firm constraint when calling C APIs that require function pointers directly — only no-capture lambdas make that conversion.

## Lambdas in Java and Python: A Brief Comparison

C++ isn't alone in offering inline callables. Seeing how other languages handle the same problem clarifies what C++'s explicit capture list actually buys.

**Python** lambdas are limited to single expressions — no multi-line bodies by design:

```python
sort_key = lambda order: order.price
sorted_orders = sorted(orders, key=sort_key)
```

Python closures over enclosing variables implicitly — no capture list required. Every outer variable is accessible inside the lambda by reference semantics. The simplicity comes at the cost of explicit dependency documentation. Python's design decision was that multi-line anonymous functions would hurt readability more than they'd help.

**Java** lambdas (introduced in Java 8) implement a single-method interface at the point of use:

```java
Comparator<Order> byPrice = (a, b) -> Double.compare(a.price, b.price);
orders.sort(byPrice);
```

Java's captured variables must be effectively final — the compiler rejects code that modifies a captured outer variable after capture. This eliminates the dangling-reference class of bugs automatically. The [Java lambda functions guide](/languages/java/lambda-function/) covers the functional interface model and how the JVM implements capture.

C++'s explicit capture list is more expressive than both: you control value vs reference per variable, and you can move into captures. It's also more error-prone for the same reason — the compiler doesn't prevent dangling references. Understanding [how closures work in JavaScript](/languages/javascript/closures/) adds another useful data point: JavaScript's implicit-by-reference capture model is the closest parallel to Python's, and comparing it to C++'s explicit model shows why explicit capture is the right choice for a language where object lifetimes aren't managed automatically.

## Frequently Asked Questions

### What is a lambda function in C++?

A c++ lambda function is an anonymous, inline callable defined at the point of use. Its syntax is `[capture-list](parameters) -> return-type { body }`. The capture list controls access to enclosing-scope variables. Lambdas were added in C++11 and extended significantly in C++14 and C++20. The complete specification is on [cppreference.com](https://en.cppreference.com/w/cpp/language/lambda).

### What is the difference between `[=]` and `[&]` capture?

`[=]` captures all accessible local variables by value — the lambda gets copies at the moment of capture, and later changes to the originals have no effect. `[&]` captures by reference — the lambda reads and writes the originals directly. Prefer `[=]` when the lambda might outlive the enclosing scope. Use `[&]` only when you need to modify the originals and the lifetime is guaranteed safe (the lambda won't outlive the captured variables).

### Can a C++ lambda be stored and called later?

Yes. Store it in an `auto` variable for simple cases, or in `std::function<ReturnType(ArgTypes...)>` when you need a concrete, named type — for example, to put it in a container or a member variable. `std::function` introduces type-erasure overhead. For performance-critical paths, prefer the `auto` variable or a template parameter.

### What is a c++ generic lambda and when should I use one?

A generic lambda uses `auto` for one or more parameter types (available from C++14). The compiler generates a templated `operator()`, producing a separate instantiation per distinct argument type. Use a generic lambda when you want a compact callable that works across multiple types — for example, a generic comparator or a visitor that handles different node types in a variant.

### Can a lambda in C++ capture member variables directly?

Not directly — in a member function, lambdas can capture `this` (by pointer) or use C++14 init captures to copy individual members by value. `[timeout = this->timeout_ms]` creates a lambda-owned copy of `timeout_ms` with no pointer dependency on the object. C++17 added `[*this]` to capture the entire object by value, which is useful when the lambda needs access to multiple members and the object may be destroyed before the lambda runs.

## Where to Go Next

Working with a c++ lambda function becomes natural once the capture model is solid. The next concept to understand is `std::function` and its type-erasure overhead — knowing when that cost is acceptable versus when a template parameter performs better is a decision you'll make frequently in modern C++ code.

For a broader view of how callable patterns translate across languages, the [Python design patterns guide](/languages/python/design-patterns/) covers the strategy and command patterns — both map directly to lambda-based designs in C++. The evolution of C++ lambda semantics from C++11 through C++23, including the proposal papers behind init captures and generic lambdas, is tracked publicly at [isocpp.org](https://isocpp.org).
