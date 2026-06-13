---
title: "C++ Substring Methods: substr, find and replace"
description: "C++ substring methods and string manipulation: learn substr(), find(), replace(), insert(), erase() and the conversions every C++ developer needs."
category: languages
language: cpp
concept: string-methods
difficulty: "beginner"
template_id: lang-v2
tags: [cpp, strings, string-methods, standard-library, cplusplus]
related_posts: []
related_tools: []
published_date: "2026-06-13"
og_image: "/og/languages/cpp/string-methods.png"
word_count_target: 2500
actual_word_count: 2815
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "C++ Substring Methods: substr, find and replace",
    "description": "C++ substring methods and string manipulation: learn substr(), find(), replace(), insert(), erase() and the conversions every C++ developer needs.",
    "datePublished": "2026-06-13",
    "programmingLanguage": "cpp",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/cpp/string-methods/",
    "mainEntity": [
      {"@type": "Question", "name": "How do I check if a C++ string contains a substring?", "acceptedAnswer": {"@type": "Answer", "text": "Use find() and compare the result against std::string::npos: if (str.find(\"token\") != std::string::npos). C++23 added a contains() method for direct use on modern compilers."}},
      {"@type": "Question", "name": "What does std::string::npos mean?", "acceptedAnswer": {"@type": "Answer", "text": "npos equals static_cast<size_t>(-1), the maximum value of size_t. It is the sentinel returned by find() and its variants when the search fails. Always test pos != std::string::npos before using a position value."}},
      {"@type": "Question", "name": "How do I replace all occurrences of a substring in C++?", "acceptedAnswer": {"@type": "Answer", "text": "The standard library has no replace_all(). Write a loop: find the substring, call replace(), then advance the position by to.length() to avoid matching the newly inserted text."}},
      {"@type": "Question", "name": "What is the difference between C++ substr() and Python slice syntax?", "acceptedAnswer": {"@type": "Answer", "text": "substr(pos, len) takes a start position and a length. Python slices take a start and an end index. Convert: str.substr(start, end - start) in C++ is equivalent to str[start:end] in Python."}},
      {"@type": "Question", "name": "Does C++ have a string split() method?", "acceptedAnswer": {"@type": "Answer", "text": "No. C++17 and earlier have no built-in split(). The standard approach uses find() and substr() in a loop, advancing the start position past each delimiter until no more are found."}}
    ]
  }
  </script>
---

Searching for a token in a C++ string and getting back `18446744073709551615` is disorienting the first time it happens. That value is `std::string::npos` — what `find()` returns when a substring search comes up empty — and it behaves conceptually like `-1` in C, except it's unsigned. Once you know the npos convention, the fix is a single comparison. Before that, it produces silent bugs or unexpected throws that look nothing like a failed string search. This guide walks through the full `std::string` method toolkit: `substr()` for C++ substring extraction, `find()` and its variants for searching, `replace()` and `erase()` for in-place modification, and the conversion functions that link strings to numbers.

## What Is std::string and Why Does Its API Look This Way?

The C++ string type is `std::string`, an alias for `std::basic_string<char>`. It lives in the `<string>` header and manages its own memory — no manual `malloc` or `free`, no fixed-size char buffers to overflow. Every `std::string` instance owns its character data, and the type handles resizing automatically as you append or insert.

`std::string` is mutable. You can change individual characters, splice in substrings, remove sections, or append to the end without creating a new string (unless the operation forces a reallocation due to capacity limits). The methods fall into four functional groups:

| Group | Methods |
|---|---|
| Searching | `find()`, `rfind()`, `find_first_of()`, `find_last_of()`, `find_first_not_of()`, `find_last_not_of()` |
| Slicing | `substr()` |
| Modifying | `replace()`, `insert()`, `erase()`, `append()`, `push_back()`, `pop_back()` |
| Converting | `stoi()`, `stol()`, `stof()`, `stod()`, `stold()`, `to_string()` |

Notice what's missing: no built-in `split()`, `replace_all()`, `trim()`, or `starts_with()` before C++20. You build those using the primitives above. C++20 added `starts_with()`, `ends_with()`, and `contains()` directly on `std::string`, and C++23 added more range-based utilities — but if you're on C++17 or earlier, the methods in the table above are your full toolkit.

