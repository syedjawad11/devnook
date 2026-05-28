# DevNook Content Style System

Single source of truth for all content written for devnook.dev. Used by writer agents in both pipelines (A = language rewrites, B = AI/Productivity new articles).

---

## How to use this file

1. **Receive the brief** — language/concept or AI-productivity topic, primary keyword, intent, difficulty.
2. **Pick the section set** — language posts use the Language set (18 sections). AI/Productivity posts use the AI/Productivity set (12 sections). Never mix the two sets in one article.
3. **Pick 5–8 sections** — always 1 opening + 1 closing. Fill the middle from Core, Code, Practical, Comparison buckets per the constraints below.
4. **Pick a voice** — from the 3 approved voices. Apply it throughout; drift = fail.
5. **Write following SEO rules** — title, meta, heading hierarchy, keyword density.
6. **Output frontmatter** — per the spec at the bottom of this file.

Before you write a single word, check the **Forbidden Language** section (Section 5). First-person experiential claims and AI clichés are hard-fail at QA. You cannot fix them in revision — avoid them at write-time.

---

## Section 1 — Language Post Section Set (18 sections)

Use this section set ONLY for posts under `/languages/{lang}/{concept}/`.

**Selection rules:**
- Exactly 1 opening. Exactly 1 closing.
- Core: 1–2 sections.
- Code: 1–3 sections.
- Practical: 0–2 sections (never more than 2 — multiple practical sections create "comprehensive coverage" fingerprint).
- Comparison: 0–1 sections.
- Total article sections: 5–8.

---

### Openings (pick exactly 1)

#### `open-problem`
**Use when:** The concept solves a recognisable pain point the reader has probably hit.
**Skip when:** Reader doesn't have a problem yet (first-time learning).
**Length:** 80–150 words.
**Voice fits:** thoughtful-explainer. Not tutorial-guide.

Open with a CONCRETE situation where a developer gets stuck without this concept. Name a real-ish project, describe a real-ish bug. The reader should think "yes, I've been there" within two sentences. Set up tension — do NOT solve it yet.

**Good:**
> You're three hours into a refactor and your async function is returning what looks like a Promise but acts like undefined. You've added `await`. You've checked the function signature. The test still fails with `Cannot read property 'id' of undefined`. The Promise you're awaiting was never returned — somewhere in the chain, a `.then()` callback forgot to `return`.

**Forbidden:** Abstract problems ("developers often need to..."). "Many developers struggle..." filler.

---

#### `open-mental-model`
**Use when:** Concept is abstract enough that showing code first would confuse (closures, ownership, lazy evaluation, generics, coroutines).
**Skip when:** Concept is concrete and code-explainable in 5 lines.
**Length:** 100–200 words.
**Voice fits:** thoughtful-explainer. Not terse-senior, tutorial-guide.

Open with an analogy the reader can picture before seeing code. State the technical concept in plain language. Signal the article will fill in the precision. Analogy must be original and topic-specific — avoid worn metaphors (closures = backpacks, async = restaurants).

**Good (Rust ownership):**
> Imagine handing someone a physical key — not a copy, the actual key. Once you give it away, you no longer have it. You can't unlock the door anymore. If you want it back, they have to explicitly hand it over. That's ownership in Rust. Values have owners. When you pass a value to a function, you're often handing the key over — unless you explicitly say otherwise.

**Forbidden:** Starting with textbook definition. Calling concept "fundamental" or "core". Tired analogy.

---

#### `open-error`
**Use when:** Topic is error-driven / debug intent.
**Skip when:** Article is not about a specific error.
**Length:** 30–60 words + error block.
**Voice fits:** terse-senior.

Quote the error VERBATIM in a code block first. Then 2 sentences stating the cause is usually not what the reader suspects.

**Good:**
> ```
> TypeError: Cannot read properties of undefined (reading 'map')
>     at processOrders (orders.js:14:18)
> ```
> The issue isn't where you're calling `.map()` — it's what's giving you `undefined` in the first place. Two upstream causes are responsible for ~90% of these.

**Forbidden:** Summarising the error in prose before quoting it. Generic "this error occurs when" framings.

---

#### `open-tldr`
**Use when:** Comparison-heavy article or reader is likely a scanner (paired with intent=reference).
**Skip when:** Article is conceptual or builds toward a verdict requiring context.
**Length:** 60–100 words. May include 2–4 bullets.
**Voice fits:** terse-senior.

