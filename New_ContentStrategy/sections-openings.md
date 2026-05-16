# Section Bucket — Openings

Exactly **1 opening** is selected per article. Always.

The opening sets the entire article's register. A bad opening signals "AI-generated" before the reader has read ten words — generic definitions, "in this comprehensive guide", "fundamental to modern programming". A good opening earns the reader's attention by being specific, concrete, or surprising.

## Table of Contents

- [`open-quick`](#open-quick) — Quick Answer
- [`open-problem`](#open-problem) — The Problem
- [`open-mental-model`](#open-mental-model) — A Mental Model First
- [`open-error`](#open-error) — The Error You're Seeing
- [`open-scenario`](#open-scenario) — A Real Situation
- [`open-tldr`](#open-tldr) — TL;DR

---

## `open-quick`

**Name:** Quick Answer
**Use when:** The article targets a "how do I do X" query and the reader wants the answer fast. Almost always paired with intent=how-to.
**Skip when:** The topic is abstract, philosophical, or requires conceptual setup before code makes sense.
**Length:** 40–80 words of prose + one code block (5–12 lines).
**Voice fits:** terse-senior, opinionated-commentator, empathetic-debugger.
**Voice mismatches:** thoughtful-explainer (too patient for this opening).

### Writer instructions

Lead with the answer in the first sentence. State what to do, then immediately show it. NO preamble. NO "In this guide we'll explore". NO defining the language. NO restating the question.

Use realistic variable names in the code (`user_email`, `cart_total`) — never `x`, `foo`, `bar`, `data`.

### Good

> Use `Array.prototype.flat()` — it ships in every modern engine, no library needed. Pass a depth argument if you have nested arrays beyond one level.
>
> ```javascript
> const orders = [[1, 2], [3, 4]];
> const flatOrders = orders.flat();
> ```

### Bad

> In modern JavaScript development, working with nested arrays is a common task that developers encounter frequently. Fortunately, JavaScript provides several elegant solutions...

### Forbidden in this section

- Any sentence starting with "In modern...", "In today's...", "When working with..."
- The phrase "this guide" or "this article" or "this post"
- Defining what the language is
- Listing "several approaches" before showing one

---

## `open-problem`

**Name:** The Problem
**Use when:** The concept solves a recognisable pain point the reader has probably hit.
**Skip when:** The reader doesn't have a problem yet (e.g., learning a new concept for the first time).
**Length:** 80–150 words.
**Voice fits:** empathetic-debugger, thoughtful-explainer, opinionated-commentator.
**Voice mismatches:** tutorial-guide.

### Writer instructions

Open with a CONCRETE situation where a developer gets stuck without this concept. Make it feel familiar — name a real-ish project, describe a real-ish bug. The reader should think "yes, I've been there" within two sentences.

Set up tension. Do NOT solve it yet — the rest of the article does that.

### Good

> You're three hours into a refactor and your async function is returning what looks like a Promise but acts like undefined. You've added `await`. You've checked the function signature. The test still fails with a useless `Cannot read property 'id' of undefined`. The Promise you're awaiting was never returned — somewhere in the chain, a `.then()` callback forgot to `return`. This kind of bug is what got `async/await` added to the language in the first place.

### Bad

> Asynchronous programming is a fundamental aspect of modern JavaScript development. Many developers struggle to understand it...

### Forbidden

- Abstract problems ("developers often need to handle multiple operations")
- "Many developers struggle..." — this is filler
- Stating the problem in textbook form

---

## `open-mental-model`

**Name:** A Mental Model First
**Use when:** The concept is abstract enough that showing code first would confuse rather than clarify (closures, monads, ownership, lazy evaluation, generics, coroutines).
**Skip when:** The concept is concrete and code-explainable in 5 lines.
**Length:** 100–200 words.
**Voice fits:** thoughtful-explainer, opinionated-commentator.
**Voice mismatches:** terse-senior, tutorial-guide.

### Writer instructions

Open with an analogy or a mental model — something the reader can picture before they see any code. Then state the technical concept in plain language. Then signal the article will fill in the precision.

The analogy should be original and topic-specific. Avoid worn analogies (closures = backpacks, async = restaurant orders, recursion = mirrors). If your analogy could appear in any other tutorial, find a better one.

### Good (for Rust ownership)

> Imagine you're handing someone a physical key — not a copy, the actual key. Once you give it away, you no longer have it. You can't unlock the door anymore. If you want them to give it back, they have to explicitly hand it over. That's ownership in Rust, roughly. Values have owners. When you pass a value to a function, you're often handing the key over — unless you explicitly say otherwise. This is the model the borrow checker is enforcing, and once it clicks, the compiler stops feeling adversarial.

### Bad

> Ownership is one of Rust's most fundamental concepts. It ensures memory safety by enforcing rules at compile time...

### Forbidden

- Starting with the textbook definition
- Calling the concept "fundamental" or "core"
- Using a tired analogy

---

## `open-error`

**Name:** The Error You're Seeing
**Use when:** Topic is error-driven / debug intent. ALWAYS paired with is_error_driven=true.
**Skip when:** Article is not about a specific error or failure mode.
**Length:** 30–60 words + error block.
**Voice fits:** empathetic-debugger (strongly preferred), terse-senior.
**Voice mismatches:** thoughtful-explainer, opinionated-commentator.

### Writer instructions

Quote the error VERBATIM in a code block at the top. Then 2 sentences acknowledging the reader is stuck and stating that the cause is usually not what they suspect.

The error must be the literal text the reader sees in their terminal/stack trace — don't paraphrase, don't summarise, don't clean up.

### Good

> ```
> TypeError: Cannot read properties of undefined (reading 'map')
>     at processOrders (orders.js:14:18)
> ```
>
> If you landed here, you've probably already added an optional chain and the error didn't go away. The issue isn't where you're calling `.map()` — it's what's giving you `undefined` in the first place. Two upstream causes are responsible for ~90% of these.

### Bad

> When working with arrays in JavaScript, developers often encounter the TypeError...

### Forbidden

- Summarising the error in prose before quoting it
- Generic "this error occurs when" framings
- Skipping the verbatim quote

---

## `open-scenario`

**Name:** A Real Situation
**Use when:** Topic benefits from being grounded in a concrete project/build context (data processing, web services, CLIs, tools).
**Skip when:** Topic is pure syntax or pure theory.
**Length:** 150–250 words.
**Voice fits:** thoughtful-explainer, tutorial-guide, opinionated-commentator.
**Voice mismatches:** terse-senior.

### Writer instructions

Tell a small, concrete story. Name a fictional but realistic project ("a CLI for cleaning up log files", "a script that batches API requests to Stripe"). Describe what the developer is trying to do. End the scenario at the moment where the concept becomes relevant.

Stories make AI output sound human because they have texture — specific projects, specific stuck moments, specific code shapes. Real humans tell stories with detail; LLMs default to abstraction. Be detailed.

### Good (for Python context managers)

> You're writing a script that processes a folder of CSV exports from your client's billing system — ~400 files, each maybe 50MB. Your first pass works: open each file, parse it, write results to a database. Then you run it on the full set and your process dies somewhere around file #180 with "Too many open files". You forgot to close some of them. Not all — you have `f.close()` calls in there — but one of your `try` blocks raised before reaching the close, and you've been leaking file handles for two hours. Welcome to the problem `with` solves.

### Bad

> File handling is a common task in Python. When you open a file, you need to remember to close it...

### Forbidden

- Generic scenarios ("imagine you have a file...")
- Scenarios without specifics (no project name, no real-ish numbers)
- Skipping the "what went wrong" moment

---

## `open-tldr`

**Name:** TL;DR
**Use when:** The article is comparison-heavy or the reader is likely a scanner who wants the conclusion fast (often paired with intent=reference).
**Skip when:** The article is conceptual or builds toward a verdict that requires context.
**Length:** 60–100 words, can include 2–4 bullets.
**Voice fits:** terse-senior, opinionated-commentator.
**Voice mismatches:** thoughtful-explainer, empathetic-debugger.

### Writer instructions

State the conclusion first. The rest of the article justifies it. This works for reference and comparison content where the reader wants to know the verdict before deciding whether to read the deep dive.

You can use a single H3 "TL;DR" header or just lead with bold prose. Don't artificially structure this section — it's meant to be skimmable.

### Good

> **TL;DR.** Default to `interface` for object shapes you'll extend or want consumers to merge into. Use `type` when you need unions, intersections, or anything beyond a plain object. They're not interchangeable, and the difference matters most around library API design — but for application code, you can usually use either.

### Bad

> In this comprehensive guide, we'll explore the differences between TypeScript interfaces and type aliases. By the end of this article, you'll understand...

### Forbidden

- "In this article you'll learn" — TL;DR means tell them now
- Hedging without committing ("it depends on your use case")
- Promising what's coming instead of stating the answer
