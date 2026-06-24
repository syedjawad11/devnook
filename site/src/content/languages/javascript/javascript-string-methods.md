---
title: "JavaScript String Methods: slice, split, replace, padStart"
description: "Learn js substring, slice, replace, split, includes, and padStart with clear examples. Master the JavaScript string methods developers reach for most."
category: "languages"
language: "javascript"
concept: "string-methods"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [javascript, string-methods, js-substring, slice, split]
related_posts: []
related_tools: []
linkAnchors:
  - "js substring"
  - "JavaScript string methods"
  - "string slice JavaScript"
published_date: "2026-06-24"
og_image: "/og/languages/javascript/string-methods.png"
word_count_target: 1998
schema_org: "<script type=\"application/ld+json\">\n{\"@context\":\"https://schema.org\",\"@type\":[\"TechArticle\",\"FAQPage\"],\"headline\":\"JavaScript String Methods: slice, split, replace, padStart\",\"description\":\"Learn js substring, slice, replace, split, includes, and padStart with clear examples. Master the JavaScript string methods developers reach for most.\",\"datePublished\":\"2026-06-24\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/languages/javascript/string-methods/\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"What is the difference between slice() and substring() in JavaScript?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"slice() supports negative indices that count from the end of the string. substring() treats negative values as 0 and silently swaps arguments when start is greater than end. For new code, slice() is the consistent and predictable choice.\"}},{\"@type\":\"Question\",\"name\":\"How do I replace all occurrences of a word in a JavaScript string?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Use replaceAll() for plain-text replacements: str.replaceAll('old', 'new'). Or use replace() with a global regex: str.replace(/old/g, 'new'). Both replace every occurrence. replaceAll() is simpler for literal strings; the regex form is necessary for case-insensitive matching or capture groups.\"}},{\"@type\":\"Question\",\"name\":\"Does split() modify the original string in JavaScript?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"No. JavaScript strings are immutable. split() returns a new array and the original string is untouched. The same rule applies to every string method: slice(), replace(), includes(), and the rest all return new values without mutating the source.\"}}]}\n</script>"
---

Strings are everywhere in JavaScript — form input you validate, API responses you format before rendering, URL paths you parse before routing. The language gives you a solid set of built-in methods, and knowing which one fits which job saves you constant guesswork.

This guide covers the JavaScript string methods that come up most in real projects: `slice()` and the `js substring` operation for text extraction, `includes()` and `indexOf()` for searching, `replace()` and `replaceAll()` for substitution, `split()` for breaking strings into arrays, and `padStart()` for consistent output formatting. Each section starts with the simplest working version, then covers the edge cases that cause real bugs.

## How JavaScript String Methods Work

Every JavaScript string is immutable. Methods do not modify the original — they return a new value. This is easy to miss early on:

```javascript
let status = 'pending';
status.toUpperCase();         // return value discarded
console.log(status);          // 'pending' — still unchanged
```

To use the result, assign it:

```javascript
const uppercased = status.toUpperCase();  // 'PENDING'
console.log(uppercased);
```

All string methods live on `String.prototype`, which means you call them as properties on any string value. Because each method returns a string, you can chain calls directly:

```javascript
const slug = '  My Blog Post Title  '
  .trim()
  .toLowerCase()
  .replace(/\s+/g, '-');

console.log(slug);  // 'my-blog-post-title'
```

Each call in the chain operates on the return value of the previous one. Immutability makes this safe — no call touches the original. Keep that rule in mind and the rest of the API falls into place.

## Extracting Text: slice() and js substring

`slice(start, end)` pulls a portion of a string from index `start` up to, but not including, index `end`. Negative values count backwards from the end of the string:

```javascript
const filename = 'report-2026-06-24.csv';

const ext      = filename.slice(filename.lastIndexOf('.'));      // '.csv'
const baseName = filename.slice(0, filename.lastIndexOf('.'));   // 'report-2026-06-24'
const lastFour = filename.slice(-4);                            // '.csv'

console.log(ext, baseName, lastFour);
```

`substring(start, end)` covers the same js substring operation but with two differences: negative indices are treated as `0`, and if `start > end`, the arguments are silently swapped:

```javascript
const tag = '<article>';

console.log(tag.slice(1, 8));       // 'article'
console.log(tag.substring(1, 8));   // 'article' — same result here

console.log(tag.slice(-1));         // '>' — last character via negative index
console.log(tag.substring(-1));     // '<article>' — negative becomes 0, full string returned

console.log(tag.substring(8, 1));   // 'article' — arguments swapped silently
console.log(tag.slice(8, 1));       // '' — no swap, empty string returned
```

The practical recommendation: use `slice()` for everything in new code. Negative index support and predictable handling of reversed arguments make it easier to reason about. You will encounter `substring()` in older codebases, but there is no reason to reach for it when writing fresh code.