State the conclusion first. The rest of the article justifies it.

**Good:**
> **TL;DR.** Default to `interface` for object shapes you'll extend or want consumers to merge into. Use `type` when you need unions, intersections, or anything beyond a plain object. They're not interchangeable — the difference matters most around library API design.

**Forbidden:** "In this article you'll learn". Hedging without committing. Promising what's coming instead of stating the answer.

---

### Core Explanation (pick 1–2)

#### `core-how-it-works`
**Use when:** The mechanism matters — reader writes better code if they understand what the runtime is doing.
**Skip when:** Mechanism is opaque enough that explaining it is academic distraction.
**Length:** 200–400 words. Max 1 small snippet (5–8 lines).
**Voice fits:** thoughtful-explainer.

Explain the underlying mechanism in plain language. What is the runtime, compiler, or interpreter actually doing? Use specific language — not "the language processes this" but "the V8 engine compiles this to bytecode and then..." or "the Python interpreter stores closures by capturing variable references in the function's `__closure__` tuple".

**Forbidden:** "Powerful feature", "elegant solution". Vague descriptions ("the language handles this efficiently"). Restating the definition without explaining the mechanism.

---

#### `core-design-decision`
**Use when:** Design philosophy is genuinely interesting and connects to broader language design.
**Skip when:** Design decision is trivial or uncontroversial.
**Length:** 300–500 words.
**Voice fits:** thoughtful-explainer.

Explain WHY the language did it this way. What problem were the designers solving? What trade-offs were they accepting? How does this fit the language's broader philosophy? Cite specific design documents, PEPs, RFCs, or maintainer quotes where possible. Reference how other languages handled this differently. State your assessment directly — don't hedge without reasoning.

**Good (Go error handling):**
> Go's decision to require explicit error returns instead of exceptions is a deliberate philosophical stance. The designers — Pike, Thompson, Griesemer — were reacting against implicit control flow in exception-based languages where reviewers can't see at a glance where a function might exit. Russ Cox has written about this directly. The trade-off is verbosity, which Go embraces. The result: code where every potential exit is visible. The right call for Go's domain (infrastructure software written in teams), with a clear ergonomic cost for application code where error paths are rare.

**Forbidden:** Statements that could be in any language's docs ("emphasises simplicity"). No stance. No reference to specific people, docs, or RFCs.

---

#### `core-syntax-detail`
**Use when:** Topic is syntax-heavy and reader needs each part explained (paired with is_syntax_heavy=true).
**Skip when:** Topic is conceptual, not syntactic.
**Length:** 200–400 words. 1–2 annotated examples (~10 lines each).
**Voice fits:** tutorial-guide, terse-senior.

Walk through the syntax piece by piece. Use an annotated code example as the anchor, refer back to specific parts by line. Include ONE non-obvious detail — a quirk, parser exception, or precedence trap.

**Forbidden:** Walking through syntax without showing it inline. Missing the non-obvious detail.

---

### Code & Examples (pick 1–3)

#### `code-minimal`
**Use when:** Almost always for code-heavy topics. Reader needs to see the simplest running version first.
**Skip when:** Already covered by the opening section.
**Length:** 5–15 lines of code + 50–80 words prose framing.
**Voice fits:** all voices.

Show the simplest possible code that demonstrates the concept and runs as-is. Use realistic variable names (`user_email`, `cart_total` — never `x`, `foo`, `bar`). Frame with 1–2 sentences before, 2–4 sentences after. The "after" adds something the code doesn't show — context, a subtle behaviour, or a connection to what comes next.

**Forbidden:** Variable names like `x`, `foo`, `data`. Comments that just restate what the code does. Empty "this code demonstrates X" framing.

---

#### `code-realistic`
**Use when:** Reader needs to see how the concept appears in production code.
**Skip when:** Article is purely about syntax basics.
**Length:** 15–30 lines + 80–150 words explanation.
**Voice fits:** all voices.

Show code that looks like something from a real project — with imports, error handling, sensible names, realistic data. After the code, explain the design decisions: why structure it this way, what alternatives existed, what trade-offs are made.

