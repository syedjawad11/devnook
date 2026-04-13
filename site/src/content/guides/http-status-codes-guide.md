---
related_content: []
actual_word_count: 2336
category: guides
description: Every HTTP status code explained with real-world examples. Bookmark this
  as your definitive HTTP reference for debugging and API development.
og_image: /og/guides/http-status-codes-guide.png
published_date: '2026-04-13'
related_cheatsheet: /cheatsheets/http-status-codes
related_posts:
- /guides/what-is-rest-api
- /guides/http-methods-explained
- /blog/debugging-api-errors
related_tools:
- /tools/http-request-tester
- /tools/curl-command-builder
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"Article\",\n  \"headline\": \"HTTP Status Codes: Complete Reference\
  \ (200, 301, 404, 500...)\",\n  \"description\": \"Every HTTP status code explained\
  \ with real-world examples. Bookmark this as your definitive HTTP reference for\
  \ debugging and API development.\",\n  \"datePublished\": \"2026-04-13\",\n  \"\
  author\": {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"\
  },\n  \"url\": \"https://devnook.dev/guides/\"\n}\n</script>"
tags:
- http
- status-codes
- web-development
- api
- reference
template_id: guide-v4
title: 'HTTP Status Codes: Complete Reference (200, 301, 404, 500...)'
---

HTTP status codes tell you what happened with an HTTP request. Every response from a web server includes a three-digit code that indicates success, failure, or a required action. This reference covers all standard HTTP status codes with practical explanations for when you'll encounter them.

## Overview

HTTP status codes are three-digit numbers grouped into five classes by their first digit. The classes are: 1xx (informational), 2xx (success), 3xx (redirection), 4xx (client errors), and 5xx (server errors). When you make an HTTP request — whether through a browser, API call, or [curl command](/tools/curl-command-builder) — the server responds with one of these codes to indicate what happened.

Understanding status codes is essential for debugging web applications, building APIs, and interpreting server logs. The code itself is standardized, but servers can customize the accompanying message. A 404 response always means "Not Found" regardless of whether the message says "Page not found" or "Resource does not exist."

## 1xx Informational

These codes indicate that the server received the request and is continuing to process it. Most developers rarely see these in practice because they're interim responses.

| Code | Name | Meaning |
|------|------|---------|
| 100 | Continue | Server received request headers, client should send request body |
| 101 | Switching Protocols | Server is switching to protocol requested in Upgrade header |
| 102 | Processing | Server received and is processing request, no response yet (WebDAV) |
| 103 | Early Hints | Used with Link headers to preload resources while server prepares response |

## 2xx Success

Success codes confirm the request was received, understood, and accepted. These are the codes you want to see.

| Code | Name | Meaning |
|------|------|---------|
| 200 | OK | Request succeeded, response contains requested data |
| 201 | Created | Request succeeded and created a new resource |
| 202 | Accepted | Request accepted for processing, but processing not complete |
| 203 | Non-Authoritative Information | Response from transforming proxy, not origin server |
| 204 | No Content | Request succeeded, no content to send back |
| 205 | Reset Content | Request succeeded, client should reset document view |
| 206 | Partial Content | Server delivering partial resource due to Range header |
| 207 | Multi-Status | Multiple status codes for multiple operations (WebDAV) |
| 208 | Already Reported | Members already enumerated in previous response (WebDAV) |
| 226 | IM Used | Server fulfilled GET request with instance manipulations applied |

## 3xx Redirection

Redirection codes indicate the client must take additional action to complete the request. The new location is typically in the `Location` header.

| Code | Name | Meaning |
|------|------|---------|
| 300 | Multiple Choices | Multiple options for resource, client should choose one |
| 301 | Moved Permanently | Resource permanently moved to new URL, update bookmarks |
| 302 | Found | Resource temporarily at different URL, use original for future requests |
| 303 | See Other | Response found at different URL using GET, regardless of original method |
| 304 | Not Modified | Cached version is still valid, no need to retransmit |
| 305 | Use Proxy | Resource must be accessed through proxy specified in Location |
| 307 | Temporary Redirect | Resource temporarily at different URL, use same method when following |
| 308 | Permanent Redirect | Resource permanently moved, use same method when following |

## 4xx Client Errors

Client error codes indicate the request contains bad syntax or cannot be fulfilled. The problem is on the client side — fix the request and try again.

