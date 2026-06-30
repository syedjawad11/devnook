---
title: "TypeScript Generics: Functions, Classes, Constraints"
description: "Learn typescript generics to write reusable functions, classes, and interfaces with type constraints. Includes examples, gotchas, and when to avoid them."
category: "languages"
language: "typescript"
concept: "generics"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [typescript, generics, typescript-generics, type-safety, constraints]
related_posts: []
related_tools: []
linkAnchors:
  - "typescript generics"
  - "generic functions typescript"
  - "generic constraints typescript"
published_date: "2026-06-30"
og_image: "/og/languages/typescript/generics.png"
word_count_target: 2032
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "TypeScript Generics: Functions, Classes, Constraints",
    "description": "Learn typescript generics to write reusable functions, classes, and interfaces with type constraints. Includes examples, gotchas, and when to avoid them.",
    "datePublished": "2026-06-30",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/typescript/generics/",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between TypeScript generics and any?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "any turns off type checking entirely — the compiler treats the value as assignable to and from anything. Generics preserve type safety: the type is a placeholder at write time but fully tracked at the call site, so return types and argument types remain linked."
        }
      },
      {
        "@type": "Question",
        "name": "Can TypeScript generics have default types?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes. TypeScript supports default type parameters since version 2.3, declared with the = syntax: interface Container<T = string> allows omitting the type argument when string is intended."
        }
      },
      {
        "@type": "Question",
        "name": "Do TypeScript generics exist at runtime?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "No. TypeScript compiles to plain JavaScript and erases all type information. Generic type parameters are compile-time constructs only — there is no runtime representation of T."
        }
      }
    ]
  }
  </script>
---

Think of a storage container that adapts to whatever type you put inside it — not a box of `any`, but one that remembers precisely what it holds and enforces that at every point it is used. TypeScript generics work on that idea. They let you write functions, classes, and interfaces that operate on a *type parameter* — a placeholder that gets resolved at the call site, giving you reusability without sacrificing type safety.

Without generics, you face a choice: write the same logic repeatedly for every type you need, or collapse everything to `any` and lose the guarantees TypeScript was designed to provide. TypeScript generics solve this by making the type part of the contract without locking it down prematurely.

## What Are TypeScript Generics?

TypeScript generics introduce *type variables*, written as angle-bracket parameters like `<T>`, that stand in for a concrete type until the caller fills them in. The letter `T` is convention; single letters (`K`, `V`, `U`) are standard for multiple parameters, though any name works.

Generics are not unique to TypeScript. Java and C# have had them for decades; C++ has templates. What makes TypeScript's version notable is that it sits on top of JavaScript — a language with no runtime type information. The compiler uses generics to enforce correctness before the code runs, then erases them entirely during compilation.

When you declare a generic function:

```typescript
function identity<T>(value: T): T {
  return value;
}

const name   = identity("devnook");   // typed as string
const port   = identity(5432);        // typed as number
const active = identity(true);        // typed as boolean
```

The compiler infers `T` from the argument at the call site. Call it with a `string` and `T` becomes `string` for that invocation. Same function body, different types, full type safety.

## The Simplest Generic Function

A more practical example than `identity`: wrapping a value in a typed array.

```typescript
function wrapInArray<T>(item: T): T[] {
  return [item];
}

const userIds  = wrapInArray<number>(42);    // number[]
const labels   = wrapInArray("active");      // string[] — T inferred from argument
const configs  = wrapInArray({ host: "localhost", port: 5432 });
// { host: string; port: number }[]
```

The second and third calls omit the explicit `<string>` and `<{host: string; port: number}>` — TypeScript infers `T` from the argument. Explicit type arguments are needed only when inference fails or when you want to document intent clearly.

A realistic function: a typed fetch wrapper that returns a promise of a known shape.

```typescript
async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

interface Repository {
  id: number;
  name: string;
  private: boolean;
  stargazers_count: number;
}

const repo = await fetchJson<Repository>(
  "https://api.github.com/repos/microsoft/typescript"
);
// repo.name typed as string — no downstream casting needed
// repo.private typed as boolean
```

This is where typescript generics pay their keep. The caller specifies what shape they expect back, and the compiler enforces it through the rest of the code. No `(response as any).name`, no runtime assertion gymnastics.

## Generic Interfaces and Classes

Generics apply to interfaces and classes, not just standalone functions.

### Typed API Response Envelope

