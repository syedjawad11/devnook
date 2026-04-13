---
actual_word_count: 1399
concept: async-await
description: Build a working concurrent web scraper in Python to learn async await
  hands-on. Master coroutines, event loops, and asynchronous execution with real code.
difficulty: intermediate
language: python
og_image: /og/languages/python/async-await.png
published_date: '2026-04-12'
related_cheatsheet: /cheatsheets/python-asyncio
related_posts:
- /languages/python/generators
- /languages/python/decorators
- /guides/concurrency-vs-parallelism
related_tools:
- /tools/python-repl
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"Async Await in Python — A Step-by-Step\
  \ Tutorial\",\n  \"description\": \"Build a working concurrent web scraper in Python\
  \ to learn async await hands-on. Master coroutines, event loops, and asynchronous\
  \ execution with real code.\",\n  \"datePublished\": \"2026-04-12\",\n  \"author\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\"\
  : \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n\
  \  \"url\": \"https://devnook.dev//\"\n}\n</script>"
tags:
- python
- async-await
- asyncio
- concurrency
- tutorial
template_id: lang-v5
title: Async Await in Python — A Step-by-Step Tutorial
---

By the end of this tutorial, you'll have a working concurrent web scraper that fetches multiple URLs simultaneously using Python's `async` and `await` syntax. This hands-on approach shows you how to use async await in Python for real-world asynchronous programming.

## What You'll Build

We'll create a **multi-URL status checker** that fetches HTTP response codes from a list of websites concurrently. Instead of waiting for each request to complete sequentially (which could take 10+ seconds for 10 URLs), our async version will complete in roughly the time of the slowest single request.

This project demonstrates the core async/await concepts: defining coroutines with `async def`, awaiting asynchronous operations, running concurrent tasks with `asyncio.gather()`, and managing the event loop. The final script will handle real network I/O, show timing comparisons, and include basic error handling for unreachable sites.

