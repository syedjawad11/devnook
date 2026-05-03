---
title: "How to Catch Errors in C++: Exception Handling with try, catch, and throw"
description: "Learn how to catch errors in C++ using try-catch blocks, custom exceptions, and std::exception to write robust, fault-tolerant programs."
category: languages
language: "cpp"
concept: "catch-error"
difficulty: "intermediate"
template_id: "lang-v1"
tags: ["cpp", "exception-handling", "error-handling", "try-catch", "runtime-errors"]
related_tools: []
related_posts: []
related_cheatsheet: ""
published_date: "2026-05-02"
og_image: "/og/languages/cpp/catch-error.png"
---

# How to Catch Errors in C++: Exception Handling with try, catch, and throw

C++ provides structured exception handling through `try`, `catch`, and `throw` — the mechanism that separates error-handling logic from normal program flow and prevents silent state corruption on failure. For sending HTTP requests in C++ without crashing on failure, see [How to Send an HTTP Request in C++](/languages/cpp/http-requests).

## What is Error Catching in C++?

Catching errors in C++ means intercepting exceptional conditions at runtime using structured exception handling (SEH). The mechanism consists of three keywords working in concert: `try` wraps the code that might fail, `throw` raises an exception object when something goes wrong, and `catch` intercepts that object and handles the failure.

This design separates the happy path from error handling completely. In C, error handling was typically done through return codes — a function would return `-1` or `NULL` on failure, and every call site had to check the result and propagate it manually. This produced deeply nested conditionals, invited inconsistent checking, and made it easy to silently ignore errors. C++ exceptions allow errors to propagate automatically up the call stack until a handler is found, without the intermediate frames needing to participate.

The C++ standard library defines a hierarchy of exception types rooted at `std::exception`, declared in `<stdexcept>`. The most commonly used derived types are:

- `std::runtime_error` — errors detectable only at runtime (bad input, failed I/O)
- `std::logic_error` — programming errors detectable in principle before execution (invalid arguments, out-of-range indices)
- `std::out_of_range` — index or key outside valid bounds
- `std::invalid_argument` — argument fails a precondition
- `std::bad_alloc` — thrown by `new` when memory allocation fails

When `throw` is executed, the C++ runtime begins **stack unwinding**: it walks back through every active stack frame, calling the destructor of each object in scope before moving to the next frame. This guarantees that resources acquired before the exception are released — provided they are managed by RAII wrappers like `std::unique_ptr` or `std::fstream`. The unwinding stops when a matching `catch` block is found; if none exists, `std::terminate()` is called.

## Why C++ Developers Use try-catch

Exception handling becomes indispensable in three classes of situations that arise routinely in C++ development.

**Parsing and converting user input.** The standard library function `std::stoi()` converts a string to an integer but throws `std::invalid_argument` when the string contains non-numeric characters and `std::out_of_range` when the value overflows. Checking each character manually before the call is fragile and duplicates logic already in the standard library. Wrapping the call in a `try-catch` block means the conversion attempt and the error path are colocated and readable.

**File I/O with `std::fstream`.** Opening a file that doesn't exist, reading past the end, or writing to a full disk are all conditions that can be caught as `std::ios_base::failure` when exceptions are enabled on a stream via `stream.exceptions(std::ios::failbit | std::ios::badbit)`. Without this, every read and write operation requires a manual check of `stream.fail()` or `stream.bad()`.

**Dynamic memory allocation.** Calling `new` when the system is out of memory throws `std::bad_alloc`. In long-running servers or embedded systems with constrained heaps, this exception must be caught and handled gracefully — logging the failure, releasing optional caches, or performing an orderly shutdown — rather than allowing the program to crash with an unhandled exception.

In all three cases, exceptions allow the error signal to travel up from the point of failure to the appropriate handler without burdening every intermediate function with error-propagation boilerplate.

## Basic Syntax

