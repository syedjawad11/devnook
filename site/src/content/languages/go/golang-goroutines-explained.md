---
title: "Go Goroutines: What They Are and How to Use Them"
description: "Golang goroutines make concurrent programming easy. Learn goroutine syntax, WaitGroups, channels, and goroutine pools with runnable Go code examples."
category: "languages"
language: "go"
concept: "goroutines"
difficulty: "intermediate"
template_id: "lang-v1"
tags: [go, goroutines, concurrency, channels, sync]
related_posts: []
related_tools: []
linkAnchors:
  - "golang goroutines"
  - "goroutines in golang"
  - "goroutines golang"
published_date: "2026-06-03"
og_image: "og-default"
word_count_target: 2200
---

Imagine your Go API service calls five external endpoints before responding — a user database, inventory check, pricing engine, recommendation service, and analytics endpoint. Done sequentially, five 200ms calls stack to a full second of dead wait. Golang goroutines let you fire all five simultaneously: each call runs in its own goroutine, results arrive as they complete, and you respond in the time of the slowest single call — not the sum of all five.

This concurrency model is built into Go's design, not bolted on. Goroutines are light enough that production services routinely run tens of thousands simultaneously without strain.

## Golang Goroutines and the Go Runtime

A goroutine is a lightweight concurrent function managed by the Go runtime rather than the operating system. The distinction matters because the Go runtime schedules goroutines using an M:N model: it multiplexes M goroutines across N OS threads, where N typically equals the number of CPU cores available. On an 8-core machine, Go runs 8 OS threads and distributes goroutines across them dynamically using a work-stealing scheduler.

Two properties make goroutines fundamentally different from OS threads:

**Small, growable stacks.** An OS thread allocates 1–8MB of stack space up front, whether it needs it or not. A goroutine starts with 2KB and grows its stack dynamically as the call stack deepens — up to a configurable maximum (default 1GB). This means spawning 100,000 goroutines on a machine with 4GB RAM is entirely practical. The equivalent number of OS threads would require hundreds of gigabytes.

**User-space context switching.** When goroutines switch, the Go runtime saves and restores only the goroutine's current registers — a fraction of what a kernel context switch involves. Goroutines blocked on I/O are parked by the runtime so their OS thread is free to run other goroutines, with no kernel involvement.

