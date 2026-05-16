# Example 2 — How-To Article

This example demonstrates the modular system applied to a "how to" topic with a different section selection and voice from Example 1. Note how the sections, voice, and structural rhythm produce a noticeably different fingerprint.

## Article metadata (from brief)

```json
{
  "language": "ruby",
  "concept": "parse-json",
  "intent": "how-to",
  "difficulty": "beginner",
  "target_keyword": "parse JSON in Ruby",
  "secondary_keywords": ["JSON.parse", "Ruby JSON module", "handling parser errors"],
  "is_abstract": false,
  "is_syntax_heavy": false,
  "is_error_driven": false,
  "has_performance_implications": false,
  "has_cross_language_analog": false
}
```

## Algorithm output

```json
{
  "sections": [
    "open-quick",
    "core-how-it-works",
    "code-realistic",
    "code-variations",
    "prac-gotchas",
    "close-checklist"
  ],
  "voice": "terse-senior",
  "word_target": 1800,
  "section_count": 6
}
```

## The article

---

```yaml
---
title: "Parsing JSON in Ruby Without the Standard Pitfalls"
description: "Use Ruby's built-in JSON module to parse JSON strings. Three idiomatic patterns and the two errors that bite production code."
language: "ruby"
concept: "parse-json"
difficulty: "beginner"
target_keyword: "parse JSON in Ruby"
secondary_keywords: ["JSON.parse", "Ruby JSON module", "handling parser errors"]
sections_used: ["open-quick", "core-how-it-works", "code-realistic", "code-variations", "prac-gotchas", "close-checklist"]
voice: "terse-senior"
word_count: 1742
published_date: "2026-05-16"
og_image: "og-default"
---
```

Use `JSON.parse` from Ruby's standard library. It ships built-in — no gem to install. Pass it a JSON string, get back a Hash, Array, or primitive.

```ruby
require 'json'

data = JSON.parse('{"user": "ada", "active": true}')
puts data["user"]  # => "ada"
```

That's the whole API. Everything else in this post covers the edge cases that bite production code.

## What `JSON.parse` Actually Does

`JSON.parse` walks the input string and converts each JSON token into the corresponding Ruby type. The mapping is straightforward: JSON objects become Hashes with string keys, arrays become Arrays, numbers become Integers or Floats, booleans become `true`/`false`, and `null` becomes `nil`.

One thing worth knowing: keys come back as strings, not symbols. `JSON.parse('{"name": "ada"}')` returns `{"name" => "ada"}`, not `{name: "ada"}`. If your code expects symbol keys (common in Ruby), pass `symbolize_names: true`:

```ruby
JSON.parse('{"name": "ada"}', symbolize_names: true)
# => {:name => "ada"}
```

The parser is strict about JSON syntax. Trailing commas, unquoted keys, and single-quoted strings all raise `JSON::ParserError`. This is correct JSON behaviour but trips up developers coming from JavaScript, which tolerates some of these.

## A Real-World Example

Parsing JSON from an HTTP response, with error handling that doesn't crash on bad input:

```ruby
require 'json'
require 'net/http'
require 'uri'

def fetch_user(user_id)
  uri = URI("https://api.example.com/users/#{user_id}")
  response = Net::HTTP.get_response(uri)

  return nil unless response.is_a?(Net::HTTPSuccess)

  begin
    JSON.parse(response.body, symbolize_names: true)
  rescue JSON::ParserError => e
    Rails.logger.error("Invalid JSON from API: #{e.message}")
    nil
  end
end
```

Three things this does that minimal examples skip. First, it checks the HTTP status before trying to parse — APIs returning HTML error pages on 500 are common, and parsing HTML as JSON gives you a confusing error. Second, it rescues `JSON::ParserError` specifically, not generic `StandardError`. Third, it logs the error message before returning nil, so you can diagnose later.

The `symbolize_names: true` is a style choice — many Ruby codebases prefer symbol keys throughout. Skip it if your code works with string keys.

## Three Variations

**Variation 1: parsing with default values**

```ruby
data = JSON.parse(response.body) rescue {}
```

