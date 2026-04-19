---
category: guides
content_type: editorial
description: Understand URL encoding, percent encoding, and how to safely encode query
  parameters to avoid bugs and security issues.
og_image: /og/guides/url-encoding-query-parameters-guide.png
published_date: '2026-04-17'
related_posts:
- /guides/base64-encoding-decoding-guide
- /guides/json-formatter-validator-best-practices
- /blog/http-request-anatomy
related_tools:
- /tools/url-encoder-decoder
tags:
- url-encoding
- percent-encoding
- query-parameters
- http
- web-development
template_id: guide-v1
title: 'URL Encoding and Query Parameters: Complete Developer Guide'
word_count_target: 1800
---

# URL Encoding and Query Parameters: Complete Developer Guide

URL encoding (also called percent encoding) converts characters that are not allowed or carry special meaning in a URL into a safe representation using a `%` followed by two hexadecimal digits. Getting it wrong causes broken links, failed API calls, and security vulnerabilities.

## Why URL Encoding Exists

URLs can only contain a defined set of characters from the ASCII character set. Everything else—spaces, Unicode characters, reserved characters like `&`, `=`, and `?`—must be encoded before inclusion in a URL.

RFC 3986 defines two categories of characters:

- **Unreserved characters**: `A–Z`, `a–z`, `0–9`, `-`, `_`, `.`, `~` — safe to use as-is
- **Reserved characters**: `:`, `/`, `?`, `#`, `[`, `]`, `@`, `!`, `$`, `&`, `'`, `(`, `)`, `*`, `+`, `,`, `;`, `=` — have special meaning in URL syntax; must be encoded when used as data

A space, for example, encodes to `%20`. The `@` symbol encodes to `%40`. Unicode characters encode to their UTF-8 byte sequences, each byte percent-encoded individually.

## How Percent Encoding Works

The encoding process is straightforward:

1. Convert the character to its UTF-8 byte representation
2. Write `%` followed by the two-character uppercase hex value of each byte

For example, the `€` (euro sign) in UTF-8 is three bytes: `0xE2 0x82 0xAC`. Its percent-encoded form is `%E2%82%AC`.

```python
import urllib.parse

# Encode a single character
encoded = urllib.parse.quote("€")
print(encoded)  # %E2%82%AC

# Encode a full string
text = "hello world & more"
encoded = urllib.parse.quote(text)
print(encoded)  # hello%20world%20%26%20more
```

Note that `quote()` does not encode the `/` character by default, since it is often a meaningful path separator. Use `quote(text, safe="")` to encode everything including `/`.

## Query String Encoding

Query parameters require special handling. The `&` character separates parameters and the `=` character separates key from value. Both must be encoded inside parameter values.

```python
import urllib.parse

params = {
    "q": "python url encoding",
    "filter": "date:2024-01 to 2024-12",
    "redirect": "https://example.com/path?key=value"
}

# urlencode handles the full dict — encodes keys and values
query_string = urllib.parse.urlencode(params)
print(query_string)
# q=python+url+encoding&filter=date%3A2024-01+to+2024-12&redirect=https%3A%2F%2Fexample.com%2Fpath%3Fkey%3Dvalue
```

`urlencode()` uses `+` to represent spaces by default (application/x-www-form-urlencoded format). To use `%20` instead, pass `quote_via=urllib.parse.quote`:

```python
query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
print(query_string)
# q=python%20url%20encoding&filter=date%3A2024-01%20to%202024-12&...
```

Both `+` and `%20` represent a space in query strings, but `%20` is correct in path segments. Mixing them is a common source of confusion.

## Decoding URL-Encoded Strings

Decoding is the reverse operation. Use `urllib.parse.unquote()` for path segments and `urllib.parse.unquote_plus()` for query strings (which handles `+` as a space):

```python
import urllib.parse

# Path segment decoding
encoded_path = "/files/my%20document%20%28draft%29.pdf"
decoded = urllib.parse.unquote(encoded_path)
print(decoded)  # /files/my document (draft).pdf

# Query string decoding (+ treated as space)
encoded_query = "name=John+Doe&city=New+York"
decoded = urllib.parse.unquote_plus(encoded_query)
print(decoded)  # name=John Doe&city=New York
```

### Parsing a Full Query String

```python
import urllib.parse

query = "q=python+url&page=2&tags=web%2Chttp"

params = urllib.parse.parse_qs(query)
print(params)
# {'q': ['python url'], 'page': ['2'], 'tags': ['web,http']}

# parse_qs returns lists (parameters can repeat); use parse_qsl for list of tuples
pairs = urllib.parse.parse_qsl(query)
print(pairs)
# [('q', 'python url'), ('page', '2'), ('tags', 'web,http')]
```

`parse_qs` returns each value as a list because query parameters can appear multiple times (`?tag=python&tag=web`). Use `parse_qsl` when you need ordered pairs instead.

## URL Encoding in JavaScript

The browser provides three functions with importantly different behaviors:

