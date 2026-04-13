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
related_posts:
- /languages/javascript/array-destructuring
- /languages/javascript/map-vs-foreach
related_tools:
- /tools/javascript-repl
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

This JavaScript array cheatsheet covers every array method from ES5 through ES2023, organized by use case with syntax, parameters, and return values.

## Creating & Converting Arrays

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

## Things to Remember

- `map()`, `filter()`, and `slice()` return new arrays — original is unchanged
- `push()`, `pop()`, `shift()`, `unshift()`, `splice()`, `reverse()`, and `sort()` mutate the original array
- `forEach()` always returns `undefined` — use `map()` if you need a return value
- `sort()` converts elements to strings by default — use compare function for numbers: `arr.sort((a, b) => a - b)`
- ES2023 added immutable versions: `toReversed()`, `toSorted()`, `toSpliced()`, and `with()`
- Negative indices work with `at()`, `slice()`, and `splice()` but not bracket notation before ES2022

## Related

For deep dives into specific array methods, see our guide on [JavaScript map vs forEach](/languages/javascript/map-vs-foreach) and [array destructuring patterns](/languages/javascript/array-destructuring). Test array methods interactively with our [JavaScript REPL](/tools/javascript-repl).