---
title: "What is Exception Handling in C#? A Complete Guide with Examples"
description: "Learn how to use exception handling in C# with try-catch-finally blocks. Includes practical examples, common mistakes, and advanced edge cases."
published_date: "2026-05-09"
category: "languages"
language: "csharp"
concept: "exception-handling"
template_id: "lang-v1"
tags: ["csharp", "exception-handling", "error-handling", "try-catch", "dotnet"]
difficulty: "beginner"
related_posts: []
related_tools: []
og_image: "/og/languages/csharp/exception-handling.png"
---

Exception handling in C# is the structured mechanism that allows developers to detect, respond to, and recover from runtime errors without crashing an application. Every C# developer who writes production code needs to understand how exception handling works because unhandled exceptions terminate processes, corrupt state, and destroy user trust.

## What is Exception Handling in C#?

Exception handling is a programming pattern that separates error-detection logic from error-recovery logic. When something goes wrong during program execution — a file is missing, a network connection drops, a user enters text where a number is expected — the .NET Common Language Runtime (CLR) creates an exception object that describes the problem. This object contains the error message, the type of failure, and a full stack trace showing exactly where the error originated.

C# handles these situations through the `try-catch-finally` construct. Code that might fail goes inside a `try` block. One or more `catch` blocks specify which exception types to handle and what recovery action to take. An optional `finally` block runs cleanup logic regardless of whether an exception occurred. This three-part structure gives developers precise control over how errors propagate through an application.

The CLR uses a two-pass exception handling model. When an exception is thrown, the runtime first walks up the call stack searching for a matching `catch` block (first pass). Once it finds one, it unwinds the stack back to that handler, executing any `finally` blocks along the way (second pass). If no handler is found anywhere on the call stack, the runtime terminates the process with an unhandled exception error.

Every exception in C# inherits from the `System.Exception` base class. The framework provides dozens of built-in exception types organized into a hierarchy: `ArgumentException`, `InvalidOperationException`, `IOException`, `NullReferenceException`, and many more. Each type represents a specific category of failure, and catching the right type is fundamental to writing robust error-handling code.

## Why C# Developers Use Exception Handling

Exception handling solves the problem of unexpected failures in code that interacts with the outside world. Any operation that depends on external resources — files, databases, networks, user input — can fail in ways that are impossible to predict at compile time.

Consider a C# application that reads configuration from a JSON file at startup. The file might not exist, the disk might be full, or the JSON might be malformed. Without exception handling, any of these conditions crashes the application immediately. With a `try-catch` block, the application can fall back to default configuration, log the problem, and continue running.

Web applications built with ASP.NET Core face similar challenges constantly. A controller action that queries a SQL Server database might encounter a closed connection, a timeout, or a deadlock. Exception handling allows the application to return a meaningful HTTP 500 response with diagnostic information instead of dumping a raw stack trace to the client.

Financial and healthcare applications have even stricter requirements. In a payment processing system, a silent failure during a transaction could result in money being deducted without the purchase being recorded. Exception handling ensures that every failure path is explicitly accounted for, either by retrying the operation, rolling back the transaction, or alerting an operator.

## Basic Syntax

```csharp
using System;                              // Import the System namespace for Exception types
using System.IO;                           // Import for file I/O operations

class Program
{
    static void Main()
    {
        string filePath = "config.txt";    // Define the path to the config file

        try
        {
            string content = File.ReadAllText(filePath);  // Attempt to read the entire file
            Console.WriteLine(content);                    // Print file contents if successful
        }
        catch (FileNotFoundException ex)                   // Handle missing file specifically
        {
            Console.WriteLine($"Config file not found: {ex.FileName}");  // Report which file is missing
        }
        catch (UnauthorizedAccessException ex)             // Handle permission errors
        {
            Console.WriteLine($"Access denied: {ex.Message}");           // Report the access issue
        }
        finally
        {
            Console.WriteLine("File operation completed.");  // Runs whether or not an error occurred
        }
    }
}
```

