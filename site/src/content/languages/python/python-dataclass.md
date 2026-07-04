---
title: "Python Dataclass Explained: Fields, Defaults, Frozen"
description: "Learn how python dataclass (python data class) works: field(), default_factory, slots=True, dataclass to dict, and frozen=True, with runnable examples."
category: "languages"
language: "python"
concept: "dataclass"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [python, dataclass, oop, fields, frozen, slots]
related_posts: []
related_tools: []
linkAnchors:
  - "python dataclass"
  - "dataclass in python"
  - "python dataclass examples"
  - "python data class"
published_date: "2026-05-31"
og_image: "/og/languages/python/dataclass.png"
word_count_target: 2600
---

Picture a paper form — the kind HR uses when a new employee joins. The blank form itself holds no data; it just defines which fields exist and what type of information each accepts. Every completed form is an instance that shares the same structure. That's roughly what a python dataclass (or python data class) does for classes.

Before dataclasses arrived in Python 3.7, building a data-carrying class meant writing an `__init__` to assign attributes, a `__repr__` to produce readable output, and an `__eq__` to compare instances — roughly 25 lines of boilerplate that contained zero business logic. The `@dataclass` decorator generates all of that from annotated field declarations. The class definition shrinks from 25 lines to 6, and the generated methods stay in sync automatically when you add or rename fields.

## What the @dataclass Decorator Actually Does

The `@dataclass` decorator is not a code generator in the offline sense — it runs at class definition time and attaches generated methods to the class object. When Python sees `@dataclass` on a class, it scans the class body for variables that carry a type annotation (e.g., `name: str`). It uses those annotations, in order, to construct the following methods:

- `__init__` — accepts each annotated field as a parameter and assigns it to `self`
- `__repr__` — returns a string of the form `ClassName(field=value, ...)`
- `__eq__` — compares two instances field by field

The decorator leaves your existing methods alone. If you define your own `__repr__`, the decorator skips generating one. You can also opt in to optional generated methods with keyword arguments:

- `order=True` — generates `__lt__`, `__le__`, `__gt__`, `__ge__` for sorting
- `frozen=True` — makes the instance immutable after construction
- `slots=True` (Python 3.10+) — generates `__slots__` for lower memory usage

You can inspect what happened after the fact: `dataclasses.fields(MyClass)` returns a tuple of `Field` objects, each describing a field's name, type, and metadata. Nothing is hidden.

## Your First Python Dataclass

Here is the smallest working python dataclass:

```python
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    in_stock: bool = True

laptop = Product(name="ThinkPad X1", price=1299.99)
print(laptop)             # Product(name='ThinkPad X1', price=1299.99, in_stock=True)
print(laptop == Product(name="ThinkPad X1", price=1299.99))  # True
print(laptop == Product(name="ThinkPad X1", price=999.99))   # False
```

`in_stock=True` is a field with a default value. Fields without defaults must come before fields with defaults — the same constraint that applies to function arguments. The `__init__` method the dataclass Python generates from these annotations is exactly equivalent to:

```python
def __init__(self, name: str, price: float, in_stock: bool = True):
    self.name = name
    self.price = price
    self.in_stock = in_stock
```

You get this for free. Annotated class variables that start with an underscore are still treated as fields — there is no automatic visibility filtering. If you want to exclude a variable from the generated methods, use `field(init=False, repr=False, compare=False)`.

## Fields, Defaults, and the field() Function

For scalar defaults — booleans, strings, numbers — assigning them directly works fine. For mutable defaults — lists, dicts, sets — you must use `field(default_factory=...)`. Assigning a mutable directly raises a `ValueError` at class definition time. This distinction holds across virtually all python data classes you write — the rule tracks mutability, not which specific field happens to hold the value.

The `field()` function gives you per-field control beyond just the default value. Here is a reference of its most useful options for a dataclass field:

| Option | Type | Purpose |
|---|---|---|
| `default` | any | Scalar default (same as direct assignment) |
| `default_factory` | callable | Returns a fresh default value per instance |
| `init` | bool | `False` → exclude from `__init__`; set in `__post_init__` |
| `repr` | bool | `False` → exclude from `__repr__` output |
| `compare` | bool | `False` → exclude from `__eq__` and comparison operators |
| `hash` | bool or None | Override hash inclusion independently of `compare` |
| `kw_only` | bool (3.10+) | `True` → keyword-only argument in `__init__` |

Here is a realistic model that uses several of these:

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Order:
    order_id: str
    customer_id: str
    line_items: list = field(default_factory=list)
    tags: set = field(default_factory=set)
    total: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow, compare=False)

