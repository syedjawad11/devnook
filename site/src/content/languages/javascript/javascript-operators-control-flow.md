---
title: JavaScript switch, Ternary, and Nullish Operators
description: "Master javascript switch, ternary, else-if, and nullish coalescing in JS. Clear examples, gotchas to avoid, and patterns for cleaner conditional logic."
category: "languages"
language: "javascript"
concept: "operators-control-flow"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [javascript, operators-control-flow, switch-statement, ternary-operator, nullish-coalescing]
related_posts: []
related_tools: []
linkAnchors:
  - "javascript switch"
  - "javascript switch statement"
  - "nullish coalescing javascript"
published_date: "2026-06-23"
og_image: "/og/languages/javascript/operators-control-flow.png"
word_count_target: 1958
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "JavaScript switch, Ternary, and Nullish Operators",
    "description": "Master javascript switch, ternary, else-if, and nullish coalescing in JS. Clear examples, gotchas to avoid, and patterns for cleaner conditional logic.",
    "datePublished": "2026-06-23",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/javascript/operators-control-flow/",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Does JavaScript switch use strict or loose equality?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "JavaScript switch uses strict equality (===), not loose equality (==). The type must match for a case to fire. switch('1') will not match case 1 because the string '1' and the number 1 are not strictly equal."
        }
      },
      {
        "@type": "Question",
        "name": "What is the difference between ?? and || in JavaScript?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "The || operator returns the right-hand side for any falsy value, including 0, empty string, false, null, and undefined. The ?? operator only falls back to the right side when the left side is null or undefined, preserving 0 and empty strings as valid values."
        }
      },
      {
        "@type": "Question",
        "name": "When should I use switch instead of if-else in JavaScript?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Use switch when testing a single variable against three or more constant values. Use if-else chains when conditions involve ranges, multiple variables, or boolean expressions that switch cannot express, such as if (score > 90 && attempts < 3)."
        }
      }
    ]
  }
  </script>
---

Branching logic sits at the heart of every JavaScript program. Choosing between a `javascript switch`, a ternary, a chain of `else-if` blocks, or the `??` nullish coalescing operator isn't always obvious — each tool handles a different shape of conditional problem. Getting this right means fewer surprises at runtime and code that stays readable six months later.

This guide covers all four patterns: how each works, when to reach for it, and the specific bugs that catch developers off guard.

## How javascript switch Statements Work

A `switch` statement tests a single expression against a series of `case` values and executes the first one that matches. Here's the basic form:

```javascript
const day = 'Tuesday';

switch (day) {
  case 'Monday':
  case 'Tuesday':
  case 'Wednesday':
    console.log('Weekday');
    break;
  case 'Saturday':
  case 'Sunday':
    console.log('Weekend');
    break;
  default:
    console.log('Unknown day');
}
// Output: Weekday
```

Three behaviors matter before you rely on `switch` in your code.

**Strict equality.** JavaScript's `switch` compares using `===`, not `==`. That means `switch('1')` will never match `case 1` — the string `'1'` and the number `1` are different types, so the comparison fails. This surprises developers who come from PHP or C, which use loose equality in switch blocks.

**Fall-through.** If you omit `break`, execution continues into the next case. The Monday/Tuesday/Wednesday grouping above deliberately uses this. Accidental fall-through — leaving out `break` unintentionally — is one of the most common switch bugs. Always add `break` unless you're explicitly grouping cases. When you do fall through deliberately, add a comment so reviewers know it's intentional.

**The `default` clause.** It runs when no case matches, acting like `else` at the end of an if-else chain. Placing it last is conventional and avoids reader confusion about evaluation order.

One reliable switch pattern: use it inside a function and `return` from each branch instead of breaking. This eliminates fall-through risk entirely and makes the intent unambiguous:

```javascript
function getDiscount(membershipTier) {
  switch (membershipTier) {
    case 'gold':
      return 0.20;
    case 'silver':
      return 0.10;
    case 'bronze':
      return 0.05;
    default:
      return 0;
  }
}

console.log(getDiscount('silver')); // 0.1
console.log(getDiscount('platinum')); // 0 (default)
```

MDN's [switch statement reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/switch) covers the full grammar, including how `case` expressions evaluate at runtime and how labeled blocks interact with break statements.

## The Ternary Operator for Inline Decisions

The ternary operator is JavaScript's only three-operand expression. The form is:

```
condition ? valueIfTrue : valueIfFalse
```

It's the right tool when you're assigning a value or returning from a function based on a single true/false condition:

```javascript
const itemCount = 3;
const label = itemCount === 1 ? 'item' : 'items';
console.log(`${itemCount} ${label}`); // "3 items"
```

