---
title: "URL Encoding and Decoding in Java — A Step-by-Step Tutorial"
description: "Build a URL parameter sanitizer in Java using URLEncoder and URLDecoder. Covers charset handling, edge cases, and testing."
published_date: "2026-05-09"
category: languages
language: "java"
concept: "url-encoder-decoder"
linkAnchors:
  - "java url encoder decoder"
  - "url encoder decoder"
template_id: "lang-v5"
tags: ["java", "url-encoding", "web-development", "tutorial"]
difficulty: "intermediate"
related_posts: []
related_tools: []
og_image: "/og/languages/java/url-encoder-decoder.png"
---

By the end of this tutorial, you will have a working `UrlParamSanitizer` utility in Java that encodes, decodes, and round-trips URL query parameters safely. Working with a url encoder decoder java solution is essential for any web application that constructs or parses URLs — and getting the charset wrong is the single most common cause of broken links in production.

## What You'll Build

The mini-project is a `UrlParamSanitizer` class that converts raw key-value pairs into properly encoded URL query strings and parses encoded query strings back into their original values. It handles special characters, Unicode text, and malformed input gracefully. The utility uses `java.net.URLEncoder` and `java.net.URLDecoder` with explicit `StandardCharsets.UTF_8` to avoid the platform-encoding trap that has caused countless bugs in Java web applications.

Why build this? Every HTTP request containing user-generated data — search terms, form inputs, filenames — must encode special characters before embedding them in a URL. A bare `&` in a parameter value breaks query string parsing. An unencoded space produces an invalid URL. A `#` truncates everything after it. The `UrlParamSanitizer` you build here encapsulates all of these concerns into a tested, reusable component. The build takes roughly 15 minutes and covers the url encoder decoder java API end-to-end.

**Prerequisites:** Basic Java syntax, familiarity with `Map` and `String` operations, understanding of command-line compilation with `javac`.

## Step 1 — Setting Up the Project

Create a single `UrlParamSanitizer.java` file with the necessary imports and class skeleton.

```java
import java.net.URLEncoder;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.StringJoiner;

public class UrlParamSanitizer {

    public static void main(String[] args) {
        UrlParamSanitizer sanitizer = new UrlParamSanitizer();

        Map<String, String> params = new LinkedHashMap<>();
        params.put("query", "java url encoding");
        params.put("page", "1");

        String encoded = sanitizer.encodeParams(params);
        System.out.println("Encoded: " + encoded);
    }
}
```

The imports are deliberate. `StandardCharsets.UTF_8` is a `Charset` object, not a `String`, which matters because the `URLEncoder.encode(String, String)` overload that accepts a charset name as a `String` has been deprecated since Java 10 in favor of the `Charset`-based overload. Using `StandardCharsets.UTF_8` directly avoids both the deprecation warning and the impossible-in-practice `UnsupportedEncodingException` that the string-based method forces you to catch. `LinkedHashMap` preserves insertion order, which makes the query string output deterministic and easier to test.

## Step 2 — Implementing URL Encoding

Add a method that takes a `Map<String, String>` of parameters and produces an encoded query string.

```java
    public String encodeParams(Map<String, String> params) {
        StringJoiner joiner = new StringJoiner("&");

        for (Map.Entry<String, String> entry : params.entrySet()) {
            String encodedKey = URLEncoder.encode(
                entry.getKey(), StandardCharsets.UTF_8
            );
            String encodedValue = URLEncoder.encode(
                entry.getValue(), StandardCharsets.UTF_8
            );
            joiner.add(encodedKey + "=" + encodedValue);
        }

        return joiner.toString();
    }

    public String encodeSingle(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }
```

`URLEncoder.encode()` converts each character that is not an unreserved character (letters, digits, `-`, `_`, `.`, `*`) into its percent-encoded form. Spaces become `+` signs — this follows the `application/x-www-form-urlencoded` MIME type specification, which is the encoding used by HTML forms. The `StringJoiner` with `"&"` as the delimiter assembles the individual `key=value` pairs into a complete query string without a trailing `&`. Notice that both keys and values are encoded separately — encoding the entire assembled string would incorrectly encode the `=` and `&` delimiters themselves. The `encodeSingle()` convenience method handles cases where you need to encode a single value rather than a full parameter map.

## Step 3 — Adding URL Decoding

Implement the reverse operation: parse an encoded query string back into a `Map<String, String>`.

