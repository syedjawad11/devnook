---
title: "How to Use Lambda Functions in Go — Anonymous Functions and Closures Explained"
description: "Learn how to use lambda functions in Go with anonymous function syntax, closures, and real-world patterns. Includes gotchas and testing tips."
published_date: "2026-05-02"
category: "languages"
language: "go"
concept: "use-lambda-function"
template_id: "lang-v2"
tags: ["go", "use-lambda-function", "anonymous-function", "closures", "higher-order-functions"]
difficulty: "intermediate"
related_posts: []
related_tools: []
og_image: "/og/languages/go/use-lambda-function.png"
---

# How to Use Lambda Functions in Go — Anonymous Functions and Closures Explained

You need to sort a slice of structs by a custom field, pass a one-off comparator to an HTTP middleware, or launch a goroutine with some captured state — but Go has no `lambda` keyword. If you are coming from Python or JavaScript, the syntax for how to use lambda functions in Go feels unfamiliar at first. Pair this guide with [Go Goroutines Explained](/languages/go/goroutines) to see how anonymous functions power concurrent patterns in Go.

## The Problem

```go
package main

import (
    "fmt"
    "sort"
)

// A named function used exactly once — just to sort by age
func sortByAge(people []Person, i, j int) bool {
    return people[i].Age < people[j].Age
}

type Person struct {
    Name string
    Age  int
}

func main() {
    people := []Person{
        {"Amira", 28},
        {"Carlos", 17},
        {"Devi", 34},
    }
    sort.Slice(people, func(i, j int) bool {
        return sortByAge(people, i, j) // extra indirection
    })
    fmt.Println(people)
}
```

This approach works but introduces unnecessary indirection. The `sortByAge` function pollutes the package namespace even though it is used exactly once. It also separates the sorting logic from the `sort.Slice` call, forcing readers to jump between two locations to understand a single operation. In larger codebases with dozens of one-off comparators, this pattern creates maintenance overhead — each comparator needs a descriptive name, and the function signature must match the expected callback format exactly.

## The Go Solution: Anonymous Functions (Lambdas)

Go does not have a `lambda` keyword, but it provides **function literals** — anonymous functions that you define inline and can pass as values. They are Go's direct equivalent to lambda functions in Python or arrow functions in JavaScript.

```go
package main

import (
    "fmt"
    "sort"
)

type Person struct {
    Name string
    Age  int
}

func main() {
    people := []Person{
        {"Amira", 28},
        {"Carlos", 17},
        {"Devi", 34},
    }

    // Anonymous function passed directly — no named function needed
    sort.Slice(people, func(i, j int) bool {
        return people[i].Age < people[j].Age // captures 'people' from outer scope
    })

    fmt.Println(people) // [{Carlos 17} {Amira 28} {Devi 34}]
}
```

The anonymous function is defined at the exact point where `sort.Slice` needs it. It captures the `people` variable from the enclosing scope — this is a **closure**. No package-level name pollution, no indirection. The comparator logic lives next to the call that uses it, making the code self-documenting. Go treats function literals as first-class values: you can assign them to variables, pass them as arguments, return them from other functions, and store them in structs.

## How Anonymous Functions Work in Go

Function literals in Go are closures by default. When a function literal references a variable from its enclosing scope, the compiler captures that variable **by reference**, not by value. This means the anonymous function sees the current value of the captured variable at the time it executes, not the value at the time it was defined.

Go's type system treats functions as first-class types. You can define a function type explicitly:

```go
type Predicate func(int) bool
```

This lets you write higher-order functions that accept or return functions with clear, documented signatures. The `http.HandlerFunc` type in the standard library is a well-known example — it is defined as `type HandlerFunc func(ResponseWriter, *Request)`, turning any matching function literal into an HTTP handler.

Unlike JavaScript, Go does not have `this` binding issues with anonymous functions. Go methods have explicit receivers, and function literals are not methods. There is no implicit context that changes based on how the function is called. This eliminates an entire class of bugs that JavaScript developers struggle with when using callbacks.

