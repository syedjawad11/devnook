---
title: "TypeScript interface vs type: A Practical Decision Guide"
description: "The typescript interface vs type choice determines how your code extends and merges. Learn declaration merging, union types, and when each construct wins."
category: "languages"
language: "typescript"
concept: "interfaces-vs-types"
difficulty: "intermediate"
template_id: "lang-v1"
tags: [typescript, interfaces, type-aliases, type-system, generics]
related_posts: []
related_tools: []
linkAnchors:
  - "typescript interface vs type"
  - "type vs interface typescript"
  - "interface vs type typescript"
published_date: "2026-06-02"
og_image: "og-default"
word_count_target: 2100
---

When you start writing TypeScript seriously, the `interface` vs `type` question surfaces quickly. Both describe named types. Both enforce structure at compile time. Both disappear completely in the compiled JavaScript output. So why does it matter which one you choose?

The `typescript interface vs type` distinction runs deeper than syntax. It determines whether your types can be merged across files, whether they can represent union shapes, and how clearly your intent reads to other developers. Choose the wrong one and you'll hit a wall when declaration merging surprises you, or when you need to express a state machine as a union and `interface` refuses.

This guide explains the structural difference between the two, where each genuinely wins, and the decision rule most TypeScript teams settle on.

## TypeScript interface vs type: The Core Distinction

At the surface, both constructs describe object shapes with nearly identical syntax:

```typescript
// interface: declares an open, named object contract
interface UserAccount {
  id: string;
  email: string;
  role: "admin" | "viewer";
  createdAt: Date;
}

// type: aliases an object shape (and can alias much more)
type ProductRecord = {
  id: string;
  title: string;
  price: number;
  inStock: boolean;
};

// Both work identically for object assignment and type checking
const account: UserAccount = {
  id: "u-001",
  email: "alice@example.com",
  role: "admin",
  createdAt: new Date()
};
const product: ProductRecord = { id: "p-042", title: "Keyboard", price: 89.99, inStock: true };
```

TypeScript enforces both identically for object assignment, and the compiled JavaScript output is identical — both are erased at build time. The differences only appear at the level of what each construct can express:

| Feature | `interface` | `type` |
|---|---|---|
| Object shapes | ✓ | ✓ |
| Union types | ✗ | ✓ |
| Tuple types | ✗ | ✓ |
| Mapped types | ✗ | ✓ |
| Conditional types | ✗ | ✓ |
| Template literal types | ✗ | ✓ |
| Composition | via `extends` | via `&` |
| Declaration merging | ✓ | ✗ |
| `implements` in classes | ✓ | ✓ (object shapes only) |

`interface` is a specialized tool for open object contracts. `type` is a general-purpose aliasing mechanism that can name any TypeScript type, including complex computed shapes that `interface` cannot express.

## Declaration Merging and Why It Changes Everything

The most consequential structural difference is that interfaces are **open** — TypeScript automatically merges multiple declarations of the same interface name:

```typescript
// First declaration — maybe in your base config file
interface AppConfig {
  apiUrl: string;
  timeout: number;
}

// Second declaration — maybe in a feature module or a .d.ts extension file
interface AppConfig {
  featureFlags: Record<string, boolean>;
  debug: boolean;
}

// TypeScript merges both. AppConfig now has all four properties.
const config: AppConfig = {
  apiUrl: "https://api.example.com",
  timeout: 5000,
  featureFlags: { darkMode: true, betaSearch: false },
  debug: false
};
```

This isn't a quirk — it's a deliberate design that enables global type augmentation. When you install `@types/node`, it extends Node.js's `global` namespace by declaring the same interfaces the TypeScript built-in lib declares. When you add a custom property to the browser's `Window`, you declare `interface Window { myProp: string }` and TypeScript merges it in. The `ProcessEnv` interface for environment variables, custom `Express.Request` properties, Webpack's `__webpack_nonce__` — all of these rely on declaration merging.

Type aliases are **closed** by design. Redeclaring the same name is an immediate compile error:

```typescript
type CacheEntry = { key: string; value: unknown };
type CacheEntry = { ttl: number }; // Error: Duplicate identifier 'CacheEntry'
```

Closed types provide a stronger guarantee in application code: this name has exactly one definition, located in one place. No other file can silently extend it. That predictability makes `type` a better default for internal domain models in application code, where accidental augmentation is more likely to be a bug than a feature.

The TypeScript team's own guidance in the [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html) frames it this way: interfaces are preferred for public APIs that consumers might extend; type aliases are appropriate for shapes you want to lock down.

## What type Can Express That interface Cannot

Union types are the clearest example of `type`'s exclusive territory. An `interface` can only describe object shapes; it cannot represent a union:

