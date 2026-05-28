---
title: "How to Catch Exception in Kotlin — try/catch, runCatching & Best Practices"
description: "Learn how to catch exceptions in Kotlin using try/catch, finally, and runCatching. Includes real-world patterns, edge cases, and testing tips."
published_date: "2026-05-09"
category: "languages"
language: "kotlin"
concept: "catch-exception"
linkAnchors:
  - "kotlin catch exception"
  - "catch exception"
template_id: "lang-v5"
tags: ["kotlin", "exception-handling", "try-catch", "error-handling", "runCatching"]
difficulty: "intermediate"
related_posts: []
related_tools: []
og_image: "/og/languages/kotlin/catch-exception.png"
---

Every Kotlin developer eventually encounters a moment where a perfectly written function crashes at runtime — an API call times out, a user submits malformed input, or a file simply isn't where you expect it to be. Kotlin removes checked exceptions entirely, unlike Java, which means the compiler won't remind you to handle them. That makes it easy to miss error paths until they cause problems in production. Kotlin provides `try/catch/finally`, the expression-form of `try`, and the `runCatching` function to handle these failures cleanly and idiomatically.

## What is Exception Handling in Kotlin?

Exception handling is the mechanism for responding to runtime errors without terminating the program. When an unexpected condition arises — a network timeout, an invalid cast, a division by zero — the JVM throws an exception object that travels up the call stack until something catches it.

Kotlin's exception system differs from Java's in one important way: **all exceptions are unchecked**. There is no `throws` declaration, no `checked` annotation. The compiler trusts you to decide what to handle. This keeps APIs cleaner but shifts the responsibility entirely to the developer.

The exception hierarchy follows the JVM: `Throwable` is the root, with `Exception` and `Error` as its two main branches. `Exception` covers recoverable conditions — `NumberFormatException`, `IllegalArgumentException`, `IOException`. `Error` covers JVM-level catastrophes like `OutOfMemoryError` and `StackOverflowError`. You should almost never catch `Error` — by the time one occurs, the JVM is in a state where meaningful recovery is impossible.

One characteristic that sets Kotlin apart: `try` is an **expression**, not just a statement. It can return a value, which enables concise error-fallback patterns without needing temporary variables or early returns.

## Basic Syntax — try/catch/finally

The foundational structure in Kotlin mirrors what Java developers already know, but with a cleaner feel:

```kotlin
fun parseAge(input: String): Int {
    return try {
        input.trim().toInt()
    } catch (e: NumberFormatException) {
        println("Invalid age format: '${input}'. Defaulting to 0.")
        0 // try is an expression — this value is returned
    } finally {
        println("parseAge() attempt complete") // always executes
    }
}

fun main() {
    println(parseAge("25"))   // 25
    println(parseAge("abc"))  // Invalid age format: 'abc'. Defaulting to 0.  →  0
}
```

Several important mechanics are at work here. The `catch` block only triggers when a `NumberFormatException` is thrown — any other exception propagates up uncaught. The `finally` block executes regardless of whether an exception occurred, making it the right place for cleanup (closing streams, releasing locks, logging). Because `try` is an expression, the function returns the result of the `try` block on success or the result of the `catch` block on failure — no intermediate variable needed.

You can stack multiple `catch` blocks to handle different exception types separately:

```kotlin
fun readConfig(path: String): String {
    return try {
        java.io.File(path).readText()
    } catch (e: java.io.FileNotFoundException) {
        println("Config not found at $path, using defaults.")
        ""
    } catch (e: java.io.IOException) {
        println("I/O error reading config: ${e.message}")
        ""
    } finally {
        println("Config read attempt finished.")
    }
}
```

Each `catch` is checked in order — the first matching type wins. Place more specific exceptions before broader ones, or the compiler will warn you that the specific handler is unreachable.

## Going Further — Real-World Patterns

Kotlin's standard library offers a functional alternative to nested `try/catch` blocks through `runCatching`.

**Pattern 1: runCatching + fold**

`runCatching` wraps a block in a `Result<T>` object, representing either success or failure. It is implemented as an inline function with zero boxing overhead — the `Result` type is an inline value class on the JVM.