| Code | Name | Meaning |
|------|------|---------|
| 400 | Bad Request | Server cannot process request due to client error (malformed syntax) |
| 401 | Unauthorized | Authentication required and failed or not provided |
| 402 | Payment Required | Reserved for future use in payment systems |
| 403 | Forbidden | Server understood request but refuses to authorize it |
| 404 | Not Found | Server cannot find requested resource |
| 405 | Method Not Allowed | Request method not supported for target resource |
| 406 | Not Acceptable | Resource cannot generate content matching Accept headers |
| 407 | Proxy Authentication Required | Client must authenticate with proxy first |
| 408 | Request Timeout | Server timed out waiting for request |
| 409 | Conflict | Request conflicts with current state of server |
| 410 | Gone | Resource permanently deleted, no forwarding address |
| 411 | Length Required | Server requires Content-Length header |
| 412 | Precondition Failed | One or more conditions in request headers evaluated false |
| 413 | Payload Too Large | Request entity larger than server limits |
| 414 | URI Too Long | Request URI longer than server can process |
| 415 | Unsupported Media Type | Request payload format not supported |
| 416 | Range Not Satisfiable | Range header cannot be satisfied |
| 417 | Expectation Failed | Expectation in Expect header cannot be met |
| 418 | I'm a teapot | Server refuses to brew coffee with teapot (April Fools' joke, RFC 2324) |
| 421 | Misdirected Request | Request directed at server unable to produce response |
| 422 | Unprocessable Entity | Request well-formed but contains semantic errors (WebDAV) |
| 423 | Locked | Resource being accessed is locked (WebDAV) |
| 424 | Failed Dependency | Request failed due to previous request failure (WebDAV) |
| 425 | Too Early | Server unwilling to process request that might be replayed |
| 426 | Upgrade Required | Client should switch to different protocol |
| 428 | Precondition Required | Server requires request to be conditional |
| 429 | Too Many Requests | Client sent too many requests in given timeframe (rate limiting) |
| 431 | Request Header Fields Too Large | Header fields too large to process |
| 451 | Unavailable For Legal Reasons | Resource unavailable due to legal demand |

## 5xx Server Errors

Server error codes indicate the server failed to fulfill a valid request. The problem is on the server side, not the client.

| Code | Name | Meaning |
|------|------|---------|
| 500 | Internal Server Error | Generic error when server encounters unexpected condition |
| 501 | Not Implemented | Server does not support functionality required to fulfill request |
| 502 | Bad Gateway | Server acting as gateway received invalid response from upstream |
| 503 | Service Unavailable | Server temporarily unable to handle request (overload or maintenance) |
| 504 | Gateway Timeout | Server acting as gateway did not receive timely response from upstream |
| 505 | HTTP Version Not Supported | Server does not support HTTP version used in request |
| 506 | Variant Also Negotiates | Server has internal configuration error |
| 507 | Insufficient Storage | Server unable to store representation needed to complete request (WebDAV) |
| 508 | Loop Detected | Server detected infinite loop while processing request (WebDAV) |
| 510 | Not Extended | Further extensions required for server to fulfill request |
| 511 | Network Authentication Required | Client needs to authenticate to gain network access |

## The Most Important Ones

**200 OK** — The universal success code. Your request worked and the server is sending you the data you asked for. When building APIs, this is your default response for successful GET requests. For POST requests that don't create resources, 200 is appropriate when you're returning data about the operation.

**201 Created** — Use this instead of 200 when a POST or PUT request successfully creates a new resource. Include a `Location` header pointing to the new resource. This tells the client exactly where to find what they just created, which is particularly useful for [REST API design](/guides/what-is-rest-api).

**301 Moved Permanently** — The resource has a new permanent home. Search engines transfer SEO value to the new URL when they see this. Browsers cache 301 redirects aggressively, so only use this when you're certain the move is permanent. If you might move it back, use 302 or 307 instead.

**400 Bad Request** — The request is malformed. This usually means invalid JSON syntax, missing required fields, or parameters in the wrong format. When you see this, check your request payload carefully. The response body should explain what's wrong, but many servers don't provide helpful details.

**401 Unauthorized** — Authentication failed or wasn't provided. Despite the name, this code actually means "unauthenticated" — you didn't prove who you are. Check your authentication headers, tokens, or API keys. The `WWW-Authenticate` header in the response tells you what authentication method the server expects.

**403 Forbidden** — You authenticated successfully, but you don't have permission to access this resource. Retrying with the same credentials won't help. This is a permissions issue, not an authentication issue. Check if your user account has the right roles or if the resource has access restrictions.

