---
related_content: []
actual_word_count: 2211
category: guides
description: JWTs are the industry standard for stateless authentication. Understand
  the header, payload, signature — and when not to use JWT.
og_image: /og/guides/what-is-jwt.png
published_date: '2026-04-13'
related_cheatsheet: ''
related_posts: []
related_tools:
- /tools/base64-encoder
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"Article\",\n  \"headline\": \"What is JWT? JSON Web Tokens Explained\
  \ with Examples\",\n  \"description\": \"JWTs are the industry standard for stateless\
  \ authentication. Understand the header, payload, signature — and when not to use\
  \ JWT.\",\n  \"datePublished\": \"2026-04-13\",\n  \"author\": {\"@type\": \"Organization\"\
  , \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\": \"Organization\", \"name\"\
  : \"DevNook\", \"url\": \"https://devnook.dev\"},\n  \"url\": \"https://devnook.dev/guides/\"\
  \n}\n</script>"
tags:
- jwt
- authentication
- security
- web-tokens
- api
template_id: guide-v1
title: What is JWT? JSON Web Tokens Explained with Examples
---

A JWT (JSON Web Token) is a compact, URL-safe token format that securely transmits information between parties as a JSON object, commonly used for authentication and information exchange in web applications.

## What is JWT?

JWT is an open standard (RFC 7519) that defines a self-contained way to transmit information between a client and server. Unlike traditional session-based authentication where the server stores user state, a JWT contains all the information needed to verify a user's identity within the token itself. This makes JWTs ideal for distributed systems, microservices architectures, and mobile applications where maintaining server-side session state becomes impractical.

The token consists of three parts: a header specifying the token type and hashing algorithm, a payload containing claims (statements about the user and metadata), and a signature that verifies the token hasn't been tampered with. These three parts are Base64URL-encoded and joined with periods, creating a compact string that can be easily transmitted via HTTP headers, URL parameters, or request bodies.

JWTs solve the scalability problem inherent in session-based authentication. Traditional sessions require the server to maintain state, which becomes problematic when horizontally scaling across multiple servers or using CDN edge functions. With JWTs, the server validates the signature and trusts the claims inside — no database lookup required for every request.

## A Brief History

JWTs were standardized in May 2015 as RFC 7519 by the Internet Engineering Task Force (IETF), though the concept emerged from earlier work on JSON-based security tokens. The specification was developed to address the limitations of XML-based tokens like SAML, which were verbose and difficult to use in web and mobile contexts. Before JWTs, web applications primarily relied on server-side sessions stored in memory or databases, creating bottlenecks as applications scaled. The JWT standard provided a language-agnostic, compact alternative that worked seamlessly with JSON-based APIs and modern web architectures.

## How JWT Works

When a user logs in, the authentication server verifies their credentials against a database. Upon successful verification, the server generates a JWT containing user information and metadata. The server signs this token using a secret key (for HMAC algorithms) or a private key (for RSA/ECDSA algorithms), then returns it to the client.

The client stores this token — typically in localStorage, sessionStorage, or a secure HTTP-only cookie — and includes it in subsequent requests, usually in the `Authorization` header with the `Bearer` scheme. When the server receives a request with a JWT, it extracts the token, verifies the signature using the secret or public key, and checks that the token hasn't expired. If the signature is valid and the token is current, the server trusts the claims in the payload and processes the request without querying a database.

This stateless approach means the server doesn't track sessions. Each request contains all the information needed to authenticate and authorize the user. The signature guarantees that the token hasn't been modified since the server issued it — if someone changes even one character in the payload, the signature verification fails.

## Key Components / Terms

**Header** — The first part of a JWT, containing metadata about the token itself: the type (`typ`, always "JWT") and the signing algorithm (`alg`, such as HS256, RS256, or ES256). This tells the receiving server how to validate the signature.

**Payload** — The second part containing claims — statements about the user and additional metadata. Claims can be registered (predefined like `iss`, `exp`, `sub`), public (defined in the IANA registry), or private (custom claims specific to your application).

**Signature** — The third part that cryptographically verifies the token's integrity. Created by encoding the header and payload, then hashing them with a secret key (HMAC) or signing with a private key (RSA/ECDSA). The recipient uses the same secret or the corresponding public key to verify.

