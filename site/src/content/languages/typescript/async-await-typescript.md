---
actual_word_count: 1680
category: languages
concept: async-await
linkAnchors:
  - "typescript async await"
  - "typescript async/await"
description: How TypeScript handles async await with type safety and clean syntax.
  Compare to Python, JavaScript, Rust, and C# with examples.
difficulty: intermediate
language: typescript
og_image: /og/languages/typescript/async-await.png
published_date: '2026-04-12'
related_cheatsheet: ''
related_content: []
related_posts:
- /languages/javascript/promises
- /languages/rust/async-await
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"Async Await in TypeScript —\
  \ How It Compares to Python, Go & More\",\n  \"description\": \"How TypeScript handles\
  \ async await with type safety and clean syntax. Compare to Python, JavaScript,\
  \ Rust, and C# with examples.\",\n  \"datePublished\": \"2026-04-12\",\n  \"author\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\"\
  : \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n\
  \  \"url\": \"https://devnook.dev/languages/\"\n}\n</script>"
sections_used:
- open-problem
- core-design-decision
- code-side-by-side
- comp-cross-language
- prac-gotchas
- close-one-thing
tags:
- typescript
- async-await
- asynchronous
- promises
- comparison
template_id: modular-v1
title: Async Await in TypeScript — How It Compares to Python, Go & More
voice: thoughtful-explainer
---

You're six weeks into a TypeScript codebase — a payments service, something where wrong data has real consequences — and you've written an async function that fetches a customer's subscription tier. The signature says `Promise<SubscriptionTier>`. The implementation awaits a fetch call, parses the JSON, returns the tier. Tests pass. Then you enable strict null checks in `tsconfig` and TypeScript tells you that `response.json()` is returning `any`, which means your `Promise<SubscriptionTier>` annotation is doing nothing — you've signed a contract in disappearing ink. In [JavaScript](/languages/javascript/), you'd never know until the response shape changed in production and suddenly customers were billed at the wrong rate. TypeScript, configured correctly, surfaces that before deployment.

That's the whole pitch, honestly. Not magic. Just: the type system follows the async operation through to the resolved value.

## What TypeScript's Designers Were Actually Solving

TypeScript's async/await is JavaScript's async/await, with a type layer built on top. That sounds like a cop-out but it's a deliberate architectural decision with real implications.

When the TypeScript team introduced async/await support — landing properly in TypeScript 1.7 in 2015, before ES2017 even standardised the syntax — they had genuine alternatives. They could have introduced a Rust-style `Result<T, E>` type that forced explicit error handling. They could have built something closer to Go's channel model. They could have diverged from JavaScript's async semantics in ways that made the type system more expressive at the cost of npm ecosystem compatibility.

They didn't. Anders Hejlsberg's team has made a consistent bet across TypeScript's entire history: the language should be JavaScript with types, not something you need to mentally translate back. The TypeScript design goals document is explicit on this point — "preserve runtime behaviour of all JavaScript code" and "avoid adding expression-level syntax." Async/await follows that rule exactly. An async function in TypeScript compiles to the same Promise chain you'd write by hand in JavaScript. The runtime is identical.

The practical payoff of this choice is ecosystem compatibility. When you `await` a result from any npm package — a Stripe API call, a Prisma query, a Redis client's `get` — you're working with Promise-returning functions written for JavaScript. TypeScript wraps those in types at your own boundary without requiring any changes to the upstream code. I find this more valuable than it sounds at first: any async model that diverges too far from JavaScript's Promise primitives eventually becomes a translation layer problem, where you're constantly bridging two different concurrency mental models.

The cost of the choice is that TypeScript can't enforce what JavaScript can't enforce. Exceptions carry no type information — a Promise rejection is untyped at the language level. `Promise<User>` tells you the shape on success but says nothing about what it rejects with. Typed error handling requires either a library like `neverthrow` or manual wrapping conventions. TypeScript doesn't pretend to solve that gap; it just makes the happy path precise.

## What the Type Annotation Actually Does

The gap between typed and untyped async functions is most visible when you compare them side by side.

Without types ([JavaScript](/languages/javascript/)):

```javascript
async function fetchInvoice(invoiceId) {
  const response = await fetch(`/api/invoices/${invoiceId}`);
  const data = await response.json();
  return data;
}
```

With types ([TypeScript](/languages/typescript/)):

```typescript
interface Invoice {
  id: string;
  amount: number;
  currency: "USD" | "EUR" | "GBP";
  paidAt: string | null;
}

async function fetchInvoice(invoiceId: string): Promise<Invoice> {
  const response = await fetch(`/api/invoices/${invoiceId}`);

  if (!response.ok) {
    throw new Error(`Invoice fetch failed: ${response.status}`);
  }

  const data: Invoice = await response.json();
  return data;
}
```

The runtime behaviour is identical — same fetch, same await, same JSON parsing. What changes is everything downstream. The caller gets autocomplete on `invoice.paidAt`. TypeScript flags it if you pass the result somewhere a `string` is expected. If the API renames `paidAt` to `settledAt`, you update the interface once and the compiler tells you every place that field was accessed.

