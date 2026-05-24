---
actual_word_count: 1258
category: languages
concept: closures
description: "JavaScript closures keep variables alive after their outer function exits. Lexical scope, the var loop bug, memory leaks, and when to use them."
difficulty: intermediate
has_cross_language_analog: true
has_performance_implications: false
intent: concept
is_abstract: true
is_error_driven: false
is_syntax_heavy: false
keyword: javascript closures
language: javascript
og_image: og-default
published_date: '2026-04-13'
related_cheatsheet: ''
related_content: []
related_posts: []
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"How JavaScript Closures Work\
  \ (and Where They Break)\",\n  \"description\": \"JavaScript closures keep variables\
  \ alive after their outer function exits. Lexical scope, the var loop bug, memory\
  \ leaks, and when to use them.\",\n  \"datePublished\": \"2026-04-13\",\n  \"author\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\"\
  : \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n\
  \  \"url\": \"https://devnook.dev/languages/javascript/javascript-closures/\"\n\
  }\n</script>"
secondary_keywords:
  - closures in javascript
  - javascript closure function
  - lexical scope in javascript
  - javascript closure example
sections_used:
  - open-mental-model
  - core-how-it-works
  - code-minimal
  - code-realistic
  - prac-gotchas
  - close-next
tags:
  - javascript
  - closures
  - scope
  - functions
  - lexical-scope
target_keyword: javascript closures
template_id: modular-v1
title: "How JavaScript Closures Work (and Where They Break)"
voice: thoughtful-explainer
word_count: 1258
---

JavaScript closures are the mechanism that lets a function remember variables from its outer scope — even after that outer scope has finished executing. They appear in every callback, event handler, and module pattern you write, which makes understanding them precisely worth the effort.

## JavaScript Closures as Captured Environments

Think of a function definition as an envelope that gets sealed at the moment it is written. The envelope holds not just the function's instructions, but also the *address* of every variable visible at that exact location in the source code. When you later open the envelope and call the function, it uses that stored address to find the current value of each variable — wherever that variable now lives in memory.

This is lexical scoping: the scope of a variable is determined by where it *appears in the source code*, not by where the function is eventually called. A javascript closure is simply a function that has been sealed with such an envelope. The interesting cases arise when that envelope outlives the function that originally created the variables inside it — the outer function has returned, but the inner function still holds a reference to its environment.

## How the Scope Chain Actually Works

When JavaScript executes, each function invocation creates a *Lexical Environment* — an object that maps variable names to their current values. Inside V8 and other engines, this environment is allocated on the heap rather than the stack whenever a function's variables might be needed after the function returns. That heap allocation is what makes closures possible: the garbage collector will not reclaim those variables as long as something holds a reference to them.

Scope resolution follows a chain. When the inner function refers to a variable, the engine first checks the inner function's own Lexical Environment. If the variable is not there, it follows a parent pointer to the outer function's environment, then outward until it reaches the global scope. A closure captures a *reference* to each Lexical Environment in that chain — not a snapshot of the values at creation time. Modifying a variable after the closure is created will be visible when the closure reads it later.

One important detail: the closure captures the *entire* outer environment, not just the variables it actually uses. A function that references one field of a large object keeps that entire object alive in memory. This is not a bug — it follows directly from reference semantics — but it is what makes closures a common source of unintentional memory retention in long-running applications.

## A Minimal Closure

```javascript
function makeCounter(label) {
  let count = 0;
  return function () {
    count += 1;
    return `${label}: ${count}`;
  };
}

const visitTracker = makeCounter('visits');
const downloadCounter = makeCounter('downloads');

console.log(visitTracker());    // visits: 1
console.log(visitTracker());    // visits: 2
console.log(downloadCounter()); // downloads: 1
console.log(visitTracker());    // visits: 3
```

`visitTracker` and `downloadCounter` are two separate closures. Each has its own Lexical Environment — its own `label` and its own `count`. Calling one does not affect the other because they were sealed with different envelopes. This independent-state property is the foundation of factory functions, module patterns, and React's `useState` hook.

