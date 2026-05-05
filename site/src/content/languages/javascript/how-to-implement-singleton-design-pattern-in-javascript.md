---
category: languages
concept: singleton-pattern
description: Master the Singleton design pattern in JavaScript to manage global state,
  coordinate resource-heavy classes, and ensure exactly one class instance exists.
difficulty: advanced
language: javascript
og_image: /og/languages/javascript/singleton-pattern.png
published_date: '2026-04-16'
related_posts:
- /languages/javascript/classes
- /languages/javascript/closures
related_tools: []
tags:
- javascript
- design-patterns
- singleton
- architecture
template_id: lang-v2
title: How to Implement the Singleton Design Pattern in JavaScript?
word_count_target: 1500
---

## The Problem

In a complex [JavaScript](/languages/javascript) application, you frequently need to manage shared state or coordinate a central resource, such as a database connection pool, a global configuration object, or an orchestration manager. When multiple developers instantiate the same utility class independently, the application creates duplicate, disjointed instances that lose synchronization.

```javascript
// A naive Database class that creates multiple uncoordinated connections
class Database {
    constructor() {
        this.connectionString = "mysql://localhost/db";
        this.connectionCache = [];
        console.log("Database connection established.");
    }
}

// Dev A creates an instance
const dbAccountService = new Database(); // "Database connection established."
// Dev B creates a separate instance elsewhere
const dbOrderService = new Database(); // "Database connection established."

// The caches are completely isolated from each other!
console.log(dbAccountService === dbOrderService); // false
```

This unrestricted instantiation wastes precious memory and introduces severe bugs, as `dbAccountService` has no knowledge of the work `dbOrderService` is performing. In scenarios like managing API rate limits or logging streams, you need absolute certainty that every component in the system is talking to the exact same memory reference.

The problem escalates in event-driven architectures. Imagine an `EventBus` class that manages subscriptions across your application. If two modules each instantiate their own `EventBus`, events published by module A are invisible to subscribers registered on module B's separate instance. You end up building point-to-point wiring between components just to work around what should be a single shared message broker. The Singleton pattern closes this gap by making "one instance" an architectural guarantee, not a convention that someone could accidentally violate.

## The JavaScript Solution: Singletons

The Singleton design pattern restricts a class from instantiating more than one object. It solves this state-duplication problem by intercepting the instantiation process and always returning the very first instance created, caching it for subsequent calls.

```javascript
// The Singleton implementation using modern Class syntax
class Database {
    constructor() {
        if (Database.instance) {
            return Database.instance;
        }
        this.connectionString = "mysql://localhost/db";
        this.connectionCache = [];
        
        Database.instance = this;
    }
}

const dbAccountService = new Database();
const dbOrderService = new Database();

// Both variables now point to the exact same instance in memory
console.log(dbAccountService === dbOrderService); // true
dbAccountService.connectionCache.push("Query1");
console.log(dbOrderService.connectionCache); // ["Query1"]
```

By leveraging the `constructor` and a static property (`Database.instance`), we ensure that `new Database()` only performs its expensive setup logic once. All future calls gracefully bypass setup and simply return the cached reference.

## How Singletons Work in JavaScript

The implementation shown above works because of a unique quirk in JavaScript constructors: if a class `constructor` explicitly returns an object, the `new` operator respects that returned object instead of creating a brand new empty `this` instance.

When the very first instance of `Database` is launched, `Database.instance` evaluates to `undefined`. The execution proceeds to setup the cache and link the current `this` object to `Database.instance`. 

On the second instantiation, `Database.instance` is now truthy. The `if` statement evaluates true, immediately executing `return Database.instance;`. The operation is short-circuited, and the old object is handed over to the new variable.

It is worth noting that this behavior — a constructor returning an explicit object — is intentional in the spec but often surprises developers. In most OOP languages, constructors cannot return values; the `new` operator always hands back the newly allocated object. JavaScript's flexibility here is what makes the class-based singleton idiom possible without needing a factory method. The trade-off is that callers still use `new Database()` syntax, which reads like an instantiation even though it may return an existing object — a subtle readability concern that the `getInstance()` pattern (used in the Closure Singleton below) avoids.

