---
title: "How to Handle Exceptions in C++? A Complete Guide"
description: "Learn how to handle exceptions in C++ using try, catch, and throw. Covers exception hierarchies, RAII, noexcept, and real-world error handling patterns."
category: "languages"
language: "cpp"
concept: "c-handle-exception"
linkAnchors:
  - "cpp c handle exception"
  - "c handle exception"
  - "c++ exceptions"
difficulty: "intermediate"
template_id: "lang-v2"
tags: ["cpp", "exception-handling", "try-catch", "raii", "error-handling"]
related_tools: []
related_posts: []
published_date: "2026-05-09"
og_image: "/og/languages/cpp/c-handle-exception.png"
---

You call a function that opens a file, parses user input, or makes a network request. You forget to check the return code — or the function gives you no way to. The program crashes with a cryptic segfault, or worse, silently continues in a broken state. This is exactly the scenario C++ exception handling was designed to prevent.

## The Problem

```cpp
#include <iostream>
#include <cstdio>

// Naive approach: return codes that callers can ignore
int divide(int a, int b) {
    if (b == 0)
        return -1;       // magic sentinel — what if -1 is a valid result?
    return a / b;
}

int main() {
    int result = divide(10, 0);
    // caller forgets to check — continues with garbage value
    std::cout << "Result: " << result << "\n";  // prints -1, no error
    return 0;
}
```

The `divide` function returns `-1` to signal an error, but this is fundamentally broken: `-1` could be a perfectly valid division result. The caller can ignore the return code entirely, and the compiler won't complain. In deeply nested call stacks, propagating error codes through every intermediate function creates boilerplate that is easy to forget and hard to maintain. Errors accumulate silently until something catastrophic happens downstream, often far from the original failure point.

## The C++ Solution: Exception Handling

C++ exceptions provide a structured mechanism for reporting and handling errors: `throw` signals the error, `try` defines the region where errors can occur, and `catch` intercepts them. Critically, if an exception is not caught, it cannot be silently ignored — the program terminates via `std::terminate`.

```cpp
#include <iostream>
#include <stdexcept>

// Corrected: throws instead of returning a sentinel
int divide(int a, int b) {
    if (b == 0)
        throw std::invalid_argument("Division by zero");
    return a / b;
}

int main() {
    try {
        int result = divide(10, 0);               // throws
        std::cout << "Result: " << result << "\n";  // never reached
    }
    catch (const std::invalid_argument& e) {
        std::cerr << "Error: " << e.what() << "\n";  // "Division by zero"
    }
    return 0;
}
```

The error can no longer be silently ignored. The `try` block wraps the risky code. When `divide` throws, execution jumps immediately to the matching `catch` — skipping any remaining code in the `try` block. The `e.what()` method (defined in `std::exception`) returns the human-readable error message set in the constructor. The return type of `divide` remains `int` with no sentinel value necessary, keeping the interface clean and unambiguous.

## How Exception Handling Works in C++

When a `throw` statement executes, C++ performs **stack unwinding**: the runtime unwinds the call stack frame by frame, calling the destructors of all local objects in reverse order until it finds a matching `catch` handler. If no handler is found anywhere in the call chain, `std::terminate()` is called, ending the program.

**Exception matching** uses the type hierarchy: a `catch(const std::exception&)` catches any exception derived from `std::exception`. Handlers are checked top-to-bottom in the order they appear. Always catch more-specific types before more-general ones:

```cpp
try {
    // ...
}
catch (const std::invalid_argument& e) { /* most specific first */ }
catch (const std::runtime_error& e)    { /* more general */       }
catch (const std::exception& e)        { /* catch-all for stdlib */ }
catch (...)                            { /* last resort: catches anything */ }
```

**Zero-cost exception model:** On modern compilers (GCC, Clang, MSVC with `/EHsc`), exceptions in the non-throwing path add essentially zero runtime overhead — no cost when no exception is thrown. The cost is paid only when an exception is thrown, because stack unwinding is inherently expensive. This makes exceptions appropriate for genuinely exceptional conditions, not for normal control flow like loop termination or optional value absence.

## Going Further — Real-World Patterns

