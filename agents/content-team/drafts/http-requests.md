---
actual_word_count: 933
concept: http-requests
description: Learn how to send HTTP requests in Rust using reqwest and ureq. Includes
  working examples for GET, POST, async/sync patterns, and error handling.
difficulty: intermediate
language: rust
og_image: /og/languages/rust/http-requests.png
published_date: '2026-04-12'
related_cheatsheet: /cheatsheets/rust-async-patterns
related_posts:
- /languages/rust/async-await
- /languages/rust/error-handling
- /languages/javascript/fetch-api
related_tools:
- /tools/json-formatter
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"How to Send HTTP Requests in\
  \ Rust — Syntax, Examples & Usage\",\n  \"description\": \"Learn how to send HTTP\
  \ requests in Rust using reqwest and ureq. Includes working examples for GET, POST,\
  \ async/sync patterns, and error handling.\",\n  \"datePublished\": \"2026-04-12\"\
  ,\n  \"author\": {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"\
  },\n  \"url\": \"https://devnook.dev//\"\n}\n</script>"
tags:
- rust
- http
- reqwest
- async
- web-development
template_id: lang-v3
title: How to Send HTTP Requests in Rust — Syntax, Examples & Usage
---

Rust sends HTTP requests using external crates like `reqwest` (async-first) or `ureq` (blocking). This guide shows you how to send HTTP requests in Rust with practical, production-ready examples covering GET, POST, error handling, and authentication.

## Syntax at a Glance

```rust
use reqwest;

#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
    // Send a GET request and read response as text
    let response = reqwest::get("https://api.example.com/data")
        .await?
        .text()
        .await?;
    
    println!("{}", response);
    Ok(())
}
```

This example uses `reqwest`, the most popular HTTP client for Rust. The `.await?` pattern handles both async execution and error propagation. You need an async runtime like `tokio` to run async HTTP requests.

## Full Working Examples

**Example 1 — Simple GET Request with JSON Response**

```rust
use reqwest;
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct User {
    id: u32,
    name: String,
    email: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let user: User = reqwest::get("https://api.example.com/users/1")
        .await?
        .json()
        .await?;
    
    println!("User: {:?}", user);
    Ok(())
}
```

The `.json()` method deserializes the response directly into a struct. You need `serde` for this to work — add `serde = { version = "1.0", features = ["derive"] }` to your `Cargo.toml`.

**Example 2 — POST Request with Form Data**

```rust
use reqwest;
use std::collections::HashMap;

#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
    let client = reqwest::Client::new();
    
    let mut form = HashMap::new();
    form.insert("username", "alice");
    form.insert("password", "secret123");
    
    let response = client
        .post("https://api.example.com/login")
        .form(&form)
        .send()
        .await?;
    
    println!("Status: {}", response.status());
    println!("Body: {}", response.text().await?);
    Ok(())
}
```

Using `Client::new()` lets you configure timeouts, headers, and middleware once, then reuse the client for multiple requests. The `.form()` method automatically sets `Content-Type: application/x-www-form-urlencoded`.

**Example 3 — Authenticated Request with Custom Headers**

```rust
use reqwest::{Client, header};
use serde_json::json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()?;
    
    let payload = json!({
        "title": "New Post",
        "content": "This is a test post",
        "published": true
    });
    
    let response = client
        .post("https://api.example.com/posts")
        .header(header::AUTHORIZATION, "Bearer YOUR_TOKEN_HERE")
        .header(header::CONTENT_TYPE, "application/json")
        .json(&payload)
        .send()
        .await?;
    
    if response.status().is_success() {
        let created_post: serde_json::Value = response.json().await?;
        println!("Created: {}", created_post);
    } else {
        eprintln!("Error: {}", response.status());
    }
    
    Ok(())
}
```

This pattern is production-ready. The timeout prevents hanging requests, bearer token authentication is standard for REST APIs, and checking `is_success()` before parsing prevents panics on error responses.

## Key Rules in Rust

