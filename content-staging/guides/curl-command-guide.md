---
category: guides
content_type: editorial
description: Learn how to use the curl command with examples for HTTP requests, API
  testing, file downloads, headers, and authentication.
og_image: /og/guides/curl-command-guide.png
published_date: '2026-04-20'
related_posts:
- /guides/http-status-codes-guide
- /guides/url-encoding-query-parameters-guide
- /cheatsheets/git-commands-cheatsheet
related_tools:
- /tools/url-encoder
- /tools/json-formatter
tags:
- curl
- http
- api
- command-line
- developer-tools
template_id: guide-v2
title: 'curl Command: The Complete Guide for Developers'
word_count_target: 1800
---

# curl Command: The Complete Guide for Developers

`curl` is a command-line tool for transferring data using URLs. Developers use it to test HTTP APIs, download files, inspect headers, send form data, and debug network requests — all from the terminal without a GUI client.

## Basic GET Request

The simplest curl invocation fetches a URL and prints the response body to stdout:

```bash
curl https://api.example.com/users
```

By default curl follows no redirects, shows no headers, and prints the body. You'll build on this with flags.

## Essential Flags

| Flag | Long form | Effect |
|------|-----------|--------|
| `-X` | `--request` | Set HTTP method (GET is default) |
| `-H` | `--header` | Add a request header |
| `-d` | `--data` | Send request body |
| `-o` | `--output` | Write response to file |
| `-O` | `--remote-name` | Write response to file named from URL |
| `-i` | `--include` | Include response headers in output |
| `-I` | `--head` | Fetch headers only (HEAD request) |
| `-L` | `--location` | Follow redirects |
| `-s` | `--silent` | Suppress progress meter |
| `-v` | `--verbose` | Show full request + response details |
| `-w` | `--write-out` | Print metadata after transfer |
| `-u` | `--user` | Basic auth credentials |
| `--compressed` | — | Request compressed response, auto-decompress |

## HTTP Methods

```bash
# GET (default)
curl https://api.example.com/posts

# POST
curl -X POST https://api.example.com/posts

# PUT
curl -X PUT https://api.example.com/posts/1

# PATCH
curl -X PATCH https://api.example.com/posts/1

# DELETE
curl -X DELETE https://api.example.com/posts/1

# HEAD (headers only, no body)
curl -I https://api.example.com/posts
```

## Sending JSON

POST and PUT requests to REST APIs typically send JSON. Set the `Content-Type` header and pass the body with `-d`:

```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

For multi-line JSON or to avoid shell escaping issues, read from a file:

```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d @user.json
```

The `@` prefix tells curl to read the body from a file. Use the [JSON Formatter tool](/tools/json-formatter) to format and validate your JSON payload before sending.

## Viewing Response Headers

Include response headers in the output with `-i`:

```bash
curl -i https://api.example.com/users
```

Output:

```
HTTP/2 200
content-type: application/json; charset=utf-8
cache-control: public, max-age=3600
x-ratelimit-remaining: 98

[response body]
```

To see only headers (HEAD request), use `-I`:

```bash
curl -I https://api.example.com/users
```

For a reference on what status codes mean, see the [HTTP Status Codes guide](/guides/http-status-codes-guide).

## Authentication

### Basic Auth

```bash
curl -u username:password https://api.example.com/private
```

curl encodes the credentials as Base64 and sends an `Authorization: Basic <token>` header.

### Bearer Token

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..." \
  https://api.example.com/protected
```

### API Key in Header

```bash
curl -H "X-API-Key: your-api-key-here" \
  https://api.example.com/data
```

### API Key in Query String

```bash
curl "https://api.example.com/data?api_key=your-api-key"
```

Note the quotes around the URL when it contains special characters like `&` or `?`. For proper URL encoding of query parameters, see the [URL Encoding guide](/guides/url-encoding-query-parameters-guide).

## Downloading Files

Download and save with the original filename:

```bash
curl -O https://example.com/archive.zip
```

Save with a custom filename:

```bash
curl -o myfile.zip https://example.com/archive.zip
```

Download multiple files:

```bash
curl -O https://example.com/file1.zip \
     -O https://example.com/file2.zip
```

Resume an interrupted download:

```bash
curl -C - -O https://example.com/largefile.zip
```

The `-C -` flag tells curl to detect the offset automatically and resume from where it stopped.

## Sending Form Data

### URL-Encoded Form (application/x-www-form-urlencoded)

