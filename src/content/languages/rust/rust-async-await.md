---
actual_word_count: 1720
category: languages
concept: async-await
description: Learn how async/await works in Rust with futures and executors. Master
  concurrent programming with practical examples and real-world patterns.
difficulty: intermediate
language: rust
og_image: /og/languages/rust/async-await.png
published_date: '2026-04-12'
related_cheatsheet: ''
related_content: []
related_posts: []
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"How Async/Await Works in Rust\
  \ — Complete Guide\",\n  \"description\": \"Learn how async/await works in Rust\
  \ with futures and executors. Master concurrent programming with practical examples\
  \ and real-world patterns.\",\n  \"datePublished\": \"2026-04-12\",\n  \"author\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\"\
  : \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n\
  \  \"url\": \"https://devnook.dev/languages/\"\n}\n</script>"
sections_used:
- open-mental-model
- core-design-decision
- core-how-it-works
- code-before-after
- prac-when-not-to
- comp-cross-language
- close-one-thing
tags:
- rust
- async-await
- concurrency
- futures
- tokio
template_id: modular-v1
title: How Async/Await Works in Rust — Complete Guide
voice: opinionated-commentator
---

Think of an async function as a contractor who, instead of standing idle while waiting for a delivery, uses a paging system: "I'm waiting, route other jobs to me when I'm ready." The executor — Tokio, async-std — is the dispatcher. It assigns work based on who's ready rather than blocking the whole crew waiting on one truck.

What makes Rust specifically interesting is that the paging protocol isn't built into a runtime you can't inspect. It's compiled into your code. When you mark a function `async`, the Rust compiler generates an anonymous struct — a state machine — that implements the `Future` trait. Each `.await` point is a state transition in that machine. The executor drives it forward by calling `poll()`. When a future yields `Poll::Pending`, the executor moves to other work and expects to be notified when the future is ready again.

That's the model. The rest of this article fills in the precision.

## Why Rust Designed It This Way

Rust's async/await has three design choices that generated real debate before RFC 2394 settled them in 2018. I think all three were right.

**Lazy futures.** In JavaScript and Python, calling an async function starts executing it to the first `await`. In Rust, calling an async function produces a `Future` value — nothing executes. The executor has to explicitly poll it to start. This confuses developers who expect async code to "start" when invoked. But the laziness is load-bearing: it's what makes `tokio::join!` safe (no execution races when combining futures), what lets you build combinators without running code twice, and what keeps futures cheap to create before deciding to run them.

**No built-in runtime.** JavaScript has an event loop baked into V8 and Node. Python's asyncio ships in the standard library. Rust ships with nothing — you pick a dependency: `tokio`, `async-std`, or `smol`. This generates real friction. Beginners wonder why their async code won't compile and discover they need a runtime before they can do anything. I'd still argue this was the right call. Rust runs on embedded targets, in WebAssembly, in game engines, and in OS-level services. A single opinionated runtime would be overhead for contexts that don't need it, or would need to be optional anyway. Making the choice explicit is more honest than hiding it.

**Zero-cost abstraction.** Async functions compile to state machines — no heap allocation per future in the common case, no virtual dispatch, no garbage collector pressure. The trade-off is compile-time complexity and generated code that's hard to read in a debugger. The RFC 2394 discussion goes deep on alternative designs including generator-based approaches. The state machine approach won because it meets Rust's core promise: you don't pay for what you don't use.

## What the Compiler Actually Generates

When you write:

```rust
async fn fetch_price(ticker: &str) -> f64 {
    let response = http_client.get(ticker).await;
    parse_price(response)
}
```

The compiler doesn't generate a function that blocks until the price arrives. It generates an anonymous struct that implements `Future`. The struct holds all local state that needs to survive across `.await` points — in this case, the `ticker` reference, the in-progress HTTP request, and whatever `parse_price` needs. Between `.await` points, no OS thread is blocked.

The `Future` trait has one required method:

```rust
fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>
```

The executor calls `poll()`. If the HTTP response is ready, it advances to `parse_price` and eventually returns `Poll::Ready(price)`. If not ready, it returns `Poll::Pending` — and the HTTP client is responsible for registering a *waker* with the system's I/O notification mechanism (epoll on Linux, kqueue on macOS, IOCP on Windows) so the executor knows when to try again.

That waker is the key piece beginners miss. Returning `Poll::Pending` without registering a waker means the executor never polls again and the future silently stalls. This is why writing your own async primitives in Rust is harder than using them — you have to manage wakers correctly.

The executor keeps a queue of ready tasks. When a waker fires, it moves the task back to the ready queue. Tokio's default runtime uses a work-stealing thread pool across multiple OS threads. Your async code sees none of this machinery directly.