Function literals can also be immediately invoked — a pattern used heavily with goroutines. The syntax `func() { ... }()` defines and calls the function in a single statement.

## Going Further — Real-World Patterns

**Pattern 1: HTTP Middleware with Closures**

```go
package main

import (
    "log"
    "net/http"
    "time"
)

// withLogging wraps a handler and logs request duration
func withLogging(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()                          // captured at call time
        next.ServeHTTP(w, r)                         // delegate to the original handler
        log.Printf("%s %s took %v", r.Method, r.URL.Path, time.Since(start))
    }
}

func main() {
    hello := func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("Hello, world"))
    }
    http.HandleFunc("/", withLogging(hello))
    http.ListenAndServe(":8080", nil)
}
```

The `withLogging` function returns a new anonymous function that wraps the original handler. The returned closure captures `next` from its enclosing scope, allowing it to delegate after recording the start time. This is the standard middleware pattern in Go's HTTP ecosystem — libraries like chi and gorilla/mux use this exact approach. Each middleware layer returns a closure that wraps the next handler.

**Pattern 2: Goroutine Launchers with Captured Variables**

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    urls := []string{
        "https://api.example.com/users",
        "https://api.example.com/posts",
        "https://api.example.com/comments",
    }

    var wg sync.WaitGroup
    for _, url := range urls {
        wg.Add(1)
        go func(u string) { // pass url as parameter to avoid capture bug
            defer wg.Done()
            fmt.Printf("Fetching %s\n", u)
            // In production: resp, err := http.Get(u)
        }(url) // immediately invoke with current url value
    }
    wg.Wait()
}
```

Each goroutine receives its own copy of `url` via the function parameter `u`. Passing the loop variable as an argument instead of capturing it directly prevents the classic closure-over-loop-variable bug where all goroutines end up processing the last URL in the slice.

## What to Watch Out For

**Loop variable capture in goroutines.** Before Go 1.22, the loop variable in a `for range` loop was reused across iterations. Capturing it in a goroutine without shadowing meant every goroutine shared the same variable, which held the last iteration's value by the time the goroutines executed. The fix was shadowing (`url := url`) or passing the variable as a function parameter. Go 1.22 changed this behaviour — each iteration now creates a new variable — but codebases targeting older versions must still use the workaround.

**Excessive closure allocation in hot paths.** Every function literal that captures variables allocates a closure struct on the heap. In tight loops processing millions of elements, this creates garbage collection pressure. Profile with `go tool pprof` before assuming closures are free. For hot paths, consider extracting the logic into a named function that takes the captured values as explicit parameters.

**Nil function values.** A variable of function type defaults to `nil` in Go. Calling a nil function panics at runtime with no compile-time warning. Always initialise function variables before use or check for nil explicitly with `if fn != nil { fn() }`.

## Under the Hood: Performance & Mechanics

When the Go compiler encounters a function literal, it generates two things: a regular function (compiled like any other) and a closure struct that holds pointers to captured variables. If the function literal captures nothing, the compiler optimises away the closure struct entirely — the function literal becomes a plain function pointer with zero overhead.

For closures that do capture variables, escape analysis determines where those variables live. If a local variable is captured by a closure that outlives the current stack frame (for example, a closure returned from a function or passed to a goroutine), that variable escapes to the heap. You can inspect escape decisions with `go build -gcflags="-m"`:

```
./main.go:15:6: moved to heap: count
./main.go:17:14: func literal escapes to heap
```

The performance difference between a named function and an equivalent closure is negligible for most workloads. The Go compiler inlines small functions regardless of whether they are named or anonymous. A closure that captures a single integer adds roughly 8 bytes of heap allocation per invocation — trivial unless you are creating millions of closures per second.

The `func` type in Go carries a single pointer internally — either a direct function pointer (for non-capturing literals) or a pointer to the closure struct. Function calls through a `func` variable use an indirect call, which prevents CPU branch prediction in some cases. For extremely hot paths (sub-microsecond loops), this indirection can show up in benchmarks, but it rarely matters in application code.

## Advanced Edge Cases

**Edge Case 1: Recursive Anonymous Functions**

```go
// This does NOT compile — fib is not yet defined when the literal references it
// fib := func(n int) int {
//     if n <= 1 { return n }
//     return fib(n-1) + fib(n-2) // compile error: undefined fib
// }