```bash
curl -X POST https://example.com/login \
  -d "username=alice&password=secret"
```

curl sets `Content-Type: application/x-www-form-urlencoded` automatically when you use `-d` with plain key=value strings.

### Multipart Form (file uploads)

```bash
curl -X POST https://api.example.com/upload \
  -F "file=@photo.jpg" \
  -F "description=Profile photo"
```

The `-F` flag triggers multipart encoding. `@filename` includes the file; plain values are sent as text fields.

## Request and Response Inspection

### Verbose Mode

`-v` prints the full transaction — DNS resolution, TLS handshake, request headers, response headers, and response body:

```bash
curl -v https://api.example.com/users
```

```
*   Trying 93.184.216.34:443...
* Connected to api.example.com (93.184.216.34) port 443
* TLS 1.3 connection using TLS_AES_256_GCM_SHA384
> GET /users HTTP/2
> Host: api.example.com
> User-Agent: curl/8.1.2
> Accept: */*
>
< HTTP/2 200
< content-type: application/json
<
[body]
```

Lines starting with `>` are sent; lines starting with `<` are received.

### Timing Breakdown

The `-w` flag prints structured metadata after the transfer:

```bash
curl -s -o /dev/null -w "
  dns_lookup:     %{time_namelookup}s
  tcp_connect:    %{time_connect}s
  tls_handshake:  %{time_appconnect}s
  ttfb:           %{time_starttransfer}s
  total:          %{time_total}s
  http_code:      %{http_code}
" https://api.example.com/users
```

This is a useful performance diagnostic for API endpoints. The `-s` suppresses the progress meter; `-o /dev/null` discards the body.

## Working with APIs

### Pretty-Print JSON Response

Pipe the response to `python -m json.tool` or `jq`:

```bash
curl -s https://api.example.com/users | python -m json.tool
curl -s https://api.example.com/users | jq .
```

### Chaining Requests

Extract a value from one response and use it in the next:

```bash
TOKEN=$(curl -s -X POST https://api.example.com/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -H "Authorization: Bearer $TOKEN" \
  https://api.example.com/profile
```

### Rate Limiting — Check Remaining Quota

```bash
curl -s -I https://api.example.com/data | grep -i "ratelimit"
```

Inspect the `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers to avoid hitting limits.

## HTTPS and SSL

### Skip Certificate Verification (Testing Only)

```bash
curl -k https://localhost:3000/api
# or
curl --insecure https://localhost:3000/api
```

Only use `-k` against local development servers you control. Never skip certificate verification in production scripts — it removes protection against man-in-the-middle attacks.

### Specify a CA Certificate

```bash
curl --cacert /path/to/ca-bundle.crt https://internal.example.com/api
```

### Client Certificate Authentication

```bash
curl --cert client.crt --key client.key https://api.example.com/secure
```

## Proxy Support

```bash
# HTTP proxy
curl -x http://proxy.example.com:8080 https://api.example.com/data

# SOCKS5 proxy
curl --socks5 proxy.example.com:1080 https://api.example.com/data

# Bypass proxy for specific hosts
curl --noproxy "localhost,internal.example.com" https://api.example.com/data
```

## Saving and Reusing Configuration

For frequently used flags, create a `.curlrc` file in your home directory:

```
# ~/.curlrc
silent
location           # always follow redirects
compressed         # always request compressed responses
```

curl reads this file automatically on every invocation. Project-specific config can live in `.curlrc` in the current directory.

## Common Patterns for CI/CD

### Health Check

```bash
# Fail if HTTP status is not 200
curl --fail -s https://yoursite.com/health || exit 1
```

### Wait for a Service to Start

```bash
until curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; do
  sleep 2
