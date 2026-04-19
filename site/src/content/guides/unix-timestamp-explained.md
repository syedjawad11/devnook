---
actual_word_count: 1793
category: guides
description: Unix timestamps count seconds since January 1, 1970. Learn why developers
  use them, how they work, and how to convert timestamps in any language.
og_image: /og/guides/unix-timestamp-explained.png
published_date: '2026-04-13'
related_cheatsheet: ''
related_content: []
related_posts: []
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"Article\",\n  \"headline\": \"Unix Timestamp: What It Is and How\
  \ to Convert It\",\n  \"description\": \"Unix timestamps count seconds since January\
  \ 1, 1970. Learn why developers use them, how they work, and how to convert timestamps\
  \ in any language.\",\n  \"datePublished\": \"2026-04-13\",\n  \"author\": {\"@type\"\
  : \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\": \"Organization\"\
  , \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n  \"url\": \"https://devnook.dev/guides/\"\
  \n}\n</script>"
tags:
- unix-timestamp
- datetime
- time-formats
- epoch
template_id: guide-v2
title: 'Unix Timestamp: What It Is and How to Convert It'
---

## The Short Answer

A Unix timestamp is an integer that counts the number of seconds since January 1, 1970, at 00:00:00 UTC. This date is called the Unix epoch. For example, `1713000000` represents April 13, 2024, at 10:40:00 UTC. Unix timestamps ignore leap seconds and time zones, making them a universal way to represent a specific moment in time across all systems and programming languages.

---

If you work with dates in software, you'll encounter Unix timestamps constantly. Here's the full picture of how they work and why they matter.

## The Problem It Solves

Before standardized time formats, every system stored dates differently. A database might store "2024-04-13 10:40:00", while another used "04/13/2024 10:40 AM". Converting between formats was error-prone. Time zones made it worse — is that timestamp EST or UTC? Unix timestamps solve this by storing time as a single number that's identical everywhere. No parsing. No ambiguity. No time zone confusion. Two systems can exchange `1713000000` and both know exactly when that moment occurred, regardless of their local time zone or date format preferences.

## How It Actually Works

The Unix timestamp system uses a simple counter that started at zero on January 1, 1970, at midnight UTC. Every second that passes increments the counter by one. This reference point is called the Unix epoch.

Here's the calculation:

1. Start at the Unix epoch: January 1, 1970, 00:00:00 UTC
2. Count every second that has elapsed since then
3. The result is your Unix timestamp

A timestamp of `0` means exactly the epoch. A timestamp of `86400` means one day later (24 hours × 60 minutes × 60 seconds = 86,400 seconds). A timestamp of `1713000000` means approximately 54.4 years have passed since the epoch.

The system ignores leap seconds for simplicity. Every day is treated as exactly 86,400 seconds, even though occasional leap seconds are added to civil time. This keeps the math predictable and consistent across platforms.

Unix timestamps are always in UTC. When you convert a timestamp to a human-readable date, you apply the time zone offset separately. The timestamp itself remains time-zone-neutral.

## Show Me an Example

Here's how to work with Unix timestamps in different languages:

```python
import time
from datetime import datetime

# Get current Unix timestamp
current = int(time.time())
print(current)  # 1713000000 (example)

# Convert timestamp to readable date
timestamp = 1713000000
date = datetime.fromtimestamp(timestamp)
print(date)  # 2024-04-13 10:40:00

# Convert date to timestamp
new_date = datetime(2024, 4, 13, 10, 40, 0)
new_timestamp = int(new_date.timestamp())
print(new_timestamp)  # 1713000000
```

```javascript
// Get current Unix timestamp (in seconds)
const current = Math.floor(Date.now() / 1000);
console.log(current);  // 1713000000

// Convert timestamp to readable date
const timestamp = 1713000000;
const date = new Date(timestamp * 1000);
console.log(date.toISOString());  // 2024-04-13T10:40:00.000Z

// Convert date to timestamp
const newDate = new Date('2024-04-13T10:40:00Z');
const newTimestamp = Math.floor(newDate.getTime() / 1000);
console.log(newTimestamp);  // 1713000000
```

These examples show the round-trip conversion: timestamp to date, and date back to timestamp. Note that [JavaScript](/languages/javascript)'s `Date.now()` returns milliseconds, so you divide by 1000 to get seconds.