```java
    public Map<String, String> decodeParams(String queryString) {
        Map<String, String> result = new LinkedHashMap<>();

        if (queryString == null || queryString.isEmpty()) {
            return result;
        }

        String[] pairs = queryString.split("&");
        for (String pair : pairs) {
            int equalsIndex = pair.indexOf('=');
            if (equalsIndex > 0) {
                String key = URLDecoder.decode(
                    pair.substring(0, equalsIndex),
                    StandardCharsets.UTF_8
                );
                String value = URLDecoder.decode(
                    pair.substring(equalsIndex + 1),
                    StandardCharsets.UTF_8
                );
                result.put(key, value);
            }
        }

        return result;
    }

    public String decodeSingle(String encoded) {
        return URLDecoder.decode(encoded, StandardCharsets.UTF_8);
    }
```

The decoder splits the query string on `&` first, then splits each pair on the first `=` using `indexOf` rather than `split("=")` — this is important because parameter values themselves might contain encoded `=` characters (`%3D`). `URLDecoder.decode()` reverses the encoding: `+` becomes a space, and `%XX` sequences become their corresponding characters. The method returns a `LinkedHashMap` to preserve parameter order, which aids debugging and makes test assertions straightforward.

## Step 4 — Handling Edge Cases and Errors

Real-world URLs contain malformed data. A url encoder decoder java implementation must handle null inputs, double-encoded strings, and broken percent sequences without crashing.

```java
    public String safeEncode(String value) {
        if (value == null) {
            return "";
        }
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    public String safeDecode(String encoded) {
        if (encoded == null || encoded.isEmpty()) {
            return "";
        }
        try {
            return URLDecoder.decode(encoded, StandardCharsets.UTF_8);
        } catch (IllegalArgumentException e) {
            // Malformed percent sequence (e.g., "%ZZ" or trailing "%")
            System.err.println("Malformed URL encoding: " + encoded
                             + " — " + e.getMessage());
            return encoded;  // Return as-is rather than crashing
        }
    }

    public boolean isAlreadyEncoded(String value) {
        // Check if the string contains percent-encoded sequences
        if (value == null) return false;
        return value.matches(".*%[0-9A-Fa-f]{2}.*");
    }
```

The `safeDecode()` method wraps `URLDecoder.decode()` in a try-catch for `IllegalArgumentException`, which the decoder throws when it encounters a `%` followed by non-hex characters (like `%ZZ`) or a trailing `%` at the end of the string. Returning the original string instead of crashing is the safe default — the caller gets usable data rather than an exception. The `isAlreadyEncoded()` method uses a regex to detect existing percent sequences, which prevents the double-encoding problem where encoding `hello%20world` produces `hello%2520world` — the `%` itself gets encoded into `%25`.

## The Complete Code

```java
import java.net.URLEncoder;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.StringJoiner;

public class UrlParamSanitizer {

    public String encodeParams(Map<String, String> params) {
        StringJoiner joiner = new StringJoiner("&");
        for (Map.Entry<String, String> entry : params.entrySet()) {
            String key = URLEncoder.encode(
                entry.getKey(), StandardCharsets.UTF_8);
            String val = URLEncoder.encode(
                entry.getValue(), StandardCharsets.UTF_8);
            joiner.add(key + "=" + val);
        }
        return joiner.toString();
    }

    public String encodeSingle(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    public Map<String, String> decodeParams(String queryString) {
        Map<String, String> result = new LinkedHashMap<>();
        if (queryString == null || queryString.isEmpty()) {
            return result;
        }
        String[] pairs = queryString.split("&");
        for (String pair : pairs) {
            int eq = pair.indexOf('=');
            if (eq > 0) {
                String key = URLDecoder.decode(
                    pair.substring(0, eq), StandardCharsets.UTF_8);
                String val = URLDecoder.decode(
                    pair.substring(eq + 1), StandardCharsets.UTF_8);
                result.put(key, val);
            }
        }
        return result;
    }

    public String decodeSingle(String encoded) {
        return URLDecoder.decode(encoded, StandardCharsets.UTF_8);
    }

    public String safeEncode(String value) {
        if (value == null) return "";
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    public String safeDecode(String encoded) {
        if (encoded == null || encoded.isEmpty()) return "";
        try {
            return URLDecoder.decode(encoded, StandardCharsets.UTF_8);
        } catch (IllegalArgumentException e) {
            System.err.println("Malformed encoding: " + encoded);
            return encoded;
        }
    }

    public boolean isAlreadyEncoded(String value) {
        if (value == null) return false;
        return value.matches(".*%[0-9A-Fa-f]{2}.*");
    }

    public static void main(String[] args) {
        UrlParamSanitizer sanitizer = new UrlParamSanitizer();

        Map<String, String> params = new LinkedHashMap<>();
        params.put("search", "java url encoder decoder");
        params.put("category", "programming & development");
        params.put("page", "1");

        String encoded = sanitizer.encodeParams(params);
        System.out.println("Encoded:  " + encoded);

        Map<String, String> decoded = sanitizer.decodeParams(encoded);
        System.out.println("Decoded:  " + decoded);

        String unicode = sanitizer.encodeSingle("Tokyo 東京");
        System.out.println("Unicode:  " + unicode);
        System.out.println("Restored: "
            + sanitizer.decodeSingle(unicode));
    }
}
```