```kotlin
import java.net.URL

fun fetchPageTitle(url: String): String {
    return runCatching {
        URL(url).readText().substringAfter("<title>").substringBefore("</title>")
    }.fold(
        onSuccess = { title -> title.trim() },
        onFailure = { error ->
            println("Failed to fetch '$url': ${error.message}")
            "Untitled"
        }
    )
}

fun main() {
    println(fetchPageTitle("https://kotlinlang.org"))
    println(fetchPageTitle("https://invalid.nonexistent.url"))
}
```

`fold` provides two branches — success and failure — in a single expression. Alternatively, use `.getOrNull()` when you just want `null` on failure, or `.getOrElse { fallback }` for a computed fallback value. This pattern shines in pipeline-style code where you are chaining transformations and want to propagate failure without propagating exceptions.

**Pattern 2: Custom exception classes**

Custom exceptions communicate intent precisely. When a generic `IllegalArgumentException` is thrown, the catch site has no way to distinguish between different invalid-argument conditions. A purpose-built class fixes this:

```kotlin
class InvalidUserInputException(
    val field: String,
    val received: String,
    cause: Throwable? = null
) : Exception("Invalid value '$received' for field '$field'", cause)

fun validateEmail(email: String): String {
    if (!email.contains("@")) {
        throw InvalidUserInputException(field = "email", received = email)
    }
    return email.lowercase()
}

fun processRegistration(email: String) {
    try {
        val normalized = validateEmail(email)
        println("Registered: $normalized")
    } catch (e: InvalidUserInputException) {
        println("Validation failed on '${e.field}': ${e.message}")
    }
}

fun main() {
    processRegistration("user@example.com")  // Registered: user@example.com
    processRegistration("not-an-email")       // Validation failed on 'email': ...
}
```

Custom exceptions also let you attach structured data — here, the field name and the bad value — making logs and error UIs far more useful than a plain message string.

## What to Watch Out For

**Catching Throwable instead of Exception.** `Throwable` encompasses both `Exception` and `Error`. If you write `catch (e: Throwable)`, you will catch `OutOfMemoryError`, `StackOverflowError`, and other JVM-level failures that signal a broken runtime state. Your catch block cannot meaningfully recover from them and may interfere with JVM shutdown hooks. Always catch `Exception` (or a more specific subtype) unless you have a very deliberate reason.

**Empty catch blocks.** A bare `catch (e: Exception) { }` silently swallows the error. The calling code proceeds as if nothing happened, often leading to subtly wrong state that is extremely hard to debug. At minimum, log the exception: `println(e.message)` or use a proper logging framework. If you genuinely cannot handle the exception, rethrow it or wrap it in a more contextual type.

**Exceptions in Kotlin coroutines behave differently.** A bare `try/catch` inside a `launch {}` block catches exceptions thrown directly in that block, but it does not catch exceptions propagated from child coroutines. A child coroutine failure cancels the parent scope entirely, bypassing your `catch`. For coroutine-safe error handling, use `supervisorScope` to isolate child failures, or install a `CoroutineExceptionHandler` on the scope.

## Under the Hood — Performance & Mechanics

Kotlin exceptions are JVM exceptions at runtime. The JVM's exception model follows a **zero-cost in the happy path** principle: entering a `try` block adds no measurable overhead. The cost only appears when an exception is actually thrown.

When a `throw` occurs, the JVM begins **stack unwinding** — it walks the call stack frame by frame, executing any `finally` blocks it encounters, until it finds a matching `catch` block or reaches the top of the thread. Each frame exited during unwinding has its local variables GC'd normally.

The dominant cost of exceptions is **stack trace capture**. Every `Throwable` constructor calls `fillInStackTrace()`, which captures the entire call stack as an array of `StackTraceElement` objects. On a deep call stack, this is expensive — far more than the actual throw/catch mechanism. This is why using exceptions for normal control flow (for example, catching `NoSuchElementException` to detect an empty collection) is a performance anti-pattern. Use `if/else`, `getOrNull()`, or explicit bounds checks instead.

