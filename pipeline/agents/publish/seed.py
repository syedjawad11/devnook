import sqlite3

DB_PATH = "agents/content-team/registry.db"

sql = """
INSERT INTO posts (slug, title, description, category, language, concept, template_id, keyword, opportunity_score, status) VALUES

-- Ring 1: Tool-adjacent (highest conversion)
('json-formatter-guide', 'JSON Formatter Online: Format, Validate & Minify JSON Free', 'Format and validate JSON instantly. Our free online JSON formatter catches syntax errors and beautifies messy JSON in one click.', 'guides', NULL, NULL, 'guide-v2', 'json formatter online', 95, 'queued'),
('base64-decode-online', 'Base64 Decode & Encode Online — Free Tool + Guide', 'Decode or encode Base64 strings instantly in your browser. Learn what Base64 is and why developers use it.', 'guides', NULL, NULL, 'guide-v2', 'base64 decode online', 92, 'queued'),
('regex-tester-guide', 'Regex Tester: Test Regular Expressions Online with Explanation', 'Test regular expressions interactively. Get real-time matches, group captures, and plain-English explanations.', 'guides', NULL, NULL, 'guide-v2', 'regex tester online', 90, 'queued'),

-- Ring 2: Web dev fundamentals
('what-is-rest-api', 'What is a REST API? A Complete Guide for Developers', 'REST APIs power the modern web. Learn what REST means, how HTTP methods work, and how to design clean API endpoints.', 'guides', NULL, NULL, 'guide-v1', 'what is REST API', 88, 'queued'),
('what-is-jwt', 'What is JWT? JSON Web Tokens Explained with Examples', 'JWTs are the industry standard for stateless authentication. Understand the header, payload, signature — and when not to use JWT.', 'guides', NULL, NULL, 'guide-v1', 'what is JWT', 86, 'queued'),
('http-status-codes-guide', 'HTTP Status Codes: Complete Reference (200, 301, 404, 500...)', 'Every HTTP status code explained with real-world examples. Bookmark this as your definitive HTTP reference.', 'guides', NULL, NULL, 'guide-v4', 'HTTP status codes', 84, 'queued'),

-- Ring 3: Language concepts (Python — highest volume)
('python-list-comprehensions', 'Python List Comprehensions: Syntax, Examples & When to Use Them', 'List comprehensions are one of Python''s most powerful features. Learn the syntax, nested comprehensions, and filtering with real examples.', 'languages', 'python', 'list-comprehensions', 'lang-v3', 'python list comprehensions', 85, 'queued'),
('python-decorators', 'Python Decorators Explained: A Practical Guide with Examples', 'Decorators modify function behavior without changing the function itself. Learn @property, @staticmethod, and how to write your own.', 'languages', 'python', 'decorators', 'lang-v2', 'python decorators', 83, 'queued'),
('python-async-await', 'Python Async/Await: Complete Guide to Asynchronous Programming', 'Async Python lets you run I/O-bound tasks concurrently. Learn async def, await, asyncio.gather(), and when async actually helps.', 'languages', 'python', 'async-await', 'lang-v1', 'python async await', 82, 'queued'),

-- JavaScript
('javascript-promises', 'JavaScript Promises Explained: then(), catch(), and async/await', 'Promises replaced callback hell. Understand the Promise lifecycle, chaining, error handling, and how async/await simplifies it all.', 'languages', 'javascript', 'promises', 'lang-v3', 'javascript promises', 84, 'queued'),
('javascript-closures', 'JavaScript Closures: What They Are and Why They Matter', 'Closures are fundamental to JavaScript. Learn how functions remember their surrounding scope and why this is useful.', 'languages', 'javascript', 'closures', 'lang-v1', 'javascript closures', 82, 'queued'),
('javascript-array-methods', 'JavaScript Array Methods: map(), filter(), reduce() and More', 'Master the functional array methods that make JavaScript elegant. Real examples with map, filter, reduce, find, and flatMap.', 'languages', 'javascript', 'array-methods', 'lang-v3', 'javascript array methods', 81, 'queued'),

-- TypeScript
('typescript-interfaces-vs-types', 'TypeScript: interface vs type — What''s the Difference?', 'Both interface and type define object shapes in TypeScript, but they''re not identical. Learn when to use each one.', 'languages', 'typescript', 'interfaces-vs-types', 'lang-v1', 'typescript interface vs type', 83, 'queued'),

-- Cross-language (Ring 3 bonus)
('sorting-algorithms-comparison', 'Sorting Algorithms Explained: Python, JS, Go, and Java Side by Side', 'Quick sort, merge sort, bubble sort — implemented in 4 languages. Understand O(n log n) vs O(n²) with visual complexity tables.', 'blog', NULL, NULL, 'blog-v1', 'sorting algorithms comparison', 80, 'queued'),

-- Cheat Sheets
('python-string-methods-cheatsheet', 'Python String Methods Cheat Sheet: split, join, replace, format & More', 'Every Python string method with syntax and examples. The only string reference you''ll need.', 'cheatsheets', 'python', 'string-methods', 'cheatsheet-v2', 'python string methods cheatsheet', 87, 'queued'),
('javascript-array-cheatsheet', 'JavaScript Array Methods Cheat Sheet: Quick Reference Guide', 'All JavaScript array methods at a glance. Includes ES6+ methods with examples and return values.', 'cheatsheets', 'javascript', 'array-methods', 'cheatsheet-v1', 'javascript array cheatsheet', 85, 'queued'),

-- AI/comparison bonus
('chatgpt-vs-gemini-for-developers', 'ChatGPT vs Gemini for Developers: Which AI Wins in 2025?', 'We tested both on real developer tasks: code generation, debugging, documentation, and API quality. Here''s the honest verdict.', 'blog', NULL, NULL, 'blog-v1', 'ChatGPT vs Gemini for developers', 78, 'queued'),

-- Go (expanding languages)
('golang-goroutines-explained', 'Go Goroutines Explained: Concurrency Made Simple', 'Goroutines are Go''s secret weapon for concurrent code. Learn go keyword, channels, WaitGroups, and when goroutines beat threads.', 'languages', 'go', 'goroutines', 'lang-v1', 'golang goroutines', 80, 'queued'),

-- Tool explainers (auto-generated by build-tool.py, but adding manually for launch)
('what-is-base64', 'What is Base64 Encoding? Why Developers Use It', 'Base64 converts binary data to ASCII text for safe transport over text-based protocols. Learn why email, APIs, and JWTs all use it.', 'guides', NULL, NULL, 'guide-v2', 'what is base64', 89, 'queued'),
('unix-timestamp-explained', 'Unix Timestamp: What It Is and How to Convert It', 'Unix timestamps count seconds since January 1, 1970. Learn why developers use them, and how to convert timestamps in any language.', 'guides', NULL, NULL, 'guide-v2', 'unix timestamp', 86, 'queued');
"""

try:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("BEGIN TRANSACTION;")
    # using executemcript as it contains comments which could ruin simple execute
    conn.executescript(sql)
    conn.commit()
    print("Seed content successfully added!")
except sqlite3.IntegrityError:
    print("Seed content already exists. Skipping insertion.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