**Forbidden:** `example` or `demo` in function/variable names. Code that wouldn't pass a basic code review. Explanation that says what the code does without saying why it's structured that way.

---

#### `code-walkthrough`
**Use when:** Concept is best understood by progressive code construction — building from a start through 3–4 steps to a finished version.
**Skip when:** No natural progression exists.
**Length:** 3–5 code blocks + 200–400 words prose.
**Voice fits:** tutorial-guide (strongly preferred).

Start with a minimal/broken version. Each subsequent block adds one thing and improves the previous. End with the final version the reader could use. After each block, explain what changed and why — add value the code doesn't show. This is the only section where step-by-step structure is warranted.

**Forbidden:** Steps that repeat the previous verbatim. More than 5 steps. Step explanations that add no new information.

---

#### `code-side-by-side`
**Use when:** Pairing this concept's code against an alternative clarifies its purpose.
**Skip when:** No clear alternative exists.
**Length:** 2 code blocks + 100–150 words.
**Voice fits:** terse-senior, thoughtful-explainer.

Show the same task implemented two ways: with this concept and without. Explain what changes — not just in line count but in readability, performance, or correctness. This is different from before/after: the alternative isn't worse, just a different choice.

**Forbidden:** Making the alternative look bad when it's valid. No discussion of when each is preferred. Code blocks that aren't actually equivalent.

---

### Practical (pick 0–2 max)

#### `prac-gotchas`
**Use when:** Topic has well-known traps that bite repeatedly.
**Skip when:** Topic is straightforward enough that gotchas would be padding.
**Length:** 200–350 words. Format as 2–3 labelled traps.
**Voice fits:** terse-senior.

List 2–3 specific traps. For each: name it, show the broken case in code or scenario, explain why it bites, give the fix in one sentence. Use concrete code examples and cite community reports or GitHub issue patterns — not personal anecdotes.

**Good trap format:**
> **Trap: the loop closure bug.**
> ```javascript
> for (var i = 0; i < 3; i++) {
>   setTimeout(() => console.log(i), 0);
> }
> // Prints 3, 3, 3
> ```
> The closures all reference the same `i`, and by the time the timeouts fire, the loop has finished. Fix: use `let` instead of `var`, or capture `i` in an IIFE.

**Forbidden:** Generic "be careful" advice without specifics. More than 3 gotchas. No code or scenario to ground each one. First-person anecdotes ("I once spent...", "I've seen this in production...").

---

#### `prac-when-not-to`
**Use when:** Concept is commonly over-applied or misused.
**Skip when:** Concept is rarely misapplied.
**Length:** 150–250 words.
**Voice fits:** thoughtful-explainer.

Give 2–3 concrete situations where this concept is the wrong tool. Be specific about what to use instead. This section is a credibility marker — saying "here's when not to use it" signals genuine familiarity with the concept.

**Forbidden:** Hedging ("it's complicated, depends on use case"). No specific alternative named. Anti-patterns too obvious to need stating.

---

#### `prac-performance`
**Use when:** Performance is decision-relevant for this concept.
**Skip when:** Performance is universally fine for this concept.
**Length:** 200–350 words.
**Voice fits:** terse-senior, thoughtful-explainer.

Discuss performance characteristics that actually matter. Big-O if relevant. Hidden costs the developer might not see. When perf becomes a problem and what to do about it. Don't invent numbers — if citing a benchmark, source it or qualify it ("benchmarked on Node 20, ~10–20% overhead in tight loops"). Vague claims ("it's faster") are AI-tells.

**Forbidden:** Invented numbers without sourcing. "Don't worry about performance" hand-waving. Performance discussion that doesn't change the developer's decision.

---

#### `prac-production-patterns`
**Use when:** The concept's textbook usage differs from how it's actually used in production codebases.
**Skip when:** Textbook and production usage are the same.
**Length:** 250–400 words.
**Voice fits:** thoughtful-explainer, terse-senior.

Show 1–2 patterns that production code uses but tutorials rarely cover — how the concept appears in a typical framework codebase, how teams structure code around it, naming conventions. Cite specific frameworks or well-known codebases where possible. If you can't cite specifics, skip this section.

**Forbidden:** Patterns that are just textbook usage with a real-ish variable name. Claims about "how production code works" without specifics.

---

### Comparison & Context (pick 0–1)