## Under the Hood: Performance and Mechanics

`URLEncoder.encode()` processes each character in the input string individually. For each character, it first converts to bytes using the specified charset (UTF-8 produces 1-4 bytes per character depending on the Unicode code point). Then it checks each byte against the set of unreserved characters defined by the `application/x-www-form-urlencoded` specification: letters (`a-z`, `A-Z`), digits (`0-9`), and four special characters (`-`, `_`, `.`, `*`). Any byte outside this set gets formatted as `%XX` where XX is the uppercase hexadecimal representation of the byte value.

Internally, `URLEncoder` builds the result using a `StringBuilder`. For ASCII-only input, the allocation overhead is minimal — most characters pass through unchanged. For strings containing many special characters or multibyte Unicode text, the output can be three times the length of the input (each byte becomes three characters: `%`, hex digit, hex digit). A 1 KB string of Chinese characters encoded in UTF-8 produces approximately 9 KB of percent-encoded output, because each character occupies 3 UTF-8 bytes, and each byte becomes a 3-character percent sequence.

The deprecated `encode(String)` method without a charset parameter defaults to the platform's default encoding, which varies between systems — `UTF-8` on modern Linux, `windows-1252` on many Windows installations, `Shift_JIS` on Japanese Windows. This means identical Java code produces different encoded output on different operating systems, which is why the charset-explicit overload is mandatory for portable applications.

Both `URLEncoder` and `URLDecoder` are stateless and thread-safe. They contain no instance fields and operate purely on their input parameters. You can safely share a single instance across threads, or use the static methods directly without synchronization. The only performance consideration for high-throughput scenarios is the `StringBuilder` allocation inside `encode()` — for applications encoding millions of strings per second, consider pre-allocating a `StringBuilder` and using a custom encoding loop.

## Advanced Edge Cases

**Edge Case 1: Space Encoding — Plus Sign vs. Percent-20**

`URLEncoder` encodes spaces as `+` signs, following the `application/x-www-form-urlencoded` specification. However, RFC 3986 (the URI standard) specifies that spaces should be encoded as `%20`. This difference matters when encoding path segments rather than query parameters.

```java
String formEncoded = URLEncoder.encode(
    "hello world", StandardCharsets.UTF_8);
// Result: "hello+world"

String rfc3986Encoded = URLEncoder.encode(
    "hello world", StandardCharsets.UTF_8)
    .replace("+", "%20");
// Result: "hello%20world"
```

Most web servers accept both forms in query strings, but path segments must use `%20`. If you send a `+` in a path segment, the server interprets it as a literal plus sign, not a space. Use `.replace("+", "%20")` when encoding values destined for URL paths.

**Edge Case 2: Encoding Path Segments Breaks Forward Slashes**

`URLEncoder` is designed exclusively for query parameter values. Applying it to an entire URL or path segment encodes forward slashes (`/`) as `%2F`, which breaks the path structure entirely.

```java
String path = "/api/users/john doe/profile";

// WRONG — encodes slashes too
String broken = URLEncoder.encode(path, StandardCharsets.UTF_8);
// Result: "%2Fapi%2Fusers%2Fjohn+doe%2Fprofile"

// CORRECT — encode only the variable segment
String fixed = "/api/users/"
    + URLEncoder.encode("john doe", StandardCharsets.UTF_8)
        .replace("+", "%20")
    + "/profile";
// Result: "/api/users/john%20doe/profile"
```

The correct approach is to split the URL into its structural components (scheme, host, path segments, query parameters), encode only the variable parts, and reassemble. Java's `java.net.URI` constructor handles this correctly when you pass each component separately.

## Testing url-encoder-decoder in Java