The `Promise<Invoice>` annotation isn't documentation that could drift out of sync — it's a constraint the compiler checks against the implementation. If a branch of your function could return `Invoice | undefined` without the signature reflecting that, TypeScript rejects it. This is the main practical value: type-checked async functions are harder to leave in a quietly broken state.

## The Same Idea in Other Languages

[Python](/languages/python/)'s approach looks syntactically closest. The `async def` and `await` keywords are nearly identical, and asyncio's event loop plays the same role as JavaScript's. The difference is that Python's type annotations are checked by separate tools (mypy, pyright) at analysis time — they're not part of the interpreter. At runtime, annotations are metadata, not enforcement:

```python
import httpx
from dataclasses import dataclass

@dataclass
class Invoice:
    id: str
    amount: int
    currency: str
    paid_at: str | None

async def fetch_invoice(invoice_id: str) -> Invoice:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/api/invoices/{invoice_id}")
        response.raise_for_status()
        return Invoice(**response.json())
```

[Rust](/languages/rust/async-await/) takes a fundamentally different path. Async functions return `Future` trait objects, and the type system integrates with the borrow checker — which means you can get compile errors not just about the return shape, but about whether the future is safe to send across threads (`Send` bounds). Error handling is typed through `Result<T, E>`, not exceptions:

```rust
use reqwest::Client;
use serde::Deserialize;

#[derive(Deserialize)]
struct Invoice {
    id: String,
    amount: i64,
    currency: String,
    paid_at: Option<String>,
}

async fn fetch_invoice(client: &Client, invoice_id: &str) -> Result<Invoice, reqwest::Error> {
    let invoice: Invoice = client
        .get(format!("/api/invoices/{}", invoice_id))
        .send()
        .await?
        .json()
        .await?;
    Ok(invoice)
}
```

The `Result<Invoice, reqwest::Error>` makes the failure type visible in the signature in a way TypeScript can't match. The `?` operator propagates errors, but they're typed — a different discipline than try/catch, and a better one for systems where every error path genuinely matters. I think Rust's model is right for infrastructure software. The ergonomic cost is real, and composing typed errors across library boundaries gets complicated fast.

[Go](/languages/go/) sits furthest from TypeScript's model: no async/await at all. Goroutines are cheap threads, concurrency happens through channels, and a Go developer writing this equivalent just calls the HTTP function and blocks the goroutine:

```go
func fetchInvoice(invoiceID string) (*Invoice, error) {
    resp, err := http.Get("/api/invoices/" + invoiceID)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    var invoice Invoice
    if err := json.NewDecoder(resp.Body).Decode(&invoice); err != nil {
        return nil, err
    }
    return &invoice, nil
}
```

Go sidesteps the async/await complexity by making the threading model cheap enough that you don't need non-blocking syntax. You trade explicit error returns at every call site for the simpler mental model of "it just blocks, and the scheduler handles the rest." TypeScript's bet is the opposite — one event loop, non-blocking by default, with types to keep it honest.

## Three Things That Will Trip You Up

**Catch blocks receive `unknown`, not `any`.**

Since TypeScript 4.0 with strict mode enabled, caught values are typed as `unknown`. Code that passed before can break quietly on upgrade:

```typescript
async function loadConfig(configPath: string): Promise<AppConfig> {
  try {
    const raw = await fs.readFile(configPath, "utf-8");
    return JSON.parse(raw) as AppConfig;
  } catch (error) {
    console.error(error.message); // TypeScript error: 'error' is of type 'unknown'
  }
}
```

You have to narrow the type before accessing properties. The fix:

```typescript
} catch (error) {
  if (error instanceof Error) {
    console.error(error.message);
  } else {
    console.error(String(error));
  }
}
```

This catches real bugs — thrown values aren't always `Error` objects, especially from third-party code that throws strings or plain objects. But it's a consistent stumbling block on codebases migrating from TypeScript 3.x.

**Sequential awaits on independent operations.**

The most common performance mistake with async/await — and the one that's hardest to spot in review because it reads as correct:

```typescript
// Each call waits for the previous one to complete
const user = await fetchUser(userId);
const preferences = await fetchPreferences(userId);
const recentOrders = await fetchRecentOrders(userId);
```

These three calls don't depend on each other. Awaiting them in series means the total latency is their sum — if each takes 80ms, you've spent 240ms where 80ms would do. Use `Promise.all` for independent operations:

```typescript
const [user, preferences, recentOrders] = await Promise.all([
  fetchUser(userId),
  fetchPreferences(userId),
  fetchRecentOrders(userId),
]);
```

TypeScript infers the tuple types correctly from `Promise.all`. The fix is mechanical once you notice the pattern, but spotting it requires knowing what to look for.

**The `unknown` type on `JSON.parse` results.**

`JSON.parse` returns `any` in TypeScript — which means using the result without asserting a type gives you no type safety at all. A common mistake is writing `const config = JSON.parse(raw)` and then accessing fields directly, treating the lack of a type error as a guarantee. You need the explicit cast or a validation library (zod, valibot) to narrow the type at the boundary where untrusted data enters your system.

## One Thing to Take Away

TypeScript's `Promise<T>` annotation describes the shape of the resolved value — not a guarantee that the operation succeeds. The Promise can still reject at runtime, and that rejection carries no type. Design your error handling around this: the generic parameter tells you what to expect on the happy path, and try/catch is still your responsibility for everything else.