#### `comp-cross-language`
**Use when:** Showing how the concept exists in other languages clarifies what's distinctive about this one.
**Skip when:** Concept is too language-specific for comparison to be meaningful.
**Length:** 200–400 words.
**Voice fits:** thoughtful-explainer.

Show 2–3 other languages' versions of the same concept. Brief code snippets. Highlight what's distinctive about THIS language's approach. Don't just list syntax differences — explain what each language's choice reveals about its design priorities.

**Forbidden:** Comparing without explaining what the difference reveals. Treating every language's approach as equally good. More than 3 languages.

---

### Closings (pick exactly 1)

#### `close-recap`
**Use when:** Long article (2,500+ words) that benefits from summarising key points.
**Skip when:** Short article — no need to remind reader what they just read.
**Length:** 100–150 words. Flowing prose, NOT bullet list.

Restate main arguments in 3–5 sentences. Fresh framing — don't repeat phrasing from the body. End with a sentence pointing outward.

**Forbidden:** "In this article we've covered...". "We've explored / we've seen...". Bullet list. "Powerful feature".

---

#### `close-next`
**Use when:** Tutorial-style or learning-path article. Reader is building knowledge and wants to know what's next.
**Skip when:** Reference or concept article complete on its own.
**Length:** 100–180 words. 2–3 inline links in prose.

Suggest specific next topics with a sentence of reasoning each. Inline links woven into prose — NOT a bulleted list. Be opinionated about the order — if learning A before B matters, say so.

**Forbidden:** Bulleted list of next topics. "Now that you understand X...". More than 3 links.

---

## Section 2 — AI/Productivity Section Set (12 sections)

Use this section set ONLY for posts under the AI/Productivity category. Intents served: Tutorial/How-to, Comparison, Listicle, Explainer.

**Selection rules:**
- Exactly 1 opening (ai-open-hook OR ai-open-promise). Exactly 1 closing (ai-conclusion-cta).
- Core: 1–2 sections (ai-core-explainer and/or ai-core-mechanism).
- Body sections: 2–5 from the remaining pool, matched to article intent.
- Total article sections: 5–8.
- Word target: 2,500–3,500 words.

All citations must be from 3rd-party sources — research papers, survey data, GitHub trends, company case studies. Never invent usage statistics or claim personal testing.

---

#### `ai-open-hook`
**Intent fit:** All.
**Use when:** A data point or research finding makes a stronger lead than a premise.
**Length:** 60–120 words.

Open with a specific, cited statistic or research finding that immediately frames why the topic matters. Source must be named (e.g., "A 2024 GitHub Copilot survey of 500 developers..."). Then bridge to what the article covers.

**Forbidden:** Inventing statistics. Vague "studies show" without naming the study. Overclaiming ("changed everything", "revolutionized").

---

#### `ai-open-promise`
**Intent fit:** All. Strong for SERP snippets.
**Use when:** Article is instructional or comparison-heavy and reader wants the payoff framed upfront.
**Length:** 60–100 words. Can use a TL;DR box.

State what the reader will know or be able to do after reading this article. Be specific — name the tools, the outcome, the skill level assumed. A good promise reads like a job spec: clear deliverable, no fluff.

**Forbidden:** "In this comprehensive guide..." openings. Vague "you'll learn everything about X". Promising more than the article delivers.

---

#### `ai-core-explainer`
**Intent fit:** Explainer, Tutorial.
**Use when:** Defining the concept or tool clearly before the article can do anything else.
**Length:** 200–350 words.

Define the concept precisely and concisely. Immediately address the most common misconception. Then state what makes this tool/concept distinctive compared to the broader category. No first-person experiential claims — cite documentation, developer surveys, or public benchmarks instead.

**Forbidden:** Starting with "X is a..." as literal first sentence. Defining without addressing common misconceptions. "Fundamental", "powerful", "revolutionary".

---

#### `ai-core-mechanism`
**Intent fit:** Explainer.
**Use when:** Understanding how something works under the hood helps the reader use it better.
**Length:** 200–400 words. Up to 1 diagram or code snippet.

Explain the underlying mechanism — how the model, pipeline, or tool actually works. Use specific language: architecture names, API call flows, token limits, retrieval steps. Cite official documentation or published research where available.

**Forbidden:** "Magic happens here" hand-waving. Vague descriptions without technical grounding. Claiming to know internal details that aren't publicly documented.

