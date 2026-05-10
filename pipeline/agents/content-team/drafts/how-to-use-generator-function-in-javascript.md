---
title: "How to Use Generator Functions in JavaScript? A Practical Guide with Examples"
description: "Learn how JavaScript generator functions work with function*, yield, and next(). Covers lazy iteration, infinite sequences, and async patterns."
published_date: "2026-05-09"
category: languages
language: "javascript"
concept: "use-generator-function"
template_id: "lang-v2"
tags: ["javascript", "generators", "iterators", "yield", "lazy-evaluation"]
difficulty: "intermediate"
related_posts: []
related_tools: []
og_image: "/og/languages/javascript/use-generator-function.png"
---

Imagine you need to paginate through a dataset with hundreds of thousands of records, or generate an infinite sequence of IDs for incoming events. The instinctive solution is to build an array — loop through everything, push each value, then work with the result. For small datasets that works fine. At scale, it stalls the browser, exhausts heap memory, and makes the user stare at a frozen tab. JavaScript generator functions solve this by producing values one at a time, on demand, without computing the next value until you ask for it.

## The Problem

Here is what the naive approach looks like for generating a sequence of the first N Fibonacci numbers:

```javascript
// PROBLEM: builds the entire sequence in memory upfront
function getAllFibonacci(limit) {
  const sequence = []; // grows to 'limit' entries — all held in RAM at once
  let [a, b] = [0, 1];

  for (let i = 0; i < limit; i++) {
    sequence.push(a);  // every value stored, even ones you'll never use
    [a, b] = [b, a + b];
  }

  return sequence; // entire array transferred back to caller
}

// Caller only needs first 5, but we computed and stored 1,000,000
const fibs = getAllFibonacci(1_000_000);
console.log(fibs.slice(0, 5)); // [0, 1, 1, 2, 3]
```

The function computes all one million values, stores them in a contiguous array, and only then lets the caller pick out the five it actually needed. Memory usage scales linearly with `limit`. Set `limit` high enough and you will trigger a garbage-collection pause, or worse, a heap out-of-memory crash. There is no way to stop the computation partway through — it is all or nothing.

This is the core problem: the function cannot pause. It must run to completion and return everything before the caller gets anything. Generator functions break that constraint.

## The JavaScript Solution: Generator Functions

A generator function is declared with a `function*` syntax — the asterisk signals to the JavaScript engine that this function can pause and resume. Inside the body, the `yield` keyword pauses execution and hands a value to the caller. When the caller asks for the next value, execution resumes from exactly where it left off, with all local variables intact.

Here is the same Fibonacci sequence, rewritten as a generator:

```javascript
// SOLUTION: yields one value at a time — O(1) memory, infinite sequence
function* fibonacci() {
  let [a, b] = [0, 1];

  while (true) {              // infinite loop is safe — only runs when .next() is called
    yield a;                  // pause here, send 'a' to the caller
    [a, b] = [b, a + b];     // only runs when the caller asks for the next value
  }
}

// Get a generator object (the function body has NOT run yet)
const gen = fibonacci();

// Consume exactly as many values as needed
console.log(gen.next()); // { value: 0, done: false }
console.log(gen.next()); // { value: 1, done: false }
console.log(gen.next()); // { value: 1, done: false }
console.log(gen.next()); // { value: 2, done: false }
console.log(gen.next()); // { value: 3, done: false }
// The sequence continues, but no further computation happens until requested
```

Calling `fibonacci()` returns a **Generator object** — a special iterator. The function body does not execute at all until the first `.next()` call. Each `.next()` runs the body until the next `yield`, returns `{ value, done }`, and then suspends again. Memory usage stays constant regardless of how many values you eventually consume.

## How Generator Functions Work in JavaScript

Understanding the execution model explains why generators are so powerful and where their limits lie.

When a regular function runs, it occupies a stack frame. When it returns, the frame is destroyed — all local variables are gone. The next call starts from scratch. Generators break this contract: each Generator object holds its own **suspended stack frame**. When execution reaches a `yield`, the engine snapshots the current state — instruction pointer, local variable values, scope chain — and stores it inside the generator object. The frame is suspended, not destroyed. The next `.next()` call restores the snapshot and continues running.

A generator can be in one of three states:

- **Suspended** — paused at a `yield` or not yet started
- **Running** — currently executing (briefly, during a `.next()` call)
- **Completed** — returned (hit a `return` statement or the end of the function body)

Once completed, calling `.next()` repeatedly returns `{ value: undefined, done: true }` — generators are exhausted after a single pass.