For extracting text by pattern rather than position, the [regex tester tool](/tools/regex-tester/) is a fast way to build and verify a pattern before dropping it into source code.

## Searching Strings: includes(), indexOf(), and startsWith()

Before replacing or extracting, you often need to check whether a substring is present.

**`includes(searchString)`** returns a boolean — the cleanest way to test for a value:

```javascript
const permissions = 'read,write,delete';

if (permissions.includes('delete')) {
  console.log('User has delete permission');
}
```

It also accepts an optional second argument to start the search at a specific position:

```javascript
const versionTag = 'v2.1.0-beta.2';
console.log(versionTag.includes('2', 3));   // true — finds the '2' in '1.0'
console.log(versionTag.includes('v', 1));   // false — starts searching after index 0
```

**`indexOf(searchString)`** returns the position of the first match, or `-1` when the value is absent. Use it when you need the position itself, not just a yes/no:

```javascript
const logLine = '[ERROR] 503 Service Unavailable — upstream timeout';

const msgStart = logLine.indexOf(']') + 2;
const message  = logLine.slice(msgStart);

console.log(message);  // '503 Service Unavailable — upstream timeout'
```

**`startsWith(prefix)` and `endsWith(suffix)`** cover the two most common positional checks without needing to compute indices:

```javascript
const apiRoute = '/api/v2/orders';
if (apiRoute.startsWith('/api/')) {
  console.log('API route detected');
}

const uploadPath = 'assets/hero-image.webp';
if (uploadPath.endsWith('.webp')) {
  console.log('WebP format confirmed');
}
```

## Replacing Content: replace() and replaceAll()

**`replace(pattern, replacement)`** substitutes the first match of a string or regex pattern:

```javascript
const notice = 'Good morning, Alice. Good morning, Bob.';

console.log(notice.replace('Good morning', 'Hello'));
// 'Hello, Alice. Good morning, Bob.' — only the first occurrence replaced
```

To replace every occurrence, use **`replaceAll()`** for literal string replacements, or `replace()` with a global regex flag:

```javascript
console.log(notice.replaceAll('Good morning', 'Hello'));
// 'Hello, Alice. Hello, Bob.'

console.log(notice.replace(/Good morning/g, 'Hello'));
// 'Hello, Alice. Hello, Bob.' — equivalent using global regex
```

Both give the same result here. `replaceAll()` reads more clearly for plain-text substitution. The regex approach becomes necessary for case-insensitive replacement (`/pattern/gi`) or when using capture groups.

`replace()` also accepts a function as the second argument, which makes the replacement depend on the matched text:

```javascript
const template = 'Invoice #{{invoiceId}} — Customer: {{customerId}}';
const values = { invoiceId: 'INV-4421', customerId: 'C-981' };

const rendered = template.replace(/\{\{(\w+)\}\}/g, (_match, key) => {
  return values[key] ?? `{{${key}}}`;
});

console.log(rendered);
// 'Invoice #INV-4421 — Customer: C-981'
```

Note that `replace()` operates on the string itself — it is not the right tool for serializing or deserializing structured data. For working with JSON payloads from APIs, see [how to parse JSON in JavaScript](/languages/javascript/json-parsing/).

## Splitting Strings into Arrays: split()

**`split(separator)`** breaks a string into an array wherever the separator appears:

```javascript
const csvRow = 'London,UK,51.5074,-0.1278';
const fields = csvRow.split(',');
// ['London', 'UK', '51.5074', '-0.1278']

const sentence = 'three word sentence';
const words = sentence.split(' ');
// ['three', 'word', 'sentence']
```

Pass a second argument to cap how many pieces you want:

```javascript
const limited = 'a:b:c:d:e'.split(':', 3);
// ['a', 'b', 'c'] — stops after 3 elements
```

Splitting on an empty string produces an array of individual characters, which is useful for character-level processing:

```javascript
const chars   = 'hello'.split('');          // ['h', 'e', 'l', 'l', 'o']
const reversed = chars.reverse().join('');  // 'olleh'
```

After a `split()`, you are working with an array. The [JavaScript array methods](/languages/javascript/array-methods/) — `map()`, `filter()`, and `reduce()` — handle the processing from there. For pulling specific values out of the result by position, [destructuring in JavaScript](/languages/javascript/destructuring/) is a concise option:

```javascript
const [city, country, lat, lon] = csvRow.split(',');
console.log(city, country);  // 'London' 'UK'
```

## Formatting with padStart() and padEnd()

**`padStart(targetLength, padChar)`** adds characters before the string until it reaches the target length. The default pad character is a space.

The most common use case is consistent numeric formatting — order IDs, timestamps, aligned output:

```javascript
const orderId = '42';
const formatted = orderId.padStart(6, '0');  // '000042'

const hour   = String(9);
const minute = String(5);
const clock  = `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}`;
console.log(clock);  // '09:05'
```