**Claims** — Key-value pairs in the payload. Registered claims include `iss` (issuer), `sub` (subject/user ID), `exp` (expiration timestamp), `iat` (issued at), and `nbf` (not before). Custom claims carry application-specific data like user roles or permissions.

**HS256** — HMAC with SHA-256, a symmetric signing algorithm where the same secret key both creates and verifies signatures. Simpler to implement but requires securely sharing the secret between all services.

**RS256** — RSA signature with SHA-256, an asymmetric algorithm using a private key to sign and a public key to verify. Preferred for microservices where multiple services need to verify tokens but shouldn't be able to create them.

**Base64URL** — An encoding scheme that converts binary data to URL-safe text by replacing `+` with `-`, `/` with `_`, and removing padding `=` characters. JWTs use this to safely transmit binary signatures in URLs and headers.

## Real-World Examples

When you log into a single-page application (SPA) like a React dashboard, the frontend sends your credentials to an API. The API validates them, generates a JWT containing your user ID and roles, and returns it. The React app stores this token and includes it in the Authorization header for every API request — fetching your profile, updating settings, or retrieving data. The API verifies the token on each request without hitting the database.

Mobile apps use JWTs to maintain authentication across app launches. After you log in, the app stores the token in the device's secure storage. When you open the app later, it sends the stored JWT to authenticate API requests without requiring you to log in again (until the token expires).

Microservices architectures rely heavily on JWTs for inter-service authentication. An API gateway might authenticate a user and issue a JWT, which then gets passed to multiple backend services. Each service independently verifies the token's signature without needing to call back to a central authentication service, reducing latency and eliminating a single point of failure.

## JWT in Practice — Code Example

Here's how you might generate and verify a JWT in a Node.js application using the `jsonwebtoken` library:

```javascript
const jwt = require('jsonwebtoken');

// Server-side: Generate a JWT after successful login
function generateToken(userId, userRole) {
  const payload = {
    sub: userId,          // subject: user identifier
    role: userRole,       // custom claim: user's role
    iat: Math.floor(Date.now() / 1000),  // issued at
    exp: Math.floor(Date.now() / 1000) + (60 * 60)  // expires in 1 hour
  };
  
  const secret = process.env.JWT_SECRET;
  return jwt.sign(payload, secret, { algorithm: 'HS256' });
}

// Middleware: Verify JWT on protected routes
function verifyToken(req, res, next) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  const token = authHeader.substring(7); // Remove "Bearer " prefix
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;  // Attach user data to request
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

// Usage example
app.post('/login', (req, res) => {
  // Validate credentials (omitted for brevity)
  const token = generateToken(user.id, user.role);
  res.json({ token });
});

app.get('/protected', verifyToken, (req, res) => {
  // req.user contains decoded JWT claims
  res.json({ message: `Hello user ${req.user.sub}` });
});
```

This example demonstrates the complete JWT lifecycle: generating a token with claims after authentication, transmitting it via the Authorization header, and verifying it on protected endpoints. The `verify` function checks both the signature and expiration, rejecting invalid or expired tokens automatically.

## Common Misconceptions

**"JWTs are encrypted and hide sensitive data"** — JWTs are signed, not encrypted by default. The payload is Base64URL-encoded, which anyone can decode. Never store passwords, credit card numbers, or other sensitive data in a JWT payload unless you use JWE (JSON Web Encryption), a separate standard that adds encryption.

**"JWTs are impossible to revoke before expiration"** — While JWTs are stateless and can't be invalidated server-side by default, you can implement revocation using a blocklist (storing invalidated token IDs in Redis or a database) or by shortening expiration times and using refresh tokens. However, this reintroduces some statefulness.

**"Longer expiration times are fine because JWTs are secure"** — A stolen JWT remains valid until expiration. If an attacker obtains a token with a 30-day expiration, they have 30 days of unauthorized access. Use short-lived access tokens (15 minutes to 1 hour) paired with refresh tokens stored securely.

## JWT vs Session Cookies

Session cookies store a session ID that references server-side state. JWTs are self-contained and stateless — they carry the data rather than referencing it. Sessions require server-side storage (memory, Redis, database), making horizontal scaling more complex. JWTs eliminate this requirement, allowing truly stateless authentication.