This example demonstrates the core structure of exception handling in C#. The `try` block wraps the risky file read operation. Two `catch` blocks handle distinct failure modes: a missing file and a permissions error. The `finally` block executes unconditionally, making it the right place for cleanup actions like closing streams or releasing locks. Notice that the most specific exception type (`FileNotFoundException`) appears before the more general one — C# requires this ordering because it matches catch blocks from top to bottom.

## A Practical Example

```csharp
using System;

class InputValidator
{
    static void Main()
    {
        int userAge = 0;                                     // Will store the validated age
        bool validInput = false;                             // Tracks whether input is valid

        while (!validInput)                                  // Keep asking until we get valid input
        {
            Console.Write("Enter your age: ");               // Prompt the user
            string rawInput = Console.ReadLine();            // Read the raw string input

            try
            {
                userAge = Convert.ToInt32(rawInput);         // Attempt to convert string to integer

                if (userAge < 0 || userAge > 150)            // Validate the range after conversion
                {
                    throw new ArgumentOutOfRangeException(   // Throw a custom exception for bad range
                        nameof(userAge),
                        $"Age must be between 0 and 150, got {userAge}");
                }

                validInput = true;                           // Mark as valid only if no exception thrown
            }
            catch (FormatException)                          // Handles non-numeric input like "abc"
            {
                Console.WriteLine("Please enter a whole number, not text.");
            }
            catch (OverflowException)                       // Handles numbers too large for Int32
            {
                Console.WriteLine("That number is too large. Enter a reasonable age.");
            }
            catch (ArgumentOutOfRangeException ex)           // Handles the custom range validation
            {
                Console.WriteLine(ex.Message);
            }
        }

        Console.WriteLine($"Your age is {userAge}.");        // Confirmed valid input
    }
}
```

This example models a real scenario that junior developers encounter frequently: validating console input with multiple failure modes. The `Convert.ToInt32` method throws a `FormatException` when the input is not a number and an `OverflowException` when the number exceeds the `Int32` range. The code also demonstrates throwing a custom exception (`ArgumentOutOfRangeException`) for business logic validation, which keeps all error handling unified in the same `catch` structure. The `while` loop ensures the program retries until the user provides a valid value. Each `catch` block provides a specific, helpful error message rather than a generic failure notice. This pattern makes the application resilient and user-friendly without sacrificing clarity in the code.

## Common Mistakes

**Mistake 1: Catching System.Exception Everywhere**

A common anti-pattern is wrapping every method in `catch (Exception ex)` and swallowing the error. This hides bugs completely. If a `NullReferenceException` occurs inside the `try` block, a generic `catch` block silently absorbs it, and the developer never knows the code has a null reference bug. The fix is to catch only the specific exceptions you expect and know how to handle. Let unexpected exceptions propagate upward to a global handler where they can be logged and investigated. Catch `IOException` when doing file work. Catch `HttpRequestException` when making API calls. Never catch `Exception` unless you re-throw it after logging.

**Mistake 2: Using Empty Catch Blocks**

Writing `catch (Exception) { }` with no body is one of the most dangerous patterns in C#. It tells the runtime to completely ignore the error. The application continues in a potentially corrupted state, and no diagnostic information is recorded anywhere. At minimum, an empty catch block should log the exception using a logging framework. The fix is straightforward: always include at least `Console.WriteLine(ex.ToString())` during development, and a proper structured log call in production code.

**Mistake 3: Using throw ex Instead of throw**

When re-throwing an exception inside a catch block, writing `throw ex;` resets the stack trace to the current location. The original call stack — which shows where the error actually originated — is lost. This makes debugging significantly harder because the stack trace now points to the catch block instead of the real source. The fix is to use `throw;` without specifying the exception variable. This preserves the entire original stack trace, giving developers the full picture when diagnosing the failure.

## Exception Handling vs Error Codes

Exception handling and error codes represent two fundamentally different philosophies for dealing with failures. C# uses structured exception handling as its primary mechanism, while languages like C and Go rely on return-value-based error signaling.

