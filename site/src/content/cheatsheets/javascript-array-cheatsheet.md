---
actual_word_count: 1083
category: cheatsheets
concept: array-methods
description: Complete JavaScript array methods reference with ES6+ syntax. All methods,
  parameters, and return values in one place.
download_png: false
language: javascript
og_image: /og/cheatsheets/javascript-array-cheatsheet.png
published_date: '2026-04-13'
related_content: []
related_posts: []
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"Article\",\n  \"headline\": \"JavaScript Array Methods Cheat Sheet:\
  \ Quick Reference Guide\",\n  \"description\": \"Complete JavaScript array methods\
  \ reference with ES6+ syntax. All methods, parameters, and return values in one\
  \ place.\",\n  \"datePublished\": \"2026-04-13\",\n  \"author\": {\"@type\": \"\
  Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\": \"Organization\"\
  , \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n  \"url\": \"https://devnook.dev/cheatsheets/\"\
  \n}\n</script>"
subject: javascript
tags:
- javascript
- arrays
- es6
- cheatsheet
- reference
template_id: cheatsheet-v1
title: 'JavaScript Array Methods Cheat Sheet: Quick Reference Guide'
---

This [JavaScript](/languages/javascript/) array cheatsheet covers every array method from ES5 through ES2023, organized by use case with syntax, parameters, and return values. Navigate it by use case: transform, search, aggregate, or mutate. Built-in array methods beat hand-rolled `for` loops on every axis — they're more readable, better optimized by the JS engine, and eliminate the off-by-one errors that plague manual index arithmetic. Scan the section headers below to jump directly to what you need.

## Creating & Converting Arrays

`Array.from()` is the go-to for converting anything iterable — strings, Sets, Maps, or NodeLists — into a real array. It also accepts a `{length: n}` object plus a mapping function, making it useful for generating ranges. `Array.of()` exists to fix the footgun in `new Array(n)`, which creates sparse arrays instead of `[n]`. Prefer `Array.from()` and spread syntax for most creation tasks; reach for `fill()` when you need to initialize an array with a repeated value.

```javascript
// Array literal
const arr = [1, 2, 3];

// Array constructor
const arr2 = new Array(5);        // Creates array with 5 empty slots
const arr3 = new Array(1, 2, 3);  // Creates [1, 2, 3]

// Array.from() — convert iterable to array
Array.from('hello');              // ['h', 'e', 'l', 'l', 'o']
Array.from([1, 2, 3], x => x * 2); // [2, 4, 6] (with map function)

// Array.of() — create array from arguments
Array.of(7);                      // [7] (not array with 7 empty slots)
Array.of(1, 2, 3);                // [1, 2, 3]

// Spread operator
const copy = [...arr];            // Shallow copy
const merged = [...arr1, ...arr2]; // Merge arrays
```

## Adding & Removing Elements

These methods mutate the original array in place — use them when you own the array and immutability isn't a concern. `push` and `pop` operate on the tail and are O(1); `unshift` and `shift` operate on the head and are O(n) because every existing index must be renumbered. `splice()` is the most flexible: it can remove, insert, or replace elements at any position. If you need the same operations without mutation, the ES2023 `toSpliced()` method returns a new array instead.

```javascript
const arr = [1, 2, 3];

// push() — add to end, returns new length
arr.push(4);                      // arr = [1, 2, 3, 4], returns 4

// pop() — remove from end, returns removed element
arr.pop();                        // arr = [1, 2, 3], returns 4

// unshift() — add to start, returns new length
arr.unshift(0);                   // arr = [0, 1, 2, 3], returns 4

// shift() — remove from start, returns removed element
arr.shift();                      // arr = [1, 2, 3], returns 0

// splice() — add/remove at index, returns removed elements
arr.splice(1, 1);                 // arr = [1, 3], returns [2]
arr.splice(1, 0, 2);              // arr = [1, 2, 3], returns []
arr.splice(1, 1, 'x', 'y');       // arr = [1, 'x', 'y', 3], returns [2]
```

## Extracting & Combining

`slice()` is non-mutating and accepts negative indices, making it the clean way to grab a portion of an array or make a shallow copy. `concat()` returns a new merged array — useful when you need to combine multiple arrays without touching either source. `flat()` and `flatMap()` (added in ES2019) handle nested structures: `flat(Infinity)` fully flattens any depth, while `flatMap()` is a performance-friendly shorthand for `.map(...).flat(1)` that avoids creating the intermediate array.