```cpp
#include <iostream>      // std::cerr
#include <stdexcept>     // std::runtime_error, std::invalid_argument

// Function that throws on division by zero
double safe_divide(double numerator, double denominator) {
    if (denominator == 0.0) {
        // Construct and throw a runtime_error with a descriptive message
        throw std::runtime_error("safe_divide: division by zero is undefined");
    }
    return numerator / denominator; // Normal path — no exception
}

int main() {
    try {
        // Wrap the risky call in a try block
        double result = safe_divide(10.0, 0.0);
        std::cout << "Result: " << result << "\n";
    } catch (const std::runtime_error& e) {
        // Catch by const reference — avoids slicing, avoids copying
        std::cerr << "Runtime error: " << e.what() << "\n";
    } catch (const std::exception& e) {
        // Fallback: catches any other std::exception-derived type
        std::cerr << "Unexpected error: " << e.what() << "\n";
    }
    return 0;
}
```

Catching by `const std::exception&` rather than by value preserves the dynamic type of the exception object. The `what()` method returns the message string passed to the exception constructor. Notice that the `catch` blocks are ordered from most specific to least specific — this matters because the first matching handler wins. If the order were reversed, `std::exception` would catch everything and the `runtime_error` branch would be unreachable.

## A Practical Example

A common real-world scenario is reading a configuration file where each line contains a numeric value. Parsing failures must be caught without aborting the entire program.

```cpp
#include <fstream>       // std::ifstream
#include <iostream>      // std::cerr, std::cout
#include <stdexcept>     // std::runtime_error, std::invalid_argument
#include <string>        // std::string, std::getline
#include <vector>        // std::vector

// Parse a config file where each line is an integer setting
std::vector<int> load_config(const std::string& path) {
    std::ifstream file(path);                          // Open the file
    if (!file.is_open()) {                             // Check if open succeeded
        throw std::runtime_error("Cannot open config: " + path);
    }

    std::vector<int> values;
    std::string line;
    int line_number = 0;

    while (std::getline(file, line)) {                 // Read line by line
        ++line_number;
        try {
            int value = std::stoi(line);               // Parse line as integer
            values.push_back(value);                   // Store if valid
        } catch (const std::invalid_argument&) {
            // Line is not a valid integer — skip and warn
            std::cerr << "Warning: line " << line_number
                      << " is not a valid integer, skipping.\n";
        } catch (const std::out_of_range&) {
            // Integer is too large or too small for int
            std::cerr << "Warning: line " << line_number
                      << " value out of int range, skipping.\n";
        }
    }
    return values;
}

int main() {
    try {
        auto config = load_config("settings.cfg");
        std::cout << "Loaded " << config.size() << " settings.\n";
    } catch (const std::exception& e) {
        std::cerr << "Fatal: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```

This example demonstrates a two-layer exception strategy. The inner `try-catch` inside the loop handles per-line parse errors gracefully by skipping bad lines rather than aborting. The outer `try-catch` in `main` handles fatal errors that make the entire operation impossible — such as the file not existing at all. Separating these two concerns means that a corrupt line in the middle of a config file does not prevent the rest from loading. The specific catch of `std::invalid_argument` and `std::out_of_range` (rather than a blanket `catch (...)`) ensures that unexpected errors from other sources are not silently swallowed inside the loop.

## Common Mistakes

**Mistake 1: Catching by value instead of by reference**

Writing `catch (std::exception e)` catches the exception by value, which triggers **object slicing**. When a `std::runtime_error` is thrown and caught as `std::exception` by value, the runtime_error portion of the object is truncated — only the `std::exception` base subobject is copied into `e`. The result is that `e.what()` may return a generic message rather than the specific one attached to the derived type, and any virtual methods overridden by `std::runtime_error` are no longer dispatched correctly. The fix is always to catch by `const` reference: `catch (const std::exception& e)`. The `const` is not strictly required but signals intent and prevents accidental modification of the exception object inside the handler.

**Mistake 2: Swallowing exceptions with a bare `catch (...)`**

A `catch (...)` block with an empty body silently discards every exception, including programming errors that indicate bugs. The application continues in a potentially invalid state with no indication of what went wrong. This makes debugging difficult. The correct use of `catch (...)` is either to rethrow with `throw;` after logging: `catch (...) { log_error(); throw; }`, or as a destructor safety net where any exception must be suppressed to avoid `std::terminate`. Never use `catch (...) {}` as a convenience to avoid dealing with error handling.

**Mistake 3: Throwing exceptions from destructors**