| Aspect | Exception Handling | Error Codes |
|--------|-------------------|-------------|
| Error flow | Separate from normal code | Mixed with normal return values |
| Ignoring errors | Compiler/runtime enforces handling | Easy to silently ignore |
| Performance (happy path) | Near zero overhead | Zero overhead |
| Performance (error path) | Expensive (stack unwinding) | Cheap (just a return value) |
| Stack trace | Automatic and detailed | Must build manually |

Exception handling separates error logic from business logic. A method that reads a file simply calls `File.ReadAllText()` and lets the exception propagate if something fails. With error codes, every call site must check the return value, creating deeply nested `if` chains.

However, exceptions are not always the best choice. In performance-critical hot paths — such as parsing millions of records — the overhead of throwing and catching exceptions becomes measurable. In these cases, the `TryParse` pattern (e.g., `int.TryParse`) or result types like `Result<T>` avoid exception overhead entirely by signaling failure through return values. The general rule in C# is: use exceptions for truly exceptional conditions, and use return values or Try-patterns for expected failures.

## Under the Hood: Performance & Mechanics

Understanding the runtime cost of exception handling requires examining how the CLR implements the `try-catch-finally` mechanism at the JIT compilation level.

Modern versions of the .NET JIT compiler use a table-based approach for exception handling. When a method containing `try` blocks is compiled, the JIT emits a table of protected regions alongside the native code. This table maps instruction pointer ranges to their corresponding catch and finally handlers. The critical insight is that entering a `try` block adds zero runtime overhead on the happy path — no extra instructions execute when no exception is thrown.

The cost appears entirely on the exception path. When `throw` executes, the CLR performs these operations sequentially: it allocates an exception object on the managed heap, captures the current stack trace by walking every frame on the call stack, and then begins the two-pass handling process. The first pass searches upward through the call stack, consulting each method's exception table to find a matching catch clause. Exception filters (the `when` keyword) execute during this first pass, before any stack unwinding occurs. The second pass then unwinds the stack from the throw site to the handler, executing every `finally` block encountered along the way.

The stack walk is where the real expense lies. The CLR must inspect each stack frame to determine whether it contains an exception handler, and each frame may involve metadata lookups. This makes the cost of throwing an exception roughly O(n) where n is the depth of the call stack between the throw site and the nearest matching handler. In deeply nested code with many layers of abstraction, a single thrown exception can involve walking dozens or even hundreds of frames.

This is precisely why experienced C# developers avoid using exceptions for control flow. Calling `Dictionary.ContainsKey()` before accessing a value is dramatically cheaper than catching `KeyNotFoundException`. Similarly, `int.TryParse()` avoids the allocation and stack-walk overhead that `Convert.ToInt32()` incurs on invalid input. Reserve exceptions for situations that are genuinely unexpected — conditions that indicate bugs or environmental failures rather than predictable input variations.

## Advanced Edge Cases

**Edge Case 1: Exception Filters with the when Keyword**

```csharp
using System;
using System.Net;
using System.Net.Http;

try
{
    var client = new HttpClient();                          // Create an HTTP client
    var response = await client.GetAsync("https://api.example.com/data");  // Make the request
    response.EnsureSuccessStatusCode();                     // Throws if status code is not 2xx
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    Console.WriteLine("Resource not found — returning default data.");  // Handle 404 specifically
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
{
    Console.WriteLine("Rate limited — retrying after delay.");          // Handle 429 specifically
}
```

Exception filters execute during the first pass of exception handling, before the stack unwinds. This means that when a filter returns `false`, the runtime continues searching for other handlers without destroying the call stack. This is fundamentally different from catching an exception and re-throwing it, which resets the stack state. Exception filters also enable conditional handling based on exception properties without the overhead of catching, inspecting, and re-throwing.

**Edge Case 2: Exceptions in Async Methods**

