---
category: languages
concept: design-patterns
description: Learn how to implement design patterns in Python using first-class functions
  and modules. Covers Strategy, Observer, Singleton, and common pitfalls.
difficulty: advanced
language: python
og_image: /og/languages/python/design-patterns.png
published_date: '2026-04-17'
related_cheatsheet: ''
related_posts:
- how-to-use-decorators-in-python
- what-is-a-closure-in-python
related_tools: []
tags:
- python
- design-patterns
- architecture
- oop
template_id: lang-v1
title: 'How to Implement Design Patterns in Python: A Modern Guide'
---

Implementing design patterns in [Python](/languages/python) often looks fundamentally different from Java or C++, because Python's dynamic typing, first-class functions, and module system make many patterns far more concise — and some patterns unnecessary altogether.

## What are Design Patterns in Python?

Design patterns are reusable solutions to recurring software architecture problems, first formalized by the Gang of Four in their 1994 book *Design Patterns: Elements of Reusable Object-Oriented Software*. The GoF catalogued 23 patterns divided into three families: creational (how objects are made), structural (how they are composed), and behavioral (how they communicate).

In Python, the implementation of these patterns diverges significantly from their canonical [Java](/languages/java) form. Java requires every behavioral abstraction to be expressed through an interface and a concrete class — two files minimum. Python can express the same abstraction with a single function, because functions are first-class objects with `__call__` semantics. A Strategy pattern that takes 50 lines in Java collapses to 5 in Python. This isn't just syntactic convenience; it reflects a deeper difference in how the languages think about behavioral abstraction.

Understanding design patterns in Python means knowing both the pattern's intent (which is language-agnostic) and the idiomatic Pythonic way to express it (which often bears little resemblance to the GoF code samples written for statically typed languages).

## Why Python Developers Need Design Patterns

As a codebase grows from a 200-line script into a 50,000-line application maintained by a team, informal ad hoc structure breaks down. Without deliberate architectural patterns, the codebase accumulates what engineers call *structural debt* — tangled dependencies, feature flags embedded in business logic, and components that must know too much about each other's internals.

Design patterns address specific, recurring failure modes. When a feature requires reaching into five different modules to make a change, the **Facade** pattern consolidates that surface into a single entry point. When a system needs to notify multiple downstream services whenever state changes — say, invalidating a cache, triggering a webhook, and writing an audit log whenever a record is updated — the **Observer** pattern decouples the source of change from its consequences. When a payment system needs to support Stripe, PayPal, and Apple Pay without duplicating processing logic, the **Strategy** pattern encapsulates each provider behind a common callable interface.

The practical value isn't just clean code — it's predictability. When a new engineer joins a team and sees that a class implements the Observer pattern, they immediately understand that it has subscribers and emits notifications. Shared vocabulary accelerates code comprehension during reviews, debugging, and onboarding.

## Basic Syntax

The **Strategy Pattern** demonstrates Python's departure from GoF idioms most clearly. In Java, you define an interface and then create a concrete class for each strategy. In Python, any callable — a function, a lambda, a class with `__call__` — serves as a strategy directly.

```python
# A context class that delegates work to an injected strategy function
class PaymentProcessor:
    def __init__(self, strategy_func):
        # Store the callable — any function matching the signature works
        self._strategy = strategy_func

    def execute_payment(self, amount: float) -> str:
        # Delegate to the injected strategy
        return self._strategy(amount)


# Strategies are plain functions — no abstract classes needed
def stripe_strategy(amount: float) -> str:
    return f"Charged ${amount:.2f} via Stripe API."


def paypal_strategy(amount: float) -> str:
    return f"Charged ${amount:.2f} via PayPal SDK."


def crypto_strategy(amount: float) -> str:
    return f"Transferred ${amount:.2f} worth of BTC on-chain."


# Swap strategies at runtime with zero structural changes
processor = PaymentProcessor(stripe_strategy)
print(processor.execute_payment(99.99))  # Charged $99.99 via Stripe API.

processor._strategy = crypto_strategy
print(processor.execute_payment(99.99))  # Transferred $99.99 worth of BTC on-chain.
```

This code avoids defining `IPaymentStrategy`, `StripeStrategy(IPaymentStrategy)`, and `PayPalStrategy(IPaymentStrategy)` as separate classes. Because Python functions are objects, passing `stripe_strategy` directly to `PaymentProcessor` is semantically identical to passing an instance of a class with a `process()` method — but with a fraction of the boilerplate.

## A Practical Example

The **Observer Pattern** (also called Pub/Sub) is one of the most practically useful patterns in Python applications, particularly for event-driven architectures where multiple subsystems must react to state changes without creating tight coupling between them.