| Function | Encodes | Does Not Encode |
|----------|---------|-----------------|
| `encodeURIComponent()` | Everything except unreserved chars | `A–Z a–z 0–9 - _ . ! ~ * ' ( )` |
| `encodeURI()` | Non-URL characters | Reserved chars (`: / ? # [ ] @ ! $ & ' ( ) * + , ; =`) |
| `escape()` | ⚠️ Deprecated — do not use | Unreliable Unicode handling |

```javascript
const searchQuery = "hello world & more";
const redirectUrl = "https://example.com/path?key=value";

// For query parameter values — use encodeURIComponent
console.log(encodeURIComponent(searchQuery));
// hello%20world%20%26%20more

// For full URLs — use encodeURI (preserves URL structure)
const url = `https://example.com/search?q=${encodeURIComponent(searchQuery)}`;
console.log(url);
// https://example.com/search?q=hello%20world%20%26%20more

// URLSearchParams handles query string construction correctly
const params = new URLSearchParams({
  q: "python url encoding",
  page: "2",
  redirect: redirectUrl
});
console.log(params.toString());
// q=python+url+encoding&page=2&redirect=https%3A%2F%2Fexample.com%2Fpath%3Fkey%3Dvalue
```

`URLSearchParams` is the right tool for building query strings in modern [JavaScript](/languages/javascript). It handles encoding, serialization, and appending parameters without manual string concatenation.

```javascript
// Decoding
const encoded = "hello%20world%20%26%20more";
console.log(decodeURIComponent(encoded));  // hello world & more

// Parse query string
const qs = "?q=python+url&page=2";
const parsed = new URLSearchParams(qs);
console.log(parsed.get("q"));    // python url
console.log(parsed.get("page")); // 2
```

## Building URLs Safely

Never build URLs by string concatenation with unencoded values. Untrusted input in a URL can break the request or introduce open redirect vulnerabilities.

```python
import urllib.parse

# Unsafe — user input injected directly
user_input = "search?redirect=https://evil.com"
unsafe_url = f"https://example.com/query?q={user_input}"
print(unsafe_url)
# https://example.com/query?q=search?redirect=https://evil.com — broken

# Safe — encode the value first
safe_url = f"https://example.com/query?q={urllib.parse.quote(user_input)}"
print(safe_url)
# https://example.com/query?q=search%3Fredirect%3Dhttps%3A%2F%2Fevil.com — correct
```

For full URL construction in [Python](/languages/python), `urllib.parse.urlencode()` plus `urllib.parse.urlunparse()` gives you precise control over each URL component:

```python
import urllib.parse

components = urllib.parse.ParseResult(
    scheme="https",
    netloc="api.example.com",
    path="/v1/search",
    params="",
    query=urllib.parse.urlencode({"q": "url encoding guide", "limit": 10}),
    fragment=""
)

url = urllib.parse.urlunparse(components)
print(url)
# https://api.example.com/v1/search?q=url+encoding+guide&limit=10
```

## Path Parameters vs Query Parameters

Understanding the difference prevents a common encoding mistake:

- **Path parameters** are part of the URL path: `/users/{id}/profile` — encode with `quote(value, safe="")`
- **Query parameters** follow the `?` separator: `/search?q={term}` — encode with `quote_plus()` or `urlencode()`

```python
import urllib.parse

user_id = "alice/bob"  # contains a slash
term = "hello world"

# Path parameter — slash must be encoded
path = f"/users/{urllib.parse.quote(user_id, safe='')}/profile"
print(path)  # /users/alice%2Fbob/profile

# Query parameter — spaces can use + or %20
query = urllib.parse.urlencode({"q": term})
print(f"/search?{query}")  # /search?q=hello+world
```

## Encoding Special Query Parameter Patterns

### Arrays and Repeated Parameters

HTTP does not define a single standard for encoding arrays as query parameters. Three common conventions exist:

```python
import urllib.parse

tags = ["python", "web", "api"]

# Convention 1: repeated keys
params_repeated = [("tags", t) for t in tags]
print(urllib.parse.urlencode(params_repeated))
# tags=python&tags=web&tags=api

# Convention 2: bracket notation (PHP/Rails style)
params_brackets = [("tags[]", t) for t in tags]
print(urllib.parse.urlencode(params_brackets))
# tags%5B%5D=python&tags%5B%5D=web&tags%5B%5D=api

# Convention 3: comma-separated values
params_csv = {"tags": ",".join(tags)}
print(urllib.parse.urlencode(params_csv))
# tags=python%2Cweb%2Capi
```

Match the convention your server expects. When consuming a third-party API, check its documentation—mismatched array encoding is a common source of `400 Bad Request` errors.

### JSON in Query Parameters

Embedding a JSON object in a query parameter requires encoding the entire JSON string:

```python
import json, urllib.parse