o1 = Order(order_id="ORD-001", customer_id="cust_9182")
o1.line_items.append({"sku": "PRD-100", "qty": 2, "unit_price": 49.99})
o2 = Order(order_id="ORD-001", customer_id="cust_9182")

print(o1 == o2)   # True — created_at is excluded from __eq__
```

The `created_at` field uses `compare=False` — two orders with the same IDs and items compare as equal regardless of when they were created. This is often what deduplication logic requires. The `line_items` and `tags` fields each get a fresh empty container per instance, not a shared object.

## Converting a Python Dataclass to a Dict

The `dataclasses.asdict()` helper converts a python dataclass to a plain Python dictionary, recursively. It handles nested dataclasses, lists of dataclasses, and dicts containing dataclasses.

```python
from dataclasses import dataclass, field, asdict
import json

@dataclass
class Address:
    street: str
    city: str
    postal_code: str

@dataclass
class Customer:
    customer_id: str
    name: str
    address: Address
    tags: list = field(default_factory=list)

customer = Customer(
    customer_id="cust_4421",
    name="Priya Sharma",
    address=Address(street="12 Baker St", city="London", postal_code="NW1 6XE"),
    tags=["vip", "eu-gdpr"],
)

data = asdict(customer)
print(json.dumps(data, indent=2))
```

The `asdict()` call above produces a fully nested dictionary — `data["address"]` is `{"street": "12 Baker St", "city": "London", "postal_code": "NW1 6XE"}`, not an `Address` instance. Each level is a new dict or list, not a reference to the internal objects, so mutating the result does not affect the dataclass.

For flat dataclasses, `vars(instance)` is a faster alternative that skips recursion, though it returns a live view of `__dict__` rather than a deep copy. The reverse direction has no built-in equivalent. For flat structures, `Customer(**data)` works if `data` contains exactly the right keys. For nested structures where `data["address"]` is a dict rather than an `Address` instance, you need a manual factory or a library like [Pydantic](https://docs.pydantic.dev/) that handles coercion.

If reshaping the resulting dict is part of your workflow, see the [Python dictionary comprehension guide](/languages/python/dictionary-comprehension/) for clean transformation patterns.

## Using __post_init__ for Validation and Derived Fields

`__post_init__` runs after the generated `__init__` finishes. This is where you put validation logic, computed attributes, or anything that depends on multiple fields being set.

```python
from dataclasses import dataclass, field
import re as re_mod

@dataclass
class EmailAddress:
    raw: str
    normalized: str = field(init=False, repr=False)
    domain: str = field(init=False)

    def __post_init__(self):
        cleaned = self.raw.strip().lower()
        if not re_mod.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', cleaned):
            raise ValueError(f"Not a valid email address: {self.raw!r}")
        self.normalized = cleaned
        self.domain = cleaned.split('@')[1]

addr = EmailAddress(raw="  Alice@Example.COM  ")
print(addr.normalized)   # alice@example.com
print(addr.domain)       # example.com
print(addr)              # EmailAddress(raw='  Alice@Example.COM  ')
```

The `normalized` and `domain` fields use `init=False` — they do not appear in the constructor. The caller passes only `raw`. `normalized` also uses `repr=False`, so the `__repr__` output shows just the raw input.

When inheriting from a parent dataclass, call `super().__post_init__()` at the top of your override so any parent validation runs first. For a broader look at validation patterns and exception handling in Python, see the [Python error handling guide](/languages/python/error-handling/).

## frozen=True: Immutable Dataclasses

Adding `frozen=True` to the decorator makes instances immutable after creation:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_from_origin(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

p = Point(x=3.0, y=4.0)
print(p.distance_from_origin())   # 5.0
```

Attempting `p.x = 10.0` after construction raises `dataclasses.FrozenInstanceError`. Frozen dataclasses are hashable, which is the main reason to reach for them. You can use frozen instances as dictionary keys, store them in sets, and rely on `functools.lru_cache` with them as arguments:

```python
seen = set()
seen.add(Point(x=1.0, y=2.0))
seen.add(Point(x=1.0, y=2.0))
print(len(seen))   # 1 — set deduplication works because Point is hashable
```

One trade-off: `__post_init__` cannot assign attributes using regular syntax in a frozen dataclass — the freeze check fires immediately. The workaround is `object.__setattr__(self, 'field_name', value)`, which bypasses the freeze. If `__post_init__` logic grows complex, consider whether a frozen dataclass is still the right tool or whether a regular class with a `@classmethod` factory is cleaner.

## dataclass slots: Lower Memory, Faster Attribute Access