done
echo "Service ready"
```

### POST with Error Handling

```bash
HTTP_STATUS=$(curl -s -o response.json -w "%{http_code}" \
  -X POST https://api.example.com/deploy \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version": "1.2.3"}')

if [ "$HTTP_STATUS" -ne 200 ]; then
  echo "Deploy failed with status $HTTP_STATUS"
  cat response.json
  exit 1
fi
```

## curl vs Other HTTP Tools

| Tool | Best for |
|------|----------|
| curl | Scripting, CI/CD, quick terminal tests |
| HTTPie | Human-readable output, interactive terminal use |
| Postman | GUI-based API exploration, collections |
| wget | Recursive downloads, mirroring |
| fetch (browser) | Client-side JavaScript [HTTP requests](/languages/cpp/http-requests) |

curl's advantage is ubiquity — it's available on every Unix-like system, Windows 10+, and most CI runners without installation. The [Git Commands cheat sheet](/cheatsheets/git-commands-cheatsheet) covers another essential developer CLI tool with a similar depth of flags and options. For encoding URLs correctly before passing them to curl, use the [URL Encoder tool](/tools/url-encoder).

## Debugging Connection Issues

### Check TLS Certificate Details

```bash
curl -v --head https://api.example.com 2>&1 | grep -E "SSL|TLS|certificate|subject|issuer"
```

### Test a Specific IP or Host

Bypass DNS and connect directly to an IP while sending the correct `Host` header — useful for testing CDN origin servers or debugging DNS propagation:

```bash
curl -H "Host: api.example.com" https://93.184.216.34/endpoint
```

### Test with a Specific Protocol Version

```bash
curl --http1.1 https://api.example.com/data   # force HTTP/1.1
curl --http2 https://api.example.com/data     # force HTTP/2
```

If an API behaves differently on HTTP/1.1 vs HTTP/2, this isolates the protocol as a variable.

## Cookies

```bash
# Send a cookie
curl -b "session_id=abc123; theme=dark" https://api.example.com/

# Save cookies to a file
curl -c cookies.txt https://api.example.com/login \
  -d "username=alice&password=secret"

# Load cookies from a file
curl -b cookies.txt https://api.example.com/dashboard

# Save and load cookies (full session simulation)
curl -c cookies.txt -b cookies.txt https://api.example.com/login \
  -d "username=alice&password=secret"
```

## Uploading to APIs with Retry Logic

For production scripts, add retry logic to handle transient failures:

```bash
curl --retry 3 \
     --retry-delay 2 \
     --retry-max-time 30 \
     --fail \
     -X POST https://api.example.com/events \
     -H "Content-Type: application/json" \
     -d @event.json
```

- `--retry 3`: retry up to 3 times on transient failures (network errors, 5xx responses)
- `--retry-delay 2`: wait 2 seconds between retries
- `--retry-max-time 30`: abort if total retry time exceeds 30 seconds
- `--fail`: exit with error code on HTTP 4xx/5xx (without this, curl exits 0 even on failure)

## WebSockets

curl has limited WebSocket support (added in curl 7.86.0). For basic testing:

```bash
curl --no-buffer -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
     -H "Sec-WebSocket-Version: 13" \
     https://ws.example.com/socket
```

For interactive WebSocket testing, `websocat` or browser DevTools are more practical. curl's WebSocket support is primarily useful for CI health checks that verify a WebSocket endpoint accepts upgrade requests.

## Environment Variables for curl Configuration

When automating curl in scripts, use [environment variables](/languages/java/environment-variables) for secrets to avoid exposing credentials in process lists or shell history:

```bash
export API_TOKEN="your-secret-token"
export BASE_URL="https://api.example.com"

curl -H "Authorization: Bearer $API_TOKEN" \
     "$BASE_URL/users"
```

In CI systems (GitHub Actions, GitLab CI), inject secrets via the platform's secret management rather than hardcoding them in workflow files. For reference on how HTTP authentication works at the protocol level, see the [HTTP Status Codes guide](/guides/http-status-codes-guide).

## curl on Windows

On Windows 10 and later, curl is available natively in PowerShell and Command Prompt (it's an alias for `Invoke-WebRequest` in PowerShell, but the actual curl binary is in `C:\Windows\System32\curl.exe`).

To use the real curl binary from PowerShell:

```powershell
curl.exe -s https://api.example.com/users
# Note: use curl.exe to avoid PowerShell's Invoke-WebRequest alias
```

The flags and behavior are identical to Linux/macOS curl since both use the same underlying libcurl library.

## Quick Reference

| Task | Command |
|------|---------|
| Simple GET | `curl https://example.com` |
| GET with headers shown | `curl -i https://example.com` |
| POST JSON | `curl -X POST -H "Content-Type: application/json" -d '{}' https://example.com` |
| Bearer auth | `curl -H "Authorization: Bearer TOKEN" https://example.com` |
| Download file | `curl -O https://example.com/file.zip` |
| Follow redirects | `curl -L https://example.com` |
| Verbose debug | `curl -v https://example.com` |
| Timing breakdown | `curl -s -o /dev/null -w "%{time_total}" https://example.com` |
| Skip TLS (dev only) | `curl -k https://localhost:3000` |
| Retry on failure | `curl --retry 3 --fail https://example.com` |