filters = {"status": "active", "role": "admin", "page": 1}
encoded_filters = urllib.parse.quote(json.dumps(filters))
url = f"https://api.example.com/users?filters={encoded_filters}"
print(url)
# https://api.example.com/users?filters=%7B%22status%22%3A%20%22active%22%2C%20%22role%22%3A%20%22admin%22%2C%20%22page%22%3A%201%7D
```

This is valid but produces long, opaque URLs. For complex filter objects, prefer a POST request with a JSON body, or use API-specific query DSLs that keep URLs readable.

## Inspecting and Debugging URLs

Python's `urllib.parse.urlparse()` breaks a URL into its components for inspection:

```python
from urllib.parse import urlparse, parse_qs

url = "https://api.example.com/v1/search?q=python+url&page=2&tags=web%2Chttp#results"

parsed = urlparse(url)
print(parsed.scheme)    # https
print(parsed.netloc)    # api.example.com
print(parsed.path)      # /v1/search
print(parsed.query)     # q=python+url&page=2&tags=web%2Chttp
print(parsed.fragment)  # results

params = parse_qs(parsed.query)
print(params)
# {'q': ['python url'], 'page': ['2'], 'tags': ['web,http']}
```

In JavaScript:

```javascript
const url = new URL("https://api.example.com/v1/search?q=python+url&page=2");
console.log(url.hostname);          // api.example.com
console.log(url.pathname);          // /v1/search
console.log(url.searchParams.get("q"));   // python url
console.log(url.searchParams.get("page")); // 2

// Modify a query parameter
url.searchParams.set("page", "3");
console.log(url.toString());
// https://api.example.com/v1/search?q=python+url&page=3
```

The `URL` class in modern browsers and Node.js (v10+) handles parsing and mutation without any string manipulation, and it handles encoding automatically when you set parameters via `searchParams`.

## Double-Encoding Pitfalls

Double-encoding occurs when an already-encoded string is encoded again. `%20` becomes `%2520` (`%25` is the encoding of `%`). This causes decoding on the server to return a literal `%20` string instead of a space.

```python
import urllib.parse

already_encoded = "hello%20world"

# Wrong — encodes the percent sign too
double_encoded = urllib.parse.quote(already_encoded)
print(double_encoded)  # hello%2520world

# Right — decode first if unsure, then re-encode
cleaned = urllib.parse.unquote(already_encoded)
re_encoded = urllib.parse.quote(cleaned)
print(re_encoded)  # hello%20world
```

When receiving URL-encoded data from an external source, always decode before processing, then re-encode when putting it back into a URL.

## Security Implications of URL Encoding

### Open Redirect Prevention

Open redirect vulnerabilities occur when a `redirect` parameter contains an attacker-controlled URL. Validation must happen after decoding, not on the raw encoded string:

```python
from urllib.parse import urlparse, unquote

ALLOWED_HOSTS = {"example.com", "api.example.com"}

def safe_redirect(redirect_param: str) -> str:
    """Validate redirect target after decoding to prevent open redirect."""
    decoded = unquote(redirect_param)
    parsed = urlparse(decoded)

    # Reject absolute URLs pointing to external hosts
    if parsed.netloc and parsed.netloc not in ALLOWED_HOSTS:
        return "/dashboard"  # safe default

    # Reject protocol-relative URLs (//)
    if decoded.startswith("//"):
        return "/dashboard"

    return decoded

# Attack attempt: double-encoded external URL
print(safe_redirect("%2F%2Fevil.com%2Fphishing"))  # /dashboard — blocked
print(safe_redirect("/profile"))                    # /profile  — allowed
```

Always decode before validation. Attackers use double-encoding (`%2F%2F` for `//`) specifically to bypass filters that check the raw encoded string.

### SQL Injection via URL Parameters

URL decoding happens before query parameters reach application code. A parameter value of `%27%20OR%201%3D1--` decodes to `' OR 1=1--`—a classic SQL injection payload. Encoding is not a security boundary; always use parameterized queries regardless of how parameters arrive.

```python
import sqlite3, urllib.parse

# Attacker-supplied query string
raw_qs = "id=1%27%20OR%20%271%27%3D%271"
params = urllib.parse.parse_qs(raw_qs)
user_id = params.get("id", [""])[0]
print(user_id)  # 1' OR '1'='1  — fully decoded

conn = sqlite3.connect(":memory:")

# Vulnerable — never do this
# cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

# Safe — parameterized query
cursor = conn.cursor()
# cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

## Encode and Decode URLs in Your Browser

The [DevNook URL Encoder/Decoder tool](/tools/url-encoder-decoder) handles percent encoding, query string parsing, and full URL analysis directly in your browser. Paste in a raw URL to decode all components, or enter plain text to get the encoded form instantly.

Related reading: the [Base64 Encoding guide](/guides/base64-encoding-decoding-guide) covers a different encoding scheme used for binary data in APIs and HTTP headers. For JSON payloads delivered over HTTP with encoded parameters, see the [JSON Formatter and Validator guide](/guides/json-formatter-validator-best-practices).

URL encoding is a small but critical detail. Using the right function for the right context—`encodeURIComponent` in JavaScript, `quote` vs `quote_plus` in Python—prevents a category of bugs that are difficult to trace once they reach a production system.