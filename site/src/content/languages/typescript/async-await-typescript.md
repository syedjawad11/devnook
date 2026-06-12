---
title: "Async/Await in TypeScript: Promises, Types, and Traps"
description: "Master typescript async await with typed Promises, real-world fetch patterns, and the common pitfalls that bite even experienced TypeScript developers."
category: "languages"
language: "typescript"
concept: "async-await"
difficulty: "intermediate"
template_id: "modular-v1"
tags: [typescript, async-await, promises, asynchronous, fetch]
related_posts: []
related_tools: []
linkAnchors:
  - "typescript async await"
  - "async/await typescript"
  - "async await typescript"
published_date: "2026-06-01"
og_image: /og/languages/typescript/async-await.png
word_count_target: 1950
---

Async operations are central to modern TypeScript applications — fetching data from an API, reading files, querying a database. `typescript async await` gives you a way to write that code so it reads like sequential code, without blocking the thread. Unlike plain JavaScript, TypeScript's type system tracks what each async operation resolves to, catching shape mismatches before they reach production. This guide walks through how async/await works in TypeScript, how to type your async functions correctly, parallel execution patterns, and the gotchas that trip up even experienced developers.

## How TypeScript Async Await Works Under the Hood

At its core, `async` and `await` are syntactic sugar over Promises. An `async` function always returns a `Promise`, and `await` pauses execution inside that function until the awaited Promise settles. Critically, only that function pauses — the JavaScript event loop keeps running, handling other callbacks and I/O while your function waits.

TypeScript's compiler, when it encounters an `async` function, generates the same Promise-chain code you would write by hand. The type system then tracks the resolved value's type through every `await` expression. So when you write:

```typescript
async function getOrderStatus(orderId: string): Promise<OrderStatus> {
  const response = await fetch(`/api/orders/${orderId}/status`);
  const data: OrderStatus = await response.json();
  return data;
}
```

TypeScript knows that `await getOrderStatus(id)` yields a value of type `OrderStatus` — not a `Promise`, not `any`, but specifically `OrderStatus`. The compiler enforces this constraint through the entire call chain. If you try to pass the result somewhere a `string` is expected, you get a type error at compile time.