A robust url encoder decoder java implementation requires tests for round-trip integrity, special characters, Unicode, and malformed input. The following example uses JUnit 5.

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.LinkedHashMap;
import java.util.Map;

class UrlParamSanitizerTest {

    private final UrlParamSanitizer sanitizer =
        new UrlParamSanitizer();

    @Test
    void roundTripPreservesOriginalValues() {
        Map<String, String> original = new LinkedHashMap<>();
        original.put("name", "Jane Doe");
        original.put("role", "engineer&manager");

        String encoded = sanitizer.encodeParams(original);
        Map<String, String> decoded =
            sanitizer.decodeParams(encoded);

        assertEquals(original, decoded);
    }

    @Test
    void encodesSpecialCharactersCorrectly() {
        assertEquals("a%26b", sanitizer.encodeSingle("a&b"));
        assertEquals("a%3Db", sanitizer.encodeSingle("a=b"));
        assertEquals("a%3Fb", sanitizer.encodeSingle("a?b"));
        assertEquals("a%23b", sanitizer.encodeSingle("a#b"));
    }

    @Test
    void handlesUnicodeCharacters() {
        String original = "Tokyo 東京";
        String encoded = sanitizer.encodeSingle(original);
        String decoded = sanitizer.decodeSingle(encoded);
        assertEquals(original, decoded);
    }

    @Test
    void safeDecodeHandlesMalformedInput() {
        String malformed = "hello%ZZworld";
        String result = sanitizer.safeDecode(malformed);
        assertEquals(malformed, result);
    }

    @Test
    void safeEncodeHandlesNull() {
        assertEquals("", sanitizer.safeEncode(null));
    }

    @Test
    void detectsAlreadyEncodedStrings() {
        assertTrue(sanitizer.isAlreadyEncoded("hello%20world"));
        assertFalse(sanitizer.isAlreadyEncoded("hello world"));
    }
}
```

The `roundTripPreservesOriginalValues` test is the most critical — it verifies that encoding followed by decoding produces the exact original input, including spaces and ampersands that would break URL parsing if left unencoded. The Unicode test ensures that multibyte characters survive the encode-decode cycle without corruption. The `safeDecodeHandlesMalformedInput` test confirms that the defensive wrapper returns the original string rather than throwing when given invalid percent sequences.

## What We Learned

- **Always specify `StandardCharsets.UTF_8` explicitly.** The deprecated `encode(String)` method defaults to the platform encoding, which varies across operating systems and produces inconsistent results. The charset-explicit overload eliminates this entire class of bugs and avoids the unnecessary `UnsupportedEncodingException`.

- **Encode parameter values individually, never the full URL.** Applying `URLEncoder` to a complete URL encodes structural characters like `/`, `?`, and `#`, breaking the URL's meaning. Split the URL into components, encode only the variable parts, and reassemble.

- **Spaces encode differently depending on context.** `URLEncoder` produces `+` for spaces (form encoding), but URL path segments require `%20` (RFC 3986). Use `.replace("+", "%20")` when building path segments, or use `java.net.URI` for proper component-level encoding.

- **Defensive decoding prevents crashes from malformed input.** `URLDecoder.decode()` throws `IllegalArgumentException` on invalid percent sequences. Wrap decode calls in try-catch and return the original string as a fallback to keep the application running.

- **Round-trip testing is the gold standard.** The most reliable test for any url encoder decoder java implementation is encoding a value and immediately decoding it, then asserting equality with the original. If this test fails, the implementation is fundamentally broken.

- **Check for double encoding before encoding.** Detect existing percent sequences with a regex check before encoding to prevent `%20` from becoming `%2520`. This is especially important when processing URLs from external sources that may already be partially encoded.

## Where to Go Next

Explore `java.net.URI` for constructing URIs with proper per-component encoding — its multi-argument constructor handles scheme, host, path, and query encoding separately, which is more correct than manual `URLEncoder` usage. For applications making HTTP requests, libraries like `java.net.http.HttpClient` (Java 11+) and Apache HttpClient handle parameter encoding automatically through their request builder APIs. To handle binary data in URLs, study `java.util.Base64` for encoding byte arrays into URL-safe Base64 strings using `Base64.getUrlEncoder()`. Once your URLs are correctly encoded, see [what is a REST API in Java](/languages/java/rest-api/) for how to integrate them into a full HTTP client workflow. For handling the JSON payloads those requests return, [JSON parsing in Java with Jackson](/languages/java/json-parse/) is the standard approach.
