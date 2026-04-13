---
actual_word_count: 1278
category: languages
concept: promises
description: Promises replaced callback hell. Understand the Promise lifecycle, chaining,
  error handling, and how async/await simplifies it all.
difficulty: intermediate
language: javascript
og_image: /og/languages/javascript/promises.png
published_date: '2026-04-13'
related_cheatsheet: /cheatsheets/javascript-async-patterns
related_posts:
- /languages/javascript/async-functions
- /languages/javascript/fetch-api
- /guides/asynchronous-javascript-guide
related_tools:
- /tools/javascript-repl
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"JavaScript Promises Explained:\
  \ then(), catch(), and async/await\",\n  \"description\": \"Promises replaced callback\
  \ hell. Understand the Promise lifecycle, chaining, error handling, and how async/await\
  \ simplifies it all.\",\n  \"datePublished\": \"2026-04-13\",\n  \"author\": {\"\
  @type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\"\
  : \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n\
  \  \"url\": \"https://devnook.dev/languages/\"\n}\n</script>"
tags:
- javascript
- promises
- async-await
- asynchronous-programming
- error-handling
template_id: lang-v3
title: 'JavaScript Promises Explained: then(), catch(), and async/await'
---

JavaScript Promises are objects representing the eventual completion or failure of an asynchronous operation. They provide a cleaner alternative to callback-based async code and form the foundation of modern async/await syntax.

## Syntax at a Glance

```javascript
// Creating a Promise
const promise = new Promise((resolve, reject) => {
  // Async operation here
  if (success) {
    resolve(value);  // Operation succeeded
  } else {
    reject(error);   // Operation failed
  }
});

// Consuming a Promise
promise
  .then(result => console.log(result))   // Handles success
  .catch(error => console.error(error))  // Handles failure
  .finally(() => console.log('Done'));   // Runs regardless
```

The Promise constructor takes an executor function with `resolve` and `reject` callbacks. Call `resolve()` when the operation succeeds, `reject()` when it fails. Chain `.then()` for success handling and `.catch()` for errors.

## Full Working Examples

**Example 1 — Basic Promise Creation**

```javascript
const fetchUserData = (userId) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (userId > 0) {
        resolve({ id: userId, name: 'Alice' });
      } else {
        reject(new Error('Invalid user ID'));
      }
    }, 1000);
  });
};

fetchUserData(1)
  .then(user => console.log('User:', user))
  .catch(error => console.error('Error:', error.message));
// Output after 1s: User: { id: 1, name: 'Alice' }
```

This simulates an async operation using `setTimeout`. When `userId` is valid, the Promise resolves with user data; otherwise, it rejects with an error.

**Example 2 — Promise Chaining**

```javascript
const getUser = (id) => Promise.resolve({ id, email: 'user@example.com' });
const getPosts = (email) => Promise.resolve(['Post 1', 'Post 2']);
const getComments = (post) => Promise.resolve([`Comment on ${post}`]);

getUser(42)
  .then(user => {
    console.log('Fetched user:', user.email);
    return getPosts(user.email);  // Return next Promise
  })
  .then(posts => {
    console.log('Fetched posts:', posts);
    return getComments(posts[0]);
  })
  .then(comments => console.log('Comments:', comments))
  .catch(error => console.error('Chain failed:', error));
// Output:
// Fetched user: user@example.com
// Fetched posts: ['Post 1', 'Post 2']
// Comments: ['Comment on Post 1']
```

Each `.then()` receives the previous Promise's resolved value. Return a Promise from `.then()` to chain async operations sequentially. A single `.catch()` handles errors from any step.

**Example 3 — async/await Syntax**

```javascript
const fetchData = async () => {
  try {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    
    const processedData = await processInBackground(data);
    
    return { success: true, result: processedData };
  } catch (error) {
    console.error('Fetch failed:', error);
    return { success: false, error: error.message };
  }
};

// Call async function
fetchData().then(result => console.log(result));
```

The `async` keyword lets you write Promise-based code that looks synchronous. `await` pauses execution until the Promise resolves, returning the resolved value. Use `try/catch` for error handling instead of `.catch()`.

## Key Rules in JavaScript

- **Promises have three states**: pending (initial), fulfilled (resolved successfully), or rejected (failed). Once settled (fulfilled or rejected), a Promise cannot change state.
- **Always return Promises in `.then()`** if you want to chain another async operation. Forgetting `return` breaks the chain and causes the next `.then()` to receive `undefined`.
- **`.catch()` catches all upstream errors** but doesn't stop the chain — subsequent `.then()` calls still execute unless you re-throw or return a rejected Promise.
- **`await` only works inside `async` functions** (or top-level in modules). Using it elsewhere throws a syntax error.
- **Unhandled Promise rejections** log warnings in Node.js 15+ and will crash future versions. Always add `.catch()` or use `try/catch` with `await`.
- **`Promise.all()` fails fast** — if any Promise rejects, the entire operation rejects immediately, even if others are still pending.

## Common Patterns

**Pattern: Parallel Execution with Promise.all()**