```javascript
const arr = [1, 2, 3, 4, 5];

// slice() — extract portion, returns new array
arr.slice(1, 3);                  // [2, 3] (from index 1 to 3, not including 3)
arr.slice(-2);                    // [4, 5] (last 2 elements)

// concat() — merge arrays, returns new array
arr.concat([6, 7]);               // [1, 2, 3, 4, 5, 6, 7]
arr.concat(6, [7, 8]);            // [1, 2, 3, 4, 5, 6, 7, 8]

// join() — convert to string
arr.join('-');                    // '1-2-3-4-5'
arr.join('');                     // '12345'

// flat() — flatten nested arrays (ES2019)
[1, [2, [3, 4]]].flat();          // [1, 2, [3, 4]] (default depth: 1)
[1, [2, [3, 4]]].flat(2);         // [1, 2, 3, 4]
[1, [2, [3, 4]]].flat(Infinity);  // [1, 2, 3, 4]

// flatMap() — map then flatten by 1 level (ES2019)
[1, 2, 3].flatMap(x => [x, x * 2]); // [1, 2, 2, 4, 3, 6]
```

## Searching & Testing

Pick the right search method based on what you need back. Use `find()` when you want the element itself, `findIndex()` when you need its position, and `includes()` for a simple boolean existence check. `some()` short-circuits on the first truthy match; `every()` short-circuits on the first falsy one — both are more semantically clear than a manual `for` loop with a flag variable. `findLast()` and `findLastIndex()`, added in ES2023, search from the tail without manually reversing the array first.

```javascript
const arr = [1, 2, 3, 4, 5];

// indexOf() — first index of element, returns -1 if not found
arr.indexOf(3);                   // 2
arr.indexOf(9);                   // -1

// lastIndexOf() — last index of element
[1, 2, 3, 2, 1].lastIndexOf(2);   // 3

// includes() — check if element exists (ES2016)
arr.includes(3);                  // true
arr.includes(9);                  // false

// find() — first element matching condition
arr.find(x => x > 3);             // 4
arr.find(x => x > 10);            // undefined

// findIndex() — index of first match
arr.findIndex(x => x > 3);        // 3
arr.findIndex(x => x > 10);       // -1

// findLast() — last element matching condition (ES2023)
arr.findLast(x => x > 3);         // 5

// findLastIndex() — index of last match (ES2023)
arr.findLastIndex(x => x > 3);    // 4

// some() — test if any element passes
arr.some(x => x > 3);             // true

// every() — test if all elements pass
arr.every(x => x > 0);            // true
arr.every(x => x > 3);            // false
```

## Transforming Arrays

`map()` and `filter()` are the workhorses of functional JavaScript — they always return a new array, so they're safe to use inside React state updates and other immutability-sensitive contexts. `reduce()` is the universal accumulator: use it for sums, groupBy operations, or building objects from arrays, but prefer a more readable method when one fits. `sort()` and `reverse()` mutate in place; if you need the original order preserved, reach for the ES2023 `toSorted()` and `toReversed()` variants that return a fresh array.

```javascript
const arr = [1, 2, 3, 4, 5];

// map() — transform each element, returns new array
arr.map(x => x * 2);              // [2, 4, 6, 8, 10]

// filter() — keep elements matching condition
arr.filter(x => x > 2);           // [3, 4, 5]

// reduce() — reduce to single value
arr.reduce((sum, x) => sum + x, 0); // 15
arr.reduce((max, x) => Math.max(max, x)); // 5

// reduceRight() — reduce from right to left
[1, 2, 3].reduceRight((acc, x) => acc + x, ''); // '321'

// reverse() — reverse in place, returns array
arr.reverse();                    // [5, 4, 3, 2, 1]

// sort() — sort in place, returns array
[3, 1, 4, 2].sort();              // [1, 2, 3, 4]
[3, 1, 4, 2].sort((a, b) => b - a); // [4, 3, 2, 1] (descending)

// toReversed() — reverse without mutation (ES2023)
arr.toReversed();                 // Returns new reversed array

// toSorted() — sort without mutation (ES2023)
arr.toSorted();                   // Returns new sorted array

// toSpliced() — splice without mutation (ES2023)
arr.toSpliced(1, 1);              // Returns new array with element removed

// with() — replace element without mutation (ES2023)
arr.with(0, 99);                  // Returns new array with arr[0] = 99
```