## Sequential vs Concurrent: The Difference That Matters

**Before — sequential, each call blocks the next:**

```rust
use std::time::Duration;
use std::thread;

fn fetch_repo_info(repo: &str) -> String {
    thread::sleep(Duration::from_millis(500));
    format!("info for {}", repo)
}

fn main() {
    let tokio_info = fetch_repo_info("tokio-rs/tokio");
    let serde_info  = fetch_repo_info("serde-rs/serde");
    let hyper_info  = fetch_repo_info("hyperium/hyper");
    println!("{}, {}, {}", tokio_info, serde_info, hyper_info);
    // takes ~1500ms — each request waits on the previous one
}
```

**After — concurrent, all three run on one thread:**

```rust
use tokio::time::{sleep, Duration};

async fn fetch_repo_info(repo: &str) -> String {
    sleep(Duration::from_millis(500)).await;
    format!("info for {}", repo)
}

#[tokio::main]
async fn main() {
    let (tokio_info, serde_info, hyper_info) = tokio::join!(
        fetch_repo_info("tokio-rs/tokio"),
        fetch_repo_info("serde-rs/serde"),
        fetch_repo_info("hyperium/hyper"),
    );
    println!("{}, {}, {}", tokio_info, serde_info, hyper_info);
    // takes ~500ms — all three run concurrently
}
```

`tokio::join!` drives all three futures concurrently on the same thread by interleaving them at each `.await` point. Total time matches the slowest request, not the sum of all three. This is the concrete gain from async: I/O wait time stops being serial.

## When Not to Reach for Async

Don't use async for CPU-bound work. Async gives you concurrency for I/O — while one task waits on a network response, the executor runs another task. If your task is computing a hash, running a physics simulation, or compressing a file, there's nothing to yield at. The future will poll, find nothing ready, and either block the executor thread or spin wastefully. For CPU-bound parallelism, use Rayon or `tokio::task::spawn_blocking`.

Don't use async for one-shot scripts. A CLI tool that reads a file and prints output has nothing to gain from async. Adding Tokio pulls in a runtime startup cost, a multithreaded scheduler, and a noticeably larger binary. Sync code is simpler and faster here.

Don't call blocking operations inside async functions. `std::thread::sleep` blocks the thread. `std::fs::File::open` blocks on disk I/O. Inside Tokio's executor, either of these stalls the entire worker thread — no other futures on that thread make progress until the block resolves. Use `tokio::time::sleep` and `tokio::fs::File` instead. If you must call blocking code, wrap it in `tokio::task::spawn_blocking`, which runs it on a dedicated thread pool outside the async executor.

## How Other Languages Made Different Choices

JavaScript's async model is built into the runtime. Every JS environment inherits an event loop — you don't choose one. More importantly, creating a Promise starts executing the async function to the first `await`:

```javascript
// JavaScript: execution begins the moment you call this
const pricePromise = fetchPrice("AAPL");
```

```rust
// Rust: nothing runs — this is just a value
let price_fut = fetch_price("AAPL");
// execution starts when the executor polls it
let price = price_fut.await;
```

Python's asyncio is closer to Rust's model: coroutines are also lazy and don't run until driven by an event loop. The important difference is the GIL. Python's asyncio gives you concurrency — one coroutine runs at a time, others yield — but not parallelism. Tokio can run futures on multiple OS threads in parallel.

Go takes a different approach entirely. Goroutines are green threads managed by the Go scheduler, not futures in the poll-based sense. You write blocking-looking code:

```go
func fetchPrice(ticker string) float64 {
    resp, _ := http.Get("https://api.example.com/" + ticker)
    return parsePrice(resp.Body)
}
```

The Go scheduler transparently switches goroutines at I/O points. Simpler to write. The trade-off: you give up control over when switching happens, and goroutines carry more overhead than Rust's state-machine futures.

My read: Go's model is the right default for most application code — the ergonomics win outweighs the overhead. Rust's model is the right choice when you need guaranteed memory safety across async boundaries, zero overhead on targets where a goroutine scheduler isn't viable (embedded, WASM), or the ability to plug in your own executor.

## One Thing to Take With You

Rust futures are lazy — they do nothing until polled. That's not a limitation, it's the design. It's what makes `tokio::join!` safe, what makes combinators compose correctly, and what keeps the executor from doing invisible work behind your back. When Rust async behavior feels surprising, it usually traces to expecting JavaScript's "starts on creation" semantics and getting Rust's "starts on poll" instead. Get that one fact into your mental model and the rest follows.