```javascript
const fetchAllData = async () => {
  const [users, posts, comments] = await Promise.all([
    fetch('/api/users').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
    fetch('/api/comments').then(r => r.json())
  ]);
  
  return { users, posts, comments };
};
```

`Promise.all()` runs Promises concurrently and resolves when all complete. This is faster than sequential `await` calls when operations don't depend on each other. If any Promise rejects, the entire operation fails.

**Pattern: Race Condition Handling with Promise.race()**

```javascript
const fetchWithTimeout = (url, timeout = 5000) => {
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Request timeout')), timeout)
  );
  
  return Promise.race([
    fetch(url),
    timeoutPromise
  ]);
};

fetchWithTimeout('https://slow-api.example.com')
  .then(response => response.json())
  .catch(error => console.error(error.message));
```

`Promise.race()` resolves or rejects as soon as the first Promise settles. This pattern implements timeouts by racing the actual operation against a timeout Promise.

## When Not to Use Promises

Avoid Promises for synchronous operations — wrapping `Math.random()` in a Promise adds complexity without benefit. Use plain functions instead. For fire-and-forget operations where you don't care about completion, callbacks or event emitters are simpler. If you need to cancel operations mid-flight, AbortController with fetch or libraries like RxJS observables provide better control — Promises cannot be cancelled once started. For stream processing or handling multiple values over time, use async iterators or Node.js streams, since Promises resolve once with a single value.

## Quick Comparison: JavaScript vs Python

| | JavaScript | Python |
|---|---|---|
| **Syntax** | `new Promise((resolve, reject) => {})` | `asyncio.Future()` or `asyncio.create_task()` |
| **Async keyword** | `async function foo() {}` | `async def foo():` |
| **Await keyword** | `await promise` | `await coroutine` |
| **Error handling** | `.catch()` or `try/catch` | `try/except` with `await` |
| **Parallel execution** | `Promise.all([p1, p2])` | `asyncio.gather(t1, t2)` |
| **Built-in support** | Native since ES6 (2015) | Native since Python 3.5 (2015) |

JavaScript Promises are first-class language features, while Python's equivalent uses the `asyncio` library. JavaScript's `.then()` chaining has no direct Python equivalent — Python relies entirely on `async/await` syntax.

## Promise Lifecycle in Detail

A Promise starts in the **pending** state when created. The executor function runs immediately and synchronously. Calling `resolve(value)` transitions the Promise to **fulfilled**, and any `.then()` handlers fire with that value. Calling `reject(reason)` moves it to **rejected**, triggering `.catch()` handlers. Once fulfilled or rejected, the Promise is **settled** and its state is immutable.

```javascript
const p = new Promise((resolve) => {
  console.log('Executor runs immediately');
  setTimeout(() => resolve('done'), 100);
});

console.log('Promise created');

p.then(value => console.log('Resolved:', value));

// Output order:
// Executor runs immediately
// Promise created
// Resolved: done (after 100ms)
```

The executor runs before the Promise constructor returns. Handlers registered with `.then()` or `.catch()` execute asynchronously, even if the Promise is already settled.

## Error Handling Best Practices

Always attach a `.catch()` to Promise chains or wrap `await` calls in `try/catch`. Unhandled rejections silently fail in browsers and crash Node.js processes.

```javascript
// Bad: Unhandled rejection
fetch('/api/data').then(r => r.json());

// Good: Explicit error handling
fetch('/api/data')
  .then(r => r.json())
  .catch(err => console.error('Failed:', err));

// Good: async/await with try/catch
const getData = async () => {
  try {
    const response = await fetch('/api/data');
    return await response.json();
  } catch (error) {
    console.error('Failed:', error);
    return null;  // Return fallback value
  }
};
```

Use `.finally()` for cleanup code that must run regardless of success or failure, like hiding loading spinners or closing database connections.

## Promise Static Methods

**Promise.resolve()** and **Promise.reject()** create already-settled Promises. Use them to wrap synchronous values in Promise-compatible interfaces.

```javascript
Promise.resolve(42).then(v => console.log(v));  // 42
Promise.reject(new Error('fail')).catch(e => console.error(e));
```

**Promise.allSettled()** waits for all Promises to settle (fulfilled or rejected) without short-circuiting on errors, unlike `Promise.all()`.

```javascript
const results = await Promise.allSettled([
  Promise.resolve(1),
  Promise.reject('error'),
  Promise.resolve(3)
]);

console.log(results);
// [
//   { status: 'fulfilled', value: 1 },
//   { status: 'rejected', reason: 'error' },
//   { status: 'fulfilled', value: 3 }
// ]
```

**Promise.any()** resolves when the first Promise fulfills, ignoring rejections unless all reject.

## Related

Learn how [async functions](/languages/javascript/async-functions) build on Promises to simplify asynchronous code. See the [Fetch API guide](/languages/javascript/fetch-api) for real-world Promise usage in HTTP requests. Check the [Asynchronous JavaScript Guide](/guides/asynchronous-javascript-guide) for a complete overview of async patterns. Test Promise code interactively with the [JavaScript REPL](/tools/javascript-repl). Reference the [JavaScript Async Patterns Cheat Sheet](/cheatsheets/javascript-async-patterns) for quick syntax reminders.