```typescript
// Unions: interface has no equivalent syntax
type LoadingState = "idle" | "loading" | "success" | "error";

// Discriminated unions — TypeScript's go-to pattern for state modeling
type FetchResult<T> =
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; message: string; retryable: boolean };

function renderUserFetch(result: FetchResult<{ name: string }[]>): string {
  switch (result.status) {
    case "loading":  return "Fetching users...";
    case "success":  return `Found ${result.data.length} users`;
    case "error":    return `Error: ${result.message}`;
  }
}

// Template literal types: build string unions from combinations
type HttpVerb = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
type ApiPrefix = "/users" | "/products" | "/orders";
type ApiCall = `${HttpVerb} ${ApiPrefix}`;
// "GET /users" | "GET /products" | ... (15 combinations)

// Conditional types: select based on a type test
type Flatten<T> = T extends Array<infer Item> ? Item : T;
type StringItem = Flatten<string[]>; // string
type NumberItem = Flatten<number>;   // number (not an array, so T itself)
```

Mapped types — which are how TypeScript's built-in utility types work — are also `type`-only:

```typescript
// These are simplified versions of TypeScript's standard library utilities
type MakeOptional<T> = {
  [K in keyof T]?: T[K];
};

type MakeReadonly<T> = {
  readonly [K in keyof T]: T[K];
};

// In practice, you use the built-in versions directly:
interface OrderItem {
  productId: string;
  quantity: number;
  unitPrice: number;
}

type PartialOrder = Partial<OrderItem>;    // all fields optional (for PATCH requests)
type FrozenOrder = Readonly<OrderItem>;   // all fields readonly (for immutable records)
type OrderKey = keyof OrderItem;          // "productId" | "quantity" | "unitPrice"
```

`Partial`, `Readonly`, `Record`, `Pick`, `Omit`, `Exclude`, `Extract`, `ReturnType`, `Parameters` — every utility type in TypeScript's standard library is built with mapped or conditional types. They exist because `type` can express what `interface` cannot.

## Extending, Implementing, and Composing Object Types

For class-based architecture — repositories, services, plugin systems — `interface` offers cleaner extension syntax:

```typescript
interface BaseEntity {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

interface UserEntity extends BaseEntity {
  email: string;
  displayName: string;
  role: "admin" | "editor" | "viewer";
}

// The extends chain reads as a domain hierarchy, not just structural composition
interface AdminEntity extends UserEntity {
  permissions: string[];
  lastAuditAt: Date;
}

// Classes implement interfaces explicitly
class UserRepository implements UserEntity {
  constructor(
    public id: string,
    public email: string,
    public displayName: string,
    public role: "admin" | "editor" | "viewer",
    public createdAt: Date,
    public updatedAt: Date
  ) {}
}
```

You can write the same structure with `type` and the `&` intersection operator:

```typescript
type BaseEntity = { id: string; createdAt: Date; updatedAt: Date };

type UserEntity = BaseEntity & {
  email: string;
  displayName: string;
  role: "admin" | "editor" | "viewer";
};

// Classes can also implement type aliases that resolve to object shapes
class UserRepository implements UserEntity {
  constructor(
    public id: string,
    public email: string,
    public displayName: string,
    public role: "admin" | "editor" | "viewer",
    public createdAt: Date,
    public updatedAt: Date
  ) {}
}
```

Both compile to the same type structure. The readability difference is intent: `extends` communicates "inherits from" in the domain-model sense; `&` communicates structural composition. For deep inheritance hierarchies, `extends` reads more naturally. For composing unrelated capabilities (mixing in timestamps, adding audit fields), `&` can be more explicit about what's happening.

When building TypeScript applications with service layers, you'll see this pattern often: interfaces define service contracts that classes implement, type aliases define the request/response shapes that flow through those services. The [TypeScript async/await guide](/languages/typescript/async-await) shows practical examples of this split in an async service architecture.

## Practical Patterns: How Production Code Uses Both

Most production TypeScript codebases use both constructs, each in its natural lane. A realistic API layer shows the split clearly:

```typescript
// Interface: the service contract (open — consumers might extend it)
interface UserService {
  findById(id: string): Promise<UserEntity | null>;
  listAll(filters: Partial<UserEntity>): Promise<UserEntity[]>;
  create(data: Omit<UserEntity, "id" | "createdAt" | "updatedAt">): Promise<UserEntity>;
  update(id: string, patch: Partial<UserEntity>): Promise<UserEntity>;
}

// Type: internal state modeling (closed union — exactly these states)
type ServiceRequestState<T> =
  | { phase: "idle" }
  | { phase: "pending"; startedAt: number }
  | { phase: "complete"; result: T; durationMs: number }
  | { phase: "failed"; error: Error; retryable: boolean };

// Type: function signature (cleaner than inline function types everywhere)
type RequestMiddleware = (
  req: Request,
  next: () => Promise<Response>
) => Promise<Response>;

// Type: reusable response envelope
type ApiEnvelope<T> = {
  data: T;
  meta: { page: number; pageSize: number; total: number };
  requestId: string;
};
```

