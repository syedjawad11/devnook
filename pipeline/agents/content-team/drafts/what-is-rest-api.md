---
actual_word_count: 1887
category: guides
description: REST APIs power the modern web. Learn what REST means, how HTTP methods
  work, and how to design clean API endpoints.
og_image: /og/guides/what-is-rest-api.png
published_date: '2026-04-13'
related_cheatsheet: /cheatsheets/rest-api-design
related_posts:
- /guides/http-methods-explained
- /guides/json-vs-xml
related_tools:
- /tools/json-formatter
- /tools/api-tester
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"Article\",\n  \"headline\": \"What is a REST API? A Complete Guide\
  \ for Developers\",\n  \"description\": \"REST APIs power the modern web. Learn\
  \ what REST means, how HTTP methods work, and how to design clean API endpoints.\"\
  ,\n  \"datePublished\": \"2026-04-13\",\n  \"author\": {\"@type\": \"Organization\"\
  , \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\": \"Organization\", \"name\"\
  : \"DevNook\", \"url\": \"https://devnook.dev\"},\n  \"url\": \"https://devnook.dev/guides/\"\
  \n}\n</script>"
tags:
- rest
- api
- http
- web-architecture
template_id: guide-v1
title: What is a REST API? A Complete Guide for Developers
---

A REST API is an architectural style for building web services that uses HTTP requests to access and manipulate data.

## What is a REST API?

REST (Representational State Transfer) is an architectural pattern for designing networked applications. A REST API uses standard HTTP methods—GET, POST, PUT, DELETE—to perform operations on resources identified by URLs. When you request data from a REST API, the server sends back a representation of the resource's current state, typically as JSON or XML.

REST APIs are stateless, meaning each request contains all the information needed to process it. The server doesn't store session data between requests. This makes REST APIs scalable and reliable—any server can handle any request without needing to know what happened in previous requests.

The REST pattern solves a fundamental problem: how do different systems communicate over the web in a predictable, standardized way? Before REST became dominant, developers used complex protocols like SOAP that required extensive configuration and XML processing. REST simplified this by leveraging the HTTP protocol that already powers the web.

## A Brief History

Roy Fielding introduced REST in his 2000 doctoral dissertation while working as a principal author of the HTTP specification. He observed that the web's architecture—with its use of URIs, HTTP methods, and stateless communication—could serve as a template for building scalable distributed systems.

Before REST, most web APIs used SOAP (Simple Object Access Protocol), which required XML envelopes, strict type definitions, and complex error handling. SOAP was powerful but heavyweight. REST's simplicity and alignment with existing web standards led to rapid adoption. By the late 2000s, major platforms like Twitter, GitHub, and Stripe had built REST APIs that became the industry standard.

## How REST APIs Work

When a client needs data from a REST API, it sends an HTTP request to a specific URL (endpoint). The request includes:

1. **HTTP Method**: Indicates the operation type (GET to retrieve, POST to create, PUT to update, DELETE to remove)
2. **URL**: Identifies the resource (`https://api.example.com/users/42`)
3. **Headers**: Contain metadata like authentication tokens and content type
4. **Body**: Contains data for POST/PUT requests (optional)

The server processes the request and sends back an HTTP response containing:

1. **Status Code**: Indicates success (200), client error (400), or server error (500)
2. **Headers**: Metadata about the response
3. **Body**: The requested data or confirmation message, usually as JSON

For example, when a mobile app displays a user profile, it sends `GET /users/42` to the API. The server retrieves user 42's data from the database, formats it as JSON, and returns it with a 200 status code. The app parses the JSON and renders the profile screen.

This request-response cycle happens hundreds of times per session in modern applications. Each request is independent—the server doesn't remember previous requests from the same client.

## Key Components and Terms

**Resource** — Any data entity that can be identified by a URI. In a blogging API, resources include posts, comments, authors, and categories. Each resource has a unique endpoint.