## Substring in C++: How substr() Works

`substr(pos, len)` returns a new `std::string` starting at index `pos`, containing at most `len` characters. Both arguments are `size_t` — an unsigned integer type.

```cpp
#include <iostream>
#include <string>

int main() {
    std::string path = "/home/alice/reports/q1_2026_final.csv";

    // Find and extract just the filename
    size_t last_slash = path.rfind('/');
    std::string filename = path.substr(last_slash + 1);
    // "q1_2026_final.csv"

    // Extract the file extension
    size_t dot_pos = filename.rfind('.');
    std::string extension = filename.substr(dot_pos + 1);
    // "csv"

    // Extract the base name (without extension)
    std::string base = filename.substr(0, dot_pos);
    // "q1_2026_final"

    std::cout << filename << "\n";
    std::cout << extension << "\n";
    std::cout << base << "\n";
    return 0;
}
```

The second argument is optional. `path.substr(5)` runs from index 5 to the end of the string. When `pos` exceeds the string's length, the runtime throws `std::out_of_range`.

The single most important thing to internalise about `substr()`: the second parameter is a **length**, not an end index. If you're coming from Python (where `text[start:end]` takes end indices), you'll write the wrong thing at least once. The conversion is: `text.substr(start, end - start)` produces the same characters as `text[start:end]` in Python.

### find() feeding into substr()

The canonical pattern for C++ substring extraction is `find()` locating a delimiter, then `substr()` slicing from there.

```cpp
#include <iostream>
#include <string>

int main() {
    std::string conn = "host=db.example.com;port=5432;user=admin;dbname=orders";

    // Extract the value for a given key
    const std::string key = "dbname=";
    size_t start = conn.find(key);

    if (start != std::string::npos) {
        start += key.length();               // skip past "dbname="
        size_t end = conn.find(';', start);  // find next delimiter
        std::string dbname = (end == std::string::npos)
            ? conn.substr(start)
            : conn.substr(start, end - start);
        std::cout << dbname << "\n";  // "orders"
    }

    return 0;
}
```

The inner `npos` check on `conn.find(';', start)` handles the case where `dbname` is the last field with no trailing semicolon. Skip it and you pass a huge number to `substr()`, which throws.

## The find() Family: Searching With Variants

`find()` searches forwards from the beginning of the string (or from an optional start position) and returns the index of the first match. The full family gives you directional and character-set searches.

```cpp
std::string log_line = "/api/v1/users/42 200 OK";

size_t first_slash  = log_line.find('/');          // 0 — first slash
size_t last_slash   = log_line.rfind('/');          // 13 — last slash
size_t second_slash = log_line.find('/', 1);        // 4 — first '/' after index 1
size_t first_digit  = log_line.find_first_of("0123456789"); // 7
size_t last_space   = log_line.find_last_of(' ');   // 19
```

`find_first_of(chars)` checks character by character and returns the first position where any character in `chars` appears. It is not a substring search — passing `"port"` to `find_first_of()` will match the first `p`, `o`, `r`, or `t` in the string, not the literal word "port". Use `find()` when you need an exact substring match.

`find_first_not_of(chars)` returns the first character NOT in `chars`. Combined with `find_last_not_of()`, it gives you the standard whitespace trim idiom used before C++20:

```cpp
std::string raw = "   some value   ";
size_t trim_start = raw.find_first_not_of(' ');
size_t trim_end   = raw.find_last_not_of(' ');
std::string trimmed = raw.substr(trim_start, trim_end - trim_start + 1);
// "some value"
```

The `+ 1` here is intentional: `trim_end` points AT the last non-space character, so the length must include it. This is the one situation in normal C++ string work where `substr()` length needs a `+ 1` relative to the two positions.

## Modifying Strings: replace(), insert() and erase()

### replace()

`replace(pos, count, new_str)` removes `count` characters starting at `pos` and inserts `new_str` in their place. The replacement does not have to be the same length as what was removed — the string grows or shrinks accordingly.

