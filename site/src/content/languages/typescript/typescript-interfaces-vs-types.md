---
actual_word_count: 1115
category: languages
concept: interfaces-vs-types
description: Both interface and type define object shapes in TypeScript, but they're
  not identical. Learn when to use each one.
difficulty: intermediate
language: typescript
og_image: og-default
published_date: '2026-04-13'
related_cheatsheet: ''
related_content: []
related_posts: []
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"TypeScript: interface vs type\
  \ — What's the Difference?\",\n  \"description\": \"Both interface and type define\
  \ object shapes in TypeScript, but they're not identical. Learn when to use each\
  \ one.\",\n  \"datePublished\": \"2026-04-13\",\n  \"author\": {\"@type\": \"Organization\"\
  , \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\": \"Organization\", \"name\"\
  : \"DevNook\", \"url\": \"https://devnook.dev\"},\n  \"url\": \"https://devnook.dev/languages/\"\
  \n}\n</script>"
tags:
- typescript
- interfaces
- type-aliases
- type-system
template_id: lang-v1
title: 'TypeScript: interface vs type — What''s the Difference?'
---

[TypeScript](/languages/typescript) offers two ways to define object shapes: `interface` and `type`. Both work for describing the structure of objects, but they have different capabilities and use cases that affect which one you should choose.

## What are interfaces and types in TypeScript?

An `interface` is a named contract that defines the shape of an object. It describes what properties and methods an object must have, and it's designed specifically for object-oriented programming patterns. TypeScript uses interfaces primarily for class implementation and object shape definition.

A `type` alias (or `type`) creates a name for any type, not just objects. While you can use `type` to define object shapes just like `interface`, it also handles unions, intersections, primitives, tuples, and any other TypeScript type. Think of `type` as the more flexible, general-purpose tool, while `interface` is specialized for object contracts.

The key distinction: `interface` focuses on describing object structures and supports declaration merging, while `type` is a broader aliasing mechanism that can represent any type shape.

## Why TypeScript Developers Use Both

TypeScript developers use `interface` when building class-based architectures or defining contracts that multiple objects must follow. If you're creating a plugin system where third-party code needs to implement specific methods, `interface` makes this contract explicit and enforceable.

You'll reach for `type` when working with union types, mapped types, or conditional types. For example, when building a form library that handles different input types (text, number, checkbox), a `type` alias using unions expresses this better than an `interface`. Type aliases also work well for defining function signatures, tuple types, or creating complex type transformations using TypeScript's utility types.

Many codebases use `interface` for object shapes and public APIs, then use `type` for everything else—unions, intersections, helper types, and internal type logic.

## Basic Syntax

Here's how each one defines a simple object shape:

```typescript
// Using interface
interface User {
  id: number;          // property with primitive type
  name: string;        // required string property
  email?: string;      // optional property (note the ?)
  isActive: boolean;   // boolean property
}

// Using type
type Product = {
  id: number;          // same syntax as interface for objects
  title: string;       // required property
  price: number;       // numeric property
  tags?: string[];     // optional array property
};

// Both work the same for object shapes
const user: User = { id: 1, name: "Alice", isActive: true };
const product: Product = { id: 101, title: "Keyboard", price: 89.99 };
```

Both examples define object shapes with the same syntax and behavior. You can use either `interface` or `type` to describe objects, and TypeScript enforces the structure identically. The difference emerges when you start extending, merging, or using more advanced type features.

## A Practical Example

Here's where the differences matter—extending types and handling unions:

```typescript
// Interface extension (object-oriented style)
interface Animal {
  name: string;
  age: number;
}

interface Dog extends Animal {  // Dog inherits all Animal properties
  breed: string;
  bark(): void;               // method signature
}

const myDog: Dog = {
  name: "Max",
  age: 3,
  breed: "Labrador",
  bark() { console.log("Woof!"); }
};

// Type with union (functional style)
type Status = "pending" | "approved" | "rejected";  // union type
type Priority = "low" | "medium" | "high";

type Task = {
  id: string;
  title: string;
  status: Status;        // using the union type
  priority: Priority;
};

// Type intersection (combining multiple types)
type Timestamps = {
  createdAt: Date;
  updatedAt: Date;
};

type TaskWithTimestamps = Task & Timestamps;  // combines both types

const task: TaskWithTimestamps = {
  id: "T-100",
  title: "Fix bug",
  status: "pending",
  priority: "high",
  createdAt: new Date(),
  updatedAt: new Date()
};
```

This example shows `interface` excelling at extension (the `extends` keyword reads naturally for class-like hierarchies), while `type` handles unions and intersections that would be impossible with interfaces alone. The `Status` and `Priority` union types can't be expressed with `interface`—you need `type` for that.

## Common Mistakes

**Mistake 1: Using interface for union types**

Developers coming from object-oriented languages try to use `interface` for everything, including unions. This fails because `interface` only describes object shapes:

```typescript
// ❌ This doesn't work
interface Status = "pending" | "approved";  // Syntax error

// ✅ Use type for unions
type Status = "pending" | "approved";
```

Union types require `type` aliases. Remember: `interface` is for object contracts only.

**Mistake 2: Accidentally merging interfaces**

TypeScript automatically merges multiple `interface` declarations with the same name. This is a feature (declaration merging), but it surprises developers:

```typescript
interface Config {
  timeout: number;
}

interface Config {  // Same name—TypeScript merges these!
  retries: number;
}

// Config now has BOTH timeout and retries
const config: Config = { timeout: 5000, retries: 3 };
```

With `type`, this is an error—you can't redeclare the same type name. Use `interface` when you want mergeable definitions (useful for extending library types), and `type` when you want to prevent accidental merging.

**Mistake 3: Overusing type for simple object shapes**

While `type` can do everything `interface` can for objects, using `type` for every object shape loses semantic meaning:

```typescript
// Less clear intent
type User = { name: string; email: string };

// Clearer intent—this is a contract/interface
interface User { name: string; email: string; }
```

If your type represents an object contract that classes might implement or that represents a public API shape, use `interface` to signal that intent.

## interface vs type: When to Use Each

Use `interface` when:
- Defining object shapes for classes to implement
- Creating public API contracts
- You want declaration merging (extending third-party library types)
- Building object-oriented code with inheritance

Use `type` when:
- Working with union types (`string | number`)
- Using intersection types to combine shapes
- Creating tuple types (`[string, number]`)
- Defining function signatures or mapped types
- You need to prevent accidental declaration merging

In practice, many teams adopt a simple rule: `interface` for object shapes and class contracts, `type` for everything else. Both are valid TypeScript—the choice is about expressing intent and leveraging the right tool for each situation.

## Quick Reference

- `interface` defines object shapes and supports extension with `extends`
- `type` creates aliases for any type, including unions and intersections
- `interface` declarations automatically merge when declared multiple times
- `type` cannot be redeclared—each name must be unique
- Use `interface` for class contracts and public APIs
- Use `type` for unions, tuples, and complex type transformations
- Both support optional properties with `?` and readonly modifiers

## Next Steps

After understanding interfaces and types, explore TypeScript generics to make your types reusable across different data types. Learn about union types to handle multiple possible types in a type-safe way. For foundational knowledge, review JavaScript objects to understand the runtime behavior TypeScript is typing.