**404 Not Found** — The classic "page not found" error. The server cannot find the requested resource at this URL. Either the URL is wrong, the resource was deleted, or it never existed. When building APIs, use 404 for missing resources but 400 for invalid resource identifiers in the URL path.

**429 Too Many Requests** — You're being rate-limited. The server is rejecting your requests because you've made too many in a short time. Check the `Retry-After` header to see when you can try again. Implement exponential backoff in your client code to handle this gracefully.

**500 Internal Server Error** — Something broke on the server. This is a catch-all for unexpected server-side errors. The server encountered a condition it didn't know how to handle. Check server logs for details. If you're seeing this as a client, there's nothing you can do except report it or try again later.

**502 Bad Gateway** — The server is acting as a proxy or gateway and received an invalid response from an upstream server. This often happens when a load balancer can't reach application servers, or when an API gateway gets garbage back from a microservice. Check connectivity between servers.

**503 Service Unavailable** — The server is temporarily unable to handle requests. This usually means the server is overloaded, down for maintenance, or out of resources. Unlike 500 errors, this explicitly says "try again later." The `Retry-After` header may specify when to retry.

## Common Questions

**What's the difference between 401 and 403?**
401 means you need to authenticate — you didn't provide credentials or they were invalid. 403 means you authenticated successfully but lack permission to access the resource. With 401, providing valid credentials might work. With 403, authentication isn't the issue — authorization is.

**Should I use 302 or 307 for temporary redirects?**
Use 307. Both indicate temporary redirects, but 302 allows browsers to change POST requests to GET when following the redirect. 307 guarantees the browser uses the same HTTP method. For modern applications, 307 is the safer choice and avoids subtle bugs.

**When should I return 204 instead of 200?**
Return 204 when the request succeeded but there's no content to send back. DELETE requests commonly return 204 to confirm deletion without sending the deleted resource. PUT requests that update existing resources sometimes use 204 when the client doesn't need the updated representation.

**What does 422 Unprocessable Entity mean?**
The request was well-formed (valid JSON, correct headers) but contains semantic errors. For example, creating a user with an email that's already taken, or a date range where the end date comes before the start date. The syntax is fine but the business logic rejects it.

**Why do I see 304 Not Modified in my browser?**
The server is telling your browser that the cached version of the resource is still valid. This saves bandwidth — the server doesn't resend data you already have. It works by comparing timestamps or ETags between your cached version and the server's current version.

## Debugging with Status Codes

When debugging HTTP issues, start by identifying which class the status code belongs to. A 4xx code means fix your request — check parameters, authentication, and payload format. A 5xx code means the server has a problem — check server logs, connectivity, and upstream dependencies.

Modern browser developer tools show status codes in the Network tab. For API development, tools like our [HTTP request tester](/tools/http-request-tester) let you inspect full request-response cycles including headers and timing information.

Here's a basic example of checking status codes in JavaScript:

```javascript
async function fetchWithErrorHandling(url) {
  const response = await fetch(url);
  
  if (response.status >= 200 && response.status < 300) {
    return await response.json();
  }
  
  if (response.status === 404) {
    throw new Error('Resource not found');
  }
  
  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    throw new Error(`Rate limited. Retry after ${retryAfter} seconds`);
  }
  
  if (response.status >= 500) {
    throw new Error('Server error. Try again later');
  }
  
  throw new Error(`Request failed with status ${response.status}`);
}
```

And in Python with requests:

```python
import requests
from requests.exceptions import HTTPError

def fetch_with_error_handling(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx
        return response.json()
    except HTTPError as e:
        status = e.response.status_code
        
        if status == 404:
            raise ValueError("Resource not found")
        elif status == 429:
            retry_after = e.response.headers.get('Retry-After', 'unknown')
            raise ValueError(f"Rate limited. Retry after {retry_after} seconds")
        elif status >= 500:
            raise ValueError("Server error. Try again later")
        else:
            raise ValueError(f"Request failed with status {status}")
```

## Related

For a quick lookup table without explanations, see our [HTTP Status Codes Cheat Sheet](/cheatsheets/http-status-codes). If you're building APIs, read our guide on [HTTP Methods Explained](/guides/http-methods-explained) to understand how GET, POST, PUT, and DELETE interact with status codes. For hands-on testing, use our [HTTP Request Tester](/tools/http-request-tester) to send requests and inspect full responses including status codes and headers.