```csharp
using System;
using System.Threading.Tasks;

static async Task<string> FetchDataAsync()
{
    await Task.Delay(100);                                  // Simulate async work
    throw new InvalidOperationException("Data source unavailable");  // Exception during async execution
}

static async Task Main()
{
    Task<string> task = FetchDataAsync();                   // Start the task — exception is NOT thrown here

    try
    {
        string result = await task;                         // Exception is thrown HERE when awaited
    }
    catch (InvalidOperationException ex)
    {
        Console.WriteLine($"Caught: {ex.Message}");         // Successfully caught the async exception
    }
}
```

Exceptions thrown inside `async` methods do not propagate immediately. The CLR captures the exception and stores it inside the `Task` object. The exception is only re-thrown when the task is awaited. If a task is never awaited, the exception becomes an unobserved task exception. In .NET 4.0, unobserved task exceptions crashed the process. Since .NET 4.5, they are silently swallowed by default, which can mask serious bugs. Developers can subscribe to `TaskScheduler.UnobservedTaskException` to log these hidden failures.

## Testing Exception Handling in C#

Verifying that code throws the correct exceptions under specific conditions is a critical part of any test suite. xUnit, the most widely adopted testing framework in the modern .NET ecosystem, provides dedicated assertion methods for exception testing.

```csharp
using System;
using Xunit;

public class AgeValidatorTests
{
    // Method under test
    public static int ValidateAge(string input)
    {
        int age = Convert.ToInt32(input);                   // Throws FormatException if not a number
        if (age < 0 || age > 150)
            throw new ArgumentOutOfRangeException(nameof(input), "Age must be 0-150");
        return age;
    }

    [Fact]
    public void ValidateAge_WithNonNumericInput_ThrowsFormatException()
    {
        Assert.Throws<FormatException>(() => ValidateAge("abc"));  // Verify correct exception type
    }

    [Fact]
    public void ValidateAge_WithNegativeAge_ThrowsArgumentOutOfRangeException()
    {
        var ex = Assert.Throws<ArgumentOutOfRangeException>(() => ValidateAge("-5"));
        Assert.Contains("Age must be 0-150", ex.Message);          // Verify exception message content
    }

    [Fact]
    public void ValidateAge_WithValidInput_ReturnsAge()
    {
        int result = ValidateAge("25");                            // Should not throw
        Assert.Equal(25, result);                                  // Verify the happy path
    }
}
```

The `Assert.Throws<T>()` method takes a lambda expression containing the code that should throw. It verifies both that an exception is thrown and that it matches the expected type exactly. If the code does not throw, or throws a different exception type, the test fails. The method also returns the caught exception object, enabling further assertions on properties like `Message`, `InnerException`, or custom fields. For async methods, xUnit provides `Assert.ThrowsAsync<T>()` which accepts an `async` lambda and correctly awaits the task before checking for exceptions. Testing exception paths with this level of precision ensures that error handling behaves correctly under all failure conditions and prevents regressions when refactoring.

## Quick Reference

- Catch the most specific exception type first — C# matches `catch` blocks top to bottom
- Use `throw;` to re-throw — never `throw ex;` which destroys the original stack trace
- `finally` blocks always execute, even if a `catch` block contains a `return` statement
- `try` blocks have near-zero cost when no exception is thrown — the expense is in `throw`
- Use `int.TryParse()` over `Convert.ToInt32()` when invalid input is expected, not exceptional
- Wrap disposable resources with `using` statements instead of manual `finally` cleanup
- Exception filters (`when`) evaluate without unwinding the stack — prefer them for conditional handling

## Next Steps

- **Custom exception classes** — learn how to create domain-specific exception types that carry structured error data, making catch blocks more expressive and debuggable.
- **The IDisposable pattern and using statements** — understand how `using` blocks and `IDisposable` work together with `finally` to guarantee resource cleanup for database connections, file handles, and HTTP clients.
- **Structured logging with Serilog** — explore how to capture exception details with rich, queryable log output that integrates with tools like Seq, Elasticsearch, and Application Insights for production monitoring of exception handling in C# applications.