If a destructor throws an exception while the stack is already being unwound due to another in-flight exception, the C++ runtime calls `std::terminate()` — there is no recovery. This means a destructor that can throw will crash the program in any situation that involves exception propagation, including legitimate error scenarios. The solution is to mark all destructors `noexcept` (which is the default in C++11 and later), and to catch and suppress any exceptions that might arise inside them: wrap any potentially-throwing cleanup code in a `try-catch` within the destructor body.

## Exception Handling vs Error Codes

| Criterion | try-catch exceptions | Error codes (C-style) |
|---|---|---|
| Error propagation | Automatic across call stack | Manual at every call site |
| Code readability | Clear separation of logic and errors | Interleaved with normal flow |
| Performance (happy path) | Zero overhead (zero-cost model) | Branch check at every call |
| Performance (error path) | High cost (stack unwinding) | Cheap (just a return) |
| Composability with RAII | Natural — destructors called on unwind | Requires manual cleanup |
| Use in kernel/embedded code | Usually disabled | Preferred |

Exceptions are the right tool when errors are genuinely exceptional (rare), when they need to propagate through many layers, and when RAII is in use. Error codes are preferred in performance-critical inner loops, in code where exceptions are disabled by policy (many game engines, kernels, embedded firmware), or when every call site genuinely needs to make a decision based on the error type. C++23 introduces `std::expected<T, E>` as a third option: a value-return style that avoids exceptions while remaining composable.

## Under the Hood: Performance & Mechanics

C++ exception handling uses the **zero-cost exception model** on modern compilers (GCC, Clang, MSVC). On the happy path — when no exception is thrown — the generated code for a `try` block contains no branches and no runtime overhead. The exception tables exist in a separate read-only section (`.eh_frame` on ELF platforms, `.pdata`/`.xdata` on Windows PE) and are never touched unless an exception is actually thrown.

When `throw` executes, the runtime invokes the **personality function** (typically `__gxx_personality_v0` on Itanium ABI platforms). This function consults the exception tables to determine how to unwind each stack frame. For each frame, it calls the destructors of all objects with automatic storage duration in reverse order of construction. This is the mechanism that makes RAII work correctly with exceptions — `std::unique_ptr`, `std::lock_guard`, and `std::fstream` all release their resources during unwinding without any explicit cleanup code.

The cost of throwing is significant: it involves table lookups, personality function calls, and frame-by-frame traversal. The complexity is O(d), where d is the depth of the call stack between the `throw` site and the matching `catch`. Throwing an exception in a tight loop is a performance anti-pattern.

Marking a function `noexcept` has two benefits beyond documentation. First, the compiler can omit the unwinding metadata for that function's stack frame, reducing binary size. Second, the standard library uses `noexcept` on move constructors to enable move optimizations in containers: `std::vector::push_back` will only use a move constructor if it is marked `noexcept`, because a throwing move during reallocation would leave the container in a half-moved, unrecoverable state.

## Advanced Edge Cases

**Edge Case 1: Re-throwing with `throw e` versus `throw`**

Inside a catch block, there are two syntaxes for re-throwing:

```cpp
#include <iostream>
#include <stdexcept>

void rethrow_wrong() {
    try {
        throw std::runtime_error("original error");
    } catch (const std::exception& e) {
        throw e;  // WRONG: throws a copy of the base std::exception subobject
    }
}

void rethrow_correct() {
    try {
        throw std::runtime_error("original error");
    } catch (const std::exception& e) {
        throw;  // CORRECT: re-throws the original std::runtime_error in-flight
    }
}

int main() {
    try { rethrow_wrong(); }
    catch (const std::runtime_error& e) { std::cout << "Caught runtime_error\n"; }
    catch (const std::exception& e)     { std::cout << "Caught base exception\n"; }
    // Prints: "Caught base exception" — wrong type propagated

    try { rethrow_correct(); }
    catch (const std::runtime_error& e) { std::cout << "Caught runtime_error\n"; }
    catch (const std::exception& e)     { std::cout << "Caught base exception\n"; }
    // Prints: "Caught runtime_error" — correct type preserved
}
```

`throw e;` constructs a new exception from `e` using the static type of `e` — which is `std::exception&` — discarding the derived `runtime_error` identity. `throw;` re-throws the original exception object without copying, preserving its dynamic type and the original `what()` message.