Python 3.10 added `slots=True` as a decorator argument, distinct from `frozen=True` and combinable with it. Where `frozen=True` controls mutability, dataclass slots controls how the instance stores its attributes in memory.

By default, every instance of a Python class — dataclasses included — carries a `__dict__` to hold its attributes. That `__dict__` is flexible (you can attach new attributes at runtime) but costs memory per instance and adds a dictionary lookup on every attribute access. `slots=True` generates a `__slots__` tuple instead, so instances store fields in a fixed-size, dict-free layout:

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Pixel:
    x: int
    y: int
    color: str = "black"

p = Pixel(x=10, y=20)
print(p.x, p.y, p.color)   # 10 20 black

# p.__dict__ raises AttributeError — there's no per-instance dict to inspect
# p.z = 5 raises AttributeError — you can't add attributes outside the declared fields
```

For a class you instantiate thousands or millions of times — parsed log lines, grid cells, graph nodes — slots meaningfully cut per-instance memory and speed up attribute reads, since Python resolves a slot by fixed offset instead of a dict lookup. The trade-off is rigidity: a slotted dataclass can't gain attributes dynamically, and mixing in a plain (non-dataclass) class that itself defines instance attributes without its own `__slots__` silently reintroduces a `__dict__` on the combined class — negating the memory savings without raising an error. If you need `slots`-like behavior on Python versions older than 3.10, you have to declare `__slots__` by hand, which is far more error-prone since a manually written `__slots__` conflicts with any class-level default value sharing the same field name — the built-in `slots=True` handles that interaction for you. The [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) covers the version-gated behavior in detail.

## Common Bugs with Python Dataclass

**Bug 1: Using a mutable default directly.**

```python
from dataclasses import dataclass

@dataclass
class Playlist:
    title: str
    tracks: list = []   # Raises ValueError at class definition time
```

Python raises `ValueError: mutable default <class 'list'> for field tracks is not allowed: use default_factory`. This is protective — if Python silently accepted the list, every `Playlist` instance would share the same list object, and appending to one would affect all. The fix is always `field(default_factory=list)`.

The rule is simpler than it looks once you separate the two cases. An immutable default value — a number, string, `bool`, `None`, or a tuple of immutables — is safe to assign directly, because there's no shared mutable state for two instances to accidentally alias. Only mutable default values — lists, dicts, sets, or other dataclass instances that aren't frozen — need `default_factory` to guarantee each instance gets its own fresh object.

**Bug 2: Inheritance field ordering conflicts.**

```python
from dataclasses import dataclass

@dataclass
class Base:
    name: str
    active: bool = True  # field with a default

@dataclass
class Employee(Base):
    department: str      # no default — TypeError at class definition