- **You need an async runtime** — `reqwest` requires `tokio` or `async-std`. Add `tokio = { version = "1", features = ["full"] }` to `Cargo.toml`.
- **Error handling is explicit** — HTTP requests return `Result<Response, Error>`. Use `?` for propagation or `match` for custom handling.
- **Response bodies are consumed** — calling `.text()` or `.json()` consumes the response. You cannot read it twice without cloning.
- **Client reuse is recommended** — creating a new `Client` for each request is inefficient. Build one client and reuse it (connection pooling is automatic).
- **Blocking alternatives exist** — if you cannot use async, `ureq` provides a synchronous API with similar ergonomics.
- **TLS is included by default** — `reqwest` uses `rustls` by default (pure Rust TLS). Switch to `native-tls` feature if you need system OpenSSL.

## Common Patterns

**Pattern: Reusable Client with Base URL**

```rust
use reqwest::{Client, Url};

struct ApiClient {
    client: Client,
    base_url: Url,
}

impl ApiClient {
    fn new(base_url: &str) -> Result<Self, Box<dyn std::error::Error>> {
        Ok(Self {
            client: Client::new(),
            base_url: Url::parse(base_url)?,
        })
    }
    
    async fn get_user(&self, id: u32) -> Result<String, reqwest::Error> {
        let url = self.base_url.join(&format!("users/{}", id)).unwrap();
        self.client.get(url).send().await?.text().await
    }
}
```

This pattern centralizes configuration and prevents hardcoding URLs throughout your codebase. The `Url::join()` method safely constructs endpoint paths.

**Pattern: Retry with Exponential Backoff**

```rust
use reqwest::Client;
use std::time::Duration;

async fn fetch_with_retry(url: &str, max_retries: u32) -> Result<String, reqwest::Error> {
    let client = Client::new();
    let mut delay = Duration::from_millis(100);
    
    for attempt in 0..max_retries {
        match client.get(url).send().await {
            Ok(response) => return response.text().await,
            Err(e) if attempt < max_retries - 1 => {
                tokio::time::sleep(delay).await;
                delay *= 2; // exponential backoff
            }
            Err(e) => return Err(e),
        }
    }
    unreachable!()
}
```

Use this when calling flaky APIs or services with rate limits. The exponential backoff prevents overwhelming the server during recovery.

## When Not to Use HTTP Requests

Do not use HTTP requests for local inter-process communication when performance matters — use Unix sockets, named pipes, or gRPC instead. For high-frequency microservice communication, consider message queues like RabbitMQ or streaming platforms like Kafka. HTTP adds latency and overhead that specialized protocols avoid.

If you need bidirectional streaming or persistent connections, WebSockets (`tokio-tungstenite`) or Server-Sent Events are better choices than polling with HTTP requests. For server-to-server communication within a data center, HTTP/2 with `h2` or `tonic` (gRPC) provides better performance than HTTP/1.1.

## Quick Comparison: Rust vs JavaScript

| Feature | Rust (reqwest) | JavaScript (fetch) |
|---|---|---|
| Async model | `async/await` with explicit runtime | `async/await` built into runtime |
| Error handling | `Result<T, E>` with `?` operator | `try/catch` or `.catch()` |
| JSON parsing | `.json::<T>()` with type checking | `.json()` returns `Promise<any>` |
| Default behavior | No automatic redirects (opt-in) | Follows redirects by default |
| Streaming | Manual with `.bytes_stream()` | `.body.getReader()` |

Rust requires explicit error handling at every step, while JavaScript lets errors bubble. Rust's type system catches JSON schema mismatches at compile time — JavaScript only fails at runtime. For production systems, Rust's explicitness prevents entire classes of bugs that JavaScript developers encounter after deployment.

## Related

Learn more about async programming in Rust with our guide to [async/await patterns in Rust](/languages/rust/async-await). For robust production code, see our post on [error handling in Rust](/languages/rust/error-handling). Compare Rust's approach with [JavaScript's Fetch API](/languages/javascript/fetch-api) to understand the tradeoffs between type safety and developer ergonomics.