A one-liner using inline rescue. The `rescue {}` falls back to an empty hash on any parse error. Useful for quick scripts. Don't ship this to production — it swallows errors silently, including ones you'd want to see.

**Variation 2: streaming large JSON**

```ruby
require 'json'
File.open('huge.json') do |f|
  JSON.parse(f.read)  # loads entire file into memory
end
```

`JSON.parse` is not streaming. If you're parsing files larger than maybe 100MB, you'll want a streaming parser like `oj` or `yajl-ruby`. Memory will spike to ~3x the file size during parsing.

**Variation 3: parsing JSON Lines (one JSON object per line)**

```ruby
File.foreach('events.jsonl') do |line|
  event = JSON.parse(line)
  process(event)
end
```

JSONL is a common format for logs and event streams. Each line is a complete JSON object. `JSON.parse` works fine line-by-line; just don't try to parse the whole file as one JSON value — it isn't.

Default to the standard pattern from the "real-world example" section. Use the inline-rescue version only for throwaway scripts. Use a streaming parser when files exceed ~100MB or memory is tight.

## Things That Will Trip You Up

**Trap 1: assuming the API returns valid JSON.**

External APIs lie. They return HTML error pages, empty bodies, or truncated JSON when something goes wrong upstream. Any code parsing untrusted JSON needs a rescue:

```ruby
# This will crash in production
data = JSON.parse(api_response)

# This won't
begin
  data = JSON.parse(api_response)
rescue JSON::ParserError
  data = nil
end
```

A junior developer at a previous job lost half a Saturday to this. The third-party API returned `<html><body>503</body></html>` during an outage, and the parser crashed every worker that processed it. Always rescue parsing of external input.

**Trap 2: NaN and Infinity.**

JSON technically doesn't support NaN or Infinity. Ruby's parser is strict by default — `JSON.parse('NaN')` raises. But some APIs return these values (Python's `json.dumps` will happily serialise NaN). If you're parsing JSON from a Python service that emits NaN, you need to pass `allow_nan: true`:

```ruby
JSON.parse(input, allow_nan: true)
```

This is one of those settings you turn on once after spending an hour on a confused error, and then never think about again until the next service emits it.

## Quick Checklist

- Use `JSON.parse` from the standard library — no gem needed
- Wrap calls to it in `rescue JSON::ParserError` when parsing external input
- Pass `symbolize_names: true` if your codebase uses symbol keys
- Don't use inline `rescue {}` in production code
- For files over ~100MB, use a streaming parser (`oj` is the standard choice)
- Use `allow_nan: true` only when consuming JSON from sources that emit NaN/Infinity
- Check HTTP status before parsing API responses — error pages won't be valid JSON

---

## Why this article works

Comparing to Example 1, notice:

1. **Completely different section composition.** Example 1 had `open-mental-model + core-how-it-works + core-design-decision + code-realistic + prac-gotchas + comp-cross-language + close-one-thing`. This one has `open-quick + core-how-it-works + code-realistic + code-variations + prac-gotchas + close-checklist`. Only 2 sections overlap (`core-how-it-works`, `prac-gotchas`, `code-realistic`) — under 50% similarity.

2. **Different voice.** Example 1 was thoughtful-explainer. This is terse-senior. Compare the opening sentences — Example 1: "Imagine you write a sticky note on the wall of a meeting room..." vs this one: "Use `JSON.parse` from Ruby's standard library. It ships built-in — no gem to install."

3. **Different word count.** Example 1: 2,387. This: 1,742. Wide variance is natural and important.

4. **Different ending shape.** Example 1 ended with a single takeaway paragraph. This ends with a 7-item checklist. Two completely different closing fingerprints.

5. **No "Under the Hood" or "Edge Cases" or "Testing" sections.** None of the three problem sections from the old template system appear in either example. They remain available in the library but are gated by topic relevance — neither of these topics needed them.

6. **Realistic code with realistic variable names.** `user_email`, `cart_total`, `parse_billing_csv` — never `x`, `foo`, `bar`, `data`.

If you generate 10 more articles using this skill and they all look meaningfully different from each other AND from these two examples, the system is working.