However, sessions provide easier revocation — delete the session from the store and the user is logged out immediately. With JWTs, revocation requires additional infrastructure. Sessions are also more secure against XSS attacks when stored in HTTP-only cookies, while JWTs stored in localStorage are vulnerable to XSS. For maximum security, store JWTs in HTTP-only, Secure cookies with the SameSite attribute — combining the statelessness of JWTs with the XSS protection of cookies.

Choose JWTs when building APIs for mobile apps, microservices, or when you need to scale horizontally without session state. Use traditional sessions for server-rendered applications where simplicity and immediate revocation matter more than statelessness.

## Verifying a JWT Structure

A complete JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

It has three parts separated by periods. Decode the first part (header):

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Decode the second part (payload):

```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022
}
```

The third part is the signature — a cryptographic hash that you verify against the header and payload using the secret key. You can use our JWT Debugger to inspect tokens without revealing your secret.

## Security Best Practices

Always use HTTPS when transmitting JWTs — an intercepted token gives an attacker full access until expiration. Set short expiration times (1 hour or less) for access tokens and implement refresh token rotation for longer sessions. Store the secret key securely in environment variables, never commit it to version control.

Validate every claim in the payload, not just the signature. Check `exp` to ensure the token hasn't expired, verify `iss` matches your expected issuer, and validate `aud` if you're using audience claims. For user-specific data, always verify the `sub` claim matches the requested resource.

Choose RS256 over HS256 for distributed systems where multiple services verify tokens but shouldn't issue them. With RS256, you can safely distribute the public key for verification while keeping the private signing key on a single authentication service.

Implement proper error handling that doesn't leak information. Return generic "invalid token" messages rather than specifics like "signature mismatch" or "token expired," which help attackers understand what went wrong.

## When Not to Use JWT

Don't use JWTs for session management in traditional server-rendered applications where you control both the frontend and backend. The added complexity isn't worth it — simple session cookies work better and offer easier revocation.

Avoid JWTs if you need instant revocation without additional infrastructure. If your application requires the ability to immediately invalidate all user sessions (for example, after a password change or security incident), traditional sessions or short-lived JWTs with a blocklist provide better solutions.

Don't store large amounts of data in JWT payloads. Every request carries the full token, increasing bandwidth usage. Keep payloads minimal — typically just user ID, roles, and expiration. Load additional user data from the database when needed.

Never use JWTs for password reset tokens or email verification links. These require revocation after use, and JWTs can't be invalidated without additional complexity. Use cryptographically random tokens stored in your database with expiration timestamps instead.

## JWT Algorithms Compared

| Algorithm | Type | Key | Use Case |
|-----------|------|-----|----------|
| HS256 | Symmetric | Shared secret | Single application, simple setup |
| HS384/HS512 | Symmetric | Shared secret | Higher security requirements |
| RS256 | Asymmetric | Private/public key pair | Microservices, third-party verification |
| ES256 | Asymmetric | ECDSA keys | Performance-critical applications |

HMAC algorithms (HS256, HS384, HS512) use the same secret for signing and verification. They're simpler but require securely sharing the secret across all services. RSA algorithms (RS256, RS384, RS512) use public-key cryptography — sign with a private key, verify with a public key. ECDSA algorithms (ES256, ES384, ES512) also use asymmetric keys but offer better performance with shorter key lengths.

## Summary

- JWTs are self-contained tokens carrying user information and metadata, enabling stateless authentication without server-side session storage
- The three-part structure (header.payload.signature) ensures data integrity through cryptographic verification while remaining compact and URL-safe
- JWTs excel in distributed systems, microservices, and mobile applications where maintaining session state across servers is impractical
- Tokens must be transmitted over HTTPS, stored securely, and given short expiration times to minimize the impact of token theft
- Signing algorithms like HS256 (symmetric) work for single applications, while RS256 (asymmetric) suits microservices architectures where multiple services verify but don't issue tokens
- JWTs aren't encrypted by default — never store sensitive data in the payload, and use JWE if encryption is required


For authentication workflows that use JWTs, see our guide on OAuth 2.0 Explained. Compare token-based authentication with session-based approaches in Session vs Token Authentication. To understand the APIs that commonly use JWTs, read What is a REST API?

Use our JWT Debugger to decode and inspect tokens during development, and [Base64 Encoder](/tools/base64-encoder) to understand how header and payload encoding works.