---

#### `ai-step-by-step`
**Intent fit:** Tutorial.
**Use when:** Article is instructional and reader is following along.
**Length:** 400–700 words. Numbered steps with code blocks or screenshots as needed.

Walk through the process step by step. Each step: what to do, what the expected output is, common failure mode and fix. Steps should be reproducible — a reader following exactly these steps should get the stated result.

**Forbidden:** Steps that are too vague to follow. Skipping prerequisite setup. Not acknowledging that tool UIs or APIs change frequently (add a date anchor).

---

#### `ai-comparison-table`
**Intent fit:** Comparison, Listicle.
**Use when:** Multiple tools or approaches are being compared.
**Length:** 200–400 words + 1 structured table.

Build a comparison table with consistent criteria across all options. Pick criteria that actually matter for a decision (cost, latency, context window, local vs cloud, free tier) — not vanity metrics. After the table, give a direct recommendation for the most common use case.

**Forbidden:** Criteria that all options score the same on (pointless comparison). No recommendation after the table. Outdated pricing data presented as current (note when data was last verified).

---

#### `ai-use-cases`
**Intent fit:** All.
**Use when:** Reader needs to understand where this tool or concept applies in the real world.
**Length:** 250–400 words. 3–4 use cases.

For each use case: name it, describe the scenario concisely, explain why this tool/approach fits. Cite public case studies, company blog posts, or developer community reports where available. Generic "can be used for..." statements are padding.

**Forbidden:** Use cases so broad they could apply to anything. No supporting evidence or citation. Implying personal validation of each use case.

---

#### `ai-pitfalls`
**Intent fit:** All.
**Use when:** Topic has meaningful failure modes that affect real-world adoption.
**Length:** 200–350 words. 2–4 labelled pitfalls.

Name specific pitfalls — hallucination patterns, rate limits, context bleed, cost blowouts, prompt injection surfaces. For each: what it is, when it manifests, how to detect it, how to mitigate it. Source pitfalls from community reports, published research, or documented incidents — not personal experience.

**Forbidden:** Generic "AI can be wrong" without specifics. More than 4 pitfalls. First-person framing ("I've found that...").

---

#### `ai-examples-cited`
**Intent fit:** All.
**Use when:** Worked examples backed by 3rd-party data strengthen the article's claims.
**Length:** 200–400 words. 1–3 examples, each with a named source.

Show concrete results or patterns from cited sources. Format: describe the scenario, name the source, state the finding or result. Community reports from Stack Overflow surveys, GitHub Next, HuggingFace blog, Google DeepMind papers, etc. are all valid.

**Forbidden:** Invented examples presented as real. Unnamed "company X" without a citation. "Based on extensive testing" without naming the test source.

---

#### `ai-faq`
**Intent fit:** All.
**Use when:** Article targets queries where Google shows People Also Ask data.
**Length:** 3–5 questions with 60–120 word answers each.

Pull questions from PAA data for the primary keyword. Write direct answers — the answer should be fully useful even if the reader doesn't read the rest of the article. No "great question!" or meta-commentary.

**Forbidden:** Questions the article already answers verbatim elsewhere. Vague answers that don't commit to a position. "It depends" without naming the conditions.

---

#### `ai-tools-list`
**Intent fit:** Listicle.
**Use when:** Article is a curated list of tools.
**Length:** 400–700 words. 4–8 tools, consistent format per tool.

For each tool: name + one-line description, key strengths (2–3 bullets), key weaknesses (1–2 bullets), best-for use case, pricing tier. Keep each entry balanced — listing only strengths reads as sponsored content.

**Forbidden:** More than 8 tools (the list becomes noise). Missing weaknesses. Pricing data without a "as of [month year]" note.

---

#### `ai-conclusion-cta`
**Intent fit:** All. Always the closing section for AI/Productivity posts.
**Length:** 100–150 words.

Summarise the 1–2 most actionable takeaways in plain language. Then give a clear call to action — not "leave a comment" but a next step the reader can actually take (try the tool, run this command, read this documentation). Specific is better than generic.

**Forbidden:** "In conclusion..." opener. Summarising the entire article. Vague CTA ("explore the tool"). More than 2 takeaways.

---

## Section 3 — Voices