The ternary works well inside template literals and JSX, where an `if` statement can't appear inline. That's its primary strength. The common overuse pattern is nesting — two or more levels deep — which becomes genuinely hard to read:

```javascript
// Avoid — nested ternaries require parsing every level before you understand the logic
const role = isAdmin
  ? 'admin'
  : isModerator
    ? 'moderator'
    : 'user';

// Prefer — early returns communicate the same logic without nesting
function getRole(isAdmin, isModerator) {
  if (isAdmin) return 'admin';
  if (isModerator) return 'moderator';
  return 'user';
}
```

A single-level ternary is clean, idiomatic JavaScript. Two or more levels deep, switch or an if-else chain reads better for anyone who hasn't just written it. The [conditional operator reference on MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Conditional_operator) covers operator precedence, which matters when mixing ternary with `&&` and `||` in the same expression.

## else-if Chains: When They're the Right Tool

`else-if` chains belong in situations where conditions aren't testing the same variable against constants, or where you need range-based comparisons that `switch` can't express:

```javascript
function classifyScore(score) {
  if (score >= 90) {
    return 'A';
  } else if (score >= 80) {
    return 'B';
  } else if (score >= 70) {
    return 'C';
  } else if (score >= 60) {
    return 'D';
  } else {
    return 'F';
  }
}

console.log(classifyScore(85)); // "B"
```

`switch` cannot express `score >= 80` — it only handles equality comparisons. The `else-if` chain is the natural fit for range-based branching.

**Quick decision guide:**

| Condition type | Reach for |
|---|---|
| One variable tested against 3+ constant strings or numbers | `switch` |
| Range comparisons (`> 10`, `<= 100`, `between A and B`) | `else-if` |
| Multiple variables in the same condition | `else-if` |
| One true/false condition, inline value assignment | ternary |
| Two branches, single boolean test | ternary |

A useful mental check: if your `else-if` chain keeps repeating the same variable name with `=== 'x'`, `=== 'y'`, `=== 'z'`, rewrite it as a `switch`. If the conditions differ in structure — ranges, compound tests, different variables — keep the `else-if`.

## Nullish Coalescing (??) vs Logical OR (||)

The `||` operator has long served as a default-value fallback in JavaScript:

```javascript
const timeout = userConfig.timeout || 3000;
```

The problem: `||` returns the right side for *any* falsy value — `false`, `0`, `''`, `null`, `undefined`, and `NaN`. If `userConfig.timeout` is `0` (a valid "no delay" configuration), `||` incorrectly substitutes `3000`.

The nullish coalescing operator `??` (ES2020) fixes this by only falling back when the left side is specifically `null` or `undefined`:

```javascript
const timeout = userConfig.timeout ?? 3000;
// userConfig.timeout === 0    → returns 0    ✓
// userConfig.timeout === null → returns 3000 ✓
// userConfig.timeout === undefined → returns 3000 ✓
```

The difference is concrete when you run them side by side:

```javascript
// || treats 0, '', false, NaN as "absent"
console.log(0 || 'default');     // 'default' — likely unintended
console.log('' || 'default');    // 'default' — likely unintended
console.log(null || 'default');  // 'default' — correct
console.log(false || 'default'); // 'default' — depends on intent

// ?? only replaces null or undefined
console.log(0 ?? 'default');     // 0         — correct
console.log('' ?? 'default');    // ''        — correct
console.log(null ?? 'default');  // 'default' — correct
console.log(false ?? 'default'); // false     — correct
```

In new code, `??` is almost always the right choice for setting a default when a value may be absent. Reserve `||` for cases where you genuinely want to replace any falsy value — such as when an empty string and `null` should be treated identically.

MDN's [nullish coalescing operator reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing) covers the `??=` logical assignment shorthand and browser compatibility history.

## Optional Chaining (?.) in Conditional Logic

Optional chaining `?.` short-circuits to `undefined` rather than throwing a `TypeError` when a property in a chain is `null` or `undefined`. It pairs naturally with `??`:

```javascript
const user = {
  profile: {
    address: null
  }
};

// Without optional chaining — throws TypeError at runtime
const city = user.profile.address.city;

// With optional chaining — returns undefined safely
const safeCity = user.profile?.address?.city;

// Combined with ?? for a clean display fallback
const displayCity = user.profile?.address?.city ?? 'City not specified';
console.log(displayCity); // "City not specified"
```

Optional chaining works on method calls and array index access too:

```javascript
const firstTag = article.tags?.[0] ?? 'untagged';
const lowerTitle = article.title?.toLowerCase();
const formatted = response?.data?.map(item => item.name) ?? [];
```