**Edge Case 2: Chaining exceptions with `std::nested_exception`**

C++11 introduced `std::throw_with_nested()` and `std::rethrow_if_nested()` for building exception chains. Library code uses this to attach context to lower-level exceptions without replacing them:

```cpp
#include <iostream>
#include <stdexcept>
#include <exception>

void parse_value() {
    throw std::invalid_argument("value is not a number");
}

void load_config() {
    try {
        parse_value();
    } catch (...) {
        // Wrap the current exception in a new one, preserving the original
        std::throw_with_nested(
            std::runtime_error("load_config failed while parsing value")
        );
    }
}

void print_exception(const std::exception& e, int depth = 0) {
    std::cerr << std::string(depth * 2, ' ') << e.what() << "\n";
    try {
        std::rethrow_if_nested(e);  // Unpack nested exception if present
    } catch (const std::exception& nested) {
        print_exception(nested, depth + 1);
    }
}

int main() {
    try { load_config(); }
    catch (const std::exception& e) { print_exception(e); }
    // Output:
    //   load_config failed while parsing value
    //     value is not a number
}
```

This technique is especially useful in library code that wants to provide context about *where* a failure occurred while preserving the original cause for the application to inspect.

## Testing Exception Behavior in C++

Google Test (`gtest`) is the dominant unit-testing framework for C++ and provides dedicated macros for asserting exception behavior:

```cpp
#include <gtest/gtest.h>
#include <stdexcept>

// Function under test
double safe_divide(double a, double b) {
    if (b == 0.0) throw std::runtime_error("division by zero");
    return a / b;
}

// Test that the correct exception type is thrown
TEST(SafeDivideTest, ThrowsOnZeroDenominator) {
    EXPECT_THROW(safe_divide(10.0, 0.0), std::runtime_error);
}

// Test that the exception message is correct
TEST(SafeDivideTest, ExceptionMessageIsCorrect) {
    try {
        safe_divide(10.0, 0.0);
        FAIL() << "Expected std::runtime_error";
    } catch (const std::runtime_error& e) {
        EXPECT_STREQ("division by zero", e.what());
    } catch (...) {
        FAIL() << "Expected std::runtime_error, got a different exception";
    }
}

// Test that no exception is thrown on valid input
TEST(SafeDivideTest, NoThrowOnValidInput) {
    EXPECT_NO_THROW(safe_divide(10.0, 2.0));
}

// Test that a base-class catch still works for derived types
TEST(SafeDivideTest, CatchesAsBaseException) {
    EXPECT_THROW(safe_divide(5.0, 0.0), std::exception);
}
```

`EXPECT_THROW` verifies both that an exception is thrown and that it matches the specified type — testing with `std::exception` rather than `std::runtime_error` is intentional only when the test is checking catch-by-base behavior. Using `EXPECT_THROW(fn(), std::exception)` when you mean `std::runtime_error` allows a wrong exception type to pass the test silently. For message content, the manual `try-catch` inside the test body with `EXPECT_STREQ` is more explicit than wrapping in a lambda. `EXPECT_NO_THROW` ensures regression tests catch accidental exception introductions in code that should be nothrow.

## Quick Reference

- Always catch by `const` reference: `catch (const std::exception& e)`
- Use bare `throw;` to rethrow — never `throw e;` (avoids object slicing)
- Destructors must be `noexcept` — catch and suppress any internal exceptions
- `catch (...)` is a catch-all — always rethrow or log before swallowing
- Common types: `std::runtime_error`, `std::logic_error`, `std::bad_alloc`, `std::out_of_range`, `std::invalid_argument`
- Zero-cost model: no runtime overhead on the non-throwing happy path
- `noexcept` enables move optimizations in STL containers and reduces binary size
- Use `std::throw_with_nested` / `std::rethrow_if_nested` for exception chaining in library code

## Next Steps

- **RAII and exception safety guarantees**: understanding the strong, basic, and nothrow guarantees clarifies how to write exception-safe C++ code that never leaks resources.
- **`std::expected` (C++23)**: a value-return error-handling alternative that avoids exceptions for recoverable failures while keeping error paths explicit and composable.
- **`noexcept` and move semantics**: how marking move constructors `noexcept` enables `std::vector` to move elements during reallocation instead of copying them.