```cpp
#include <iostream>
#include <string>

int main() {
    std::string msg = "Hello, {{username}}. Your order {{order_id}} ships today.";

    // Replace first placeholder
    const std::string user_key  = "{{username}}";
    size_t uname_pos = msg.find(user_key);
    if (uname_pos != std::string::npos) {
        msg.replace(uname_pos, user_key.length(), "Alice");
    }

    // Replace second placeholder — find AFTER the previous replacement
    const std::string order_key = "{{order_id}}";
    size_t order_pos = msg.find(order_key);
    if (order_pos != std::string::npos) {
        msg.replace(order_pos, order_key.length(), "ORD-8204");
    }

    std::cout << msg << "\n";
    // "Hello, Alice. Your order ORD-8204 ships today."
    return 0;
}
```

After the first `replace()`, every index in the string may have shifted. Always call `find()` fresh for each subsequent replacement rather than using positions computed before earlier replacements ran.

### insert()

`insert(pos, str)` inserts `str` at index `pos`, shifting everything to the right.

```cpp
std::string entry = "ERROR: connection timed out";
entry.insert(0, "[2026-06-13T14:32:00Z] ");
// "[2026-06-13T14:32:00Z] ERROR: connection timed out"
```

`insert()` also accepts a character-count form: `str.insert(5, 3, '-')` inserts three dashes at index 5. For prepending or splicing into the middle of a string it's the clearest option; for building strings from parts, `append()` or the `+` operator are typically more readable.

### erase()

`erase(pos, count)` removes `count` characters starting at `pos`. Omitting `count` removes everything from `pos` to the end.

```cpp
std::string html = "<strong>formatted text</strong>";

// Strip the opening tag
size_t close = html.find('>');
html.erase(0, close + 1);       // "formatted text</strong>"

// Strip the closing tag
size_t open = html.rfind('<');
html.erase(open);               // "formatted text"
```

## Converting Between Strings and Numbers

C++11 moved string-to-number conversion out of the `<cstdlib>` functions (`atoi`, `atof`) and into `<string>` with exception-throwing equivalents.

### String to number

```cpp
#include <iostream>
#include <string>
#include <stdexcept>

int main() {
    std::string port_str  = "8080";
    std::string price_str = "29.99";
    std::string bad_input = "abc";

    int    port  = std::stoi(port_str);       // 8080
    double price = std::stod(price_str);      // 29.99

    try {
        int x = std::stoi(bad_input);  // throws
    } catch (const std::invalid_argument& e) {
        std::cout << "Not a number: " << e.what() << "\n";
    } catch (const std::out_of_range& e) {
        std::cout << "Overflow: " << e.what() << "\n";
    }

    return 0;
}
```

The conversion family: `stoi()` (int), `stol()` (long), `stoll()` (long long), `stoul()` (unsigned long), `stof()` (float), `stod()` (double), `stold()` (long double). All throw `std::invalid_argument` for non-numeric strings and `std::out_of_range` for values that overflow the target type.

One quirk: `stoi("42abc")` returns `42` without throwing — conversion stops at the first non-digit. Pass a `size_t*` as the second argument to get the number of characters consumed: `std::stoi("42abc", &consumed)` sets `consumed` to `2`. Use this to validate that the entire string was consumed when parsing strict numeric input.

### Number to string

```cpp
int   http_status = 404;
double temperature = 23.5;

std::string status_str = std::to_string(http_status);  // "404"
std::string temp_str   = std::to_string(temperature);  // "23.500000"
```

`to_string()` always uses six decimal places for floating-point types. For formatted output — fewer decimals, scientific notation, zero-padded integers — `std::ostringstream` with `<iomanip>` manipulators (`std::setprecision`, `std::fixed`, `std::setw`) gives full control.

## Comparing Strings in C++

`std::string` supports `==`, `!=`, `<`, `>`, `<=`, and `>=`. All comparisons are lexicographic, based on character values. Case matters: `"Apple" < "apple"` because uppercase letters have lower ASCII values.

```cpp
std::string environment = "production";

if (environment == "production") {
    // live traffic path
} else if (environment == "staging") {
    // test path
}
```

The `compare()` method mirrors C's `strcmp()` return convention: negative if the caller comes before the argument, zero if equal, positive if after.

