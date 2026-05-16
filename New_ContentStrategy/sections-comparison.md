# Section Bucket — Comparison & Context

0–1 comparison sections per article. Used sparingly — overusing comparison creates a "feature checklist" feel that reads as AI-generated.

## Table of Contents

- [`comp-cross-language`](#comp-cross-language) — The Same Idea in Other Languages
- [`comp-alternatives`](#comp-alternatives) — Alternatives Within This Language
- [`comp-history`](#comp-history) — A Brief History
- [`comp-spec-comparison`](#comp-spec-comparison) — How This Differs From Other Specs

---

## `comp-cross-language`

**Name:** The Same Idea in Other Languages
**Use when:** Showing how the concept exists in other languages would clarify what's distinctive about this one. Almost always paired with has_cross_language_analog=true.
**Skip when:** The concept is too language-specific for cross-comparison to be meaningful.
**Length:** 200–400 words.
**Voice fits:** thoughtful-explainer, opinionated-commentator.

### Writer instructions

Show 2–3 other languages' versions of the same concept. Brief code snippets. Highlight what's distinctive about THIS language's approach.

Don't just list syntax differences. Explain what each language's choice reveals about its design priorities.

### Good (Python closures, comparing to JavaScript and Rust)

> JavaScript closures look superficially similar but differ in important ways:
>
> ```javascript
> function makeCounter() {
>   let count = 0;
>   return () => ++count;
> }
> ```
>
> No `nonlocal` keyword — JavaScript closures can mutate captured variables directly. This is more ergonomic but eliminates Python's explicit "I'm modifying enclosing scope" signal.
>
> Rust takes a different approach entirely:
>
> ```rust
> let mut count = 0;
> let mut increment = || { count += 1; count };
> ```
>
> The `move` keyword (not shown here) controls whether captures borrow or take ownership. Rust closures are deeply tied to the ownership model — they're not just "functions that remember variables", they're values with carefully tracked lifetimes.
>
> Python's design sits in the middle: closures work, but the `nonlocal` keyword forces explicit acknowledgment when you're modifying enclosing scope. This catches a class of bugs JavaScript silently allows.

### Forbidden

- Comparing without explaining what the difference reveals
- Treating every language's approach as equally good (have a perspective)
- More than 3 languages compared

---

## `comp-alternatives`

**Name:** Alternatives Within This Language
**Use when:** Other ways exist in the same language to accomplish the concept's job, and the comparison matters for choosing.
**Skip when:** This is the only reasonable way in the language.
**Length:** 200–350 words.
**Voice fits:** opinionated-commentator, thoughtful-explainer.

### Writer instructions

Show 1–2 alternative approaches in the same language. Explain when each wins. Commit to a recommendation.

This is different from `code-variations`: variations are different ways to write the same concept; alternatives are different concepts that solve the same problem.

### Good

> Python's `dataclass` isn't the only way to write a class that mostly holds data. The alternatives:
>
> **NamedTuple** — immutable, tuple-based, lighter weight:
>
> ```python
> from typing import NamedTuple
> class Point(NamedTuple):
>     x: float
>     y: float
> ```
>
> Best when you want immutability and tuple-like access. Loses mutability and can't have methods that modify state.
>
> **TypedDict** — for dict-shaped data with a known structure:
>
> ```python
> from typing import TypedDict
> class PointDict(TypedDict):
>     x: float
>     y: float
> ```
>
> Best when interfacing with JSON or external systems that hand you dicts. Type checking only — there's no runtime class.
>
> Default to `@dataclass` for general-purpose data classes. Reach for NamedTuple when immutability is required. Use TypedDict only when the data is *literally* a dict (parsed JSON, API responses).

### Forbidden

- Listing alternatives without a recommendation
- Treating clearly inferior alternatives as equally valid
- More than 3 alternatives

---

## `comp-history`

**Name:** A Brief History
**Use when:** The concept's evolution genuinely informs how to use it today. Examples: Python 2 vs 3 idioms, ES5 vs ES6+ patterns, Java pre/post-streams, before/after generics.
**Skip when:** History is academic and doesn't change current usage.
**Length:** 200–300 words.
**Voice fits:** thoughtful-explainer, opinionated-commentator.

### Writer instructions

Trace how the concept evolved. Reference specific version numbers, PEPs, RFCs, or release notes. Explain WHY the change happened and what it means for code being written today.

This section signals genuine familiarity with the language. Get specifics right.

### Good

> Async/await landed in JavaScript in ES2017, but `async` as a pattern existed long before. The progression went: callbacks (forever), Promises (ES2015), async/await (ES2017). Each step solved a real problem with the previous one — callback pyramids became unmanageable, Promise chains improved structure but still had awkward error flow, async/await made async code look synchronous.
>
> This history matters because a large amount of production JavaScript was written before async/await. If you're working in an older codebase, you'll see callback patterns and raw Promise chains — they're not wrong, just from a different era. New code should use async/await by default, but understanding the older patterns is necessary because they appear in every npm dependency.
>
> One historical wrinkle: Promise was a community pattern (jQuery, Q, Bluebird) before it was standardised. The standardisation in ES2015 cleaned up incompatibilities between implementations, but Promise libraries shipped with extra features (cancellation, retry) that the standard doesn't have. Some teams still use these libraries for that reason.

### Forbidden

- History that's a list of release notes without context
- No specific versions, PEPs, or RFCs cited
- Skipping the "what this means for code today" connection

---

## `comp-spec-comparison`

**Name:** How This Differs From Other Specs
**Use when:** The concept is part of a standard (HTTP, JSON, ECMAScript, Unicode, etc.) and differs subtly between specs or versions.
**Skip when:** No formal spec exists, or the spec is unambiguous.
**Length:** 200–350 words.
**Voice fits:** terse-senior, opinionated-commentator.

### Writer instructions

Highlight where this language's implementation differs from the formal spec, or where two related specs say different things. Be precise — specs are unforgiving and getting this wrong is more discrediting than getting an opinion wrong.

### Good

> The ECMAScript specification defines `Array.prototype.sort()` as not necessarily stable, but as of ES2019 it's required to be stable. The change matters because earlier engines (V8 before Chrome 70, in particular) used unstable sorts for arrays above 10 elements. Code that depended on stable ordering would behave differently in old vs new environments.
>
> The Python equivalent (`list.sort()`) has been guaranteed stable since 2.3. Java's `Arrays.sort(Object[])` is also stable. `Arrays.sort(int[])` is not — primitive sorts use a quicksort variant that's faster but unstable. This inconsistency within Java itself trips people up.
>
> If you're writing code that depends on stable sorting and may target older runtimes, be explicit — sort by a tuple of (primary key, secondary key) rather than relying on the runtime's stability guarantee. The cost is one tuple allocation per element; the benefit is correctness across engines.

### Forbidden

- Wrong section numbers or version numbers
- Vague "the spec says" without specifics
- Comparing things that aren't actually specs