## A Realistic Pattern: Function Factories

Rate limiting shows where closures earn their keep in production code. You need multiple independent limiters — each tracking its own request count and time window — without a shared class instance or global state:

```javascript
function createRateLimiter(maxRequests, windowMs) {
  let requests = 0;
  let windowStart = Date.now();

  return function (action) {
    const now = Date.now();
    if (now - windowStart > windowMs) {
      requests = 0;
      windowStart = now;
    }
    if (requests >= maxRequests) {
      return { allowed: false, retryAfter: windowMs - (now - windowStart) };
    }
    requests += 1;
    return { allowed: true, remaining: maxRequests - requests };
  };
}

const apiLimiter      = createRateLimiter(100, 60_000);       // 100 req/min
const checkoutLimiter = createRateLimiter(5,   3_600_000);    // 5 req/hr

console.log(apiLimiter('GET /data'));      // { allowed: true, remaining: 99 }
console.log(checkoutLimiter('POST /buy')); // { allowed: true, remaining: 4 }
```

Each limiter closes over its own `requests`, `windowStart`, `maxRequests`, and `windowMs`. Libraries like `express-rate-limit` and `bottleneck` use the same pattern internally — just with more configuration surface area.

## Three Traps Worth Knowing

**The `var` loop bug.** Using `var` inside a loop creates one shared binding across all iterations, not one per iteration. Every closure created inside the loop closes over the same variable, so by the time any callback runs, the loop has finished and `i` is at its final value:

```javascript
// All three print 3 — they share the same i
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}

// Each prints its own value — let creates a new binding per iteration
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
```

The fix is `let`. It creates a fresh binding for each loop iteration, so each closure captures its own independent variable.

**Unintentional large-object retention.** Because a closure captures the entire Lexical Environment, keeping a reference to a small inner function can pin a large outer object in memory indefinitely:

```javascript
function setup() {
  const hugeBuffer = new Uint8Array(10_000_000);
  return function ping() {
    return 'ok'; // hugeBuffer stays alive until ping is garbage collected
  };
}
```

If `ping` lives in a long-running event listener, `hugeBuffer` will never be freed. The solution is to restructure so the closure does not capture the large object, or to explicitly null out the binding once it is no longer needed.

**Stale closures in async code and React.** A closure created inside a React render captures the state values at that specific render cycle. If the function runs later — in a `setTimeout`, an event handler, or after an awaited call — it reads stale values rather than the current ones:

```javascript
function Counter() {
  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    const id = setInterval(() => {
      setCount(count + 1); // count is stale — always 0 from the initial render
    }, 1000);
    return () => clearInterval(id);
  }, []); // missing count in the dependency array

  return <div>{count}</div>;
}
```

The idiomatic fix is the updater form of the state setter: `setCount(c => c + 1)`. The updater receives the latest state value at call time, bypassing the stale snapshot held in the closure.

## Where to Go Next

Closures interact with two other JavaScript concepts in ways that reward close attention. Arrow functions do not rebind `this`, which means an arrow function inside a method reliably captures the outer `this` through the lexical environment — a common pattern in event handlers and class methods. Understanding when that is useful, and when it creates unexpected behavior, follows directly from what you now know about how closures seal their environment.

From there, async/await and Promises are closures working at scale: every `.then()` callback and every line of code after an `await` is a function that captures the surrounding scope. The state machine that async/await compiles to is essentially a series of closures threaded together by the JavaScript runtime. If async code behaves unexpectedly, the explanation usually lives in the closure semantics described here.

Finally, React hooks are the most pervasive modern application of closures in frontend development. Every `useState`, `useEffect`, and `useCallback` call is built on the same Lexical Environment mechanics covered in this article. The stale closure trap above is the single most common React bug, and recognizing it comes down to knowing that closures capture references, not values, at a point in time.

MDN's [Closures guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures) is a reliable reference for the formal definition and additional examples — worth bookmarking alongside this article.
