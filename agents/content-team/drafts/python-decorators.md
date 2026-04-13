---
actual_word_count: 949
category: languages
concept: decorators
description: Decorators modify function behavior without changing the function itself.
  Learn @property, @staticmethod, and how to write your own.
difficulty: intermediate
language: python
og_image: /og/languages/python/decorators.png
published_date: '2026-04-13'
related_cheatsheet: /cheatsheets/python-functions
related_posts:
- /languages/python/lambda-functions
- /languages/python/generators
- /languages/python/context-managers
related_tools:
- /tools/python-repl
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"TechArticle\",\n  \"headline\": \"Python Decorators Explained:\
  \ A Practical Guide with Examples\",\n  \"description\": \"Decorators modify function\
  \ behavior without changing the function itself. Learn @property, @staticmethod,\
  \ and how to write your own.\",\n  \"datePublished\": \"2026-04-13\",\n  \"author\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\": {\"@type\"\
  : \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"},\n\
  \  \"url\": \"https://devnook.dev/languages/\"\n}\n</script>"
tags:
- python
- decorators
- functions
- metaprogramming
template_id: lang-v2
title: 'Python Decorators Explained: A Practical Guide with Examples'
---

## The Problem

You need to add logging to twenty different functions across your codebase. Copy-pasting the same logging code into each function creates maintenance nightmares — when the log format changes, you edit twenty functions. The same problem hits when adding authentication checks, performance timing, or caching to multiple functions.

```python
def calculate_total(items):
    print(f"[LOG] Called calculate_total at {datetime.now()}")
    result = sum(item['price'] for item in items)
    print(f"[LOG] calculate_total returned {result}")
    return result

def process_order(order_id):
    print(f"[LOG] Called process_order at {datetime.now()}")
    # ... actual order processing logic
    print(f"[LOG] process_order completed")
    return True

# ... 18 more functions with duplicate logging code
```

Every function now contains three lines of logging mixed with business logic. When you need to add timestamps to the log format, you hunt through every function. When a bug appears in the logging code, you fix it in twenty places. The logging concerns pollute the core function logic.

## The Python Solution: Decorators

Python decorators wrap functions to add behavior without modifying the function's code. A decorator is a function that takes another function and returns a modified version. You apply decorators using the `@` syntax above function definitions.

```python
from datetime import datetime
from functools import wraps

def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Called {func.__name__} at {datetime.now()}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} returned {result}")
        return result
    return wrapper

@log_calls
def calculate_total(items):
    return sum(item['price'] for item in items)

@log_calls
def process_order(order_id):
    # ... actual order processing logic
    return True
```

Each function now contains only its core logic. The `@log_calls` decorator adds logging automatically. Change the log format in one place — the `log_calls` function — and all decorated functions update instantly. The decorator wraps the original function in a `wrapper` function that runs code before and after calling the original.

## How Decorators Work in Python

When Python encounters `@log_calls` above a function definition, it passes the function to `log_calls()` and replaces the original function with the returned wrapper. The syntax `@log_calls` is shorthand for `calculate_total = log_calls(calculate_total)`.

The wrapper function accepts `*args` and `**kwargs` to forward any arguments to the original function. This makes the decorator work with functions that have any signature. The `@wraps(func)` decorator from `functools` preserves the original function's name and docstring — without it, `calculate_total.__name__` would return `"wrapper"` instead of `"calculate_total"`.

Decorators can stack. Multiple decorators apply from bottom to top:

```python
@decorator_one
@decorator_two
def my_function():
    pass
```

This is equivalent to `my_function = decorator_one(decorator_two(my_function))`. The innermost decorator wraps the function first.

## Going Further — Real-World Patterns

**Pattern 1: Parameterized Decorators**

Decorators can accept arguments by adding another layer of nesting. This creates a decorator factory that returns the actual decorator.

```python
def retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed, retrying...")
            return wrapper
        return decorator

@retry(max_attempts=5)
def fetch_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

The `retry` function returns a decorator configured with the specified number of attempts. This pattern appears frequently in web frameworks and API clients.

**Pattern 2: Class-Based Decorators**

Classes can act as decorators by implementing `__call__`. This approach works well when decorators need to maintain state between calls.

```python
class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            self.calls = [call for call in self.calls if now - call < self.period]
            
            if len(self.calls) >= self.max_calls:
                raise Exception(f"Rate limit exceeded: {self.max_calls} calls per {self.period}s")
            
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper

@RateLimiter(max_calls=10, period=60)
def api_call(endpoint):
    return requests.get(endpoint).json()
```

The `RateLimiter` instance stores call timestamps across invocations, enforcing rate limits per decorated function.

**Pattern 3: Built-In Decorators**

Python includes several built-in decorators. The `@property` decorator converts methods into read-only attributes:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def area(self):
        return 3.14159 * self._radius ** 2
    
    @property
    def diameter(self):
        return self._radius * 2

circle = Circle(5)
print(circle.area)      # 78.53975 — called like an attribute, not a method
print(circle.diameter)  # 10
```

The `@staticmethod` and `@classmethod` decorators modify how methods bind to classes. Static methods receive no implicit first argument, while class methods receive the class as their first argument instead of an instance. These are covered in depth in our [Python class methods guide](/languages/python/class-methods).

## What to Watch Out For

**Decorator Order Matters**: When stacking decorators, the order determines which wrapper runs first. A `@cache` decorator above `@log_calls` will cache before logging, while reversing them logs every call even for cached results. Test decorator combinations carefully to ensure they compose as intended.

**Performance Overhead**: Each decorator adds a function call layer. For functions called millions of times in tight loops, this overhead can impact performance. Profile before optimizing, but consider using decorators selectively on high-level functions rather than low-level utilities.

**Debugging Complexity**: Stack traces show wrapper function calls instead of original function names when `@wraps` is missing. Always use `functools.wraps` in custom decorators to preserve function metadata. This makes debugging and introspection work as expected.

## Summary

Python decorators solve the problem of duplicating cross-cutting concerns across multiple functions by wrapping functions to modify their behavior. Instead of copying logging, authentication, or caching code into every function, you write the behavior once in a decorator and apply it with `@decorator_name` syntax. Decorators can accept parameters, maintain state using classes, or stack to combine behaviors. The key principle: modify function behavior without touching the function's source code.

## Related

Learn more about Python functions in our [lambda functions guide](/languages/python/lambda-functions) and [generators tutorial](/languages/python/generators). For hands-on practice writing decorators, try our [Python REPL tool](/tools/python-repl). Check out our [Python functions cheat sheet](/cheatsheets/python-functions) for quick reference on function syntax and patterns.