---
title: "HTTP Headers Guide: CORS, Caching, Content-Type"
description: "HTTP vs HTTPS headers explained: master CORS, cache-control, content-type negotiation, and authorization patterns used in real-world web applications."
category: guides
subcategory: "Web Concepts"
template_id: guide-v2
tags: [http-headers, cors, caching, content-type, authorization]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-07-07"
og_image: "/og/guides/http-headers-guide.png"
actual_word_count: 3231
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["Article", "FAQPage"],
    "headline": "HTTP Headers Guide: CORS, Caching, Content-Type",
    "description": "HTTP vs HTTPS headers explained: master CORS, cache-control, content-type negotiation, and authorization patterns used in real-world web applications.",
    "datePublished": "2026-07-07",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/guides/http-headers-guide/",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between HTTP and HTTPS headers?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "HTTP and HTTPS use the same header format. HTTPS wraps the connection in TLS, encrypting headers and body in transit. This enables security-specific headers like Strict-Transport-Security that browsers only honour over a secure connection."
        }
      },
      {
        "@type": "Question",
        "name": "What headers do I need to set for CORS?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Every cross-origin response needs Access-Control-Allow-Origin set to the requesting origin. For authenticated requests add Access-Control-Allow-Credentials: true with an explicit origin. Non-simple requests need an OPTIONS preflight response with Access-Control-Allow-Methods and Access-Control-Allow-Headers."
        }
      },
      {
        "@type": "Question",
        "name": "What is the difference between no-cache and no-store in Cache-Control?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "no-store prevents the response from being stored anywhere — every request fetches fresh from the origin. no-cache allows caches to store the response but requires revalidation with the server before serving. Use no-store for sensitive data, no-cache when freshness checks are acceptable."
        }
      }
    ]
  }
  </script>
---

HTTP headers run quietly beneath every web interaction, shaping what browsers cache, which origins can read your API responses, and how clients know what format your server is sending. Whether your application speaks HTTP or HTTPS, the header mechanism is identical — TLS encrypts the transport, but the headers themselves are the same key-value pairs in both protocols.

This guide covers the four header categories developers interact with most: CORS, caching, Content-Type, and Authorization. HTTP status codes have [their own reference](/guides/http-status-codes-guide/); this guide stays on headers.

## HTTP vs HTTPS: What Changes in the Header Layer

The HTTP vs HTTPS distinction is often reduced to "one is encrypted, one isn't" — which is accurate but leaves out the specific consequence for headers.

HTTP/1.1 and HTTPS use the same wire format: `Header-Name: value\r\n`. Under HTTPS, TLS wraps the entire TCP stream, so both headers and body are encrypted in transit. An attacker conducting a man-in-the-middle attack on a plain HTTP connection can read and modify headers, including `Authorization` tokens and `Cookie` values. Over HTTPS they can see only the hostname (from TLS SNI) and the approximate response size.

That transport difference unlocks a set of headers that only work over HTTPS. `Strict-Transport-Security` (HSTS) tells browsers to refuse plain-HTTP connections to your domain for a set duration — but browsers only honour it when received via HTTPS. Cookie attributes like `Secure` and `SameSite=None` also require HTTPS; without it, the `Secure` flag is silently ignored in many browsers. If security headers you've configured don't appear to take effect, verify that the entire connection — including any load balancers or reverse proxies in front of your application — is HTTPS end-to-end and not just between client and proxy.

HTTP/2 introduced structural changes to how headers travel on the wire. Header names are always lowercase in HTTP/2 frames (`content-type`, not `Content-Type`), and the HPACK compression algorithm reduces header overhead across connections. Application code rarely sees this directly — HTTP frameworks normalise header names — but it explains why HTTP header names are specified as case-insensitive by the HTTP/1.1 spec, and why tooling sometimes shows lowercase names even when your code sent mixed-case ones.

One practical consequence: header name case is not a safe signal for detecting protocol version. Always treat header names as case-insensitive in parsing code; any comparison should use `.toLowerCase()` or equivalent.

## The Anatomy of an HTTP Header

Each header is a name-value pair separated by a colon and a space. Request headers travel from client to server; response headers travel back. Some headers, like `Content-Type`, appear in both directions with different meanings.

A browser making an authenticated JSON API call sends something like this:

```http
GET /api/users/42 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
Origin: https://app.example.com
```

The server responds:

```http
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Cache-Control: private, max-age=300
Access-Control-Allow-Origin: https://app.example.com
ETag: "d4e5f6a7b8c9"
```

The `Host` header is mandatory in HTTP/1.1 — it routes requests when multiple virtual hosts share an IP. `Accept` declares what response formats the client handles. `Content-Type` on the response describes what the body actually is.

Header names are case-insensitive by spec. `content-type`, `Content-Type`, and `CONTENT-TYPE` all refer to the same header. Values are case-sensitive unless a specific header's spec says otherwise.