**Pattern 1: Custom exception hierarchy**

```cpp
#include <stdexcept>
#include <string>

// Base application exception
class AppError : public std::runtime_error {
public:
    explicit AppError(const std::string& msg)
        : std::runtime_error(msg) {}
};

// Specific error types derive from AppError
class DatabaseError : public AppError {
    int error_code_;
public:
    DatabaseError(const std::string& msg, int code)
        : AppError(msg), error_code_(code) {}
    int code() const { return error_code_; }
};

class NetworkError : public AppError {
public:
    using AppError::AppError;  // inherit constructors
};

void query_db() {
    throw DatabaseError("Connection refused", 1045);
}

int main() {
    try {
        query_db();
    }
    catch (const DatabaseError& e) {
        std::cerr << "DB error " << e.code() << ": " << e.what() << "\n";
    }
    catch (const AppError& e) {
        std::cerr << "App error: " << e.what() << "\n";
    }
}
```

Building a custom exception hierarchy lets you catch at different granularities. A top-level handler catches `AppError&` for centralised logging; a specific handler catches `DatabaseError&` to trigger a reconnect attempt. This pattern is standard in production C++ applications and keeps error handling both expressive and maintainable.

**Pattern 2: RAII for exception-safe resource management**

```cpp
#include <fstream>
#include <stdexcept>

void process_file(const std::string& path) {
    std::ifstream file(path);       // constructor opens file
    if (!file)
        throw std::runtime_error("Cannot open: " + path);

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty())
            throw std::runtime_error("Unexpected empty line");
        // even if this exception propagates, the file is closed
    }
}   // file.close() called here automatically via RAII destructor
```

**RAII (Resource Acquisition Is Initialisation)** is C++'s primary exception-safety mechanism. Because stack unwinding calls destructors, resources wrapped in RAII objects — `ifstream`, `unique_ptr`, `lock_guard` — are automatically released even when exceptions propagate. Never manage resources manually with raw `new`/`delete` in code that can throw; there is no `finally` in C++, and RAII is the replacement.

## What to Watch Out For

**1. Catching by value instead of reference**

```cpp
catch (std::exception e) { ... }         // BAD: slices the derived type!
catch (const std::exception& e) { ... }  // GOOD: preserves full type info
```

Catching by value causes **object slicing** — the derived exception's additional data (such as a custom `code()` field) is stripped away, and you're left with only the `std::exception` base portion. Always catch by `const` reference to preserve the full exception type and its data.

**2. Exceptions in destructors**

If a destructor throws while another exception is already propagating, `std::terminate()` is called immediately with no recovery possible. Since C++11, destructors are implicitly `noexcept`. Mark them explicitly and handle all errors internally:

```cpp
~MyResource() noexcept {
    try { close(); }
    catch (...) { /* log but never rethrow */ }
}
```

**3. Using exceptions for normal control flow**

Exception throwing has non-trivial runtime overhead when an exception is raised (stack unwinding, type matching). Using `throw`/`catch` to drive normal program logic — loop termination, optional-value branching, expected absence of a key — is an anti-pattern that degrades both performance and readability. For expected failure modes, prefer `std::optional` (C++17) or `std::expected` (C++23).

## Under the Hood: Performance and Mechanics

C++ implements exceptions using the **zero-cost exception model** on the Itanium ABI (Linux, macOS) and a similar structured exception handling (SEH) mechanism on MSVC. The compiler generates static **unwind tables** describing how to clean up each stack frame — these tables live in a read-only section of the binary and cost binary size, but zero CPU cycles when no exception is active.

When `throw` executes, the runtime calls `__cxa_throw` (Itanium ABI), which:

1. Allocates the exception object on a special exception-specific heap region
2. Calls `__cxa_find_matching_catch` to scan the unwind tables for a matching handler
3. Executes `_Unwind_RaiseException` to walk the stack frame by frame, running destructors via personality routines
4. Transfers control to the matching `catch` block

This process is **O(stack depth)** — a deep call stack means more unwind work. Throwing across thousands of frames carries measurable cost. For tight loops or high-frequency error conditions, `std::expected` (C++23) or `std::optional` are better choices since they carry errors as values without any unwinding.