```python
from typing import Callable, List


class OrderService:
    """Manages order state and notifies subscribers on changes."""

    def __init__(self):
        # Each event type maps to a list of subscriber callbacks
        self._subscribers: dict[str, List[Callable]] = {
            "order_placed": [],
            "order_shipped": [],
        }

    def subscribe(self, event: str, callback: Callable) -> None:
        """Register a callback for a specific event."""
        if event not in self._subscribers:
            raise ValueError(f"Unknown event: {event}")
        self._subscribers[event].append(callback)

    def place_order(self, order_id: str, items: list) -> None:
        """Process a new order and notify all registered observers."""
        print(f"[OrderService] Processing order {order_id} with {len(items)} items.")
        # Notify every subscriber — OrderService has no knowledge of what they do
        for callback in self._subscribers["order_placed"]:
            callback(order_id, items)

    def ship_order(self, order_id: str, tracking_number: str) -> None:
        """Mark an order as shipped and notify all registered observers."""
        print(f"[OrderService] Shipping order {order_id}.")
        for callback in self._subscribers["order_shipped"]:
            callback(order_id, tracking_number)


# Independent observers — completely decoupled from OrderService internals
def send_confirmation_email(order_id: str, items: list) -> None:
    print(f"[Email] Confirmation sent for order {order_id}.")


def update_inventory(order_id: str, items: list) -> None:
    print(f"[Inventory] Stock reduced for {len(items)} items in order {order_id}.")


def push_tracking_notification(order_id: str, tracking: str) -> None:
    print(f"[Push] Tracking #{tracking} sent to customer for order {order_id}.")


# Wire up the system
service = OrderService()
service.subscribe("order_placed", send_confirmation_email)
service.subscribe("order_placed", update_inventory)
service.subscribe("order_shipped", push_tracking_notification)

service.place_order("ORD-7821", ["Laptop", "Mouse"])
service.ship_order("ORD-7821", "UPS-98423")
```

This design means that switching from SendGrid to AWS SES for email requires changing only `send_confirmation_email` — the `OrderService` class is untouched. Adding a new Slack notification for shipments means registering one additional function. The pattern scales to any number of subscribers with zero changes to the core business logic that drives them.

## Common Mistakes

**Mistake 1: Forcing Java idioms into Python**

Developers with Java backgrounds often reach for Abstract Base Classes (ABCs) and full interface hierarchies even when Python has no need for them. A Command pattern that passes functions as arguments doesn't need an `AbstractCommand` base class with an abstract `execute()` method. The Python type system is structural, not nominal — any callable with the right signature suffices.

The fix is to use `typing.Protocol` when you genuinely need to document an interface for a type checker, and otherwise just accept plain callables. Reserve formal ABCs for cases where you want to enforce method implementation at instantiation time and runtime `isinstance` checks are part of the design.

**Mistake 2: Over-engineering the Singleton**

Python developers frequently implement Singletons using `__new__` overrides with threading locks, following Java examples. This is fragile and hard to test. Python has a simpler built-in Singleton: the module.

When the Python interpreter imports a module for the first time, it executes the module body and caches the resulting module object in `sys.modules`. Every subsequent `import` returns the cached object. A `db_connection.py` module that instantiates a connection pool at the bottom of the file is a native Singleton — thread-safe, GC-friendly, and trivially testable by re-importing.

**Mistake 3: Using decorators for stateful logic**

Python's decorator syntax is elegant, but nesting multiple stateful decorators on a single method creates debugging nightmares. When an exception surfaces three decorator layers deep, the stack trace becomes difficult to parse. More importantly, using decorators to manage mutable instance state is semantically surprising to readers who expect decorators to handle cross-cutting concerns (logging, rate limiting, auth), not core data flow.

The fix is to reserve decorators for pure cross-cutting concerns and use explicit class composition for state-carrying behavior.

## Strategy vs. State Pattern

These two patterns are structurally similar — both involve swapping behaviors on a context object — but their intent is different. **Strategy** is driven by an *external decision*: the client code chooses which behavior to inject (the user selects Stripe as their payment method). **State** is driven by *internal transitions*: the object itself changes its behavior in response to its own state (a vending machine moves from `IdleState` to `DispensingState` after a coin is inserted).

In code, the difference is where the swap happens. With Strategy, the caller invokes `processor._strategy = crypto_strategy`. With State, the object calls `self._state = DispensingState()` internally, often inside one of its own methods. If external code is swapping the behavior, it's Strategy. If the object is transitioning itself, it's State.

## Under the Hood: Performance & Mechanics

