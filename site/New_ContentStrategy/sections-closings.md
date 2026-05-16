# Section Bucket — Closings

Exactly **1 closing** is selected per article. Always.

The closing is the second most important fingerprint location after the opening. The previous template system always closed with "Next Steps" or "Related" sections — a uniform tail that Google detected. These closings deliberately differ in shape, length, and purpose.

## Table of Contents

- [`close-recap`](#close-recap) — Quick Recap
- [`close-next`](#close-next) — Where to Go From Here
- [`close-one-thing`](#close-one-thing) — One Thing to Remember
- [`close-checklist`](#close-checklist) — Quick Checklist
- [`close-open-question`](#close-open-question) — A Question to Sit With

---

## `close-recap`

**Name:** Quick Recap
**Use when:** Long article (2,500+ words) that benefits from summarising the key points before the reader closes the tab.
**Skip when:** Short article — the reader doesn't need to be reminded what they just read.
**Length:** 100–150 words.
**Voice fits:** all voices.

### Writer instructions

Restate the main arguments or facts of the article in 3–5 sentences. NOT a bullet list — flowing prose. Don't repeat phrasing from the body; this is a fresh framing.

End with a sentence that points outward — what does this knowledge connect to?

### Good

> Closures are a binding between a function and the variables it captured from its enclosing scope. In Python, that binding goes through cell objects, and the `nonlocal` keyword controls whether you can rebind enclosing-scope variables. The pattern is most useful for state-holding callbacks, decorators, and factory functions — anywhere you'd otherwise reach for a class with one method. The trade-off is debuggability: closures hide their state from inspection unless you reach for `__closure__`. Once you have the mental model, they stop feeling magical and start feeling like ordinary functions with backpacks.

### Bad

> In this article, we've explored closures in Python. We've seen what they are, how they work, and several common patterns. Closures are a powerful feature that...

### Forbidden

- "In this article we've covered..."
- "We've explored / we've seen..."
- Bullet list format
- "Powerful feature"

---

## `close-next`

**Name:** Where to Go From Here
**Use when:** Tutorial-style or learning-path article. The reader is building knowledge and wants to know what's next.
**Skip when:** Reference or concept article that's complete on its own.
**Length:** 100–180 words. Can include 2–3 inline links.
**Voice fits:** tutorial-guide, thoughtful-explainer.

### Writer instructions

Suggest specific next topics with a sentence of reasoning each. Inline links woven into prose — NOT a bulleted list of links.

Be opinionated about the order — if learning A before B matters, say so.

### Good

> If decorators are the next thing you want to tackle, start with the standard library — Python's `functools.wraps` and `functools.lru_cache` are decorator implementations using closures under the hood, and reading their source is a good education. After that, the [Python decorators guide](url) covers writing your own. If you'd rather go deeper on the closure mechanism, the [Python data model docs section on function objects](url) walks through `__closure__` and `__code__` attributes — it's denser than this article but worth the read once the basics are solid.

### Forbidden

- A bulleted list of "next topics"
- "Now that you understand X..."
- More than 3 links

---

## `close-one-thing`

**Name:** One Thing to Remember
**Use when:** Conceptual article where one insight matters more than the rest.
**Skip when:** No single takeaway dominates — the article is a balanced reference.
**Length:** 50–100 words.
**Voice fits:** opinionated-commentator, thoughtful-explainer, terse-senior.

### Writer instructions

State the ONE thing the reader should carry forward. Brief. Pointed. Memorable.

This works well as a closing because it's distinctive — most articles don't end with a single-sentence takeaway, and the brevity itself is a fingerprint differentiator.

### Good

> One thing to take with you: closures in Python capture references, not values. Every weird closure bug — every "all my buttons share the same click handler", every "the loop variable's value is wrong" — traces back to that one fact. Internalise it and the rest follows.

### Bad

> In conclusion, closures are an important Python feature that every developer should master. They enable many powerful patterns...

### Forbidden

- "In conclusion..."
- "To summarise..."
- More than one takeaway
- Longer than 100 words

---

## `close-checklist`

**Name:** Quick Checklist
**Use when:** Reference or how-to article where the reader will return to scan for the specific thing they forgot.
**Skip when:** Conceptual article — checklists don't fit narrative content.
**Length:** 4–7 bullet points, terse. 80–150 words total.
**Voice fits:** terse-senior, tutorial-guide.

### Writer instructions

A tight bullet list of the key rules or steps. Each bullet a single sentence or fragment. Skimmable.

This is a section format that's *expected* to be templated — checklists look like checklists everywhere. The variation here comes from the specific content, not the format.

### Good

> - Use `nonlocal` when modifying an enclosing scope's variable; without it, you create a new local
> - Closures capture references, not values — so loop variables share state if not handled
> - Inspect captures via `function.__closure__` for debugging
> - Default arguments aren't closures; they're evaluated once at function definition
> - Prefer closures over single-method classes for stateful callbacks
> - Use `functools.partial` instead of a closure when all you need is to pre-fill arguments

### Forbidden

- Sentences (use fragments)
- More than 7 items
- Numbered list (use bullets — numbered implies order)

---

## `close-open-question`

**Name:** A Question to Sit With
**Use when:** Essay-style or philosophical article. The closing should provoke thought, not summarise.
**Skip when:** Article is technical reference or tutorial.
**Length:** 80–150 words.
**Voice fits:** thoughtful-explainer, opinionated-commentator.

### Writer instructions

End with a question or observation that opens rather than closes. The reader should leave thinking, not feeling "done".

This works rarely — only when the article has earned a philosophical close. Most articles should not use this. If you're not sure, pick a different closing.

### Good

> One thing worth thinking about: most languages built since 2010 have closures. Most languages built before 1990 didn't. The intervening period — Lisp aside — was a strange detour through pure object-orientation. We ended up rediscovering that functions-as-values is a fundamental primitive, not a "functional programming feature". What other primitives are mainstream languages currently missing? My bet's on first-class effects, but ask me again in ten years.

### Bad

> What do you think? Let me know in the comments!

### Forbidden

- "Let me know what you think"
- Engagement bait
- Rhetorical questions that don't actually invite reflection
- Closings that contradict the article's tone