Compile-time exception tables can be suppressed with `-fno-exceptions`, a common setting in embedded C++. This eliminates table overhead but removes RAII-safe propagation and forces error-code conventions throughout the codebase.

## Advanced Edge Cases

**Edge Case 1: `std::exception_ptr` and cross-thread exception propagation**

```cpp
#include <exception>
#include <iostream>
#include <thread>

std::exception_ptr g_ex;

void worker() {
    try {
        throw std::runtime_error("error in thread");
    }
    catch (...) {
        g_ex = std::current_exception();  // capture the active exception
    }
}

int main() {
    std::thread t(worker);
    t.join();
    if (g_ex) {
        try {
            std::rethrow_exception(g_ex);  // rethrow on main thread
        }
        catch (const std::exception& e) {
            std::cerr << "Caught from thread: " << e.what() << "\n";
        }
    }
}
```

Exceptions cannot propagate across thread boundaries automatically — an unhandled exception in a `std::thread` calls `std::terminate`. Use `std::exception_ptr` with `std::current_exception()` to capture the active exception inside a `catch (...)` block, and `std::rethrow_exception()` to replay it on another thread. This is exactly how `std::promise` and `std::future` transport exceptions between threads internally.

**Edge Case 2: `noexcept` and the `std::terminate` trap**

```cpp
void safe_func() noexcept {
    throw std::runtime_error("oops");  // compiles, but calls std::terminate!
}
```

Marking a function `noexcept` is a *contract*, not a compiler constraint: the compiler does not prevent you from throwing inside such a function. But if an exception propagates out of a `noexcept` function at runtime, `std::terminate` is called immediately — no `catch` handler anywhere in the program can intercept it. This makes `noexcept` a powerful optimisation hint (the compiler can skip generating unwind tables for the function's callers) but a dangerous one if the contract is violated. Always wrap potentially-throwing code inside a `try`/`catch (...)` when you must mark a function `noexcept`.

## Testing Exception Handling in C++

```cpp
#include <gtest/gtest.h>
#include <stdexcept>

int divide(int a, int b) {
    if (b == 0) throw std::invalid_argument("Division by zero");
    return a / b;
}

// Verify the correct exception type is thrown
TEST(DivideTest, ThrowsOnZeroDivisor) {
    EXPECT_THROW(divide(10, 0), std::invalid_argument);
}

// Verify the exception message
TEST(DivideTest, ExceptionMessageIsCorrect) {
    try {
        divide(10, 0);
        FAIL() << "Expected std::invalid_argument";
    }
    catch (const std::invalid_argument& e) {
        EXPECT_STREQ(e.what(), "Division by zero");
    }
    catch (...) {
        FAIL() << "Wrong exception type thrown";
    }
}

// Verify the happy path is clean
TEST(DivideTest, ReturnsCorrectResult) {
    EXPECT_EQ(divide(10, 2), 5);
    EXPECT_EQ(divide(-10, 2), -5);
    EXPECT_NO_THROW(divide(0, 5));
}
```

Google Test provides `EXPECT_THROW(expr, ExceptionType)` for verifying that a specific exception type is thrown. For asserting on the exception message or performing other assertions inside the catch block, use the explicit `try`/`catch`/`FAIL()` pattern. Use `EXPECT_NO_THROW(expr)` to assert that a code path is clean. When testing RAII classes and exception safety, pair with AddressSanitizer and LeakSanitizer (`-fsanitize=address,leak`) to detect resource leaks that occur during exception propagation — errors that are otherwise invisible to normal test assertions.

## Summary

C++ exception handling replaces fragile error-code conventions with a structured, un-ignorable mechanism for signalling and recovering from errors. When a `throw` executes, the runtime unwinds the stack — safely destroying all RAII-managed resources along the way — until a matching `catch` is found. Building a custom exception hierarchy derived from `std::exception` gives callers fine-grained control over what they handle and at what level. Always catch by `const` reference to avoid slicing. Mark functions `noexcept` only when you can guarantee no exception escapes. Use RAII wrappers rather than manual cleanup, since C++ has no `finally` keyword — and with RAII, it doesn't need one.