To inspect what headers your server sends in production, use [curl with the `-I` or `-v` flag](/guides/curl-command-guide/). The `-I` flag sends a HEAD request and shows response headers; `-v` shows the full request-response exchange including request headers and TLS handshake information.

## CORS Headers: Cross-Origin Resource Sharing

CORS is what happens when the browser's same-origin policy meets the reality that frontends and APIs often live on different domains. The same-origin policy prevents JavaScript from reading responses from a different origin — different scheme, host, or port — unless the server explicitly permits it via response headers.

### The Basic CORS Exchange

When JavaScript at `https://app.example.com` fetches `https://api.example.com/data`, the browser automatically adds an `Origin` header:

```http
GET /data HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
```

The server must respond with `Access-Control-Allow-Origin` for the browser to let the script read the response body:

```http
Access-Control-Allow-Origin: https://app.example.com
```

Setting `Access-Control-Allow-Origin: *` opens the endpoint to any origin — appropriate for public, unauthenticated APIs but never for endpoints that accept `Authorization` headers or session cookies. For credentialed requests, you need an explicit origin and:

```http
Access-Control-Allow-Credentials: true
```

Combining `Access-Control-Allow-Origin: *` with `Access-Control-Allow-Credentials: true` is invalid — browsers reject it. Use an explicit origin whenever credentials are involved.

See the [MDN CORS documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) for the complete list of request types and how the browser evaluates each.

### Preflight Requests

"Simple" requests — GET, HEAD, and POST with standard Content-Type values — skip a preflight check. Everything else triggers an automatic OPTIONS preflight before the real request:

```http
OPTIONS /api/data HTTP/1.1
Host: api.example.com
Origin: https://app.example.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: Authorization, X-Correlation-Id
```

The server must respond with permission headers:

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, X-Correlation-Id
Access-Control-Max-Age: 86400
```

`Access-Control-Max-Age` caches the preflight result — the browser skips the OPTIONS check for the same method/headers combination for 86400 seconds (one day). Without it, the browser preflights every non-simple request, doubling round trips for DELETE, PUT, and PATCH calls.

### Securing the Origin Allowlist

Reflecting the incoming `Origin` header back verbatim without validation is a common mistake:

```javascript
// Dangerous — echoes any origin including attacker-controlled ones
res.setHeader('Access-Control-Allow-Origin', req.headers.origin);
```

This effectively grants any origin the same access as `*` but also enables credentials. The correct pattern checks against an explicit allowlist:

```javascript
const ALLOWED_ORIGINS = ['https://app.example.com', 'https://admin.example.com'];

