---
actual_word_count: 1219
category: languages
concept: goroutines
description: Goroutines are Go's secret weapon for concurrent code. Learn go keyword,
  channels, WaitGroups, and when goroutines beat threads.
difficulty: intermediate
language: go
og_image: og-default
published_date: '2026-04-13'
related_cheatsheet: ''
related_content: []
related_posts:
- /languages/go/channels
- /languages/go/context
- /languages/javascript/async-await
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"Go Goroutines Explained: Concurrency\
  \ Made Simple\",\n  \"description\": \"Goroutines are Go's secret weapon for concurrent\
  \ code. Learn go keyword, channels, WaitGroups, and when goroutines beat threads.\"\
  ,\n  \"datePublished\": \"2026-04-13\",\n  \"author\": {\"@type\": \"Organization\"\
  , \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\": \"Organization\", \"name\"\
  : \"DevNook\", \"url\": \"https://devnook.dev\"},\n  \"url\": \"https://devnook.dev/languages/\"\
  \n}\n</script>"
tags:
- go
- goroutines
- concurrency
- channels
- waitgroups
template_id: lang-v1
title: 'Go Goroutines Explained: Concurrency Made Simple'
---

Golang goroutines are lightweight concurrent functions that let you run thousands of tasks simultaneously without the memory overhead of traditional threads. They're the foundation of Go's concurrency model and the reason Go excels at building high-performance servers and concurrent applications.

## What is a Goroutine in Go?

A goroutine is a function that runs concurrently with other functions in your Go program. Unlike operating system threads, goroutines are managed by the Go runtime and are extremely lightweight — you can spawn thousands of them with minimal memory overhead (typically 2KB per goroutine vs 1MB+ per OS thread).

Go's scheduler multiplexes goroutines onto a small number of OS threads, automatically handling the complexity of context switching and load balancing. When you prefix a function call with the `go` keyword, the Go runtime creates a new goroutine and executes that function concurrently while the calling function continues executing.

The Go runtime uses a work-stealing scheduler that efficiently distributes goroutines across available CPU cores, making concurrent code both simple to write and performant to run.

## Why Go Developers Use Goroutines

Goroutines solve the problem of handling multiple tasks simultaneously without blocking program execution. When building a web server that handles thousands of concurrent requests, spawning a goroutine for each request lets your server remain responsive without the memory overhead of thread-per-request models.

API clients use goroutines to fetch data from multiple endpoints simultaneously, reducing total request time from sequential seconds to concurrent milliseconds. Instead of waiting for each API call to complete before starting the next, you fire off all requests concurrently and collect results as they arrive.

Background processing tasks like sending emails, processing images, or generating reports run in goroutines without blocking the main application flow. A user uploads a file, your handler immediately returns a success response, and a goroutine handles the time-consuming processing work asynchronously.

## Basic Syntax

The simplest goroutine is a function call prefixed with `go`. Here's a basic example showing concurrent execution:

```go
package main

import (
    "fmt"
    "time"
)

func printMessage(msg string) {
    // Simulate some work with a delay
    time.Sleep(1 * time.Second)
    fmt.Println(msg)
}

func main() {
    // Launch goroutine - runs concurrently
    go printMessage("Hello from goroutine")
    
    // Main function continues immediately
    printMessage("Hello from main")
    
    // Wait for goroutine to complete
    time.Sleep(2 * time.Second)
}
```

This demonstrates goroutine basics: the `go` keyword spawns a concurrent function, and both `printMessage` calls execute simultaneously rather than sequentially. The `time.Sleep` at the end prevents the main function from exiting before the goroutine completes — a common pattern we'll improve shortly.

## A Practical Example

Real applications use channels and `sync.WaitGroup` to coordinate goroutines properly. Here's a concurrent URL fetcher that demonstrates production-ready patterns:

```go
package main

import (
    "fmt"
    "io"
    "net/http"
    "sync"
    "time"
)

// FetchResult holds the URL and response or error
type FetchResult struct {
    URL      string
    BodySize int
    Duration time.Duration
    Error    error
}

func fetchURL(url string, results chan<- FetchResult, wg *sync.WaitGroup) {
    defer wg.Done() // Signal completion when function exits
    
    start := time.Now()
    resp, err := http.Get(url)
    
    if err != nil {
        results <- FetchResult{URL: url, Error: err}
        return
    }
    defer resp.Body.Close()
    
    body, err := io.ReadAll(resp.Body)
    results <- FetchResult{
        URL:      url,
        BodySize: len(body),
        Duration: time.Since(start),
        Error:    err,
    }
}

func main() {
    urls := []string{
        "https://api.github.com",
        "https://go.dev",
        "https://golang.org/doc/",
    }
    
    // Buffered channel to receive results
    results := make(chan FetchResult, len(urls))
    
    // WaitGroup to track goroutine completion
    var wg sync.WaitGroup
    
    // Launch goroutine for each URL
    for _, url := range urls {
        wg.Add(1)
        go fetchURL(url, results, &wg)
    }
    
    // Close results channel when all goroutines finish
    go func() {
        wg.Wait()
        close(results)
    }()
    
    // Process results as they arrive
    for result := range results {
        if result.Error != nil {
            fmt.Printf("Failed to fetch %s: %v\n", result.URL, result.Error)
            continue
        }
        fmt.Printf("Fetched %s: %d bytes in %v\n", 
            result.URL, result.BodySize, result.Duration)
    }
}
```

This example shows production patterns for golang goroutines: `sync.WaitGroup` tracks when all goroutines complete, channels communicate results safely between goroutines, and a separate goroutine closes the results channel after all fetchers finish. The `defer wg.Done()` ensures completion signals even if the function exits early with an error.

## Common Mistakes

**Mistake 1: Forgetting to Wait for Goroutines**

New Go developers often spawn goroutines but let `main()` exit before they complete, causing goroutines to terminate prematurely. Using `time.Sleep()` to "wait long enough" is unreliable and creates race conditions.

The fix: Use `sync.WaitGroup` to explicitly wait for goroutine completion, or use channels to signal when work finishes. For simple cases, a done channel works: `done := make(chan bool)`, send `done <- true` when work completes, and `<-done` blocks until the signal arrives.

**Mistake 2: Sharing Memory Without Synchronization**

Concurrent goroutines that modify shared variables without synchronization cause data races — one of the hardest bugs to debug. Go's race detector (`go run -race main.go`) catches these, but prevention is better.

The fix: Follow Go's concurrency principle — "don't communicate by sharing memory; share memory by communicating." Use channels to pass data between goroutines, or protect shared state with `sync.Mutex`. For simple counters or flags, use the `sync/atomic` package for lock-free operations.

**Mistake 3: Goroutine Leaks**

Creating goroutines that never exit leads to memory leaks. Common causes include blocking channel operations that never unblock, or goroutines waiting on conditions that never occur.

The fix: Always ensure goroutines have an exit path. Use `context.Context` for cancellation signals, set timeouts on blocking operations, and ensure channels used by goroutines eventually close. The pattern `select { case <-ctx.Done(): return }` provides an escape hatch for long-running goroutines.

## Goroutines vs Threads

Traditional operating system threads require significant memory (1MB+ stack space) and expensive context switching. Goroutines start with 2KB stacks that grow dynamically, and Go's scheduler handles context switching in user space, avoiding expensive kernel operations.

You can run hundreds of thousands of goroutines on modest hardware, while the same number of OS threads would exhaust system resources. The Go scheduler multiplexes goroutines onto a small pool of OS threads (typically matching CPU core count), automatically distributing work efficiently.

Use goroutines when you need massive concurrency — web servers handling thousands of connections, parallel data processing, or concurrent I/O operations. The lightweight nature and built-in channel communication make goroutines the default choice for any concurrent task in Go.

## Quick Reference

- Spawn a goroutine with `go functionName()` — execution continues immediately
- Use `sync.WaitGroup` to wait for multiple goroutines to complete
- Communicate between goroutines with channels, not shared variables
- Goroutines cost ~2KB memory; spawn thousands without concern
- Always ensure goroutines have an exit condition to prevent leaks
- Use `go run -race` to detect data races during development
- The `context` package provides cancellation and deadline support
- Buffered channels let goroutines send without blocking: `make(chan T, bufferSize)`

## Next Steps

After mastering golang goroutines, learn [channels](/languages/go/channels) to communicate safely between goroutines without shared memory. Channels are the idiomatic way to coordinate concurrent work in Go.

Explore the [context package](/languages/go/context) for cancellation, deadlines, and request-scoped values across goroutine boundaries — essential for production services where goroutines need coordinated shutdown.

Compare Go's concurrency model with [JavaScript async/await](/languages/javascript/async-await) to understand different approaches to asynchronous programming across languages.

For comprehensive Go concurrency patterns, check out the [official Go documentation on concurrency](https://go.dev/doc/effective_go#concurrency), which covers advanced patterns like worker pools, semaphores, and pipeline patterns using goroutines and channels.