**Prerequisites:** Basic Python syntax, understanding of functions, familiarity with HTTP requests (we'll use `aiohttp` library)

## Step 1 — Setup and Synchronous Baseline

First, we'll create a synchronous version to establish a baseline. This shows what we're improving with async/await.

```python
import time
import requests

def fetch_status_sync(url):
    """Fetch HTTP status code synchronously."""
    try:
        response = requests.get(url, timeout=5)
        return url, response.status_code
    except requests.RequestException as e:
        return url, f"Error: {str(e)}"

def main_sync():
    urls = [
        "https://python.org",
        "https://github.com",
        "https://stackoverflow.com",
        "https://reddit.com",
        "https://example.com"
    ]
    
    start = time.time()
    results = [fetch_status_sync(url) for url in urls]
    elapsed = time.time() - start
    
    for url, status in results:
        print(f"{url}: {status}")
    print(f"\nTotal time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main_sync()
```

This synchronous version fetches each URL one at a time. If each request takes 1 second, five URLs will take roughly 5 seconds total. The code blocks on each `requests.get()` call, waiting for the network response before moving to the next URL. This is the exact inefficiency that async/await solves.

## Step 2 — Converting to Async Coroutines

Now we introduce `async` and `await`. A coroutine is a special function defined with `async def` that can pause execution at `await` points, allowing other code to run.

```python
import asyncio
import aiohttp
import time

async def fetch_status_async(session, url):
    """Fetch HTTP status code asynchronously."""
    try:
        async with session.get(url, timeout=5) as response:
            return url, response.status
    except Exception as e:
        return url, f"Error: {str(e)}"

async def main_async():
    urls = [
        "https://python.org",
        "https://github.com",
        "https://stackoverflow.com",
        "https://reddit.com",
        "https://example.com"
    ]
    
    start = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    
    for url, status in results:
        print(f"{url}: {status}")
    print(f"\nTotal time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main_async())
```

The `async def` keyword marks `fetch_status_async` as a coroutine. When we call it, it returns a coroutine object—not the result. The `await` keyword pauses the coroutine until the awaited operation completes, but crucially, it allows the event loop to run other coroutines during that pause. `asyncio.gather(*tasks)` runs all tasks concurrently and waits for all to complete. The `async with` context manager ensures the `aiohttp` session is properly managed.

## Step 3 — Adding Concurrent Task Control

Let's extend our scraper to show progress in real-time and limit concurrent connections to avoid overwhelming servers.

```python
import asyncio
import aiohttp
import time

async def fetch_status_async(session, url, semaphore):
    """Fetch status with concurrency control."""
    async with semaphore:  # Limit concurrent requests
        print(f"Starting: {url}")
        try:
            async with session.get(url, timeout=5) as response:
                status = response.status
                print(f"Completed: {url} -> {status}")
                return url, status
        except Exception as e:
            print(f"Failed: {url} -> {str(e)}")
            return url, f"Error: {str(e)}"

async def main_async():
    urls = [
        "https://python.org",
        "https://github.com",
        "https://stackoverflow.com",
        "https://reddit.com",
        "https://example.com",
        "https://news.ycombinator.com",
        "https://dev.to",
        "https://medium.com"
    ]
    
    start = time.time()
    
    # Limit to 3 concurrent requests
    semaphore = asyncio.Semaphore(3)
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status_async(session, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    
    print(f"\n{'='*50}")
    print("RESULTS:")
    for url, status in results:
        print(f"{url}: {status}")
    print(f"\nTotal time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main_async())
```

The `asyncio.Semaphore(3)` limits how many requests run simultaneously. When a coroutine enters `async with semaphore`, it acquires a semaphore slot. If all three slots are taken, additional coroutines wait until a slot becomes available. This prevents opening too many connections at once while still maintaining concurrency. The print statements show tasks starting and completing in interleaved order—proof that they're running concurrently, not sequentially.

## Step 4 — Handling Timeouts and Retries

Real-world async code needs robust error handling. Let's add retry logic and individual timeouts.

```python
import asyncio
import aiohttp
import time

async def fetch_with_retry(session, url, semaphore, max_retries=2):
    """Fetch with retry logic and timeout handling."""
    async with semaphore:
        for attempt in range(max_retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                async with session.get(url, timeout=timeout) as response:
                    status = response.status
                    print(f"✓ {url} -> {status} (attempt {attempt + 1})")
                    return url, status
            except asyncio.TimeoutError:
                print(f"⏱ {url} timed out (attempt {attempt + 1}/{max_retries + 1})")
                if attempt == max_retries:
                    return url, "Timeout"
                await asyncio.sleep(1)  # Wait before retry
            except Exception as e:
                print(f"✗ {url} failed: {str(e)}")
                return url, f"Error: {type(e).__name__}"

async def main_async():
    urls = [
        "https://python.org",
        "https://github.com",
        "https://stackoverflow.com",
        "https://httpstat.us/200?sleep=3000",  # Slow endpoint
        "https://this-will-definitely-fail-12345.com",  # Non-existent
        "https://example.com"
    ]
    
    start = time.time()
    semaphore = asyncio.Semaphore(3)
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_retry(session, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed = time.time() - start
    
    print(f"\n{'='*50}")
    print("FINAL RESULTS:")
    for result in results:
        if isinstance(result, tuple):
            url, status = result
            print(f"{url}: {status}")
        else:
            print(f"Unexpected error: {result}")
    print(f"\nTotal time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main_async())
```

The retry logic wraps the fetch in a loop that attempts up to `max_retries + 1` times. `asyncio.TimeoutError` specifically catches timeout exceptions, while the generic `except` block handles other failures like DNS errors or connection refused. The `await asyncio.sleep(1)` between retries is itself an async operation—it doesn't block the entire program, just that specific coroutine. The `return_exceptions=True` argument in `asyncio.gather()` prevents one failing task from canceling all others.

## The Complete Code

Here's the full working status checker with all features integrated:

```python
import asyncio
import aiohttp
import time

async def fetch_with_retry(session, url, semaphore, max_retries=2):
    """Fetch URL status with retry logic and timeout handling."""
    async with semaphore:
        for attempt in range(max_retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                async with session.get(url, timeout=timeout) as response:
                    status = response.status
                    print(f"✓ {url} -> {status} (attempt {attempt + 1})")
                    return url, status
            except asyncio.TimeoutError:
                print(f"⏱ {url} timed out (attempt {attempt + 1}/{max_retries + 1})")
                if attempt == max_retries:
                    return url, "Timeout"
                await asyncio.sleep(1)
            except Exception as e:
                print(f"✗ {url} failed: {str(e)}")
                return url, f"Error: {type(e).__name__}"

async def main_async():
    """Main async function to check multiple URLs concurrently."""
    urls = [
        "https://python.org",
        "https://github.com",
        "https://stackoverflow.com",
        "https://httpstat.us/200?sleep=3000",
        "https://this-will-definitely-fail-12345.com",
        "https://example.com",
        "https://dev.to",
        "https://reddit.com"
    ]
    
    print(f"Checking {len(urls)} URLs concurrently...\n")
    start = time.time()
    
    # Limit to 3 concurrent requests
    semaphore = asyncio.Semaphore(3)
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_with_retry(session, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed = time.time() - start
    
    print(f"\n{'='*60}")
    print("FINAL RESULTS:")
    print('='*60)
    for result in results:
        if isinstance(result, tuple):
            url, status = result
            print(f"{url:50} {status}")
        else:
            print(f"Unexpected error: {result}")
    
    print(f"\n{'='*60}")
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Average time per URL: {elapsed/len(urls):.2f} seconds")
    print('='*60)

if __name__ == "__main__":
    asyncio.run(main_async())
```

Run this script and watch the URLs get fetched concurrently. The total time will be close to the slowest single request, not the sum of all requests—that's the power of async/await.

## What We Learned

- **Coroutines are defined with `async def`** and must be awaited or scheduled to run—calling them directly just returns a coroutine object
- **The `await` keyword pauses the current coroutine** without blocking the entire program, allowing the event loop to execute other coroutines
- **`asyncio.gather()` runs multiple coroutines concurrently** and collects their results in the order tasks were passed
- **`asyncio.Semaphore` controls concurrency** by limiting how many coroutines can access a resource simultaneously
- **`asyncio.run()` is the entry point** that creates the event loop, runs the main coroutine, and cleans up when done
- **Async context managers (`async with`) work like regular context managers** but with `__aenter__` and `__aexit__` as coroutines

## Where to Go Next

Extend this project by adding JSON output, saving results to a database, or building a simple FastAPI endpoint that triggers the scraper. For deeper understanding of how coroutines work under the hood, read our guide on [Python generators](/languages/python/generators), which share similar suspension mechanics.

Explore Python's broader async ecosystem in our [Python asyncio cheat sheet](/cheatsheets/python-asyncio), or learn how async/await differs from traditional threading in our [concurrency vs parallelism guide](/guides/concurrency-vs-parallelism). For testing your async functions interactively, use our [Python REPL tool](/tools/python-repl) to experiment with coroutines in real-time.