The [Go documentation on effective goroutines](https://go.dev/doc/effective_go#goroutines) explains the underlying design philosophy: Go's concurrency model is built on communicating sequential processes (CSP), where goroutines are independent processes and channels are the communication mechanism. The runtime handles all scheduling complexity so your code focuses on what to do, not how to schedule it.

When a goroutine blocks — waiting for a network response, a file read, a channel receive — the Go scheduler moves it off its OS thread. That thread picks up a runnable goroutine from the ready queue. When the I/O completes, the blocked goroutine becomes runnable again and gets scheduled back onto a thread. This is why goroutines excel at I/O-heavy workloads: goroutines in golang achieve high concurrency without burning OS threads on idle waiting.

## Starting a Goroutine: Syntax and the `go` Keyword

Launching a goroutine takes one word: `go` in front of a function call.

```go
package main

import (
	"fmt"
	"time"
)

func sendNotification(userID int) {
	time.Sleep(100 * time.Millisecond) // simulate a network call
	fmt.Printf("Notification sent to user %d\n", userID)
}

func main() {
	for i := 1; i <= 5; i++ {
		go sendNotification(i)
	}

	fmt.Println("All notifications queued")
	time.Sleep(500 * time.Millisecond) // placeholder — next section shows the right approach
}
```

Five goroutines launch and run concurrently. `main` prints its line immediately and continues executing. The `time.Sleep` at the end is a fragile placeholder — if any notification takes longer than 500ms, `main` exits and kills the outstanding goroutines. You will replace it in the next section.

You can also pass an anonymous function directly to `go`, which is useful for short, one-off goroutines defined inline:

```go
go func(jobID string) {
	fmt.Printf("Processing job %s\n", jobID)
}("order-8821")
```

The `("order-8821")` at the end immediately invokes the anonymous function with that argument. Note the argument being passed explicitly — goroutines that close over loop variables instead of accepting them as parameters run into a variable capture bug covered later. For a full treatment of how closures and captures work in Go, [anonymous functions in Go](/languages/go/use-lambda-function) covers the mechanics in detail.

## Waiting for All Goroutines to Finish

`sync.WaitGroup` is the standard synchronization mechanism for waiting on a known number of goroutines. It acts as a countdown counter:

```go
package main

import (
	"fmt"
	"sync"
)

func processItem(itemID int, wg *sync.WaitGroup) {
	defer wg.Done() // always decrement, even if the function exits early
	fmt.Printf("Processed item %d\n", itemID)
}

func main() {
	var wg sync.WaitGroup
	itemIDs := []int{101, 102, 103, 104, 105}

	for _, id := range itemIDs {
		wg.Add(1)                // increment before launching
		go processItem(id, &wg) // pass pointer — never copy a WaitGroup
	}

	wg.Wait() // blocks until all five goroutines call Done
	fmt.Println("All items processed")
}
```

Two rules prevent subtle bugs here:

**Pass the WaitGroup by pointer, never by value.** Copying a `WaitGroup` copies its internal counter. Operations on the copy do not affect the original, breaking synchronization silently and without a compile-time error.

**Call `wg.Add(1)` before the `go` statement, never inside the goroutine.** If you increment inside the goroutine, the calling goroutine could reach `wg.Wait()` before the counter is incremented — `Wait` sees zero and returns immediately, leaving goroutines running unchecked.

The `defer wg.Done()` pattern is intentional: `defer` guarantees the call runs when the function returns, regardless of how many code paths exist. A goroutine that returns early due to an error still decrements the counter.

## Goroutine Pools: Limiting Concurrency

Spawning one goroutine per item works for small, bounded input. For large or unbounded input — crawling thousands of URLs, draining a message queue, processing image batches — you need to cap how many goroutines run at once. Unbounded spawning can exhaust file descriptors, saturate connection pools, or overwhelm downstream services with simultaneous requests.

The worker pool pattern fixes this: a fixed number of worker goroutines read jobs from a shared channel. Only `numWorkers` goroutines are ever active, regardless of input size:

```go
package main

import (
	"fmt"
	"sync"
)

func crawlPage(workerID int, urls <-chan string, results chan<- string, wg *sync.WaitGroup) {
	defer wg.Done()
	for url := range urls { // range on a channel blocks until a value arrives or the channel closes
		results <- fmt.Sprintf("worker-%d: crawled %s", workerID, url)
	}
}

func main() {
	pages := []string{
		"/", "/tools/", "/languages/", "/guides/", "/blog/",
		"/languages/go/goroutines", "/languages/go/interfaces",
	}

	const numWorkers = 3
	jobCh := make(chan string, len(pages))
	resultCh := make(chan string, len(pages))

	var wg sync.WaitGroup
	for i := 1; i <= numWorkers; i++ {
		wg.Add(1)
		go crawlPage(i, jobCh, resultCh, &wg)
	}

	// Feed all jobs into the channel, then close so workers stop when done
	for _, page := range pages {
		jobCh <- page
	}
	close(jobCh)

	// Close results once all workers have finished
	go func() {
		wg.Wait()
		close(resultCh)
	}()

	for result := range resultCh {
		fmt.Println(result)
	}
}
```

Closing `jobCh` is the shutdown signal. Workers use `range` over the channel, and `range` exits cleanly when the channel closes with no remaining values. The anonymous goroutine waits for all workers (`wg.Wait()`), then closes `resultCh`, which causes the `for result := range resultCh` loop in main to terminate.

This pattern is the right tool when you're building something like a parallel auditor that checks pages from a generated [sitemap](/tools/sitemap-generator-from-url) against expected routes — you want bounded concurrency, not one goroutine per page.

## Communicating Between Goroutines with Channels

Goroutines in golang and channels work together naturally. Channels give goroutines a typed, safe way to pass values without shared memory — no locks, no data races, no manual synchronization for the value transfer itself.

A channel has a type and a direction. Goroutines can receive a receive-only (`<-chan T`) or send-only (`chan<- T`) view of the same underlying channel:

```go
package main

import "fmt"

func producer(output chan<- int) {
	for i := 0; i < 5; i++ {
		output <- i
	}
	close(output) // signal that no more values are coming
}

func consumer(input <-chan int, done chan<- bool) {
	for value := range input {
		fmt.Println("received:", value)
	}
	done <- true
}

func main() {
	ch := make(chan int)
	doneCh := make(chan bool)

	go producer(ch)
	go consumer(ch, doneCh)

	<-doneCh // block until consumer signals completion
}
```

Channel directionality is enforced at compile time. A goroutine that accepts `<-chan int` cannot accidentally send on it — the compiler rejects the attempt. This matters in larger codebases where goroutines are defined far from their callers.

An **unbuffered channel** (`make(chan T)`) synchronizes sender and receiver: the sender blocks until a receiver is ready, and vice versa. Use it when both sides must acknowledge the exchange. A **buffered channel** (`make(chan T, n)`) holds up to `n` values before blocking, decoupling producer and consumer when they run at different speeds.

When designing channel-based APIs, [Go interfaces](/languages/go/interfaces) define the contracts that larger systems rely on — libraries often accept a channel-producing function rather than a concrete channel, making the code testable and the implementation swappable.

The [sync package](https://pkg.go.dev/sync) covers cases where shared state is unavoidable: `sync.Mutex` for exclusive locks, `sync.RWMutex` for read-heavy workloads, `sync.Once` for one-time initialization, and `sync.Map` for concurrent map access without a custom mutex.

## Three Goroutine Bugs You Will Write First

**Bug 1: Loop variable capture in Go 1.21 and earlier**

Before Go 1.22, goroutines launched inside a loop closed over the loop variable by reference, not by value:

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	for i := 0; i < 5; i++ {
		go func() {
			fmt.Println(i) // closes over i — all goroutines likely print 5
		}()
	}
	time.Sleep(100 * time.Millisecond)
}
```

By the time the goroutines actually run, the loop has finished and `i` is 5. All five goroutines print `5`. The fix before Go 1.22 is to pass the loop variable as an argument:

```go
for i := 0; i < 5; i++ {
	go func(n int) {
		fmt.Println(n) // each goroutine gets its own copy of i at launch time
	}(i)
}
```

Go 1.22 changed loop semantics so each iteration gets its own variable, fixing the closure capture behavior by default. Codebases that must support Go 1.21 or earlier still need the explicit copy.

**Bug 2: All goroutines are asleep — deadlock**

```
fatal error: all goroutines are asleep - deadlock!
```

This error means every goroutine in the program is blocked, and no goroutine can make progress. Common causes:

- Sending to an unbuffered channel with no goroutine waiting to receive
- Receiving from an empty channel that nobody ever writes to or closes
- Two goroutines each waiting for the other to send first (a classic circular dependency)

To diagnose: trace every channel operation in your code and verify each send has a corresponding receive — and vice versa. If a goroutine sends on a channel, something must receive from it, and the receive must actually be reachable at that point in the program's execution.

**Bug 3: Goroutine leaks**

A goroutine that blocks forever without an exit condition leaks for the lifetime of the program. Leaked goroutines accumulate over time, grow their stacks, and eventually exhaust memory. The most common cause: a goroutine waiting on a channel that nobody ever closes or writes to.

Use `context.Context` to give goroutines a cancellation path:

```go
package main

import (
	"context"
	"fmt"
)

func worker(ctx context.Context, jobs <-chan string) {
	for {
		select {
		case <-ctx.Done():
			return // context cancelled — exit cleanly
		case job, ok := <-jobs:
			if !ok {
				return // channel closed — exit cleanly
			}
			fmt.Println("Job:", job)
		}
	}
}
```

Every long-running goroutine should have a `ctx.Done()` case in its `select` statement. When the caller calls `cancel()`, every goroutine listening on that context exits within one select iteration. This is standard in Go services that require coordinated shutdown.

## Goroutines vs Threads: What Actually Differs

Here is how goroutines compare to OS threads across the dimensions that matter for real applications:

| Dimension | OS Thread | Goroutine |
|---|---|---|
| Starting stack size | 1–8 MB (fixed up front) | 2 KB (grows dynamically) |
| Creation cost | ~10–100 µs | ~0.3 µs |
| Context switch | Kernel-mode (~1 µs+) | User-space (~100 ns) |
| Practical max count | Thousands | Hundreds of thousands |
| Scheduling | OS scheduler | Go runtime scheduler |
| Communication | Shared memory + locks | Channels (or shared memory) |

For I/O-heavy workloads — HTTP servers, database clients, message queue consumers — goroutines hold a clear advantage. A Go HTTP server handling 10,000 concurrent connections spawns 10,000 goroutines without strain. The equivalent thread-per-connection model would require either a thread pool with complex hand-off logic or a prohibitive amount of memory.

For CPU-bound work, goroutines distribute across real CPU cores because the Go scheduler maps them to OS threads that can run on any core. Setting `runtime.GOMAXPROCS(n)` controls how many OS threads Go uses for goroutine execution — it defaults to the number of available CPU cores.

Compared to JavaScript's [async/await model](/languages/javascript/async-await), goroutines offer true parallelism. JavaScript's event loop is single-threaded and interleaves callbacks rather than running them simultaneously. Two goroutines can execute at exactly the same wall-clock moment on different cores; two JavaScript async functions cannot.

## Frequently Asked Questions

### How many goroutines can a Go program handle?

The language imposes no hard limit. Go programs have been benchmarked running millions of goroutines concurrently on single machines. The practical constraint is memory: each goroutine needs at minimum 2KB of stack space, so one million goroutines require at least 2GB of stack memory at minimum — and more as they do real work and their stacks grow. In practice, external limits (open file descriptors, database connection pools, API rate limits) constrain goroutine count long before memory does for most applications.

### How do I wait for all goroutines to finish in Go?

Use `sync.WaitGroup`. Call `wg.Add(1)` before launching each goroutine, put `defer wg.Done()` as the first statement inside each goroutine, and call `wg.Wait()` in the calling goroutine to block until all finish. Always pass the WaitGroup as a pointer (`&wg`), never by value. Increment with `Add` before the `go` statement, not inside the goroutine.

### What causes "all goroutines are asleep — deadlock!" in Go?

Every goroutine in the program is blocked and none can proceed. The most common cause is a channel operation with no counterpart: a send with nobody receiving, or a receive on an empty channel that nobody writes to or closes. Trace every channel in your code and verify that each send has a reachable receive, and vice versa. The Go race detector (`go run -race`) detects data races but not deadlocks; channel auditing is manual.

### When should I use a goroutine pool instead of one goroutine per task?

Use a pool when input is large or unbounded, or when goroutines hold limited external resources — database connections, open file handles, API rate budget. A pool with 10 workers processes 100,000 items without opening 100,000 connections simultaneously. For small, bounded input (a few hundred items at most) with no shared external resources, spawning one goroutine per item is simpler and works fine.

### What is the difference between buffered and unbuffered channels in Go?

An unbuffered channel (`make(chan T)`) requires a sender and receiver to be ready simultaneously — the send blocks until a goroutine receives, and vice versa. It provides strict synchronization. A buffered channel (`make(chan T, n)`) accepts up to `n` values before blocking, decoupling producer and consumer timing. Use unbuffered channels when you need to guarantee that a value was received before proceeding; use buffered channels when you want to smooth out speed mismatches between goroutines.

## What to Learn Next

Goroutines in golang are the starting point, not the finish line. Channels are the natural next concept — they are what make concurrent programs composable rather than just concurrent. Work through the producer/consumer pattern from this article, then add error propagation via a dedicated error channel, then add cancellation using `context.Context`.

After channels, study `select` statements, which let a goroutine wait on multiple channels simultaneously and handle whichever becomes ready first. Combined with `time.After`, `select` implements non-blocking channel operations and deadline-aware goroutines — patterns that appear in nearly every Go service.

From there, the worker pool structure in this article is a stepping stone to pipeline architectures: sequences of goroutine stages connected by channels, where each stage transforms and forwards values to the next. The official Go documentation on effective concurrency covers the pipeline pattern in detail, building on exactly the mechanics you practiced here.