Python's dynamic dispatch model has concrete performance implications when you build deeply abstracted pattern hierarchies.

Every attribute access in Python (e.g., `obj.method`) goes through `__getattribute__`, which performs a dictionary lookup in `obj.__dict__`, then `type(obj).__dict__`, then the MRO chain. This is an optimized C-level operation in CPython, but it is still more expensive than a direct virtual table dispatch in C++. For Strategy patterns called millions of times in a tight loop (e.g., sorting comparators on large datasets), this overhead is measurable.

When performance is critical, use `__slots__` on your context class to replace the per-instance `__dict__` with a fixed-size array, reducing attribute lookup overhead and memory footprint. Alternatively, inline the strategy function into a compiled extension (Cython or ctypes) for hot paths.

For Proxy and Adapter patterns implemented with `getattr`/`setattr`, be aware that intercepting attribute access via `__getattr__` adds a Python-level frame to every property access. In highly reflective metaprogramming (dynamic proxies that forward N attributes to a wrapped object), this can degrade inner-loop performance by 5–10x compared to direct attribute access. Profile before generalizing.

## Advanced Edge Cases

**Edge Case 1: Metaclass Singletons and Memory Leaks**

Metaclass-based Singletons store instances in a class-level dictionary, which creates strong references that prevent garbage collection.

```python
class SingletonMeta(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # This dict entry holds a strong reference to the instance forever
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DataCache(metaclass=SingletonMeta):
    def __init__(self):
        self.data = {}  # Could grow to hundreds of MB
```

If `DataCache` accumulates a large `self.data` dictionary at runtime, the `_instances` dict inside `SingletonMeta` will prevent the garbage collector from reclaiming that memory even if all user-facing references to the cache are deleted. The solution is to use weak references (`weakref.ref`) to store the instance in `_instances`, allowing GC to collect it when no other references exist.

**Edge Case 2: Factory Late Binding in Closures**

When building a Factory pattern using closures inside a loop, Python's late-binding closure semantics produce counterintuitive results.

```python
def button_factory():
    buttons = []
    for i in range(3):
        # BUG: The lambda captures the variable 'i', not its current value
        buttons.append(lambda: f"Button {i}")
    return buttons

btns = button_factory()
print(btns[0]())  # Prints "Button 2" — NOT "Button 0"!
print(btns[1]())  # Prints "Button 2"
print(btns[2]())  # Prints "Button 2"
```

All three lambdas reference the same `i` variable in the enclosing scope. After the loop completes, `i` holds its final value of `2`. Every lambda evaluates `i` at call time, not at definition time.

The fix is to bind the current value explicitly using a default argument:

```python
buttons.append(lambda x=i: f"Button {x}")
```

Default argument values are evaluated at function *definition* time, so each lambda captures the correct value at the moment of creation.

## Testing Design Patterns in Python

The primary value of patterns like Strategy and Observer from a testing perspective is that they eliminate hidden dependencies, making behavior injectable and therefore mockable.

```python
import unittest


def mock_payment_strategy(amount: float) -> str:
    return "MOCK_OK"


class TestPaymentProcessor(unittest.TestCase):
    def test_delegates_to_strategy(self):
        # No Stripe API key, no network call — just inject the mock function
        processor = PaymentProcessor(mock_payment_strategy)
        result = processor.execute_payment(100.0)
        self.assertEqual(result, "MOCK_OK")

    def test_strategy_is_replaceable(self):
        processor = PaymentProcessor(stripe_strategy)
        processor._strategy = mock_payment_strategy
        result = processor.execute_payment(50.0)
        self.assertEqual(result, "MOCK_OK")


if __name__ == "__main__":
    unittest.main()
```

Because the Strategy pattern accepts any callable, there is no need for `unittest.mock.patch`, no monkey-patching of global imports, and no dependency on external services. The architectural decision to inject behavior rather than hardcode it pays dividends directly in test simplicity.

## Quick Reference

- **Functions are first-class:** Pass functions directly instead of wrapping them in Strategy classes.
- **Modules are Singletons:** Use module-level instances rather than metaclass trickery.
- **Late binding:** Use `lambda x=i: ...` to capture loop variable values in factories.
- **ABCs vs. Protocols:** Use `typing.Protocol` for lightweight structural interfaces; ABCs for runtime enforcement.
- **Avoid decorator state:** Decorators for cross-cutting concerns; composition for business state.

## Next Steps

To fully understand how Python enables Strategy and Observer patterns through its function model, study closures in Python — they are the mechanism that lets functions carry environment state across call sites. For patterns that manipulate class behavior at definition time, decorators in Python cover the metaprogramming tools that make Python patterns uniquely expressive.