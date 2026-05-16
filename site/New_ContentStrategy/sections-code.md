# Section Bucket — Code & Examples

1–3 code sections per article. These are where the article shows code. Pure prose code-explanation lives in core sections; this bucket is for sections where code IS the content.

## Table of Contents

- [`code-minimal`](#code-minimal) — The Smallest Working Example
- [`code-realistic`](#code-realistic) — A Real-World Example
- [`code-walkthrough`](#code-walkthrough) — Step-by-Step Walkthrough
- [`code-before-after`](#code-before-after) — Before & After
- [`code-variations`](#code-variations) — Three Ways to Do This
- [`code-side-by-side`](#code-side-by-side) — Side-by-Side With an Alternative

---

## `code-minimal`

**Name:** The Smallest Working Example
**Use when:** Almost always for code-heavy topics. The reader needs to see the simplest version that runs before anything else.
**Skip when:** Already covered by an opening section (e.g., `open-quick` already showed the minimum).
**Length:** 5–15 lines of code + 50–80 words of prose framing.
**Voice fits:** all voices.

### Writer instructions

Show the simplest possible code that demonstrates the concept and runs as-is. NO setup boilerplate beyond what's necessary. Use realistic variable names.

Frame the code in 1–2 sentences before, and 2–4 sentences after. The "after" sentences should add something the code doesn't already show — context, a subtle behavior, or a connection to what comes next.

### Good

> The pattern at its simplest:
>
> ```python
> def make_counter():
>     count = 0
>     def increment():
>         nonlocal count
>         count += 1
>         return count
>     return increment
>
> counter = make_counter()
> print(counter())  # 1
> print(counter())  # 2
> ```
>
> The `nonlocal` keyword is doing real work here — without it, `count += 1` would raise an `UnboundLocalError` because Python would treat `count` as a new local variable. This is the most common stumble when writing closures in Python.

### Bad

```python
# This is a simple example
def example():
    x = 5
    def inner():
        return x
    return inner
```

> The above code demonstrates closures.

### Forbidden

- Variable names like `x`, `foo`, `bar`, `data`, `result` (unless contextually correct)
- Comments in the code that just restate what the code does
- Empty "this code demonstrates X" framing

---

## `code-realistic`

**Name:** A Real-World Example
**Use when:** The reader needs to see how the concept is used in actual production code.
**Skip when:** Article is purely about syntax basics.
**Length:** 15–30 lines + 80–150 words of explanation.
**Voice fits:** all voices.

### Writer instructions

Show code that looks like something from a real project — with imports, error handling, sensible names, realistic data. The reader should think "this is the shape of code I'd actually write at work."

After the code, explain the design decisions: why structure it this way, what alternatives you considered, what trade-offs you're making.

### Good

```python
from contextlib import contextmanager
import logging
import time

log = logging.getLogger(__name__)

@contextmanager
def timed_block(operation_name):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        log.info("%s took %.3fs", operation_name, elapsed)

# Usage in a real pipeline
with timed_block("parse_billing_csv"):
    rows = parse_billing_csv(path)

with timed_block("upload_to_warehouse"):
    upload(rows)
```

> The `yield` inside the try is the whole context manager mechanism — code outside the `with` block runs before the yield, code inside runs as the yielded value, and the finally clause runs after, regardless of whether the inner block raised. I use this pattern frequently for ad-hoc instrumentation: it's lighter than wiring up a full APM tool when you just want timings for a few specific operations during a debugging session.

### Bad

```python
def example_function(input):
    # Process the input
    result = process(input)
    return result
```

### Forbidden

- "Example" or "demo" anywhere in function/variable names
- Code that wouldn't pass a basic code review
- Explanation that says what the code does without saying why it's structured that way

---

## `code-walkthrough`

**Name:** Step-by-Step Walkthrough
**Use when:** Concept is best understood by progressive code construction — building from a starting point through 3–4 steps to a finished version.
**Skip when:** No natural progression exists (it's one snippet or it's a comparison).
**Length:** 3–5 code blocks + 200–400 words of prose.
**Voice fits:** tutorial-guide (strongly preferred), thoughtful-explainer.
**Voice mismatches:** terse-senior (too verbose for terse style).

### Writer instructions

Start with a minimal/broken version. Each subsequent code block adds one thing and improves the previous. End with the final version that the reader could use.

After each block, explain what changed and why. Don't repeat the code in prose — add value the code doesn't show.

This is the only section where step-by-step structure is genuinely warranted. Don't use it elsewhere.

### Good (abbreviated for space)

> Start with the naive version:
>
> ```python
> def fetch_user(user_id):
>     return api.get(f"/users/{user_id}")
> ```
>
> This works until the API has a transient blip. Let's add a retry:
>
> ```python
> def fetch_user(user_id):
>     for attempt in range(3):
>         try:
>             return api.get(f"/users/{user_id}")
>         except APIError:
>             if attempt == 2:
>                 raise
> ```
>
> Better, but we're hammering the API. Add a backoff:
>
> ```python
> def fetch_user(user_id):
>     for attempt in range(3):
>         try:
>             return api.get(f"/users/{user_id}")
>         except APIError:
>             if attempt == 2:
>                 raise
>             time.sleep(2 ** attempt)
> ```

> Each version is small enough to read in five seconds, and the progression makes the rationale visible.

### Forbidden

- Steps that repeat the previous step verbatim
- Step counts beyond 5 (split into two sections if needed)
- Step explanations that don't add new information beyond the code

---

## `code-before-after`

**Name:** Before & After
**Use when:** The concept is a refactoring pattern, idiom upgrade, or replacement for a worse approach.
**Skip when:** No clear "before" exists.
**Length:** 2 code blocks + 100–150 words.
**Voice fits:** terse-senior, opinionated-commentator, tutorial-guide.

### Writer instructions

Show the "before" code — the version a developer who hasn't learned this concept would write. Show the "after" — the version they'd write with it. Explain the specific improvements.

The "before" must be plausible, not a strawman. If your "before" is obviously bad code no one would write, find a better example.

### Good

> Before:
>
> ```javascript
> function getUser(users, id) {
>   for (let i = 0; i < users.length; i++) {
>     if (users[i].id === id) {
>       return users[i];
>     }
>   }
>   return null;
> }
> ```
>
> After:
>
> ```javascript
> const getUser = (users, id) => users.find(u => u.id === id) ?? null;
> ```
>
> The `find()` method handles the search, and the nullish coalescing `??` makes the "not found" case explicit at the call site rather than burying it in an early return. Six lines down to one. The "after" is also easier to extend — adding a filter is one chained call away.

### Forbidden

- A "before" that's obviously dumb (no one writes that)
- An "after" that's worse than the "before"
- Explanation that doesn't enumerate the specific improvements

---

## `code-variations`

**Name:** Three Ways to Do This
**Use when:** Multiple idiomatic approaches exist and choosing between them matters.
**Skip when:** There's one right way.
**Length:** 3 short blocks + 150–250 words across them.
**Voice fits:** thoughtful-explainer, opinionated-commentator.

### Writer instructions

Show 2 or 3 idiomatic variations. Briefly explain when each is preferred. End by recommending a default — committing to a position.

### Good

> Three reasonable ways to flatten a list of lists in Python:
>
> ```python
> # Comprehension — most readable for one-level flattening
> flat = [item for sublist in nested for item in sublist]
> ```
>
> ```python
> # itertools.chain — best for very large lists, lazy
> from itertools import chain
> flat = list(chain.from_iterable(nested))
> ```
>
> ```python
> # functools.reduce — works but slow due to repeated concatenation
> from functools import reduce
> flat = reduce(lambda a, b: a + b, nested, [])
> ```
>
> Default to the comprehension. Switch to `chain.from_iterable` when memory matters and you can keep it as an iterator. Don't use the reduce version — it's quadratic.

### Forbidden

- "Each approach has its merits" without committing to a default
- More than 3 variations (split into a separate section or use comparison bucket)
- Equal-weight presentation when one is clearly worse

---

## `code-side-by-side`

**Name:** Side-by-Side With an Alternative
**Use when:** Pairing this concept's code against the version using a different concept clarifies its purpose.
**Skip when:** No clear alternative exists.
**Length:** 2 code blocks + 100–150 words.
**Voice fits:** terse-senior, thoughtful-explainer.

### Writer instructions

Show the same task implemented two ways: with this concept and without. Explain what changes — not just in line count, but in readability, performance, or correctness.

This is different from `code-before-after`: the alternative isn't worse, it's just a different choice. Both might be valid.

### Good

> Same task, two approaches. Using async/await:
>
> ```javascript
> async function loadDashboard() {
>   const user = await fetchUser();
>   const orders = await fetchOrders(user.id);
>   return { user, orders };
> }
> ```
>
> Using Promise chaining:
>
> ```javascript
> function loadDashboard() {
>   return fetchUser().then(user =>
>     fetchOrders(user.id).then(orders => ({ user, orders }))
>   );
> }
> ```
>
> The behaviour is identical — same network calls, same order. The async version reads top-to-bottom and the variable scoping is intuitive. The Promise version makes the asynchrony explicit at every step but pays for it with nesting. For sequential awaits like this, async wins. For complex error handling across many parallel promises, Promise combinators are sometimes clearer.

### Forbidden

- Making the alternative look bad when it's valid
- No discussion of when each is preferred
- Code blocks that aren't actually equivalent