## Iteration Methods

`forEach()` is for side effects only — logging, DOM mutations, accumulating into an external variable. It always returns `undefined`, so never assign its result. When you need a new array, use `map()` instead. `entries()`, `keys()`, and `values()` return iterators rather than arrays, so pair them with `for...of` or spread them if you need array methods on the result. These iterators are lazy, which matters when you're working with very large datasets and want to bail early.

```javascript
const arr = [1, 2, 3];

// forEach() — execute function for each element, returns undefined
arr.forEach((val, idx, array) => {
  console.log(val, idx);
});

// entries() — iterator of [index, value] pairs
for (const [idx, val] of arr.entries()) {
  console.log(idx, val);
}

// keys() — iterator of indices
for (const idx of arr.keys()) {
  console.log(idx);               // 0, 1, 2
}

// values() — iterator of values
for (const val of arr.values()) {
  console.log(val);               // 1, 2, 3
}
```

## Array Properties & Static Methods

`Array.isArray()` is the reliable way to check for arrays — `typeof []` returns `"object"`, which is useless for this purpose. `at()` (ES2022) makes negative indexing ergonomic without the `arr[arr.length - 1]` ceremony. `fill()` is handy for initializing fixed-size arrays; combine it with `new Array(n)` to quickly create arrays of a given length filled with a default value. `copyWithin()` is niche but useful for circular buffers and typed array manipulation where you want zero-allocation in-place copying.

```javascript
// length — number of elements (writable)
arr.length;                       // 3
arr.length = 1;                   // arr = [1] (truncates array)

// Array.isArray() — check if value is array
Array.isArray([]);                // true
Array.isArray({});                // false

// at() — access element by index (supports negative) (ES2022)
arr.at(0);                        // 1
arr.at(-1);                       // 3 (last element)

// fill() — fill with static value
new Array(3).fill(0);             // [0, 0, 0]
arr.fill(9, 1, 3);                // [1, 9, 9] (from index 1 to 3)

// copyWithin() — copy part of array to another location
[1, 2, 3, 4, 5].copyWithin(0, 3); // [4, 5, 3, 4, 5]
```

## Common Pitfalls

**`sort()` without a comparator** converts every element to a string before comparing, so `[10, 9, 2].sort()` produces `[10, 2, 9]` — not `[2, 9, 10]`. Always pass `(a, b) => a - b` for ascending numeric sort, or `(a, b) => b - a` for descending. This surprises developers who come from [Python](/languages/python/) or [Java](/languages/java/), where the default sort is numeric.

**`splice()` vs `slice()`** are easy to mix up. `splice()` mutates the original array and returns the removed elements; `slice()` leaves the original untouched and returns a new array containing the extracted portion. A quick mnemonic: `splice` has a `p` for "permanent change."

**`indexOf()` with `NaN`** always returns `-1` because `NaN !== NaN` by definition. If you need to locate a `NaN` in an array, use `findIndex(x => Number.isNaN(x))` instead — it uses the `Number.isNaN` check, which correctly identifies `NaN` values.

**`reduce()` on an empty array without an initial value** throws a `TypeError` at runtime. Always supply the second argument (the initial accumulator value) when there is any chance the array could be empty. For a sum, pass `0`; for an array accumulator, pass `[]`; for an object, pass `{}`.

## Quick Decision Guide

Choosing the right array method cuts down on unnecessary iterations and makes intent obvious to whoever reads the code next. When you need a new array with every element transformed, `map()` is the answer. When you only want items that satisfy a condition, reach for `filter()`. When you need to collapse the array down to a single output — a sum, a max, a grouped object — `reduce()` handles it. For stopping at the first match, `find()` returns the element and `some()` returns a boolean; both short-circuit as soon as a match is found, so they're more efficient than filtering and checking length. When every element must satisfy a condition, `every()` makes that intent explicit. When you need the position rather than the value, `indexOf()` works for primitives and `findIndex()` works for complex conditions. When your pipeline involves both filtering and transforming, `filter().map()` chains cleanly, or use `flatMap()` when the transform itself produces arrays that you want flattened into a single result.

For deep dives into specific [array methods](/languages/javascript/array-methods/), see our guide on JavaScript map vs forEach and array destructuring patterns. Test array methods interactively with our JavaScript REPL.