The `yield*` operator delegates to another iterable — an array, a string, or another generator — yielding each of its values in turn before continuing:

```javascript
function* combined() {
  yield* [1, 2, 3];       // delegates to the array iterator
  yield* "ab";            // delegates to the string iterator
  yield 100;              // then yields its own value
}

console.log([...combined()]); // [1, 2, 3, 'a', 'b', 100]
```

Generators implement the **iterator protocol** — they have `.next()`, `.return()`, and `.throw()` methods — making them composable with `for...of`, the spread operator, and destructuring assignment without any adapter code.

## Going Further — Real-World Patterns

**Pattern 1: Lazy infinite sequences**

A generator-based ID generator or counter is a classic production pattern — each call to `.next()` produces the next unique value, with no array allocation and no coordination needed:

```javascript
function* idGenerator(prefix = 'item') {
  let count = 0;
  while (true) {
    yield `${prefix}-${String(count++).padStart(6, '0')}`;
  }
}

const ids = idGenerator('order');

console.log(ids.next().value); // "order-000000"
console.log(ids.next().value); // "order-000001"
console.log(ids.next().value); // "order-000002"
// Continues indefinitely — zero memory growth
```

The same pattern applies to paginated API consumers: the generator fetches one page at a time inside the loop, yielding each record. The calling code sees a clean sequence of records, unaware of pagination boundaries. Network calls only happen when the consumer advances the generator.

**Pattern 2: Custom iterators with generator functions**

The verbose approach to making a class iterable requires manually implementing `Symbol.iterator` with a closure to track state. A generator collapses this to a few lines:

```javascript
class DateRange {
  constructor(start, end) {
    this.start = new Date(start);
    this.end = new Date(end);
  }

  // Generator-based Symbol.iterator — clean, no manual state tracking
  *[Symbol.iterator]() {
    const current = new Date(this.start);
    while (current <= this.end) {
      yield new Date(current);           // yield a copy of the current date
      current.setDate(current.getDate() + 1); // advance by one day
    }
  }
}

const range = new DateRange('2026-05-01', '2026-05-04');

for (const date of range) {
  console.log(date.toISOString().slice(0, 10));
}
// 2026-05-01
// 2026-05-02
// 2026-05-03
// 2026-05-04
```

The `*[Symbol.iterator]()` shorthand defines a generator method. The class is now directly iterable — compatible with `for...of`, spread, `Array.from()`, and destructuring — with no external iterator class or manual `{ value, done }` bookkeeping.

## What to Watch Out For

**Generators are one-time iterators.** Once a generator is exhausted (`done: true`), it cannot be reset. Calling `.next()` on a completed generator always returns `{ value: undefined, done: true }`. If you need to iterate the sequence multiple times, call the generator function again to create a fresh generator object. Storing the generator object in a variable and attempting to "rewind" it is a common mistake.

**Spreading an infinite generator will crash the runtime.** The spread operator `[...gen]` exhausts an iterator completely before constructing the array. Applied to an infinite generator like `fibonacci()`, this allocates values without bound until the process runs out of heap memory or the tab crashes. Always consume infinite generators with a `for...of` loop containing an explicit `break` condition, or manually step with `.next()` until you have what you need.

**The `return` value is not visible to `for...of`.** When a generator hits a `return value` statement, `.next()` returns `{ value: returnValue, done: true }`. However, `for...of` stops iterating as soon as `done` is `true` and does not expose the final value. If you need the generator's return value, you must use manual `.next()` calls and check the result object directly.

## Under the Hood — Performance & Mechanics