// Fix: declare the variable first, then assign
var fib func(n int) int
fib = func(n int) int {
    if n <= 1 {
        return n
    }
    return fib(n-1) + fib(n-2) // now fib is in scope
}
fmt.Println(fib(10)) // 55
```

Go's short variable declaration (`:=`) defines and assigns in one statement, but the function literal on the right-hand side cannot reference the variable being defined on the left. The solution is to split declaration and assignment: `var fib func(int) int` creates the variable with a nil value, then the assignment gives it the function literal that can reference `fib` by name.

**Edge Case 2: Method Values vs Function Literals**

```go
type Logger struct {
    Prefix string
}

func (l *Logger) Log(msg string) {
    fmt.Printf("[%s] %s\n", l.Prefix, msg)
}

func main() {
    logger := &Logger{Prefix: "APP"}

    // Method value — implicitly binds logger as receiver
    logFn := logger.Log
    logFn("started") // [APP] started

    // Function literal — explicitly wraps the method call
    logFn2 := func(msg string) { logger.Log(msg) }
    logFn2("ready") // [APP] ready
}
```

A method value (`logger.Log`) is already a closure that captures the receiver. It is functionally equivalent to the explicit wrapper, but the method value form is more concise and avoids allocating an additional closure struct. Use method values when you need to pass a method as a callback — they are the idiomatic Go approach.

## Testing Anonymous Functions in Go

```go
package main

import "testing"

// filterSlice accepts a predicate function and filters a slice
func filterSlice(nums []int, predicate func(int) bool) []int {
    var result []int
    for _, n := range nums {
        if predicate(n) {
            result = append(result, n)
        }
    }
    return result
}

func TestFilterSlice(t *testing.T) {
    tests := []struct {
        name      string
        input     []int
        predicate func(int) bool
        expected  []int
    }{
        {"positive numbers", []int{3, -1, 4, -5, 9}, func(n int) bool { return n > 0 }, []int{3, 4, 9}},
        {"even numbers", []int{1, 2, 3, 4, 5}, func(n int) bool { return n%2 == 0 }, []int{2, 4}},
        {"all pass", []int{10, 20}, func(n int) bool { return true }, []int{10, 20}},
        {"none pass", []int{10, 20}, func(n int) bool { return false }, nil},
    }

    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            got := filterSlice(tc.input, tc.predicate)
            if len(got) != len(tc.expected) {
                t.Errorf("got %v, want %v", got, tc.expected)
            }
        })
    }
}
```

Table-driven tests are Go's standard testing pattern, and they pair naturally with anonymous functions. Each test case supplies a different predicate lambda as part of the test struct. The `t.Run` call creates a named subtest, making failures easy to identify. This approach tests the higher-order function `filterSlice` by injecting different behaviours through its function parameter — the same technique applies to testing middleware, validators, and any function that accepts a callback.

## Summary

Go uses `func` literals instead of a `lambda` keyword, but the concept is identical: anonymous, inline functions that can capture variables from their enclosing scope. Closures in Go capture variables by reference, which means mutations inside the closure are visible outside it. Use anonymous functions for sort comparators, HTTP middleware, goroutine launchers, and any situation where a named function adds unnecessary indirection. For reusable logic, prefer named functions. Understanding how to use lambda functions in Go — and the closure capture semantics that come with them — is essential for writing idiomatic, concurrent Go code.