```

This raises `TypeError: non-default argument 'department' follows default argument`. The generated `__init__` for `Employee` would need to place `department` before `active`, but the inheritance chain prevents reordering parent fields. Three clean fixes: give `department` a default, use `kw_only=True` on the field (Python 3.10+), or rethink whether inheritance is the right model here. Python's [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) covers the `kw_only` field option in detail.

**Bug 3: Sorting without order=True.**

If you try to sort a list of dataclass instances without `order=True`, you get `TypeError: '<' not supported`. The fix is `@dataclass(order=True)`, which generates comparison operators using field values in declaration order.

## When Not to Use @dataclass

Python dataclasses are not the universal answer to structured data.

**Reach for `typing.NamedTuple`** when you need tuple unpacking, positional indexing (`record[0]`), or interoperability with code that expects tuples. A python namedtuple supports type annotations and default values just like a dataclass, but it's immutable by default, has no per-instance `__dict__`, and ships with built-in `_asdict()`, `_replace()`, and `_fields` helpers instead of a decorator API. That makes a named tuple a strong choice for small, read-only records you pass straight into tuple-expecting functions — CSV rows, coordinate pairs, function results with named fields — where you want positional access and don't need methods beyond simple field access.

**Reach for `TypedDict`** when your data stays as a plain dictionary through its entire lifecycle — JSON parsing, boto3 responses, FastAPI request bodies. A `TypedDict` in Python adds static type checking for dict keys and value types without changing runtime behavior at all: a `TypedDict` instance is still a regular `dict`, so `isinstance(data, dict)` is `True`, and there's no generated `__init__` or attribute access. That's the core difference from a dataclass — `TypedDict` declares shape for the type checker only, while `@dataclass` gives you a real object with attributes, `__eq__`, and room for methods. Converting a dict to a dataclass and back with `asdict()` just adds overhead when the dict representation is what you actually need.

**Reach for Pydantic's `BaseModel`** when you need runtime type coercion and validation. A python dataclass with a `str` annotation will happily accept an integer at runtime — no error. Pydantic validates on construction and raises structured errors. The trade-off is a dependency and slightly higher instantiation overhead. Teams that want `@dataclass` syntax without giving up validation can reach for `pydantic.dataclasses.dataclass` instead — a pydantic dataclass decorator that's largely a drop-in replacement for the standard library one, adding coercion and validation while keeping the same field-declaration style. It doesn't inherit from `BaseModel` and skips some `BaseModel`-only features like arbitrary config classes, but it's a practical middle ground when you need dataclass ergonomics with runtime checks.

**Reach for a plain class** when behavior dominates data. If the class has 15 methods and 2 fields, the boilerplate saved by `@dataclass` is negligible, and the decorator becomes noise. Understanding when to reach for different class patterns is covered in depth in the [Python design patterns guide](/languages/python/design-patterns/).

### Dataclass vs NamedTuple vs TypedDict vs Dict vs Pydantic

| Type | Mutable | Runtime validation | Extra methods | Best for |
|---|---|---|---|---|
| `@dataclass` | Yes (unless `frozen=True`) | No | Yes | Domain objects that carry behavior |
| `NamedTuple` | No | No | Limited (`_asdict`, `_replace`) | Small, tuple-compatible read-only records |
| `TypedDict` | Yes (it's a dict) | No — type-checker only | No | Data that stays a dict (JSON, API payloads) |
| plain `dict` | Yes | No | No | Dynamic or short-lived key/value data |
| Pydantic `BaseModel` | Yes | Yes | Yes | Validated data crossing a trust boundary |

## Frequently Asked Questions

### What is a dataclass in Python?

A dataclass in Python is a class decorated with `@dataclass` from the standard library `dataclasses` module, available since Python 3.7. The decorator inspects annotated class variables and automatically generates `__init__`, `__repr__`, and `__eq__`. Fields with defaults must follow fields without defaults. The result is a class that behaves like a normal class but requires far less boilerplate for data-carrying types.

### How do I convert a Python dataclass to a dict?

Use `dataclasses.asdict(instance)`. It recursively converts the dataclass and any nested dataclasses into plain dictionaries. For flat structures, `vars(instance)` is a faster alternative that returns a live view of `__dict__`. To go the other direction, use `MyClass(**data_dict)` for flat structures with exactly matching keys. There is no built-in equivalent of `from_dict()` for nested structures.

### What does frozen=True do in a Python dataclass?

`@dataclass(frozen=True)` makes the instance immutable: any attempt to set an attribute after construction raises `FrozenInstanceError`. It also makes the instance hashable by default, so frozen dataclass instances can be used as dictionary keys or stored in sets. Inside `__post_init__`, attribute assignment must use `object.__setattr__(self, name, value)` to bypass the freeze.

### What is python dataclass field()?

`field()` from the `dataclasses` module configures individual fields beyond a simple default. Key options: `default_factory` provides a callable that creates a fresh mutable value per instance; `init=False` excludes a field from the constructor; `repr=False` excludes it from `__repr__`; `compare=False` excludes it from equality checks. Use `field()` whenever you need behavior that a bare default value cannot express.

### Can I add methods to a Python dataclass?

Yes. `@dataclass` only generates dunder methods — it does not remove or restrict user-defined methods. You can add instance methods, class methods, static methods, and properties freely. The decorator only acts on annotated class-level attributes and the missing dunder methods it is configured to generate.

### How does python dataclass __post_init__ work?

`__post_init__` is a regular method that the generated `__init__` calls as its final step, after assigning all field values. Use it for cross-field validation, raising `ValueError` for invalid combinations, or computing derived fields marked with `init=False`. In frozen dataclasses, use `object.__setattr__(self, name, value)` inside `__post_init__` rather than direct assignment.

## Where to Go Next

Dataclasses handle the structural side of domain modeling. Once your models are in place, two closely related topics tend to come up quickly.

The first is how to format dataclass fields cleanly in output — f-strings and the `__format__` protocol are covered in the [Python string formatting guide](/languages/python/string-formatting/), which also explains how format specs work for numeric fields like prices and percentages.

The second is design patterns that structure how multiple dataclasses interact. The repository, factory, and value-object patterns each have natural dataclass-based implementations — see the [Python design patterns guide](/languages/python/design-patterns/) for worked examples.

For a full accounting of what `@dataclass` supports — including `InitVar`, `ClassVar`, `slots=True`, and the `__dataclass_fields__` introspection API — the official [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) is the authoritative reference. [PEP 557](https://peps.python.org/pep-0557/), which introduced dataclasses, explains the design rationale, including why mutable defaults are rejected at class definition time rather than at instantiation.