For function type aliases in particular — callbacks, event handlers, middleware signatures — `type` is cleaner than repeating inline function types across every call site. The [TypeScript arrow functions reference](/languages/typescript/write-lambda-function) covers how type aliases simplify complex callback signatures in detail.

## Common Traps When Mixing Both

**Trap 1: Accidental interface merging.** Using `interface` for an internal config that you don't intend to be augmented means any file that declares the same name silently extends it. TypeScript won't warn you.

```typescript
// If another module also declares "ApiConfig", TypeScript merges them silently
interface ApiConfig { baseUrl: string; }

// Use type to get a hard error on duplicate declarations:
type ApiConfig = { baseUrl: string }; // Error if declared again: caught immediately
```

**Trap 2: Trying to extend a union type.** If a type alias resolves to a union, it cannot appear in `extends` or `implements` clauses:

```typescript
type ResourceStatus = "draft" | "published" | "archived";

// This fails — union types cannot be extended
// interface PublishedResource extends ResourceStatus {} // Error

// Correct approach: use the union as a field type
interface Resource {
  id: string;
  status: ResourceStatus;
}
```

**Trap 3: Property conflicts in merged interfaces.** When two interface declarations with the same name have conflicting types for the same property, TypeScript intersects the types — which may produce `never` for incompatible types:

```typescript
interface Plugin { version: string }
interface Plugin { version: number } // Merges to: version: string & number = never

// This looks valid but TypeScript rejects every possible value for `version`
const plugin: Plugin = { version: "1.0" }; // Error: not assignable to never
```

The [official TypeScript documentation on object types](https://www.typescriptlang.org/docs/handbook/2/objects.html) covers property compatibility rules in declaration merging, including how method signature merging works differently from property merging.

## Frequently Asked Questions

### When should I use interface vs type in TypeScript?

Use `interface` when defining object shapes that represent public contracts — things classes implement, shapes that library consumers might augment, or types that live in `.d.ts` declaration files. Use `type` for unions, discriminated unions, tuple types, mapped types, conditional types, function signatures, and any shape you want to keep sealed against accidental extension. For purely internal object shapes where neither merging nor union capability matters, both work; many teams default to `interface` for objects and `type` for everything else.

### Is there a performance difference between interface and type?

No runtime difference exists — both are erased before your code runs. At the TypeScript compiler level, interface shape checks can be cached more aggressively than type alias expansions in some scenarios, which can affect type-checking speed in very large monorepos with thousands of types. For application-scale codebases, the difference is not measurable.

### Can a class implement a type alias?

Yes, if the type alias resolves to an object shape. A class can use `implements TypeAlias` the same way it uses `implements SomeInterface`. The constraint is that the type must be an object shape — you cannot `implements` a union type, a primitive type alias, or a conditional type. TypeScript checks structural compatibility in both cases.

### Does declaration merging work with generics?

Yes. If you declare `interface Container<T> { value: T }` twice, TypeScript merges both declarations and requires that any use of the generic satisfies both. Merging generic interfaces requires that the type parameter signatures match exactly across all declarations — mismatched generics produce an error rather than merging.

### What does the TypeScript team recommend?

The TypeScript team's official documentation recommends `interface` as the default for object types, citing two reasons: interfaces produce cleaner error messages (showing the named type rather than an expanded inline shape), and they support augmentation patterns that library authors and framework consumers depend on. The docs also clearly state that `type` is the right choice when you need union, tuple, or mapped type capabilities that `interface` cannot express.

## Putting TypeScript interface vs type Into Practice

The working decision rule: use `interface` for open contracts — things classes implement, shapes library consumers might extend, and objects that belong to the public API surface of a module. Use `type` for everything that needs to be closed or expressive — unions of valid states, function signatures, mapped transformations, conditional types, and domain models that should have exactly one definition.

The `typescript interface vs type` question doesn't have a universal winner. Each construct signals intent that the other cannot, and that clarity is where the real value lies. An `interface` on a service contract says: this is a named, extensible protocol. A discriminated `type` union on a state value says: these are the exact possible states, closed to extension, each with its own shape.

For the next step in TypeScript's type system, generics extend both constructs to handle reusable type patterns across different data shapes. And if TypeScript's scoping behavior for captured type parameters in nested generic functions feels non-obvious, [understanding how JavaScript closures work](/languages/javascript/closures) provides helpful grounding — TypeScript's type parameter scoping follows the same lexical binding rules as JavaScript's closure variables.