A common pattern in API clients is a generic response wrapper:

```typescript
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
  timestamp: string;
}

interface User {
  id: number;
  email: string;
  role: "admin" | "viewer";
}

interface PaginatedList<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

const userResponse: ApiResponse<User> = {
  data: { id: 1, email: "dev@company.com", role: "admin" },
  status: 200,
  message: "ok",
  timestamp: "2026-06-30T00:00:00Z",
};

const listResponse: ApiResponse<PaginatedList<User>> = {
  data: { items: [], total: 0, page: 1, pageSize: 20 },
  status: 200,
  message: "ok",
  timestamp: "2026-06-30T00:00:00Z",
};
```

Define the interface once. Instantiate it with different types to get properly typed envelopes without duplication. Notice `ApiResponse<PaginatedList<User>>` — generics compose cleanly.

### Generic Classes

```typescript
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }

  get size(): number {
    return this.items.length;
  }

  isEmpty(): boolean {
    return this.items.length === 0;
  }
}

const numberStack = new Stack<number>();
numberStack.push(10);
numberStack.push(20);
console.log(numberStack.pop()); // 20 — typed as number, not any

const messageQueue = new Stack<string>();
messageQueue.push("queued");
messageQueue.push("processing");

// numberStack.push("string") — compile-time error
```

Trying to push a `string` onto `numberStack` is a compile-time error. The constraint propagates through every method — `pop()` returns `number | undefined`, `peek()` returns `number | undefined`. The class shape is defined once, typed correctly for every instantiation.

## Constraints: Narrowing What T Can Be

By default, `T` in a generic can be anything. Constraints let you require that `T` satisfies a specific shape, giving you safe access to its properties inside the function body.

```typescript
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(item: T): T {
  console.log(item.length);
  return item;
}

logLength("typescript generics");   // ✓ — string has .length
logLength([1, 2, 3]);               // ✓ — array has .length
logLength({ length: 5, label: "box" }); // ✓ — satisfies HasLength
logLength(42);                      // Error: number has no .length
```

The constraint `T extends HasLength` tells the compiler: accept any `T` that has a `length: number` property. Inside the function, `item.length` is safe. The return type is still `T` — not `HasLength` — so callers retain the full specificity of what they passed in.

A two-parameter constraint using `keyof` for type-safe property access:

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const config = {
  host: "localhost",
  port: 5432,
  debug: false,
};

const host  = getProperty(config, "host");    // typed as string
const port  = getProperty(config, "port");    // typed as number
const debug = getProperty(config, "debug");   // typed as boolean
// getProperty(config, "other")               // Error: not a key of config
```

`K extends keyof T` constrains the key to only valid properties of the object, and `T[K]` gives the return type as precisely the type of that property. This utility is covered in detail in the [TypeScript handbook on generics](https://www.typescriptlang.org/docs/handbook/2/generics.html) and appears throughout codebases that handle dynamic property access.

## Built-in Generic Utilities

TypeScript ships several utility types that are themselves generic: `Partial<T>`, `Required<T>`, `Readonly<T>`, `Record<K, V>`, `Pick<T, K>`, `Omit<T, K>`, `ReturnType<F>`. Understanding generics is what makes these utilities readable rather than magical.

```typescript
interface UserProfile {
  id: number;
  name: string;
  email: string;
  role: "admin" | "viewer";
  createdAt: string;
}

// All fields optional — useful for PATCH/update endpoints
type UserUpdate = Partial<UserProfile>;

// Only the fields a list view needs
type UserPreview = Pick<UserProfile, "id" | "name" | "role">;

// All fields required — useful when a draft type made them optional
type CompleteUser = Required<UserProfile>;

// A flexible map of user settings
type UserSettings = Record<string, string | boolean | number>;
```

See the [TypeScript utility types reference](https://www.typescriptlang.org/docs/handbook/utility-types.html) for the full list. These types are used throughout React — `React.FC<Props>` is a generic component type, `useState<T>()` is a generic hook, and `Promise<T>` in async code is itself generic. For async TypeScript patterns, the [async/await in TypeScript guide](/languages/typescript/async-await/) covers how generics and `Promise<T>` interact in practice.

When working with typed JSON shapes during development, the [JSON formatter tool](/tools/json-formatter/) helps validate and inspect the structure of interface-shaped data.

## Common Gotchas With TypeScript Generics

**Gotcha 1: Return type is `T` but value may be `undefined`.**

```typescript
function first<T>(arr: T[]): T {
  return arr[0]; // undefined at runtime if arr is empty
}