## Going Further — Real-World Patterns

**Pattern 1: The ES6 Module Singleton (The Best Way)**

In modern JavaScript (ES6+), the module system actively implements Singleton behaviors out-of-the-box. When a module is imported across multiple files, Node.js and browsers cache the module evaluation. This is the cleanest and most idiomatic way to handle singletons today.

```javascript
// logger.js
class Logger {
    constructor() {
        this.logs = [];
    }
    print(msg) {
        this.logs.push(msg);
        console.log(`LOG: ${msg}`);
    }
}

// By exporting an instance, rather than the Class, we create a Singleton!
export default new Logger();
```

When `fileA.js` and `fileB.js` both `import logger from './logger.js'`, they both receive identical references to the same `new Logger()` instantiated during the first import resolution.

**Pattern 2: The Closure Singleton**

Before ES6 class syntax, creating Singletons meant utilizing closure scopes and Immediately Invoked Function Expressions (IIFE). This pattern perfectly hides the underlying structure and prevents external modifications to the wrapper.

```javascript
const ConfigManager = (function() {
    let instance;

    function createInstance() {
        return { isLoaded: true, retries: 5 };
    }

    return {
        getInstance: function() {
            if (!instance) {
                instance = createInstance();
            }
            return instance;
        }
    };
})();

const config1 = ConfigManager.getInstance();
const config2 = ConfigManager.getInstance();
console.log(config1 === config2); // true
```

## What to Watch Out For

**Hidden Mutable State:** Because Singletons maintain state for the lifetime of an application, it is incredibly easy for one module to modify a variable inside the singleton, creating devastating side-effects for another structurally unrelated module. Modifying a Singleton is akin to modifying global variables.

**Testing Headaches:** Singletons carry state aggressively across tests. If test 'A' causes a database Singleton to change its `connectionCache` array, test 'B' has to deal with a polluted array, causing brittle test failures.

**Tight Coupling:**
Singletons create invisible dependencies. When a function deep in your codebase calls `Database.getInstance()` directly, it is reaching out to a global object with no indication in its signature that it depends on a database at all. This makes the dependency graph opaque: you cannot tell from a function's inputs and outputs what external state it touches. Over time, singletons become coordination hubs that every module depends on, making the codebase increasingly difficult to modularize or run in parallel test environments. If you find yourself needing a singleton in more than two or three places, it is worth evaluating whether dependency injection would make those dependencies explicit and the system easier to reason about.

## Under the Hood: Performance & Mechanics

Singletons generally consume very little operational overhead on retrieval, requiring essentially an O(1) property lookup and early return. The primary memory profile complication arises from Garbage Collection (GC). 

Normally, an object is swept away by the Garbage Collector when it is no longer referenced in scope. However, because a Singleton binds itself to a static class property (`Database.instance`) or a module export cache, it is effectively immortal. The instance, and all its deeply nested Arrays and Objects, will persist in the heap until the JavaScript runtime completely terminates.

In the browser, multiple tabs run in separate JavaScript runtimes, so a singleton defined in a module is isolated to its tab — there is no shared memory between tabs. Web Workers are similarly isolated; if you need coordination across workers, you must use `postMessage` or a `SharedArrayBuffer`. In Node.js, the module cache is per-process, so a singleton is shared across all `require()` or `import` calls within the same process. Worker threads in Node.js each get their own module cache, so a singleton module instantiated in the main thread is not the same object as one in a worker thread — an important distinction for CPU-bound offloading patterns.

## When to Use Singletons in Node.js vs the Browser

The module caching behavior that makes singletons work is subtly different between Node.js and browser environments, and the difference matters for how you design them.

In Node.js, `require()` caches modules by their resolved file path. The first call executes the module code; every subsequent call returns the cached exports object. This means a module that exports `new Logger()` is effectively a singleton for the lifetime of that Node.js process. The same cache behavior applies to ES module `import` statements in Node.js 12+. This makes the "exported instance" pattern — exporting `export default new Logger()` from a module — the idiomatic Node.js singleton.