**Endpoint** — A URL path that represents a resource or collection of resources. `/api/posts` returns all posts, while `/api/posts/15` returns a specific post.

**HTTP Method** — The verb that specifies what operation to perform. GET retrieves data, POST creates new resources, PUT updates existing resources, and DELETE removes them.

**Representation** — The format in which resource data is transmitted. JSON is the dominant format today, but REST supports XML, HTML, and other formats. The client and server negotiate the format using headers.

**Stateless** — Each request must contain all information needed to process it. The server doesn't store session data. If authentication is required, the client includes credentials (typically a token) with every request.

**Idempotent** — An operation that produces the same result when called multiple times. GET, PUT, and DELETE are idempotent—calling them repeatedly has the same effect as calling them once. POST is not idempotent.

**Status Code** — A three-digit number indicating the request outcome. 2xx means success, 3xx means redirection, 4xx means client error, and 5xx means server error.

## Real-World Examples

When you load your Twitter feed, the Twitter mobile app sends a GET request to `https://api.twitter.com/2/tweets/home_timeline`. The API returns a JSON array of tweet objects. Your app parses this data and displays each tweet with text, images, and metadata.

When you post a photo to Instagram, the app sends a POST request to an endpoint like `/api/media` with your image data and caption in the request body. The API validates the data, stores the image, creates a database record, and returns the new post's ID.

When a payment processor like Stripe charges a credit card, your server sends a POST request to `https://api.stripe.com/v1/charges` with the card token, amount, and currency. Stripe processes the payment and returns a charge object with the transaction status. Your server checks the status and updates the order accordingly.

## REST API in Practice — Code Example

Here's how a REST API handles common operations using JavaScript's fetch API:

```javascript
// GET - Retrieve a user
const getUser = async (userId) => {
  const response = await fetch(`https://api.example.com/users/${userId}`, {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer your-token-here',
      'Content-Type': 'application/json'
    }
  });
  const user = await response.json();
  return user;
};

// POST - Create a new user
const createUser = async (userData) => {
  const response = await fetch('https://api.example.com/users', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer your-token-here',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: userData.name,
      email: userData.email
    })
  });
  const newUser = await response.json();
  return newUser;
};

