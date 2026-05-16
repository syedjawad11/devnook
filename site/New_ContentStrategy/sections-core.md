# Section Bucket — Core Explanation

1–2 core sections per article. These are where the article does its main explanatory work — defining what something is, explaining how it works, or unpacking the design philosophy.

## Table of Contents

- [`core-how-it-works`](#core-how-it-works) — How It Actually Works
- [`core-definition`](#core-definition) — What This Is, Precisely
- [`core-syntax-detail`](#core-syntax-detail) — The Syntax in Detail
- [`core-design-decision`](#core-design-decision) — Why the Language Designers Chose This
- [`core-spec-reading`](#core-spec-reading) — What the Spec Actually Says

---

## `core-how-it-works`

**Name:** How It Actually Works
**Use when:** The mechanism matters — the reader will write better code if they understand what the runtime is doing.
**Skip when:** The mechanism is opaque enough that explaining it is academic distraction.
**Length:** 200–400 words.
**Voice fits:** thoughtful-explainer, opinionated-commentator.
**Code allowed:** Maximum 1 small snippet (5–8 lines) if it illustrates the mechanism. Otherwise prose only.

### Writer instructions

Explain the underlying mechanism in plain language. What is the runtime, compiler, or interpreter actually doing? Walk through it as if you were drawing on a whiteboard.

Use specific language. Not "the language processes this" — say "the V8 engine compiles this to bytecode and then..." or "the Python interpreter stores closures by capturing variable references in the function's __closure__ tuple".

### Good

> When you create a closure in Python, the interpreter does something specific: it captures the *variable name*, not the value, in a special tuple attached to the function called `__closure__`. Each variable is wrapped in a "cell" object. When the closure runs later, it looks up the current value through the cell — which is why closures see the current value of a variable, not the value at the time the closure was created. This is the source of the classic "all closures in this loop print the same thing" bug.

### Bad

> Python's closure mechanism works by capturing variables from the enclosing scope. This is a powerful feature that...

### Forbidden

- "Powerful feature", "elegant solution", "fundamental mechanism"
- Vague descriptions ("the language handles this efficiently")
- Restating the definition without explaining the mechanism

---

## `core-definition`

**Name:** What This Is, Precisely
**Use when:** The concept is unfamiliar enough that the reader needs a precise definition before the article can do anything else.
**Skip when:** The concept is well-known and the article is targeting an audience that already understands the basics.
**Length:** 150–300 words.
**Voice fits:** thoughtful-explainer, terse-senior, tutorial-guide.

### Writer instructions

Define the concept precisely. Then immediately follow with the most common misconception and correct it.

Definitions feel "AI-generated" when they're generic. Make this one specific to the language — what makes Python's version of this different from Java's? What does this language's documentation actually call it?

Avoid leading with "X is a..." as the literal opening. Reorder to lead with something more interesting and put the definition in the second or third sentence.

### Good

> The closure in Python is not the function object itself — that's a common mix-up. The closure is the *binding* between a function and the cells holding its captured variables. You can inspect it directly: any function defined inside another function has a `__closure__` attribute containing those cells, and you can read their current values via `cell.cell_contents`. This matters because closures don't capture values at definition time; they capture references that are resolved when the inner function runs.

### Bad

> A closure is a function that remembers variables from the scope in which it was created. This is a fundamental concept in functional programming...

### Forbidden

- "X is one of the most important concepts..."
- "X allows developers to..."
- Defining without addressing the most common misconception

---

## `core-syntax-detail`

**Name:** The Syntax in Detail
**Use when:** Topic is syntax-heavy and the reader needs each part of the syntax explained (always paired with is_syntax_heavy=true).
**Skip when:** Topic is conceptual, not syntactic.
**Length:** 200–400 words.
**Code budget:** 1–2 small annotated examples, ~10 lines each.
**Voice fits:** tutorial-guide, terse-senior.
**Voice mismatches:** thoughtful-explainer (too discursive for syntax).

### Writer instructions

Walk through the syntax piece by piece. Use a small annotated code example as the anchor, and refer back to specific parts of it by line. Be precise about what each token does.

This section often becomes mechanical. Counter that by including ONE non-obvious detail — a quirk, a parser exception, a precedence trap.

### Good

```python
result = [transform(item) for item in items if item.valid]
#         └────┬────┘ └─┬─┘ └──┬──┘ └─────┬─────┘
#              │        │       │          └─ filter clause (evaluated FIRST per item)
#              │        │       └─ source iterable
#              │        └─ loop variable, scoped to the comprehension
#              └─ expression applied to each surviving item
```

> The order this reads is misleading. The filter (`if item.valid`) is evaluated *before* the expression on the left — Python iterates `items`, applies the filter, and only then evaluates `transform()` on the survivors. The visual left-to-right doesn't match execution order. This trips people up when the `transform()` expression has side effects and they're surprised it didn't fire on filtered items.

### Bad

> The list comprehension syntax in Python consists of three main parts: the expression, the loop, and an optional filter clause. Each part serves a specific purpose...

### Forbidden

- Walking through syntax without showing it inline
- "Powerful feature" or "elegant syntax"
- Missing the non-obvious detail

---

## `core-design-decision`

**Name:** Why the Language Designers Chose This
**Use when:** The design philosophy is genuinely interesting and connects to broader language design (often paired with is_abstract=true or intent=concept).
**Skip when:** The design decision is trivial or uncontroversial.
**Length:** 300–500 words.
**Voice fits:** thoughtful-explainer, opinionated-commentator.
**Voice mismatches:** terse-senior, tutorial-guide.

### Writer instructions

This is the "insight" section. Explain WHY the language did it this way. What problem were the designers solving? What trade-offs were they accepting? How does this fit the language's broader philosophy?

Cite specific design documents, PEPs, RFCs, or maintainer quotes where possible. Reference how other languages did this differently.

You can have an opinion here. "I think Go's choice was right for what Go is trying to be." "The Rust ownership model has obvious ergonomic costs but the safety guarantees are worth it." Opinions read as human.

### Good

> Go's decision to require explicit error returns instead of exceptions is a deliberate philosophical stance. The designers — Pike, Thompson, Griesemer — were reacting against what they saw as the failure mode of exception-based languages: control flow becomes implicit and reviewers can't see at a glance where a function might exit. Russ Cox has written about this directly. The trade-off is verbosity, which Go embraces. The result is code that *looks* repetitive (`if err != nil`) but where every potential exit is visible. Personally, I think this is the right call for Go's domain (infrastructure software written in teams) but it's a clear ergonomic cost for application code where error paths are rare and known.

### Bad

> Go takes a different approach to error handling than many other modern languages. This design choice reflects Go's emphasis on simplicity and explicitness, which is a core part of the language's philosophy...

### Forbidden

- Statements that could be in any language's docs ("emphasises simplicity")
- No opinion or stance
- No reference to specific people, docs, or RFCs

---

## `core-spec-reading`

**Name:** What the Spec Actually Says
**Use when:** The topic has a formal specification and the spec language matters (often advanced or standards-based topics — ECMAScript spec features, Java JLS sections, Go specification clauses).
**Skip when:** Topic is informal or no canonical spec exists for it.
**Length:** 200–400 words.
**Voice fits:** terse-senior, opinionated-commentator.
**Voice mismatches:** empathetic-debugger.

### Writer instructions

Quote the relevant section of the spec (or paraphrase precisely if it's long), and translate the formal language into plain English. Explain what the spec language actually requires of implementations.

This section signals deep expertise. Get the spec citation right (section numbers, version). Don't fake it — if you can't cite the spec accurately, use a different section.

### Good

> The ECMAScript specification (section 13.15.4, "Runtime Semantics: AssignmentExpression : LeftHandSideExpression = AssignmentExpression") defines what happens during destructuring assignment with surprising precision. The right-hand side is fully evaluated before any property access begins on it. This is why `let { a } = throwingFunction()` will throw from the function call, not from any property access — there is no property access yet at the moment the call fires. Implementations that "optimise" by accessing properties lazily are not conformant. This is one of those spec details that almost never matters until you're chasing a weird ordering bug.

### Bad

> According to the ECMAScript specification, destructuring assignment evaluates the right-hand side first. This is an important detail to understand...

### Forbidden

- Vague references ("the spec says")
- No section number or citation
- Restating the rule without explaining what it requires of implementations