In browsers with bundlers (Webpack, Vite, Rollup), module caching works similarly within a single bundle: the module is evaluated once, and every `import` receives the same reference. The key difference is that each browser tab runs its own JavaScript context, so "one instance per application" really means "one instance per tab." There is no global singleton across tabs without explicitly using mechanisms like `localStorage`, `BroadcastChannel`, or `SharedWorker`.

The practical guidance: in Node.js server code, exported module instances are the preferred singleton pattern — they are testable, explicit, and require no boilerplate. In browser code, consider whether you truly need a singleton or whether component-level state management (React Context, Svelte stores, Vue's provide/inject) is a better fit.

## Advanced Edge Cases

**Edge Case 1: Thwarting the `new` Operator with Symbols**

If you want to prevent developers from recklessly using the `new` operator and force them into a strict `getInstance()` getter method, you can employ `Symbol`s to guard the constructor.

```javascript
const singletonToken = Symbol('SingletonToken');

class StrictSingleton {
    constructor(token) {
        if (token !== singletonToken) {
            throw new Error('Use StrictSingleton.getInstance() to instantiate.');
        }
        this.data = [];
    }

    static getInstance() {
        if (!StrictSingleton.instance) {
            StrictSingleton.instance = new StrictSingleton(singletonToken);
        }
        return StrictSingleton.instance;
    }
}

// Throws Error!
// const fail = new StrictSingleton(); 
```

**Edge Case 2: Freezing the Instance**

Because JavaScript objects are extremely dynamic, external code can still modify methods on the Singleton structure. `Object.freeze()` can lock the architecture down entirely.

```javascript
class ImmutableSingleton {
    constructor() {
        if (!ImmutableSingleton.instance) {
            this.id = Math.random();
            ImmutableSingleton.instance = Object.freeze(this);
        }
        return ImmutableSingleton.instance;
    }
}
```

## Alternatives to Singleton

Before committing to a Singleton, consider whether one of these patterns better fits your situation.

**Module-level variables** are the simplest alternative. A module-scoped `let` or `const` at the top of a file is already a singleton within that module's scope. If you only need shared state within one file, a module variable is cleaner than a full Singleton class.

**Dependency injection** passes the shared object as a parameter rather than having modules reach out and grab it. A single `logger` instance is created at application startup and injected into every module that needs it via constructor arguments or function parameters. The dependency is explicit in every call site — no hidden global wiring — and swapping in a mock for tests requires no monkey-patching.

**React Context** (or equivalent in other UI frameworks) is the browser-native answer to shared state that needs to be accessible anywhere in a component tree without prop drilling. For frontend applications, context is usually the right tool where a developer might otherwise reach for a Singleton-based state container.

Use a Singleton when you need a single shared resource with its own behavior — a connection pool, a rate limiter, a pub/sub bus — and when the consuming code genuinely cannot or should not own a local copy. Prefer the alternatives when shared state is simpler and the dependency should be visible.

## Testing Singletons in JavaScript

To make Singletons testable, it is crucially important to provide a teardown or reset mechanism. Testing frameworks like Jest require test isolation to prevent state pollution.

State pollution is the core testing problem. If test A calls a method that caches a value on the Singleton, test B inherits that cached state even though the tests appear independent. Test ordering starts to matter — a test that passes in isolation fails when another test runs first. The `resetInstanceForTesting()` pattern below is a pragmatic solution: it explicitly nullifies the cached instance so each test starts with a clean slate. The `afterEach` hook (or `beforeEach` with a reset call) guarantees the teardown happens even if a test throws.

```javascript
class StateSingleton {
    constructor() {
        // ... singleton logic
        this.cache = [];
    }
    
    // An explicit testing helper
    static resetInstanceForTesting() {
        StateSingleton.instance = null;
    }
}

// In your Jest testing file:
afterEach(() => {
    StateSingleton.resetInstanceForTesting();
});
```

## Summary

The Singleton pattern is paramount when you need unfragmented global access to a specific object or resource, such as logging hubs or connection strings. In JavaScript, you can implement this by intercepting the `constructor()` return value or powerfully leveraging ES6 exported instances. While singletons enhance orchestration, their immortal state requires developers to exercise caution regarding test pollution and accidental global mutations.