// PUT - Update an existing user
const updateUser = async (userId, updates) => {
  const response = await fetch(`https://api.example.com/users/${userId}`, {
    method: 'PUT',
    headers: {
      'Authorization': 'Bearer your-token-here',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  });
  const updatedUser = await response.json();
  return updatedUser;
};

// DELETE - Remove a user
const deleteUser = async (userId) => {
  const response = await fetch(`https://api.example.com/users/${userId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': 'Bearer your-token-here'
    }
  });
  return response.status === 204; // 204 = success with no content
};
```

This code demonstrates the four core HTTP methods mapped to CRUD (Create, Read, Update, Delete) operations. Each request includes an authorization header for security. The GET and POST methods return JSON data, while DELETE returns only a status code.

## Common Misconceptions

**"REST APIs must return JSON"** — While JSON is the most common format, REST is format-agnostic. The client and server negotiate the format using `Accept` and `Content-Type` headers. XML, HTML, and plain text are all valid REST responses.

**"PUT and PATCH are the same"** — PUT replaces an entire resource with new data. PATCH applies partial updates. If you PUT a user with only `{name: "Alice"}`, you might accidentally delete the email field. PATCH updates only the specified fields.

**"REST APIs need sessions or cookies"** — REST APIs are stateless by design. Authentication typically uses tokens (like JWT) sent in headers, not cookies. The server validates the token on each request without maintaining session state.

**"Any API using HTTP is RESTful"** — Many APIs claim to be REST but violate its principles. True REST APIs use resource-based URLs (`/users/42`, not `/getUser?id=42`), leverage HTTP methods correctly, and return meaningful status codes.

## REST vs GraphQL

REST and GraphQL solve the same problem—data fetching over HTTP—but with different approaches. REST exposes multiple endpoints, each returning a fixed data structure. GraphQL uses a single endpoint where clients specify exactly what data they need using a query language.

REST works well for simple, predictable data needs. GraphQL excels when clients need flexible queries or want to reduce the number of requests. REST is easier to cache and has better HTTP-level tooling. GraphQL reduces over-fetching but adds complexity to the server and requires specialized clients.

For most web applications, REST remains the simpler choice. GraphQL makes sense when you have diverse client needs or complex, nested data relationships. Many companies use both—REST for public APIs, GraphQL for internal tools.

## Designing Clean REST Endpoints

Good REST API design follows consistent patterns. Use nouns for resources, not verbs: `/users` instead of `/getUsers`. Collection endpoints are plural (`/posts`), individual resources use an ID (`/posts/42`).

Nest resources logically when there's a clear parent-child relationship. For comments on a blog post, use `/posts/42/comments` rather than `/comments?post_id=42`. This makes the relationship explicit in the URL structure.

Return appropriate status codes. 200 means success with data, 201 means resource created, 204 means success with no content, 400 means bad request, 401 means unauthorized, 404 means not found, and 500 means server error. Clients rely on these codes to handle responses correctly.

Version your API from the start. Use `/v1/users` or include the version in headers. This lets you make breaking changes without disrupting existing clients. Many APIs maintain multiple versions simultaneously during transition periods.

Use query parameters for filtering, sorting, and pagination on collection endpoints: `/users?role=admin&sort=created_at&page=2`. The base URL represents the resource, parameters modify how the collection is returned.

## Authentication and Security

Most REST APIs require authentication to protect data and track usage. Token-based authentication is the standard approach. The client sends credentials to an authentication endpoint, receives a token (often a JWT), and includes that token in the `Authorization` header of subsequent requests.

```http
GET /api/users/me HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Always use HTTPS for REST APIs in production. HTTP transmits data in plain text, exposing tokens and sensitive information. HTTPS encrypts the entire request and response.

Rate limiting prevents abuse by restricting how many requests a client can make in a time window. APIs typically return a 429 status code when limits are exceeded, along with headers indicating when the client can retry.

Validate all input on the server. Never trust client data. Check data types, format, and business rules before processing requests. Return detailed error messages for invalid input to help developers debug integration issues.

## Error Handling Best Practices

When a request fails, return a clear status code and a JSON error object. The error object should include a human-readable message and optionally a machine-readable error code:

```json
{
  "error": {
    "code": "INVALID_EMAIL",
    "message": "The email address format is invalid",
    "field": "email"
  }
}
```

Use 4xx status codes for client errors (bad input, unauthorized access, resource not found). Use 5xx codes only for actual server failures (database down, unhandled exception). This distinction helps clients determine whether retrying the request will succeed.

For validation errors, return 400 (Bad Request) with details about which fields failed validation. For authentication failures, return 401 (Unauthorized). For authorization failures (authenticated but lacking permission), return 403 (Forbidden).

## Summary

- REST APIs use HTTP methods (GET, POST, PUT, DELETE) to perform operations on resources identified by URLs
- Each request is stateless and contains all information needed to process it
- Resources are represented as JSON (or other formats) transmitted between client and server
- Proper REST design uses resource-based URLs, meaningful HTTP status codes, and clear error messages
- Authentication typically uses tokens in headers rather than sessions or cookies
- REST's simplicity and alignment with HTTP make it the dominant pattern for web APIs

## Related

For deeper understanding of HTTP mechanics, see our [HTTP Methods Explained](/guides/http-methods-explained) guide. Learn about data format choices in [JSON vs XML](/guides/json-vs-xml). Use our [JSON Formatter](/tools/json-formatter) to validate API responses and our [API Tester](/tools/api-tester) to test endpoints. Download the [REST API Design Cheat Sheet](/cheatsheets/rest-api-design) for quick reference on endpoint patterns and status codes.