Three approved voices. One is selected per article. Maintain it throughout — voice drift is the second-biggest AI fingerprint after structural uniformity.

**Dropped voices (do not use):**
- `opinionated-commentator` — built on first-person rhetorical stances incompatible with no-personal-experience policy.
- `empathetic-debugger` — built on "I've been there" war stories which are first-person experiential claims.

---

### `terse-senior`

The terse senior engineer. Writes like they're answering a colleague's Slack message — short sentences, plain verbs, no preamble. Believes most explanation is filler.

**Sentence shape:** Short to medium (8–18 words). Frequent fragments. Almost no subordinate clauses. Direct subject-verb-object. Few hedges.

**Vocabulary:** Plain Anglo-Saxon verbs (use, run, get, make, fix, ship). Domain terms used precisely. No filler adjectives. Acronyms used without expansion when domain-standard.

**Register:** No first person. Third person dominant. Imperative common ("call this, return that"). Second person occasional ("you'd want...").

**Good:**
- "Use `Array.find()`. Returns the element or undefined."
- "Three reasons this breaks. First..."
- "Don't reach for reduce here — a for loop is clearer."

**Bad:**
- "There are several reasons why this might break..."
- "It's worth noting that Array.find() is a useful method..."

**Best for:** Reference content, how-to articles, syntax-focused pieces, error articles.

**Voice integrity check:** Any sentence over 25 words → cut it in half.

---

### `thoughtful-explainer`

The thoughtful explainer. Writes like they're explaining over coffee — paragraphs, analogies, occasional stance. Believes the right metaphor saves a thousand words.

**Sentence shape:** Medium to long (15–30 words). Subordinate clauses used to add nuance, not to pad. Occasional dash-aside for context. Paragraphs 3–5 sentences typically.

**Vocabulary:** Wide range, including occasional unusual word for texture. Concrete nouns over abstract ("a Promise" not "an asynchronous operation"). Specific examples preferred ("Stripe's webhook handler" not "a webhook handler"). Analogies welcomed — must be original.

**Register:** No first-person experiential claims. Opinions and assessments allowed — state them as direct judgements without "I personally" or "in my experience" framing. Second person: yes ("you'll notice..."). Hedges in moderation ("usually", "typically").

**Good:**
- "Closures aren't really about functions — they're about bindings. The function part is incidental."
- "Go's error-return approach was the right call for infrastructure software, though it pays an ergonomic cost."

**Bad:**
- "Closures are a fundamental concept that every developer should understand."
- "In my experience, this pattern causes the most confusion..."

**Best for:** Conceptual articles, design-decision discussions, anything where understanding > doing. Pairs with `core-design-decision`, `open-mental-model`, `comp-cross-language`.

**Voice integrity check:** Bullet lists where prose would do → convert to flowing prose. Any "in my experience" or "I've found" → rewrite as a direct claim with evidence.

---

### `tutorial-guide`

The tutorial guide. Writes like they're walking the reader through a build. Second person, imperative, instructional. Believes you learn by doing.

**Sentence shape:** Medium (12–25 words). Imperative often ("Open your editor. Create a new file."). Many "you'll" constructions ("you'll see...", "you'll want to..."). Step-by-step structure even outside step sections.

**Vocabulary:** Action verbs (open, create, run, save, check, verify). Concrete and specific (filenames, paths, commands). Avoids abstract nouns. Welcomes realistic example data.

**Register:** Second person dominant. "We" when describing the project collectively. No first person. Observed outputs: "you should see...", "this prints...".

**Good:**
- "Open your terminal and run `pip install requests`. You'll see a couple of dependencies install."
- "Now create the function — three arguments, returning a tuple."

**Bad:**
- "Developers typically install requests using pip..."
- "A function with three arguments can be defined as follows..."

**Best for:** Tutorial articles, how-to articles, anything where the reader is following along. Best paired with `code-walkthrough`. Don't use for purely conceptual articles.

**Voice integrity check:** Third-person abstraction ("the developer can...") → switch to second person ("you can...").

---

## Section 4 — Universal Forbidden Language

### First-person experiential claims (hard-fail at QA)

The articles on devnook.dev are AI-generated. Claiming personal experience or personal testing is misleading.

**Banned phrases — any variant triggers a QA hard-fail:**