`runCatching` wraps a `Result<T>`, which is an inline value class — on the JVM it compiles to the raw return type when possible, incurring no boxing. The `onSuccess`/`onFailure` lambdas in `fold` are also inlined at the call site. In practice, `runCatching` performs identically to a manually written `try/catch` block.

## Advanced Edge Cases

**Edge Case 1: Rethrowing with context — exception chaining.**

When catching and rethrowing, preserve the original exception as the `cause` so the full diagnostic chain remains intact:

```kotlin
fun loadUserPreferences(userId: String): Map<String, String> {
    return try {
        // simulated DB call
        if (userId.isBlank()) error("blank userId")
        mapOf("theme" to "dark")
    } catch (e: IllegalStateException) {
        // wrap with context, preserve cause
        throw RuntimeException("Failed to load preferences for user '$userId'", e)
    }
}
```

Calling `throw RuntimeException("...", e)` sets `e` as the `cause` of the new exception. When printed, the JVM displays both: `Caused by: java.lang.IllegalStateException: blank userId`. Without this, the original error disappears from the stack trace, and debugging becomes a guessing game.

**Edge Case 2: Exceptions thrown inside finally blocks.**

If a `finally` block itself throws an exception, it **replaces** the original exception being propagated. The first exception is silently discarded:

```kotlin
fun riskyCleanup() {
    try {
        throw IllegalStateException("original error")
    } finally {
        throw RuntimeException("cleanup failed") // swallows the original!
    }
}
// Only RuntimeException("cleanup failed") propagates — the original is lost
```

This is one of the most insidious bugs in exception-heavy code. The fix is to wrap the `finally` body in its own `try/catch` and log any failure separately rather than letting it escape.

## Testing Exception Handling in Kotlin

The standard testing frameworks for Kotlin are JUnit 5 (with `assertThrows`) and the built-in `kotlin.test` library (with `assertFailsWith`). Both let you assert that a specific exception type is thrown, inspect its message and cause, and verify that the right path executed.

```kotlin
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

class ExceptionHandlingTest {

    @Test
    fun `validateEmail throws InvalidUserInputException for missing at-sign`() {
        val ex = assertThrows<InvalidUserInputException> {
            validateEmail("not-an-email")
        }
        assertEquals("email", ex.field)
        assertTrue(ex.message!!.contains("not-an-email"))
    }

    @Test
    fun `parseAge returns 0 for non-numeric input`() {
        assertEquals(0, parseAge("abc"))
    }

    @Test
    fun `runCatching returns failure result on exception`() {
        val result = runCatching { parseAge("xyz").also { check(it > 0) } }
        assertTrue(result.isFailure)
        assertNull(result.getOrNull())
    }
}
```

Testing `runCatching` results directly — asserting `.isFailure`, checking `.exceptionOrNull()` — keeps tests readable without relying on thrown exception semantics. For exception paths involving external dependencies (HTTP clients, databases), use MockK or Mockito to make the dependency throw a specific exception type, then assert your error-handling logic responds correctly.

## Quick Reference

- `try { } catch (e: Type) { } finally { }` — standard exception handling
- `try` is an expression — it can return a value directly
- All Kotlin exceptions are unchecked — no `throws` declaration needed
- `runCatching { }` — functional alternative returning `Result<T>`
- Catch specific types, not `Exception` or `Throwable` broadly
- Never swallow exceptions silently — always log or rethrow
- `finally` always runs — but exceptions thrown inside it erase the original
- Avoid exceptions for control flow — `fillInStackTrace()` is expensive

## Next Steps

After mastering basic exception handling in Kotlin, the logical next area is **coroutine exception handling** — `CoroutineExceptionHandler`, `supervisorScope`, and how structured concurrency changes exception propagation in async code. From there, consider **sealed class result types** as an architectural alternative to exceptions for expected failure cases, making error handling part of the type system rather than a runtime surprise. You might also explore how [Kotlin data classes](/languages/kotlin/data-class/) pair well with sealed result types to model structured errors. Check the Kotlin language hub for related guides on coroutines and idiomatic error modelling.