```cpp
std::string city_a = "Barcelona";
std::string city_b = "Cardiff";

int result = city_a.compare(city_b);
// result < 0: "Barcelona" sorts before "Cardiff"
```

`compare()` also accepts range overloads: `a.compare(0, 3, b, 0, 3)` compares the first three characters of each string without allocating temporaries. Useful in tight parsing loops where avoiding copies matters.

For case-insensitive comparison, C++17 has no single-call solution for `std::string`. The portable approach is normalising both strings to lowercase with `std::transform` and `::tolower`, then comparing. The ICU library and platform-specific functions offer locale-aware comparisons when you need them.

## Where C++ String Methods Trip You Up

### Trap 1: Using find() result without checking npos

```cpp
std::string config = "debug=false";
size_t pos = config.find("release");

// pos is std::string::npos — a huge unsigned number
std::string after = config.substr(pos);  // throws std::out_of_range
```

`npos` is `static_cast<size_t>(-1)` — on 64-bit systems, `18446744073709551615`. Every call to `find()` and its variants returns this value on failure. Passing it to `substr()` causes a throw. The fix is a single check before every use:

```cpp
if (pos != std::string::npos) {
    std::string after = config.substr(pos);
}
```

### Trap 2: Off-by-one when computing substr() lengths

```cpp
std::string date = "2026-06-13";

std::string year = date.substr(0, 4);   // "2026" — correct (length = 4)
std::string bad  = date.substr(0, 3);   // "202"  — one too short

// When using two find() positions:
size_t start = 5;  // points at '0' in "06"
size_t end   = 7;  // points at '-' after "06"

// end - start = 2 = correct length of "06"
std::string month = date.substr(start, end - start);  // "06" ✓
```

The rule: when `end` points to the character AFTER the last one you want (which is how `find()` positions work), use `end - start`. When `end` points AT the last character (as in the trim pattern), use `end - start + 1`.

### Trap 3: Storing find() result in a signed int

`find()` returns `size_t`, an unsigned type. Storing it in `int` and comparing to `-1` compiles but breaks silently.

```cpp
// Wrong — narrowing conversion, comparison with -1 doesn't work
int pos = str.find("token");
if (pos == -1) { /* never reached when npos > INT_MAX */ }

// Correct
size_t pos = str.find("token");
if (pos == std::string::npos) { /* correct */ }
```

Compile with `-Wall -Wconversion`; the signed/unsigned mismatch generates a warning that catches this class of bug at compile time rather than runtime.

## C++ vs Python vs JavaScript: How String Methods Compare

Comparing the C++ substring approach against Python and JavaScript shows what each language optimises for.

```python
# Python — slice syntax uses end index
path = "/api/v2/users"
last_slash = path.rfind('/')
after_slash = path[last_slash + 1:]  # "users"

# Python replace() replaces all occurrences by default
result = "aabbaa".replace("aa", "XX")  # "XXbbXX"
```

```javascript
// JavaScript — substring() and slice() both use end index
const path = "/api/v2/users";
const lastSlash = path.lastIndexOf('/');
const afterSlash = path.substring(lastSlash + 1);  // "users"

// replaceAll() added in ES2021; older code uses regex
const result = "aabbaa".replaceAll("aa", "XX");  // "XXbbXX"
```

```cpp
// C++ — substr() uses length, not end index; no built-in replace_all
std::string path = "/api/v2/users";
size_t last_slash = path.rfind('/');
std::string after_slash = path.substr(last_slash + 1);  // "users"

// replace_all requires manual loop (see FAQ section)
```

Python's slice notation is concise and uses the index-range mental model most developers already have. JavaScript has two overlapping methods (`substring` and `slice`), where `slice` additionally supports negative indices. C++ has one unambiguous `substr()` and explicit length semantics — more verbose, but there's only one mental model to hold.

One area where C++ has no built-in equivalent: `replace_all`. Python's `str.replace()` replaces all matches by default; JavaScript's `String.replaceAll()` does the same (ES2021+). In C++, you write the loop yourself. The FAQ section below has the canonical implementation.