One nuance worth knowing: `?.` only guards the step it's placed after, not the entire chain. `user?.profile.address.city` guards only the `user` → `profile` access. If `profile` exists but `address` is `null`, you still get a `TypeError`. To guard every step, use `?.` at each potential null point: `user?.profile?.address?.city`.

## Control Flow Bugs Worth Knowing

**Bug 1: Forgetting `break` in a switch block**

```javascript
const action = 'save';

switch (action) {
  case 'save':
    console.log('Saving...');
    // Missing break — falls through to 'delete'
  case 'delete':
    console.log('Deleting...');
    break;
}
// Prints both: "Saving..." then "Deleting..."
```

Add `break` after each case. The ESLint `no-fallthrough` rule catches this automatically. If you're falling through intentionally, add a `// falls through` comment — eslint recognizes it and readers understand it.

**Bug 2: Using `||` for numeric defaults**

```javascript
function createServer(config) {
  const port = config.port || 8080;
  // config.port === 0 means "bind to any port" — but 0 is falsy
  return port;
}

console.log(createServer({ port: 0 })); // 8080, not 0
```

Switch to `??` and port `0` is preserved: `const port = config.port ?? 8080`.

**Bug 3: Comparing objects in a switch**

```javascript
const response = { status: 200 };

switch (response) {
  case { status: 200 }:
    console.log('OK'); // Never runs
    break;
}
```

`===` compares references, not content. Two object literals are never the same reference. Test a primitive property instead: `switch(response.status)`.

When building control flow that validates string patterns — routing by URL slug, parsing command names, or checking status codes — the [regex tester](/tools/regex-tester/) lets you build and test patterns interactively before embedding them in a switch or if-else branch.

## Frequently Asked Questions

### Does JavaScript switch use strict or loose equality?

JavaScript's `switch` statement uses strict equality (`===`), not loose equality (`==`). Both the value and the type must match for a case to fire. `switch('1')` will not match `case 1`, because `'1' === 1` evaluates to `false`. This differs from PHP and C, which apply loose comparison rules in switch constructs. If you need type-coercing comparisons, convert the value before the `switch` expression — for example, `switch(Number(userInput))`.

### What is the difference between ?? and || in JavaScript?

The `||` (logical OR) operator returns the right-hand side whenever the left side is falsy — this includes `0`, `''`, `false`, `NaN`, `null`, and `undefined`. The `??` (nullish coalescing) operator only returns the right side when the left side is `null` or `undefined`. Use `??` when your data might legitimately contain `0` or an empty string and you only want to fall back when a value is genuinely absent. Use `||` only when you want to replace all falsy values.

### When should I use switch instead of if-else in JavaScript?

Use `switch` when you're testing a single variable against three or more constant values — strings, numbers, or any type that supports `===`. It reads more clearly than a long `else-if` chain that repeats the same variable name in every condition. Use `else-if` when conditions involve ranges (`score >= 90`), compound boolean logic (`isAdmin && hasSession`), or multiple variables in the same condition — none of which switch can express.

### Can you use switch with strings in JavaScript?

Yes. `switch` works with strings, numbers, booleans, and any other type that supports strict equality. Testing string command names such as `'play'`, `'pause'`, and `'stop'` is one of the most common switch use cases in JavaScript. Keep in mind that string comparisons are case-sensitive: `case 'Hello'` will not match `'hello'`. Normalize case before the switch expression when case insensitivity matters: `switch(input.toLowerCase())`.

### What does ?. do in JavaScript?

`?.` is the optional chaining operator. It safely accesses a property or calls a method on a value that might be `null` or `undefined`, returning `undefined` at the first missing step instead of throwing a `TypeError`. `user?.profile?.address?.city` evaluates to `undefined` if any step in that chain is nullish. It's most useful when working with API responses or user-provided data where nested objects may not always be present.

## Conclusion

The `javascript switch` statement, ternary operator, `else-if` chains, and `??` each solve a distinct problem. Switch is the right choice when branching on a single value against multiple constants — it communicates that pattern more clearly than repeating variable names in an `else-if` chain. The ternary keeps single-condition inline assignments concise. `else-if` handles ranges and multi-variable conditions that `switch` can't model. And `??` is almost always the better `||` whenever you're setting a default for a value that might be absent but not necessarily falsy.

For working with collections alongside your conditional logic — filtering arrays, transforming data, reducing sets — see [JavaScript Array Methods: map(), filter(), reduce() and More](/languages/javascript/array-methods/). When your switch or if-else branches on data parsed from an API response, [How to Parse JSON in JavaScript](/languages/javascript/json-parsing/) walks through the safe parsing patterns that prevent unexpected `undefined` values from reaching your control flow. JavaScript's [How JavaScript Closures Work](/languages/javascript/closures/) is the natural next stop if you're combining conditional logic with callbacks and event handlers where variable capture matters.