const val = first<number>([]); // typed as number, actually undefined
val.toFixed(2);                 // runtime crash
```

The type says `T`, but an empty array yields `undefined`. Fix: use `T | undefined` as the return type and handle the empty case explicitly. TypeScript's `--strictNullChecks` option forces this discipline at the compiler level.

**Gotcha 2: A generic where a specific type would do.**

```typescript
// No benefit from the generic — T is always number at every call site
function addTwo<T extends number>(a: T, b: T): T {
  return (a + b) as T; // forced cast signals something is wrong
}
```

If a function only ever handles one type, use that type directly. Generics earn their place when the type genuinely varies between call sites — not when it is always `number` or always `string`.

**Gotcha 3: Type inference failing on complex signatures.**

TypeScript sometimes cannot infer `T` from a function with multiple overloads, conditional returns, or deeply nested generics. The resulting error ("Type 'unknown' is not assignable to type 'T'") is not always obvious. The fix is usually an explicit type argument at the call site, or simplifying the signature until inference recovers.

## When Not to Use Generics

Generics add a layer of abstraction. That abstraction pays off when the type genuinely varies — and costs more than it saves when it does not.

**When the type is always the same.** A function that exclusively processes `User` objects does not benefit from `<T extends User>`. Type it with `User` directly. Generics add visual noise and slow down error messages without providing any safety benefit.

**When `unknown` with a type guard is cleaner.** For functions that accept truly arbitrary input and narrow it themselves — validation, deserialization, runtime type checking — `unknown` combined with a type guard is usually more readable than a generic. The type is checked at one point rather than threaded through the signature.

**When the signature becomes unreadable.** Nested generics create substantial maintenance burden. If a colleague cannot understand the type signature at a glance, the abstraction is costing more than it saves. See also [TypeScript interface vs type](/languages/typescript/interfaces-vs-types/) for decisions about structuring the types that feed into generics.

## Frequently Asked Questions

### What is the difference between TypeScript generics and `any`?

`any` turns off type checking — the compiler accepts the value anywhere, assigning it to any type and accessing any property without error. Generics preserve type safety: the type is unknown at write time but fully tracked at the call site. A function typed as `<T>(value: T): T` guarantees the return type matches the input type exactly. A function typed as `(value: any): any` gives no such guarantee and loses all downstream inference.

### Can TypeScript generics have default types?

Yes. TypeScript has supported default type parameters since version 2.3:

```typescript
interface Container<T = string> {
  value: T;
  label: string;
}

// T defaults to string
const box: Container = { value: "default", label: "box" };

// T explicitly set to number
const numBox: Container<number> = { value: 42, label: "count" };
```

Default type parameters keep call sites concise when a type is almost always the same but occasionally needs to differ.

### When should I use multiple type parameters?

Use multiple parameters (`<T, K>`) when the relationship between two types needs to be captured independently. The `getProperty<T, K extends keyof T>` example is the canonical case: `T` is the object type, `K` is constrained to be a key of `T`. You cannot express that constraint with a single type parameter.

### Do TypeScript generics exist at runtime?

No. TypeScript compiles to plain JavaScript and erases all type information. Generic type parameters are compile-time constructs only — there is no runtime representation of `T`. You cannot do `typeof T`, check `instanceof T`, or call `new T()` inside a generic function without additional patterns such as passing the constructor as a parameter:

```typescript
function create<T>(ctor: new () => T): T {
  return new ctor();
}
```

## Conclusion

TypeScript generics let you write typed code that works across many types — without duplication and without the `any` escape hatch. The core idea stays consistent: a type parameter gets filled in at the call site, and the compiler tracks it through every return type and argument from there. Constraints narrow what that parameter can be, giving the function body and its callers stronger guarantees.

The three patterns most worth practising first with typescript generics: a typed fetch wrapper (`fetchJson<T>`), a typed collection class (`Stack<T>`), and a key-access utility using `keyof` constraints. Those cover the majority of real-world scenarios.

From here, [TypeScript tuples](/languages/typescript/tuples/) build on similar type-system thinking for fixed-length typed arrays. The official [TypeScript generics documentation](https://www.typescriptlang.org/docs/handbook/2/generics.html) is the most reliable reference for edge cases and advanced patterns like conditional types and inferred generics.