const origin = req.headers.origin;
if (ALLOWED_ORIGINS.includes(origin)) {
  res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Vary', 'Origin');
}
```

The `Vary: Origin` header tells CDNs and shared caches that responses differ by origin, preventing a CORS response cached for one origin from being served to a different one.

## Caching Headers: Cache-Control, ETag, and Revalidation

Caching headers tell browsers, CDNs, and proxies what they can store, for how long, and when to fetch a fresh copy. Correct cache headers reduce server load, speed up page loads, and make CDN behaviour predictable.

### Cache-Control Directives

`Cache-Control` is the primary caching directive in HTTP/1.1. Its value is a comma-separated list. See the [MDN Cache-Control reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control) for the full list; the most commonly used directives are:

| Directive | Effect |
|-----------|--------|
| `public` | Any cache may store this (browsers, CDNs, shared proxies) |
| `private` | Only the user's browser cache may store it — not shared caches |
| `no-store` | Do not store the response anywhere; always fetch from origin |
| `no-cache` | Cache it, but revalidate with the server before serving |
| `max-age=N` | Response is fresh for N seconds from when it was generated |
| `s-maxage=N` | Like `max-age` but only for shared caches; overrides `max-age` for CDNs |
| `must-revalidate` | Once stale, do not serve without revalidating — even if the server is unreachable |
| `stale-while-revalidate=N` | Serve stale content for N seconds while fetching an update in the background |
| `immutable` | This resource will not change; skip revalidation even after `max-age` expires |

**Static assets with content hashes** — like `main.a3c8f1.js` from a build tool — should use `public, max-age=31536000, immutable`. The hash changes whenever the file changes, so the URL is effectively versioned and a year-long cache is safe. Browsers never revalidate immutable assets before expiry, which eliminates unnecessary conditional requests.

**HTML documents** should use `no-cache` or `max-age=0, must-revalidate`. You want browsers to check for a new HTML file on every visit — it may reference new asset hashes — but you allow them to store it locally and verify freshness cheaply with a conditional request rather than re-downloading the full document.

**User-specific API responses** should use `private, no-store` to prevent shared caches from leaking one user's data to another.

### ETag and Conditional Requests

An ETag is a fingerprint the server assigns to a version of a resource:

```http
HTTP/1.1 200 OK
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Cache-Control: no-cache
Content-Type: application/json
```

On subsequent requests, the client sends the cached ETag in `If-None-Match`:

```http
GET /api/posts/5 HTTP/1.1
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
```

If the resource hasn't changed, the server responds with `304 Not Modified` and no body — saving the bandwidth of re-sending the full payload. The client uses its cached copy. If the resource changed, the server sends the new version with a new ETag.

`Last-Modified` / `If-Modified-Since` works the same way but uses a timestamp instead of a hash. ETags are more reliable in practice. Timestamps have one-second resolution and can vary across server instances behind a load balancer — two instances may report slightly different `Last-Modified` values for the same file. ETags derived from content hashes are deterministic regardless of which server generates the response.

## Content-Type and Content Negotiation

`Content-Type` announces the format of the message body. Mismatched or missing Content-Type values cause a disproportionate share of API integration bugs, typically appearing as unexpected parse errors on the receiving end.

### What the Header Contains

```http
Content-Type: application/json; charset=utf-8
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryABCD1234
Content-Type: text/plain; charset=iso-8859-1
Content-Type: application/octet-stream
```

The MIME type before the semicolon identifies the format. Parameters after it provide decoding instructions — `charset` for text types, `boundary` for multipart bodies. For JSON, the charset is always UTF-8 per RFC 8259. Stating it explicitly (`; charset=utf-8`) avoids parsing ambiguity in older or non-compliant clients.

### In Requests vs Responses

In **requests**, `Content-Type` describes what the client is sending. POST and PUT requests with a body should always include it. GET, HEAD, and DELETE requests typically have no body, so they don't need the header.

In **responses**, `Content-Type` describes what the server is returning. Set it explicitly on every response — never leave it absent and rely on browser content-sniffing. Without a declared Content-Type, some browsers guess the format based on the body bytes, which can lead them to execute JavaScript served as `text/plain`. The `X-Content-Type-Options: nosniff` response header instructs browsers not to override the declared type.

### Accept and Content Negotiation

The `Accept` request header lets clients express preferences among response formats:

```http
Accept: application/json;q=1.0, text/html;q=0.8, */*;q=0.1
```

The `q` value is a quality factor from 0 to 1 — higher means more preferred. Servers that support negotiation pick the highest-priority format they can produce and set the corresponding `Content-Type` on the response. If no acceptable format is available, the server returns `406 Not Acceptable`.

Most REST APIs ignore `Accept` and always return JSON, which is fine. Frameworks that serve both HTML and API responses from the same routes — Rails, Django REST Framework — use `Accept` to dispatch to the right renderer.

For file uploads, `Content-Type: multipart/form-data` splits the body into named parts. Each part has its own `Content-Disposition` naming the field and optional filename:

```http
Content-Disposition: form-data; name="avatar"; filename="photo.jpg"
Content-Type: image/jpeg
```

## Authorization Headers: Basic, Bearer, and API Keys

The `Authorization` request header carries credentials. Its general format is:

```http
Authorization: <scheme> <credentials>
```

The scheme identifies the credential type; the rest of the value is scheme-specific.

### Basic Authentication

Basic auth Base64-encodes `username:password`:

```http
Authorization: Basic dXNlcjpwYXNzd29yZA==
```

The encoding is trivially reversible — Base64 is not encryption. Basic auth is only acceptable over HTTPS, and even then most new systems avoid it. The credentials are sent on every request, there is no expiry mechanism, and revocation requires a password change.

### Bearer Tokens (JWT)

Bearer tokens are the dominant mechanism for stateless API authentication:

```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

Most Bearer tokens in modern APIs are JWTs (JSON Web Tokens). A JWT has three Base64Url-encoded segments separated by dots: a header specifying the signing algorithm, a payload containing claims (user ID, expiry timestamp, scopes), and a cryptographic signature. The server verifies the signature and checks the expiry before accepting the token. The client never needs to verify — it just presents the opaque string on every request.

To inspect a JWT's payload without writing decoding code, paste it into the [JWT Decoder tool](/tools/jwt-decoder/) — the claims become readable JSON in the browser.

JWTs are stateless: the server needs no session store. The tradeoff is that revoking a token before expiry requires either very short expiry times or maintaining a server-side blocklist of revoked token IDs.

### API Keys

API keys appear in one of two header positions depending on the provider:

```http
Authorization: ApiKey sk_live_abc123def456
X-API-Key: sk_live_abc123def456
```

There is no universal convention — check the API's documentation. API keys don't expire automatically, which requires active key management: rotate them on a schedule and revoke immediately on exposure. For [API rate limiting](/guides/api-rate-limiting-guide/) responses, look for `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After` response headers, which signal your current usage against the limit and how long to wait before retrying.

### WWW-Authenticate and Challenge Responses

When a server rejects a request due to missing or invalid credentials, it includes `WWW-Authenticate` to tell the client which scheme to use:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="api.example.com", error="invalid_token", error_description="The access token expired"
```

This header is how OAuth 2.0-compliant servers communicate authentication errors to clients, enabling automated token-refresh logic. Clients that parse `WWW-Authenticate` can distinguish between "no token provided", "token expired", and "token invalid" and handle each case differently.

## Security Headers Worth Setting

Beyond CORS, several response headers directly improve browser security with minimal configuration cost.

### Strict-Transport-Security (HSTS)

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

Once a browser receives this header over HTTPS, it refuses plain-HTTP connections to that domain for the duration of `max-age`. It upgrades HTTP URLs to HTTPS locally before sending a request — no server round trip required. `includeSubDomains` extends the rule to all subdomains. `preload` adds your domain to the browser's built-in HSTS preload list, enforcing HTTPS even on a user's first visit before they've ever received the header. Submission to the preload list is a one-way commitment — research the requirements at [hstspreload.org](https://hstspreload.org) before adding it.

### X-Content-Type-Options

```http
X-Content-Type-Options: nosniff
```

Prevents browsers from MIME-sniffing a response away from the declared `Content-Type`. Without it, a browser might execute a JavaScript file served as `text/plain` if the content looks like JavaScript — a stored XSS vector via user-uploaded content. One header, zero logic.

### Content-Security-Policy

CSP restricts which origins can load scripts, styles, fonts, frames, and other subresources:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.example.com; img-src *; object-src 'none'
```

A strict CSP is among the most effective mitigations for cross-site scripting. The recommended starting point is `default-src 'none'` — block everything — then add specific sources as your application requires them. The browser blocks any resource not explicitly permitted, regardless of what an injected script attempts to load.

### Referrer-Policy

```http
Referrer-Policy: strict-origin-when-cross-origin
```

Controls how much of the current page URL appears in the `Referer` header on outgoing requests. `strict-origin-when-cross-origin` sends the full URL for same-origin navigations and only the origin (no path or query string) for cross-origin ones. This prevents URL parameters — session IDs, search queries, internal route structures — from leaking to third-party analytics or CDN providers included on your page.

For context on how HTTP headers enable protocol upgrades, [WebSockets vs HTTP](/blog/websockets-vs-http/) covers the `Upgrade` and `Connection` headers that initiate the WebSocket handshake from a plain HTTP connection.

## Frequently Asked Questions

### What is the difference between HTTP and HTTPS headers?

HTTP and HTTPS use the same header syntax and the same header names. The difference is transport: HTTPS wraps the connection in TLS, encrypting both headers and body in transit. This protects `Authorization` tokens and `Cookie` values from network interception. HTTPS also enables security-specific headers like `Strict-Transport-Security` that browsers only honour when received over a secure connection.

### What headers do I need to set for CORS?

At minimum, every cross-origin response needs `Access-Control-Allow-Origin` set to the requesting origin or `*` for public APIs. For authenticated requests, add `Access-Control-Allow-Credentials: true` with an explicit origin — the wildcard and credentials combination is rejected by browsers. Non-simple requests (DELETE, PUT, custom headers) trigger a preflight that requires `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers` in an OPTIONS response.

### What is the difference between `no-cache` and `no-store` in Cache-Control?

`no-store` prevents the response from being stored anywhere — every request fetches fresh from the origin server. `no-cache` allows caches to store the response but requires them to revalidate with the server before serving it (typically via an ETag or `Last-Modified` check). Use `no-store` for responses containing sensitive data that must never persist in a cache. Use `no-cache` when you want caching infrastructure to hold a local copy but always verify freshness first.

### How should I send API credentials — header or query string?

Always use the `Authorization` header. Query string parameters appear in server access logs, browser history, HTTP `Referer` headers forwarded to third parties, and any monitoring tool recording request URLs. An API key in `?api_key=sk_live_abc123` will be captured across your infrastructure and can leak to external parties. The `Authorization` header is excluded from typical access logs by default and is encrypted by TLS in transit.

## Conclusion

HTTP vs HTTPS transport differences aside, headers are where web protocol behaviour is configured at runtime. CORS headers decide which browser origins can consume your API. `Cache-Control` and ETags give precise control over what gets stored and when it expires. `Content-Type` ensures both ends parse the body correctly. `Authorization` headers carry the credentials that protect every private endpoint.

The patterns here apply regardless of stack — Node.js, Python, Go, or anything else. What changes between stacks is the API for setting headers, not the semantics. The most direct way to verify you're getting them right is to inspect your actual server responses with [curl](/guides/curl-command-guide/) and check them against these rules.