| Phrase | Why banned |
|---|---|
| "I have personally tried" | Claims personal experience |
| "I once" / "I once spent" | Personal anecdote |
| "I've found" / "I find that" | Claims personal discovery |
| "in my experience" | Claims personal history |
| "personally, I" | Personal stance framing |
| "I spent [time] debugging/building/testing" | Personal effort claim |
| "I built" / "I tested" / "I ran" | Claims first-hand action |
| "when I [verb]" (in past tense) | Personal history |
| "my own [project/code/testing]" | Claims personal work |
| "trust me" | Informal personal endorsement |
| "let me tell you" | Personal narrator |
| "I'd recommend" (when followed by "because I've...") | Personal basis for recommendation |

**Allowed:** Direct assessments without personal framing. "Go's error handling is the right default for infrastructure teams." "This approach is faster for the common case — see the benchmarks linked below."

**Allowed:** Citing 3rd-party experience. "Multiple teams at Shopify reported..." / "GitHub issue #1234 shows a common pattern..." / "The Stack Overflow 2024 survey found..."

---

### AI clichés (hard-fail if used more than once per article)

Banned per spec Section 7. First use is allowed if truly appropriate. Second use in the same article is a hard-fail.

"In conclusion," / "It's important to note," / "delve into" / "navigate the landscape" / "harness the power of" / "unlock the potential" / "game-changer" / "revolutionize" / "cutting-edge" / "robust solution" / "seamlessly integrate" / "leverage" (when "use" works) / "Furthermore," (max 1/article) / "Moreover," (max 1/article)

**Also banned globally (any use):** "comprehensive guide" / "complete guide" / "fundamentals" / "in this article, we will" / "in this guide" / "in today's world" / "the world of [X]" / "in modern [X]" / "everything you need to know"

---

### Universal vocabulary bans (all voices)

Avoid: professional, fundamental, robust, indispensable, crucial, essential, powerful, elegant, drastically, absolutely, meticulously, seamlessly, leverages, utilizes, employs (as synonym for "uses"), facilitates.

Replace with: plain verbs (use, not utilize), specific claims (30% faster per the cited benchmark, not "drastically faster"), direct framings.

---

## Section 5 — SEO Writer-Time Rules

### Title
- **Length:** 50–60 characters
- **Include target keyword** naturally — not forced to position 1
- **Avoid colons** unless they add real meaning (overused in AI titles)
- **Avoid formulas:** "What is X in Y? — A Complete Guide" / "X in Y: Syntax, Examples & Usage" / "Mastering X in Y" / "Understanding X: A Beginner's Guide"

**Good title patterns:**
- "Closures in Python, Quietly Demystified"
- "Why Your TypeScript Interface Won't Extend"
- "The Async Bug That Looks Like a Sync Bug"
- "When to Use Generators in Python (And When Not To)"

Rotate patterns across articles on the same language hub — never use the same pattern twice in a row.

### Meta description
- **Length:** 140–160 characters
- **First 120 characters carry the weight**
- **Include primary keyword** naturally
- **State the answer or value**, not the topic

**Good:** "Parse JSON in Ruby with the built-in JSON module. Three patterns, with the gotchas from inconsistent API response shapes."
**Bad:** "A comprehensive guide to parsing JSON in Ruby, covering everything you need to know about working with JSON data."

### Heading hierarchy
- No H1 in the body — PostLayout.astro renders `title` frontmatter as the page `<h1>`. Any `# Title` in the body creates a duplicate H1.
- H2s for each major section. H3s for subsections within a section (used sparingly).
- Never skip levels (H2 → H4 is invalid).

### H2 wording
Section IDs (`open-problem`, `core-design-decision`) are internal labels — the writer writes a fresh, topical H2 for each section. Rotate phrasings across articles on the same language hub.

Examples for `prac-gotchas`: "Things That Will Trip You Up" / "Where This Breaks" / "Two Bugs You'll Probably Write First"
Examples for `core-design-decision`: "Why Python Did It This Way" / "The Design Trade-off Behind This"

### Keyword usage
- In title: required, naturally placed
- In first 100 words of body: required
- In at least one H2: required
- Density: ~1–2% (1 mention per 50–100 words)
- Never repeat exact phrase mechanically — use variants and synonyms