V8 (Chrome's JavaScript engine) compiles generator functions into **state machines** at parse time. The engine identifies each `yield` point and assigns it a state number. The compiled code is essentially a large `switch` statement — each `.next()` call jumps to the current state, executes until the next `yield` or `return`, updates the state number, and exits. This transformation happens at compile time, so there is no runtime reflection or dynamic dispatch overhead.

From a memory perspective, each Generator object holds one paused activation record — the set of local variables captured at the last `yield`. For a generator with three local variables, this is O(1) space regardless of how many values it produces. Compare to an array-based approach: generating N values costs O(N) memory. For large N, the generator wins decisively.

Performance of individual `.next()` calls is slightly higher than the equivalent step in a plain `for` loop, due to state machine transition overhead and the `{ value, done }` object allocation on each call. For hot, tight inner loops over small, known-size arrays, a traditional `for` or `forEach` will be faster. Generators pay off when the sequence is large, lazy, or potentially infinite — the O(1) memory advantage outweighs the per-call overhead many times over.

Avoid creating millions of simultaneous paused generator objects. Each holds a live reference that prevents GC, even if you never call `.next()` on it again.

## Advanced Edge Cases

**Edge Case 1: Passing values into a generator via `.next(arg)`.**

The argument passed to `.next()` becomes the **resolved value of the `yield` expression** inside the generator — not a new item to yield outward, but a value flowing inward:

```javascript
function* multiplier() {
  let factor = 1;
  while (true) {
    const input = yield factor; // 'input' receives whatever .next(arg) sends
    if (typeof input === 'number') {
      factor = input;           // update the factor for future yields
    }
  }
}

const gen = multiplier();
console.log(gen.next().value);    // 1   — first .next() arg is always ignored
console.log(gen.next(10).value);  // 10  — sets factor to 10
console.log(gen.next().value);    // 10  — factor still 10
console.log(gen.next(3).value);   // 3   — sets factor to 3
```

The first `.next()` call always ignores its argument because the generator hasn't reached its first `yield` yet — there is no `yield` expression to receive it.

**Edge Case 2: `.throw()` and `.return()` for external control.**

Callers can inject an exception into the generator at its current yield point using `.throw(error)`, or terminate it early with `.return(value)`. A `try/finally` inside the generator still executes its `finally` block even when these methods are used:

```javascript
function* withCleanup() {
  try {
    yield 'working';
    yield 'still working';
  } finally {
    console.log('cleanup ran'); // executes on .throw() and .return()
  }
}

const gen = withCleanup();
gen.next();                           // { value: 'working', done: false }
gen.return('early exit');             // logs "cleanup ran", returns { value: 'early exit', done: true }

const gen2 = withCleanup();
gen2.next();                          // { value: 'working', done: false }
gen2.throw(new Error('injected'));    // logs "cleanup ran", then throws the error
```

This guarantee makes generators safe to use with resources — a generator managing a file handle or database cursor can place cleanup in `finally` and trust it will run even if the caller abandons iteration midway.

## Testing Generator Functions in JavaScript

Jest is the standard testing framework for JavaScript projects. Testing generators breaks down into a few distinct scenarios:

```javascript
// generators.test.js
const { fibonacci, idGenerator, DateRange } = require('./generators');

describe('fibonacci generator', () => {
  it('produces the correct sequence for the first five values', () => {
    const gen = fibonacci();
    const results = [0, 1, 1, 2, 3].map(() => gen.next().value);
    expect(results).toEqual([0, 1, 1, 2, 3]);
  });

  it('never sets done: true for an infinite generator', () => {
    const gen = fibonacci();
    for (let i = 0; i < 100; i++) {
      expect(gen.next().done).toBe(false);
    }
  });
});

describe('multiplier generator (two-way communication)', () => {
  it('updates the factor when a number is passed via next()', () => {
    const gen = multiplier();
    gen.next();                          // prime the generator
    expect(gen.next(5).value).toBe(5);  // set factor to 5
    expect(gen.next().value).toBe(5);   // factor unchanged
    expect(gen.next(2).value).toBe(2);  // set factor to 2
  });
});

describe('withCleanup generator', () => {
  it('runs finally block when .throw() is called', () => {
    const gen = withCleanup();
    gen.next(); // advance to first yield
    expect(() => gen.throw(new Error('test'))).toThrow('test');
    // "cleanup ran" should have been logged — verify via jest.spyOn(console, 'log')
  });
});
```

Testing finite generators is straightforward: collect all values with `[...gen()]` or map `.next()` calls into an array. Testing infinite generators requires stepping manually — never spread them in tests. For two-way generators, step through the call sequence explicitly, verifying each `{ value, done }` object.

## Summary

JavaScript developers frequently need to work with sequences too large or open-ended to hold in memory at once. Loading everything into an array first fails at scale — it wastes memory, delays execution, and makes infinite sequences impossible. Generator functions, defined with `function*` and controlled with `yield`, solve this by pausing execution between values and resuming on demand. Each `.next()` call returns one `{ value, done }` result and suspends again, keeping memory usage constant. Because generators implement the iterator protocol natively, they compose directly with `for...of`, spread, and destructuring — no adapter code required. The one thing to keep in mind when using generator functions in JavaScript: a generator object is exhausted after a single pass — always create a new one if you need to iterate again. To go further with asynchronous patterns, see the complete guide to [async/await in JavaScript](/languages/javascript/async-await/). For handling the data that generators commonly produce from API calls, [JSON parsing in JavaScript](/languages/javascript/json-parsing/) covers the safe and efficient approach.
