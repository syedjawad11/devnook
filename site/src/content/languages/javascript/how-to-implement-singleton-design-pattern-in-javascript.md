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

## Under the Hood: Performance & Mechanics

Singletons generally consume very little operational overhead on retrieval, requiring essentially an O(1) property lookup and early return. The primary memory profile complication arises from Garbage Collection (GC). 

Normally, an object is swept away by the Garbage Collector when it is no longer referenced in scope. However, because a Singleton binds itself to a static class property (`Database.instance`) or a module export cache, it is effectively immortal. The instance, and all its deeply nested Arrays and Objects, will persist in the heap until the JavaScript runtime completely terminates.

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

## Testing Singletons in JavaScript

To make Singletons testable, it is crucially important to provide a teardown or reset mechanism. Testing frameworks like Jest require test isolation to prevent state pollution.

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