**For "python closures":** use "python closures" (exact, 1–2 times), "closures in Python" (reordered), "Python's closure mechanism" (possessive), "closures" (when context is clear), "captured variables" / "lexical scope" (semantic variants).

### Internal linking
Writer's role is limited:
- Reference related concepts in prose naturally — no markdown links. The `auto-internal-links` build plugin handles all internal link insertion.
- Leave `related_posts` as `[]` — seo_optimizer fills it in.
- Do NOT add `[X](url)` links in the body. The writer doesn't have a live view of the registry.

### Code blocks
- Always specify language for syntax highlighting
- Realistic variable names (`user_email`, not `x`)
- Comments add information, not narration
- Code should run as-is where the language allows it

---

## Section 6 — Frontmatter Spec

### Language posts (Pipeline A)

```yaml
---
title: "..."                          # 50–60 chars, includes target keyword
description: "..."                    # 140–160 chars, value statement not topic label
language: "python"                    # lowercase language slug
concept: "closures"                   # concept slug (matches URL)
difficulty: "intermediate"            # beginner | intermediate | advanced
target_keyword: "python closures"     # primary keyword from brief
secondary_keywords:                   # from brief
  - "python closure examples"
  - "python nonlocal keyword"
intent: "concept"                     # how-to | explainer | concept | debug | reference
template_id: "modular-v1"             # always this value
sections_used:                        # list of section IDs used — required for diversity tracking
  - "open-problem"
  - "core-how-it-works"
  - "code-minimal"
  - "prac-gotchas"
  - "close-next"
voice: "thoughtful-explainer"         # terse-senior | thoughtful-explainer | tutorial-guide
word_count: 0                         # actual count, filled after writing
published_date: "YYYY-MM-DD"          # set by publisher agent
og_image: "og-default"               # build pipeline regenerates
related_posts: []                     # filled by seo_optimizer
is_error_driven: false                # topic flags
is_syntax_heavy: false
is_abstract: false
has_performance_implications: false
has_cross_language_analog: false
---
```

### AI/Productivity posts (Pipeline B)

```yaml
---
title: "..."                          # 50–60 chars
description: "..."                    # 140–160 chars
category: "ai-productivity"           # always this value for Pipeline B
topic_slug: "claude-code-hooks"       # URL slug
difficulty: "intermediate"            # beginner | intermediate | advanced
target_keyword: "claude code hooks"   # primary keyword from brief
secondary_keywords:
  - "claude hooks tutorial"
  - "claude pre-tool hook"
intent: "tutorial"                    # how-to | explainer | comparison | listicle
template_id: "modular-v1"
sections_used:
  - "ai-open-promise"
  - "ai-core-explainer"
  - "ai-step-by-step"
  - "ai-pitfalls"
  - "ai-faq"
  - "ai-conclusion-cta"
voice: "tutorial-guide"
word_count: 0
published_date: "YYYY-MM-DD"
og_image: "og-default"
related_posts: []
---
```

**Required for all articles:**
- `title`, `description`, `target_keyword`, `sections_used`, `voice`, `template_id`
- `word_count` is filled by writer after writing, not set to the target
- `published_date` is set by the publisher agent, not the writer
- No `# H1` anywhere in the body

---

## Quick Reference

| Need | Use |
|---|---|
| Language post opening (problem/debug) | `open-problem` or `open-error` |
| Language post opening (abstract concept) | `open-mental-model` |
| Language post opening (reference/comparison) | `open-tldr` |
| AI article opening (data-led) | `ai-open-hook` |
| AI article opening (instructional) | `ai-open-promise` |
| Writing about mechanism or runtime | `core-how-it-works` or `ai-core-mechanism` |
| Writing about design philosophy | `core-design-decision` |
| Syntax-heavy topic | `core-syntax-detail` + `code-minimal` |
| Tutorial/following-along article | `code-walkthrough` + `tutorial-guide` voice |
| Comparing with alternatives | `code-side-by-side` or `ai-comparison-table` |
| Common traps and bugs | `prac-gotchas` |
| When not to use the concept | `prac-when-not-to` |
| Production code patterns | `prac-production-patterns` |
| Cross-language comparison | `comp-cross-language` |
| Long article (2500+w) | `close-recap` |
| Tutorial / learning path | `close-next` |
| AI/Productivity closing | `ai-conclusion-cta` (always) |