**`padEnd(targetLength, padChar)`** does the same from the right, which is useful for left-aligned column output:

```javascript
const cols = ['Name', 'Role', 'Department'];
cols.forEach(col => process.stdout.write(col.padEnd(15, ' ')));
// 'Name           Role           Department     '
```

Both methods return the original string unchanged if it already meets or exceeds the target length — they never truncate, only extend.

## Quick Reference: Common JavaScript String Methods

| Method | What it does | Returns |
|--------|-------------|---------|
| `slice(start, end)` | Extract substring; supports negative indices | String |
| `substring(start, end)` | Extract substring; treats negatives as 0 | String |
| `includes(str)` | Check if string contains a value | Boolean |
| `indexOf(str)` | Find position of first match (−1 if absent) | Number |
| `startsWith(str)` | Check if string begins with value | Boolean |
| `endsWith(str)` | Check if string ends with value | Boolean |
| `replace(pat, rep)` | Replace first match (string or regex) | String |
| `replaceAll(str, rep)` | Replace all string matches | String |
| `split(sep)` | Split into array by separator | Array |
| `padStart(len, ch)` | Pad from the front to target length | String |
| `padEnd(len, ch)` | Pad from the end to target length | String |
| `trim()` | Strip leading and trailing whitespace | String |
| `toLowerCase()` | Convert all characters to lowercase | String |
| `toUpperCase()` | Convert all characters to uppercase | String |
| `length` | Number of characters (property, not method) | Number |

For the complete specification, the [MDN String reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String) covers every method with detailed browser support tables, and the [MDN slice() page](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/slice) goes deep on negative index behavior and edge cases.

## Two Mistakes You Will Write at Least Once

**Mistake 1: Discarding the return value**

String methods don't mutate in place. The most common string bug is calling a method and expecting the variable to update:

```javascript
let title = 'hello world';
title.replace('hello', 'goodbye');  // return value thrown away
console.log(title);                 // 'hello world' — unchanged
```

Always capture what the method returns:

```javascript
const newTitle = title.replace('hello', 'goodbye');
console.log(newTitle);  // 'goodbye world'
```

**Mistake 2: Using `replace()` when you need `replaceAll()`**

`replace()` with a string pattern stops after the first match. When every occurrence needs to change, reach for `replaceAll()` or a global regex:

```javascript
const feedback = 'good work, good effort, good result';

console.log(feedback.replace('good', 'great'));
// 'great work, good effort, good result' — second and third unchanged

console.log(feedback.replaceAll('good', 'great'));
// 'great work, great effort, great result' — all three replaced
```

## Frequently Asked Questions

### What is the difference between slice() and substring() in JavaScript?

Both methods extract a portion of a string given start and end indices, but they diverge on two points. `slice()` supports negative indices — `-1` gives the last character, `-3` the last three characters. `substring()` converts any negative value to `0`, so `substring(-2)` returns the entire string. Second, if you pass `start > end`, `slice()` returns an empty string while `substring()` silently swaps the arguments and returns content anyway. For new code, `slice()` is the predictable choice. `substring()` shows up in older codebases and you will read it, but there is no reason to write it.

### How do I replace all occurrences of a word in a JavaScript string?

Use `str.replaceAll('old', 'new')` for a plain string pattern — it was added in ES2021 and is available in all modern browsers and Node.js 15+. For older environments or when you need pattern matching, use `str.replace(/old/g, 'new')` with the global `g` flag. Add an `i` flag for case-insensitive replacement: `str.replace(/old/gi, 'new')`. The callback form of `replace()` also handles all occurrences when combined with the global flag: `str.replace(/pattern/g, match => transform(match))`.

### Does split() modify the original string in JavaScript?

No. JavaScript strings are immutable — `split()` returns a new array and the original string is left exactly as it was. Every string method follows this rule: `slice()`, `replace()`, `trim()`, `padStart()`, and the rest all return new values without touching the source. You can call multiple methods on the same variable in sequence and each call works against the original unless you explicitly assign the result back.

### Can I chain string methods in JavaScript?

Yes. Because every method that returns a string gives you a string you can call another method on, chains like `str.trim().toLowerCase().replace(' ', '-')` work cleanly. The chain reads left to right: each method receives the output of the previous one. The only point where the chain transitions from strings to arrays is after `split()` — from that point you switch to array methods like `map()`, `filter()`, and `join()` rather than string methods.

## Conclusion

JavaScript string methods give you a composable toolkit for text work. The `js substring` operation belongs to `slice()`, which handles both positive and negative indices cleanly. `includes()` is the readable choice for boolean searches. `replace()` handles first-match substitution; `replaceAll()` covers every occurrence. `split()` bridges string processing and array processing. And `padStart()` keeps formatted output consistent without manual loops.

The one rule that connects all of them: strings are immutable. Every method returns a new value. Capture results, chain freely, and you will find the built-in API covers most real-world string work without reaching for external utilities.