## The Details That Matter

**Precision varies by language.** Most languages store Unix timestamps as integers representing seconds. JavaScript uses milliseconds (you'll see timestamps like `1713000000000`). Some databases and languages support microsecond or nanosecond precision. Always check what unit your system expects.

**The 2038 problem is real.** Traditional 32-bit signed integers max out at `2,147,483,647`. That's January 19, 2038, at 03:14:07 UTC. After that, 32-bit systems will overflow. Most modern systems use 64-bit integers, which won't overflow for 292 billion years. If you're working with legacy code or embedded systems, verify the integer size.

**Negative timestamps work.** A timestamp of `-86400` represents December 31, 1969, one day before the epoch. This lets you represent dates before 1970, though not all systems support negative timestamps consistently.

**Timestamps don't include time zone information.** When you display a timestamp to a user, you convert it to their local time zone. The timestamp `1713000000` displays as "April 13, 2024, 10:40:00 AM" in UTC, "6:40:00 AM" in New York (UTC-4), and "7:40:00 PM" in Tokyo (UTC+9). The timestamp itself never changes.

**Comparison and sorting is trivial.** Because timestamps are integers, you can compare them with simple math: `timestamp1 < timestamp2` tells you which moment came first. This makes database queries and sorting extremely fast.

## When You'll Use This

- **Storing event times in databases.** Log entries, user actions, transaction records — any event where you need to record exactly when something happened gets stored as a Unix timestamp.
- **API data exchange.** REST and GraphQL APIs often return timestamps for created_at, updated_at, or expires_at fields. Using integers avoids date parsing issues across different client languages.
- **Comparing or calculating time differences.** Subtract two timestamps to get the number of seconds between events. Add 3600 to a timestamp to get one hour later. The math is simple and fast.
- **Session expiration and token validity.** JWTs include `exp` (expiration) and `iat` (issued at) claims as Unix timestamps. Your authentication logic compares these against the current time.
- **Caching and rate limiting.** Cache headers like `Expires` can use timestamps. Rate limiters track request times as timestamps to enforce per-minute or per-hour limits.

## Frequently Asked Questions

**Why does Unix time start in 1970?**
Unix development began in the late 1960s at Bell Labs. The first edition of Unix launched in 1971, and developers chose January 1, 1970, as a recent, memorable date to use as the epoch. The choice was somewhat arbitrary but became a permanent standard once the system gained adoption.

**Are Unix timestamps affected by daylight saving time?**
No. Unix timestamps represent UTC time, which doesn't observe daylight saving. When you convert a timestamp to local time for display, your system applies the DST offset for that specific date. The timestamp itself stays constant regardless of DST rules.

**Can I represent dates before 1970 with Unix timestamps?**
Yes, using negative timestamps. The timestamp `-86400` represents December 31, 1969. However, older systems and some programming languages don't handle negative timestamps reliably. If you need to work with historical dates before 1970, test your specific platform's support.

**What's the difference between Unix time and epoch time?**
These terms are interchangeable. "Unix timestamp", "Unix time", "epoch time", and "POSIX time" all refer to the same system: seconds since January 1, 1970, at 00:00:00 UTC.

**How do I convert a timestamp to a specific time zone?**
First convert the timestamp to a date object in your programming language, then apply the time zone offset. Most languages provide built-in functions: [Python](/languages/python)'s `datetime.fromtimestamp()` with `tz` parameter, JavaScript's `toLocaleString()` with `timeZone` option, or dedicated libraries like [Moment.js](https://momentjs.com/) or Luxon for complex time zone handling.

## Converting Timestamps in Practice

Here's how to handle common conversion scenarios across multiple languages:

```python
from datetime import datetime, timezone
import pytz

timestamp = 1713000000

# To UTC
utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
print(utc_time)  # 2024-04-13 10:40:00+00:00

# To specific timezone
ny_tz = pytz.timezone('America/New_York')
ny_time = datetime.fromtimestamp(timestamp, tz=ny_tz)
print(ny_time)  # 2024-04-13 06:40:00-04:00

# From ISO string to timestamp
iso_string = "2024-04-13T10:40:00Z"
dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
new_timestamp = int(dt.timestamp())
print(new_timestamp)  # 1713000000
```

```javascript
const timestamp = 1713000000;

// To UTC string
const utcDate = new Date(timestamp * 1000);
console.log(utcDate.toISOString());
// 2024-04-13T10:40:00.000Z

// To specific timezone
const options = {
  timeZone: 'America/New_York',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit'
};
console.log(utcDate.toLocaleString('en-US', options));
// 04/13/2024, 06:40:00 AM

// From ISO string to timestamp
const isoString = "2024-04-13T10:40:00Z";
const newTimestamp = Math.floor(new Date(isoString).getTime() / 1000);
console.log(newTimestamp);  // 1713000000
```

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    timestamp := int64(1713000000)
    
    // To UTC
    utcTime := time.Unix(timestamp, 0).UTC()
    fmt.Println(utcTime)
    // 2024-04-13 10:40:00 +0000 UTC
    
    // To specific timezone
    loc, _ := time.LoadLocation("America/New_York")
    nyTime := time.Unix(timestamp, 0).In(loc)
    fmt.Println(nyTime)
    // 2024-04-13 06:40:00 -0400 EDT
    
    // From time to timestamp
    newTime := time.Date(2024, 4, 13, 10, 40, 0, 0, time.UTC)
    newTimestamp := newTime.Unix()
    fmt.Println(newTimestamp)  // 1713000000
}
```

The pattern is consistent: multiply by 1000 when converting to milliseconds (JavaScript), divide by 1000 when converting from milliseconds. Always specify UTC explicitly when working with timestamps to avoid accidental local time zone conversions.

## Common Pitfalls and How to Avoid Them

**Off-by-one-thousand errors.** JavaScript developers frequently forget that `Date.now()` returns milliseconds. When sending timestamps to a backend that expects seconds, divide by 1000. When receiving timestamps from an API, check the documentation — some systems use milliseconds, others use seconds.

**Assuming timestamps are in local time.** Unix timestamps are always UTC. If you display `1713000000` directly without converting to the user's time zone, users will see incorrect times. Always convert to local time for display purposes using your language's time zone libraries.

**Not handling leap years correctly.** While Unix timestamps ignore leap seconds, leap years still affect date calculations. Don't assume every year has exactly 31,536,000 seconds. Use your language's date library to handle date arithmetic rather than multiplying timestamps by approximate values.

**Comparing timestamps with different precision.** If one system uses seconds and another uses milliseconds, direct comparison fails. Normalize both to the same unit before comparing. A timestamp of `1713000000` (seconds) equals `1713000000000` (milliseconds).

## Working with Timestamps in Databases

Most databases provide functions to work with Unix timestamps:

**PostgreSQL:**
```sql
-- Current timestamp
SELECT EXTRACT(EPOCH FROM NOW());

-- Convert timestamp to date
SELECT TO_TIMESTAMP(1713000000);

-- Convert date to timestamp
SELECT EXTRACT(EPOCH FROM TIMESTAMP '2024-04-13 10:40:00');
```

**MySQL:**
```sql
-- Current timestamp
SELECT UNIX_TIMESTAMP();

-- Convert timestamp to date
SELECT FROM_UNIXTIME(1713000000);

-- Convert date to timestamp
SELECT UNIX_TIMESTAMP('2024-04-13 10:40:00');
```

Store timestamps as `BIGINT` (or `INTEGER` if you're certain all dates are after 1970 and before 2038). This makes indexing fast and keeps storage requirements minimal. Many ORMs and database libraries handle the conversion automatically.

## The Future of Unix Timestamps

The 64-bit timestamp standard effectively solves the 2038 problem for modern systems. Languages and databases have largely migrated to 64-bit integers, which support dates until the year 292,277,026,596. By that point, we'll have different problems.

Some newer systems use alternative formats. ISO 8601 provides human-readable timestamps with time zone support. Protocol Buffers uses a Timestamp message with seconds and nanoseconds fields. However, Unix timestamps remain the de facto standard for system-level time tracking due to their simplicity and universal support.

For most applications, Unix timestamps are the right choice. They're compact, fast to compare, easy to store, and supported everywhere. When you need human readability or explicit time zone information, convert to ISO 8601 or another format for display.


Use our timestamp converter tool to convert between Unix timestamps and human-readable dates in real-time. For more on date formats, see our guide on ISO 8601 date formatting and our explanation of how time zones work. Check the date and time conversion cheat sheet for quick reference on common conversions.