The TypeScript handbook at [typescriptlang.org](https://www.typescriptlang.org/docs/handbook/2/functions.html) documents how async functions automatically return `Promise<T>` wrappers, and TypeScript's inference unwraps the `Promise<T>` at `await` sites, giving you the resolved type directly in the local scope.

This model — one event loop, Promise-based async, type-checked at compile time — keeps TypeScript's async code safe without changing JavaScript's runtime semantics. The compiled output is plain JavaScript. The runtime behavior is identical; only the static analysis layer differs.

## Writing Typed Async Functions

The return type of an `async` function is always `Promise<T>`. You can let TypeScript infer it from the return statement, or annotate it explicitly. Explicit annotation is worth the extra characters: TypeScript will catch any branch that returns the wrong shape, including branches you forgot to handle.

Define the shape of your data with an interface first, then use it as the generic parameter:

```typescript
interface UserProfile {
  id: string;
  username: string;
  email: string;
  createdAt: string;
}

async function fetchUserProfile(userId: string): Promise<UserProfile> {
  const response = await fetch(`/api/users/${userId}`);

  if (!response.ok) {
    throw new Error(`Fetch failed: ${response.status} ${response.statusText}`);
  }

  const profile: UserProfile = await response.json();
  return profile;
}
```

Two details worth noting here. First, if a branch throws instead of returning, TypeScript correctly handles that — thrown errors exit the function, so they don't affect the return type. Second, `response.json()` returns `Promise<any>` in the browser Fetch API; the explicit `: UserProfile` annotation narrows that `any` at the assignment site.

If you're building [arrow functions in TypeScript](/languages/typescript/write-lambda-function/) rather than function declarations, the async syntax is identical — add `async` before the parameter list:

```typescript
const createInvoice = async (
  customerId: string,
  amount: number
): Promise<Invoice> => {
  const response = await fetch('/api/invoices', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ customerId, amount }),
  });
  return response.json() as Promise<Invoice>;
};
```

TypeScript infers `await`'s result type by unwrapping `Promise<T>`. Inside the function, `await fetch(...)` has type `Response`, and `await response.json()` has type `any` — which is why explicit type assertions or validation matter at JSON boundaries.

## Running Async Operations in Parallel

The most common performance mistake with async/await is awaiting independent operations sequentially. It reads correctly but compounds latency unnecessarily:

```typescript
// Sequential — each call waits for the previous to finish
const user = await fetchUser(userId);
const preferences = await fetchUserPreferences(userId);
const cart = await fetchCart(userId);
```

If each call takes 100ms, this totals 300ms. These three fetches have no dependency on each other — there's no reason to serialize them. `Promise.all` runs them concurrently:

```typescript
const [user, preferences, cart] = await Promise.all([
  fetchUser(userId),
  fetchUserPreferences(userId),
  fetchCart(userId),
]);
```

Total time: ~100ms — the time of the slowest single request. TypeScript infers a correctly typed tuple from the `Promise.all` arguments: `user` is `User`, `preferences` is `UserPreferences`, `cart` is `Cart`, all without any casting.

The tradeoff: if any Promise rejects, `Promise.all` rejects immediately and discards the other results. When you need all results regardless of individual failures, use `Promise.allSettled`:

```typescript
const results = await Promise.allSettled([
  fetchUser(userId),
  fetchUserPreferences(userId),
  fetchCart(userId),
]);

for (const result of results) {
  if (result.status === 'fulfilled') {
    console.log('Data:', result.value);
  } else {
    console.error('Failed:', result.reason);
  }
}
```

`Promise.allSettled` always resolves. Each element is either `{ status: 'fulfilled', value: T }` or `{ status: 'rejected', reason: unknown }`. You trade the simplicity of `Promise.all` for the guarantee that one failure doesn't block the rest.

The [MDN reference on Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) covers the full static API, including `Promise.race` and `Promise.any`, which are less common but useful in specific scenarios like race conditions and fallback patterns. Understanding [JavaScript Promises](/languages/javascript/promises/) — how `.then()`, `.catch()`, and chaining work — makes these parallel patterns more predictable. TypeScript's `Promise<T>` is the typed version of the same primitive.

## Async/Await vs Promise Chains: A Direct Comparison

`async/await` and `.then()` chains compile to the same output. Choosing between them is a readability call, not a correctness one.

**With `.then()` chains:**

```typescript
function loadUserDashboard(userId: string): Promise<Dashboard> {
  return fetchUser(userId)
    .then(user => fetchPermissions(user.roleId))
    .then(permissions => buildDashboard(permissions))
    .catch(err => {
      logError(err);
      return defaultDashboard();
    });
}
```

**With async/await:**

```typescript
async function loadUserDashboard(userId: string): Promise<Dashboard> {
  try {
    const user = await fetchUser(userId);
    const permissions = await fetchPermissions(user.roleId);
    return buildDashboard(permissions);
  } catch (err) {
    logError(err);
    return defaultDashboard();
  }
}
```

When operations are sequential and dependent — each step uses the result of the previous one — async/await reads more naturally. When you want a functional pipeline of transformations, `.then()` chains can be more concise.

The TypeScript compiler knows the type of `user` from `fetchUser`'s return type, the type of `permissions` from `fetchPermissions`'s return type, and the final return type of `loadUserDashboard` — without additional annotations. The same typed inference applies in both styles. For the runtime foundations, see [how async/await works in JavaScript](/languages/javascript/async-await/) — TypeScript inherits that behavior directly.

## Three Gotchas That Catch TypeScript Developers

**Catch blocks get `unknown`, not `any`.**

With `strict: true` in `tsconfig.json` (which enables `useUnknownInCatchVariables`), caught values are typed `unknown` — TypeScript 4.0+ behavior. Code that accessed error properties without narrowing worked before this change and now fails:

```typescript
try {
  const order = await submitOrder(cart);
} catch (err) {
  console.error(err.message); // TypeScript error: 'err' is of type 'unknown'
}
```

Fix: narrow the type before accessing properties:

```typescript
} catch (err) {
  if (err instanceof Error) {
    console.error(err.message);
  } else {
    console.error('Unexpected error:', String(err));
  }
}
```

This surfaces real bugs. Third-party libraries sometimes throw strings, numbers, or plain objects rather than `Error` instances. The `unknown` type forces you to handle that reality.

**Floating Promises.**

A floating Promise is an async function call whose result is never awaited or handled. TypeScript won't catch this by default — you need the `@typescript-eslint/no-floating-promises` rule:

```typescript
async function sendWelcomeEmail(userId: string): Promise<void> {
  await emailClient.send({ to: userId, template: 'welcome' });
}

function onUserCreated(userId: string): void {
  sendWelcomeEmail(userId); // floating Promise — rejection is unhandled
  updateUserIndex(userId);
}
```

If `sendWelcomeEmail` throws, nothing catches the rejection — it may terminate the process or be silently swallowed, depending on the environment. Either `await` the call inside an async context, or attach `.catch()`. The ESLint rule turns this into a compile-time error rather than a runtime surprise.

**`response.json()` returns `any`.**

The browser Fetch API returns `Promise<any>` from `.json()`. Casting with `as MyType` is a type assertion, not a runtime check:

```typescript
const profile = (await response.json()) as UserProfile; // compiler trusts you; runtime does not
```

If the API returns a different shape, TypeScript will not detect it. For real safety at the boundary, validate before asserting — Zod is the popular choice in TypeScript codebases:

```typescript
import { z } from 'zod';

const UserProfileSchema = z.object({
  id: z.string(),
  username: z.string(),
  email: z.string().email(),
  createdAt: z.string(),
});

const raw = await response.json();
const profile = UserProfileSchema.parse(raw); // throws ZodError if shape is wrong
```

This pattern matters most when consuming third-party APIs where the response schema can change without notice.

## Async/Await in React Components

React component functions cannot be `async`. The render cycle doesn't know how to wait for a Promise returned from a component function — you'll get a React error or an unresolved Promise instead of rendered output.

The standard pattern is to define an inner async function inside `useEffect` and call it immediately:

```typescript
import { useState, useEffect } from 'react';

interface Article {
  id: number;
  title: string;
  body: string;
}

function ArticleView({ articleId }: { articleId: number }) {
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadArticle() {
      const response = await fetch(`/api/articles/${articleId}`);
      const data: Article = await response.json();
      setArticle(data);
      setLoading(false);
    }

    loadArticle();
  }, [articleId]);

  if (loading) return <p>Loading...</p>;
  if (!article) return null;
  return <h2>{article.title}</h2>;
}
```

The inner `async function` runs inside `useEffect` without making the effect callback itself async — `useEffect` does not accept async callbacks that return Promises, only cleanup functions or nothing. React 19 introduced the `use` hook and server components with native async support, but the `useEffect` + inner async function pattern remains the standard for existing React codebases.

For production-grade async data fetching in React, libraries like React Query or SWR build on this foundation and add caching, background refetching, and error states — but understanding this base pattern is necessary before reaching for them.

## Frequently Asked Questions

### Can I use `await` outside an async function in TypeScript?

At the top level of a module, yes — if `tsconfig.json` sets `module` to `ESNext`, `ES2022`, `NodeNext`, or `Node16` with a compatible `moduleResolution`. This is top-level `await`, and it lets you write `const config = await loadConfig()` directly at module scope. Inside function bodies, `await` is only valid inside an `async` function. Using it elsewhere is a TypeScript compile-time error.

### What does `Promise<void>` mean as a return type?

`Promise<void>` means the async function completes but doesn't produce a meaningful return value — a write operation, a cache invalidation, a fire-and-forget side effect. You can `await` it to pause until the operation finishes; you just don't get a usable value back. Use `Promise<void>` for async functions that do work but return no data.

### How do I handle errors from `Promise.all` independently?

`Promise.all` rejects at the first failure, discarding the rest. For independent error handling per operation, wrap each Promise with `.catch()` before passing it to `Promise.all`:

```typescript
const [userResult, ordersResult] = await Promise.all([
  fetchUser(userId).catch(err => ({ error: err, data: null })),
  fetchOrders(userId).catch(err => ({ error: err, data: null })),
]);
```

Alternatively, use `Promise.allSettled`, which always resolves — each element is marked `fulfilled` or `rejected` so you can handle them separately.

### What happens if I forget `await` on an async function call?

You get the `Promise` object itself instead of the resolved value. TypeScript may flag this as a type mismatch if the downstream code expects the resolved type rather than `Promise<T>`. Without a type mismatch, the unhandled rejection fails silently. Enable `@typescript-eslint/no-floating-promises` to catch these at lint time rather than in production.

### Is `async await typescript` code slower than using raw Promises?

At runtime, no meaningful difference exists — async/await compiles to Promise chains. There is a tiny microtask overhead per `await` suspension point, but it's negligible for real I/O where network or disk latency dominates by orders of magnitude. The choice between async/await and `.then()` is a readability decision, not a performance one.

## Where to Go From Here

`typescript async await` is the foundation for nearly all async code you'll write — but mastering it means going beyond syntax. The patterns worth learning next: typed error handling with wrapper types using a library like `neverthrow` for errors-as-values instead of exceptions, schema validation with Zod to replace unsafe `as MyType` assertions at API boundaries, and `Promise.all` / `Promise.allSettled` composition for efficient parallel data loading.

If you're working on TypeScript type design more broadly, understanding [how interface and type differ](/languages/typescript/interfaces-vs-types/) will sharpen how you model the data structures your async functions return. And if you're building TypeScript utilities that work with web resources — including tools that process [URLs and sitemaps](/tools/sitemap-generator/) — the typed fetch pattern from this guide is the right foundation to start from.
