# Section Bucket — Practical

0–2 practical sections per article. These cover real-world friction: gotchas, edge cases, performance, testing, common mistakes, production patterns. NEVER include more than 2 from this bucket — multiple practical sections in one article create a "comprehensive coverage" fingerprint.

## Table of Contents

- [`prac-gotchas`](#prac-gotchas) — Things That Will Trip You Up
- [`prac-when-not-to`](#prac-when-not-to) — When Not to Use This
- [`prac-edge-cases`](#prac-edge-cases) — Edge Cases Worth Knowing
- [`prac-performance`](#prac-performance) — Performance Notes
- [`prac-common-mistakes`](#prac-common-mistakes) — Common Mistakes
- [`prac-production-patterns`](#prac-production-patterns) — In Production Code
- [`prac-testing`](#prac-testing) — Testing Considerations

---

## `prac-gotchas`

**Name:** Things That Will Trip You Up
**Use when:** The topic has well-known traps that bite people repeatedly. Almost always paired with is_error_driven=true.
**Skip when:** Topic is straightforward enough that gotchas would be padding.
**Length:** 200–350 words. Format as 2–3 labelled traps.
**Voice fits:** empathetic-debugger (strongly preferred), terse-senior.

### Writer instructions

List 2–3 specific traps. For each: name it, show the broken case (in code or scenario), explain why it bites, give the fix in one sentence.

Tell stories where possible — "I once spent an hour..." or "A coworker hit this last month..." These signals are what AI output usually lacks.

### Good

> **Trap 1: the loop closure bug.**
>
> ```javascript
> for (var i = 0; i < 3; i++) {
>   setTimeout(() => console.log(i), 0);
> }
> // Prints 3, 3, 3
> ```
>
> The closures all reference the same `i`, and by the time the timeouts fire, the loop has finished. I've seen this in production code that worked fine in tests because the test mocked `setTimeout`. Fix: use `let` instead of `var`, or capture `i` in an IIFE.
>
> **Trap 2: silent failure on async/await without try-catch.**
>
> An unhandled rejection in an async function doesn't crash your program but it doesn't produce a useful stack trace either — it shows up as `UnhandledPromiseRejectionWarning` and your code continues with garbage state. Always wrap awaits in production code where the failure mode matters.

### Forbidden

- Generic "be careful" advice without specifics
- Listing more than 3 gotchas (split or use a different section)
- No code or scenario to ground each gotcha

---

## `prac-when-not-to`

**Name:** When Not to Use This
**Use when:** The concept is commonly over-applied or misused.
**Skip when:** The concept is rarely misapplied.
**Length:** 150–250 words.
**Voice fits:** opinionated-commentator (strongly preferred), thoughtful-explainer.

### Writer instructions

Give 2–3 concrete situations where this concept is the wrong tool. Be specific about what to use instead.

This section is a credibility marker. Most tutorials present a concept as universally good. Saying "here's when not to use it" signals you've actually used the thing.

### Good

> Don't reach for `async/await` when you have multiple independent operations that could run in parallel:
>
> ```javascript
> // Slow — runs sequentially
> const user = await fetchUser();
> const settings = await fetchSettings();
> const billing = await fetchBilling();
> ```
>
> These three calls are independent. Awaiting them sequentially makes the page three times slower than necessary. Use `Promise.all()` for independent operations and keep `await` for sequential dependencies.
>
> Also: don't `await` in a tight loop without batching. If you're processing 10,000 records and each one calls an API, you'll either flood the API or run for hours. Reach for `Promise.allSettled` with batching, or a library like p-limit, depending on whether you need ordered results.

### Forbidden

- Hedging ("it's complicated, depends on use case")
- No specific alternative to use instead
- Anti-patterns that are too obvious to need stating

---

## `prac-edge-cases`

**Name:** Edge Cases Worth Knowing
**Use when:** The topic has genuinely surprising edges that real production code hits.
**Skip when:** The topic doesn't have meaningful edges, or the edges are academic.
**Length:** 250–400 words. 2 edge cases, no more.
**Voice fits:** terse-senior, opinionated-commentator.

### Writer instructions

Pick 2 specific edge cases where the concept behaves unexpectedly. For each: show the surprising case in code, explain why it happens, give the practical lesson.

DO NOT pick edges that are just curiosities. Each edge case must be something a real developer would actually hit in production. If you're reaching for edges, skip this section entirely.

This section was historically over-included on every page. Use it sparingly — only when it adds real value.

### Good

> **Edge case 1: empty iterables in `reduce()` without an initial value.**
>
> ```python
> from functools import reduce
> reduce(lambda a, b: a + b, [])  # TypeError: reduce() of empty iterable with no initial value
> ```
>
> Most languages have similar behaviour for "fold without initial value". The fix is to always provide an initial value when the iterable might be empty, even if it seems redundant: `reduce(lambda a, b: a + b, items, 0)`. I've watched a production batch job crash on a quiet weekend because of this exact mistake — the data feed was empty for the first time in months.
>
> **Edge case 2: `reduce()` with side effects.**
>
> ```python
> reduce(lambda a, b: print(b) or a + b, [1, 2, 3], 0)
> ```
>
> This works, but if you find yourself doing side effects in a reducer, you've picked the wrong tool. Use a regular for-loop. Reducers should be pure, both for readability and because some implementations (in JavaScript, for example) make no guarantees about execution order.

### Forbidden

- Edges that are academic curiosities, not production realities
- More than 2 edges in one section
- Edges that overlap with `prac-gotchas` content

---

## `prac-performance`

**Name:** Performance Notes
**Use when:** Performance is decision-relevant for this concept (the developer might pick a different approach based on perf). Often paired with has_performance_implications=true.
**Skip when:** Performance is uninteresting or universally fine for this concept.
**Length:** 200–350 words.
**Voice fits:** terse-senior, opinionated-commentator.

### Writer instructions

Discuss the performance characteristics that actually matter. Big-O if relevant. Hidden costs the developer might not see. When perf becomes a problem and what to do about it.

Don't invent numbers. If you cite a benchmark, source it or qualify it ("in my testing on Node 20..."). Vague claims ("it's faster") are AI-tells.

### Good

> Closures in Python are cheap — the runtime creates a new function object on each call, but the function-object creation is fast (a few hundred nanoseconds on CPython 3.12). What's not free is the captured variables: each cell is a separate Python object, and looking up `nonlocal` variables goes through a slightly slower path than local variables. For most code this doesn't matter. Where it can matter is tight inner loops calling closures millions of times — in that case, the cell lookup adds maybe 10–20% overhead vs a plain local. Most code never hits this. When you do, the fix is usually to refactor the closure-creating code out of the hot loop, not to abandon closures.

### Bad

> Closures are very efficient and you should not worry about performance...

### Forbidden

- Invented numbers without sourcing
- "Don't worry about performance" hand-waving
- Performance discussion that doesn't change the developer's decision

---

## `prac-common-mistakes`

**Name:** Common Mistakes
**Use when:** Beginner-to-intermediate topic where junior developers stumble in predictable ways.
**Skip when:** Article targets advanced audience.
**Length:** 200–300 words.
**Voice fits:** tutorial-guide, empathetic-debugger.

### Writer instructions

Different from `prac-gotchas` — gotchas are non-obvious traps that surprise experienced developers. Mistakes are predictable errors a junior makes while learning the concept. Pick 2–3.

For each: name the mistake, show what it looks like in code, explain what they probably intended, give the correct version.

### Good

> **Mistake: forgetting to return the inner function.**
>
> ```python
> def make_counter():
>     count = 0
>     def increment():
>         nonlocal count
>         count += 1
>         return count
>     # Forgot: return increment
>
> counter = make_counter()
> counter()  # TypeError: 'NoneType' object is not callable
> ```
>
> A closure isn't useful if you don't return it. The function defines `increment` but never gives it back. This is the most common first-time-closures mistake.
>
> **Mistake: assigning to the captured variable without `nonlocal`.**
>
> Skipping `nonlocal` makes Python treat the name as a new local. `count += 1` becomes "read local count" which fails because no local `count` exists yet.

### Forbidden

- Mistakes that experienced developers also make (those are gotchas)
- Generic "always remember to..." advice
- More than 3 mistakes

---

## `prac-production-patterns`

**Name:** In Production Code
**Use when:** The concept's textbook usage differs from how it's actually used in production codebases.
**Skip when:** Textbook and production usage are the same.
**Length:** 250–400 words.
**Voice fits:** opinionated-commentator, thoughtful-explainer, terse-senior.

### Writer instructions

Show 1–2 patterns that production code uses but tutorials rarely cover. Things like: how this concept appears in a typical framework codebase, how teams structure code around it, what naming conventions emerge.

This section is hard to fake. If you don't have production experience with the concept, skip it — readers can tell.

### Good

> In production Django codebases, context managers are heavily used for transaction control. The typical pattern wraps the entire view in a `transaction.atomic()`:
>
> ```python
> from django.db import transaction
>
> def transfer_funds(from_account_id, to_account_id, amount):
>     with transaction.atomic():
>         debit = Account.objects.select_for_update().get(id=from_account_id)
>         credit = Account.objects.select_for_update().get(id=to_account_id)
>         debit.balance -= amount
>         credit.balance += amount
>         debit.save()
>         credit.save()
> ```
>
> The `select_for_update()` adds row-level locking inside the transaction — without it, you have a race condition. The thing tutorials miss: the lock is held until the `with` block exits, so the order matters. Lock high-contention rows last to minimize contention time. I've seen production incidents from getting this order wrong.

### Forbidden

- Patterns that are just textbook usage with a real-ish variable name
- Claims about "how production code works" without specifics
- Patterns that aren't actually production-tested

---

## `prac-testing`

**Name:** Testing Considerations
**Use when:** The topic is genuinely testable AND there's something non-obvious about testing it. The threshold for "use this section" is high.
**Skip when:** Testing the concept is the same as testing any function (most cases). Topic is conceptual rather than code (definitions, mental models).
**Length:** 200–350 words + small code block.
**Voice fits:** terse-senior, tutorial-guide.

### Writer instructions

Cover the non-obvious testing concern for this specific concept. Examples of WHEN this section earns its place:

- Testing async code (timing, fake timers, awaiting)
- Testing closures (verifying the right values are captured)
- Testing context managers (verifying cleanup runs on exception)
- Testing generators (consumption semantics, exhaustion)

If the testing story is "write a test like any other function", skip this section. This was over-included in the old templates.

### Good

> Testing closures requires verifying the captured state, not just the return value. Here's a common bug closure code has: capturing a mutable list and then mutating it through external code:
>
> ```python
> from unittest import TestCase
>
> def make_appender():
>     items = []
>     def append(x):
>         items.append(x)
>         return list(items)
>     return append, items  # exposing items for testability is itself a smell
>
> class TestAppender(TestCase):
>     def test_captures_state(self):
>         append, _ = make_appender()
>         self.assertEqual(append("a"), ["a"])
>         self.assertEqual(append("b"), ["a", "b"])
> ```
>
> The test asserts state evolution across calls — that's the closure-specific concern. If your tests just verify return values, you're not testing what closures actually do.

### Forbidden

- Generic "write unit tests" advice
- Testing concerns that apply to all code, not specifically to this concept
- Adding this section because "articles should have testing" — they shouldn't, unless testing is non-obvious