For the complete Python string API with examples, the [Python string methods cheatsheet](/cheatsheets/python-string-methods-cheatsheet) covers every method. For a parallel look at iteration and slicing patterns in JavaScript, the [JavaScript array methods reference](/languages/javascript/array-methods) is a useful comparison. The complete `std::string` specification — including C++20 additions like `starts_with()`, `ends_with()`, and `contains()` — is at [cppreference.com/w/cpp/string/basic_string](https://en.cppreference.com/w/cpp/string/basic_string).

When strings interact with other C++ data structures — particularly `std::vector<std::string>` for tokenized lines or `std::map<std::string, T>` for key-value parsing — the [C++ STL data structures guide](/languages/cpp/data-structures-stl) covers how those containers work alongside string operations.

## Frequently Asked Questions

### How do I check if a C++ string contains a substring?

Use `find()` and compare the result against `std::string::npos`:

```cpp
std::string header = "Content-Type: application/json";
bool is_json = (header.find("application/json") != std::string::npos);
```

In C++23, `std::string::contains()` makes this one method call: `header.contains("application/json")`. For C++17 and earlier, the `find() != npos` idiom is the standard approach and works on all compliant compilers.

### What does std::string::npos mean?

`npos` is `static_cast<size_t>(-1)`. On a 64-bit system where `size_t` is a 64-bit unsigned integer, this wraps around to `18446744073709551615`. It was chosen to be unreachable as a real string index — no string will ever be that long. The name means "no position". Every method in the `find()` family returns `npos` on a failed search. For the exact definition and guarantees, the [cppreference npos page](https://en.cppreference.com/w/cpp/string/basic_string/npos) is the authoritative reference.

### How do I replace all occurrences of a substring in C++?

The standard library does not have `replace_all()`. Write the loop:

```cpp
void replace_all(std::string& text, const std::string& from, const std::string& to) {
    size_t pos = 0;
    while ((pos = text.find(from, pos)) != std::string::npos) {
        text.replace(pos, from.length(), to);
        pos += to.length();  // advance past the replacement
    }
}
```

The `pos += to.length()` line is not optional. When `to` contains `from` — for example replacing `"a"` with `"aa"` — advancing by `to.length()` skips past the newly inserted text. Without it, the loop matches the inserted characters and runs until memory is exhausted.

### What is the difference between C++ substr() and Python slice syntax?

`substr(pos, len)` takes a start position and a length. Python slices take a start and an end index.

```cpp
// C++ — start position + length
std::string msg = "hello world";
std::string world = msg.substr(6, 5);  // "world" (start=6, length=5)
```

```python
# Python — start index + end index
msg = "hello world"
world = msg[6:11]  # "world" (start=6, end=11)
```

To convert: `msg.substr(start, end - start)` in C++ produces the same characters as `msg[start:end]` in Python.

### Does C++ std::string have a split() method?

No. C++17 and earlier provide no built-in `split()`. The standard implementation uses `find()` and `substr()` in a loop:

```cpp
#include <vector>
#include <string>

std::vector<std::string> split(const std::string& text, char delimiter) {
    std::vector<std::string> parts;
    size_t start = 0;
    size_t end;
    while ((end = text.find(delimiter, start)) != std::string::npos) {
        parts.push_back(text.substr(start, end - start));
        start = end + 1;  // skip past the delimiter
    }
    parts.push_back(text.substr(start));  // final segment after last delimiter
    return parts;
}
```

C++20 ranges and libraries like Boost.Algorithm provide more ergonomic split utilities when those are available in your project.

## Conclusion

The C++ string method toolkit covers everything text processing requires in standard C++: `substr()` for C++ substring extraction, the `find()` family for searching in both directions, `replace()`, `insert()`, and `erase()` for in-place modification, and `stoi()` through `to_string()` for bridging the string–number boundary. The two conventions that take getting used to are the `npos` sentinel — always check before using `find()` results — and `substr()`'s length-not-end-index parameter. Once those patterns are internalised, the rest of the API is predictable and consistent. For the complete method signatures including C++20 and C++23 additions, [cppreference std::string](https://en.cppreference.com/w/cpp/string/basic_string) is the reference to bookmark. To apply these string operations in a real-world encoding context, [base64 encoding and decoding](/guides/base64-encoding-decoding-guide) walks through exactly this kind of character-by-character and substring manipulation.
