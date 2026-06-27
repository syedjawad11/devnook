---
title: "C++ Virtual Functions: Polymorphism and Abstract Classes"
description: "Learn how C++ virtual functions enable runtime polymorphism. Covers abstract classes, pure virtual functions, vtables, and common pitfalls to avoid."
category: "languages"
language: "cpp"
concept: "oop-concepts"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [cpp, oop-concepts, virtual-functions, polymorphism, abstract-class]
related_posts: []
related_tools: []
linkAnchors:
  - "cpp virtual function"
  - "virtual function in C++"
  - "pure virtual function"
published_date: "2026-06-27"
og_image: "/og/languages/cpp/oop-concepts.png"
word_count_target: 2224
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "C++ Virtual Functions: Polymorphism and Abstract Classes",
    "description": "Learn how C++ virtual functions enable runtime polymorphism. Covers abstract classes, pure virtual functions, vtables, and common pitfalls to avoid.",
    "datePublished": "2026-06-27",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/cpp/oop-concepts/",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between a virtual function and a pure virtual function in C++?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "A virtual function has a body in the base class providing a default implementation that derived classes may override. A pure virtual function (= 0) has no body and forces every concrete derived class to supply one. A class with any pure virtual function is abstract and cannot be instantiated."
        }
      },
      {
        "@type": "Question",
        "name": "Does using virtual functions have a performance cost in C++?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes, but typically small. Each virtual call follows a vptr to a vtable — one extra pointer dereference per call. The larger cost is that virtual calls cannot be inlined by the compiler. For most application code the overhead is negligible."
        }
      },
      {
        "@type": "Question",
        "name": "Can you have a virtual constructor in C++?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "No. Constructors cannot be virtual because the vtable does not exist when the constructor runs. The common workaround is a virtual clone() method or a factory function that returns a base class pointer to the right derived type."
        }
      }
    ]
  }
  </script>
---
Imagine you have a `Shape` base class with a `draw()` method, and both `Circle` and `Rectangle` inherit from it. Without virtual functions, calling `draw()` through a base class pointer always invokes `Shape::draw()`, regardless of what object you're actually holding. A cpp virtual function changes that: C++ checks the real type at runtime and calls the right override. That one keyword unlocks runtime polymorphism, and this article covers exactly how it works — from vtable mechanics to pure virtual functions and abstract classes.

## How a cpp virtual function Works Under the Hood

When you mark a function `virtual`, the compiler builds a **vtable** (virtual function table) for that class. A vtable is a per-class lookup table: each slot maps a virtual function name to the address of the actual implementation for that class. Every class that declares or inherits a virtual function gets its own vtable.

Each object of a polymorphic class carries a hidden pointer — the **vptr** — that points to its class's vtable. When you call a virtual function through a pointer or reference, C++ follows the vptr to the vtable and dispatches to the stored address. This extra indirection happens at runtime, which is what makes it *dynamic dispatch*.

Here's what the dispatch path looks like at a conceptual level:

```cpp
Shape* shape = new Circle();
shape->draw();
// C++ follows: shape.vptr -> Circle's vtable -> Circle::draw() -> call it
```

The mechanism is deterministic. If a method is not marked `virtual`, the compiler resolves the call at compile time based on the pointer type — always `Shape::draw()`, every time, even if the underlying object is a `Circle`. That's static dispatch, and it's the silent default that trips up most C++ newcomers who expect polymorphism without the keyword.

A concrete detail worth knowing: every object of a class with virtual functions carries a hidden 8-byte vptr on 64-bit systems. The vtable itself lives in read-only memory and is shared across all instances of a class. The per-object overhead is one pointer; the per-call overhead is one extra dereference.

## Your First cpp virtual function: A Minimal Working Example

Here's the smallest version that demonstrates virtual dispatch in action:

```cpp
#include <iostream>

class Shape {
public:
    virtual void draw() const {
        std::cout << "Drawing a generic shape\n";
    }
    virtual ~Shape() = default;
};

class Circle : public Shape {
public:
    void draw() const override {
        std::cout << "Drawing a circle\n";
    }
};

class Rectangle : public Shape {
public:
    void draw() const override {
        std::cout << "Drawing a rectangle\n";
    }
};

int main() {
    Shape* shapes[] = { new Circle(), new Rectangle(), new Shape() };
    for (Shape* s : shapes) {
        s->draw();   // resolved at runtime based on actual type
    }
    for (Shape* s : shapes) delete s;
    return 0;
}
// Output:
// Drawing a circle
// Drawing a rectangle
// Drawing a generic shape
```

Two details to note. The `override` specifier on derived methods is optional but valuable — it tells the compiler "this is intended to override a base method" and catches signature mismatches at compile time. Without `override`, a typo in the method name silently creates a new method instead of an override, and no warning is issued. The virtual destructor on `Shape` is not optional for polymorphic base classes — skipping it causes undefined behavior when deleting derived objects through a base pointer. That pitfall gets its own section below.

## Pure Virtual Functions and Abstract Classes

A **pure virtual function** has no implementation in the base class. You declare it with `= 0`:

```cpp
#include <string>

class Renderer {
public:
    virtual void render(const std::string& scene_name) = 0;
    virtual int get_frame_count() const = 0;
    virtual ~Renderer() = default;
};
```

`Renderer` is now an **abstract class** — you cannot instantiate it directly. Any derived class that fails to implement all pure virtual functions also becomes abstract and cannot be instantiated. This gives you a strict interface contract enforced at compile time.

Per the [C++ abstract class specification on cppreference](https://en.cppreference.com/w/cpp/language/abstract_class), abstract classes cannot be used as the type of an object, but you can freely hold pointers and references to them. The constraint is on instantiation, not on use through a base type.

Why use pure virtual instead of a regular virtual with an empty body? A regular virtual function with an empty body is a silent default: a derived class that forgets to implement it compiles fine and calls the empty base version — often a subtle bug that's hard to trace. A pure virtual function turns that omission into a compile error. The contract is enforced at the language level, not by convention.

```cpp
class OpenGLRenderer : public Renderer {
public:
    void render(const std::string& scene_name) override {
        std::cout << "OpenGL rendering: " << scene_name << "\n";
    }
    int get_frame_count() const override { return frame_count_; }
private:
    int frame_count_ = 0;
};

// Renderer r;           // compile error: cannot instantiate abstract class
OpenGLRenderer renderer;       // fine — all pure virtuals implemented
renderer.render("outdoor_scene");
```

## Runtime Polymorphism in Practice

Here's how virtual dispatch appears in a real-world scenario — a logging system where the calling code doesn't need to know which concrete backend is active:

```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <memory>

class Logger {
public:
    virtual void log(const std::string& message) = 0;
    virtual ~Logger() = default;
};

class ConsoleLogger : public Logger {
public:
    void log(const std::string& message) override {
        std::cout << "[CONSOLE] " << message << "\n";
    }
};

class FileLogger : public Logger {
public:
    explicit FileLogger(const std::string& filepath) : filepath_(filepath) {}
    void log(const std::string& message) override {
        std::ofstream file(filepath_, std::ios::app);
        file << "[FILE] " << message << "\n";
    }
private:
    std::string filepath_;
};

void emit_event(const std::vector<std::unique_ptr<Logger>>& loggers,
                const std::string& event) {
    for (const auto& logger : loggers) {
        logger->log(event);   // vtable dispatch — each logger handles it differently
    }
}

int main() {
    std::vector<std::unique_ptr<Logger>> loggers;
    loggers.push_back(std::make_unique<ConsoleLogger>());
    loggers.push_back(std::make_unique<FileLogger>("app.log"));

    emit_event(loggers, "server_started");
    emit_event(loggers, "request_received");
    return 0;
}
```

`emit_event` doesn't know what concrete logger it holds — it calls `log()` and the vtable resolves the rest. Add a `NetworkLogger` or `MetricsLogger` later and `emit_event` stays unchanged. That's the practical payoff of runtime polymorphism: the calling site is insulated from type details.

When refactoring existing code to introduce virtual dispatch, using a [diff viewer](/tools/diff-viewer/) to compare the before and after versions helps confirm you changed exactly what you intended without silently altering method signatures elsewhere.

## Three Virtual Function Pitfalls Worth Knowing

**Pitfall 1: Missing virtual destructor**

```cpp
class Connection {
public:
    ~Connection() {}   // not virtual — bug waiting to happen
};

class DatabaseConnection : public Connection {
    std::vector<std::string> query_cache_;
public:
    ~DatabaseConnection() { /* flushes cache to disk */ }
};

Connection* conn = new DatabaseConnection();
delete conn;  // calls Connection::~Connection() only
              // DatabaseConnection::~DatabaseConnection() never runs
              // query_cache_ is never destroyed
```

When you delete through a base class pointer and the destructor is not virtual, only the base destructor runs. Resources owned by the derived class go unreclaimed — a memory leak, or worse if the destructor releases locks or file handles. Fix: always declare `virtual ~Base() = default` on any base class intended for polymorphic use. It costs nothing.

**Pitfall 2: Calling virtual functions in constructors or destructors**

Virtual dispatch does not work during construction or destruction. When a derived object's constructor runs, the vptr points to the base class vtable because the derived class isn't fully initialized yet. Calling a virtual function from a base constructor invokes the base version, not the override.

```cpp
class Config {
public:
    Config() { load_settings(); }      // calls Config::load_settings(), NOT AppConfig::
    virtual void load_settings() {}
};

class AppConfig : public Config {
public:
    AppConfig() : Config() {}
    void load_settings() override { /* loads from file */ }
};

AppConfig cfg;   // load_settings() fires inside Config::Config() — base version runs, not AppConfig::
```

The fix is a factory function or explicit two-phase initialization: construct the object, then call `load_settings()` on the fully initialized instance.

**Pitfall 3: Hiding instead of overriding due to a signature mismatch**

```cpp
class EventHandler {
public:
    virtual void handle(int event_id) {}
};

class ClickHandler : public EventHandler {
public:
    void handle(double event_id) {}   // different type — hides, does NOT override
};

EventHandler* handler = new ClickHandler();
handler->handle(42);   // calls EventHandler::handle(int), not ClickHandler::handle(double)
```

`ClickHandler::handle` takes a `double`, not an `int`. Different parameter type means no override happens — the vtable entry for `handle(int)` still points to `EventHandler::handle`. Add `override` and the compiler catches this at compile time rather than at runtime. Use `override` on every intended override, without exception.

## When Virtual Functions Are the Wrong Tool

**When the hierarchy is shallow and closed.** If you have two concrete types and the set is not expected to grow, a simple `if/else` or a `switch` on a type tag is often more readable than setting up a virtual hierarchy. Polymorphism infrastructure for two permanent cases adds indirection without adding extensibility.

**When call frequency makes virtual overhead measurable.** Virtual calls prevent inlining and introduce a cache-miss risk when iterating large arrays of polymorphic objects through base class pointers. This matters in game engines, signal processing, and tight numeric loops — not in typical application request handlers. The [C++ Data Structures and STL](/languages/cpp/data-structures-stl/) article covers how container layout interacts with performance: storing objects by value in a flat `std::vector` is cache-friendly; storing them as `std::vector<Base*>` breaks that locality.

**When compile-time polymorphism fits better.** C++ templates provide polymorphism at zero runtime cost — the behavior is resolved at compile time. For callbacks where the concrete type is known at the call site, [C++ lambda functions](/languages/cpp/lambda-function/) captured in a `std::function` are often faster than a virtual call and require less boilerplate. When the full set of types is known at compile time, templates or `std::variant` with `std::visit` are usually the right tools.

Virtual dispatch is the right choice when you genuinely need to select behavior at runtime based on a type that varies across program lifetimes — plugin architectures, command objects, strategy patterns. Understanding [C++ class inheritance](/languages/cpp/class-inheritance/) is the foundation; `virtual` is the addition you layer on specifically when runtime selection is required.

## Frequently Asked Questions

### What is the difference between a virtual function and a pure virtual function in C++?

A virtual function has a body in the base class and provides a default implementation. Derived classes may override it, but those that don't inherit the base version automatically. A pure virtual function (`= 0`) has no body in the base class and forces every concrete derived class to supply its own implementation. A class containing any pure virtual function is abstract and cannot be instantiated directly. Use pure virtual when the base class cannot provide a meaningful default — when every concrete subtype genuinely needs its own implementation.

### Does using virtual functions have a performance cost in C++?

Yes, but typically small. Each virtual call follows the vptr to the vtable — one extra pointer dereference — and the indirection prevents the compiler from inlining the callee. On modern x86-64 hardware, a virtual call adds roughly 1–5 ns compared to a direct call assuming a warm instruction cache. The cost becomes relevant when processing millions of objects per second through base class pointers in tight loops. For most application code — request handlers, business logic, UI interactions — the overhead is negligible. Profile before treating virtual dispatch as a bottleneck.

### Can you have a virtual constructor in C++?

No. Constructors cannot be virtual because the vtable doesn't exist when the constructor runs — the object's type isn't yet fully established. The standard workaround is the *virtual constructor idiom*: implement a virtual `clone()` method on the base class that returns a heap-allocated copy of the concrete derived object. This enables type-preserving duplication through a base class pointer without knowing the concrete type at the call site. Destructors, by contrast, must almost always be virtual on polymorphic base classes.

### What is a vtable in C++ and how does it work?

A vtable (virtual function table) is a compiler-generated data structure containing one function pointer per virtual method in a class. Every class with virtual functions gets its own vtable, and every object of that class carries a hidden vptr pointing to it. When you call a virtual function, C++ follows the vptr to locate the vtable, then dispatches through the stored function pointer for that method. The vtable is shared across all instances of a class and lives in read-only memory — only the vptr is per-object. See the [cppreference page on virtual functions](https://en.cppreference.com/w/cpp/language/virtual) for the complete specification.

## Conclusion

The cpp virtual function keyword is C++'s mechanism for runtime polymorphism: mark a function virtual, and C++ resolves which implementation to call at runtime based on what object actually exists, not what pointer type holds it. Pure virtual functions extend this into an enforced contract — abstract base classes that every concrete derived type must fully implement. Apply the pattern correctly — virtual destructor, no virtual calls in constructors, `override` on every override — and it's safe and predictable.

The larger question is when virtual dispatch is the right tool at all versus templates, lambdas, or simpler control flow. After solidifying virtual functions, the natural next step is exploring how [C++ exception handling](/languages/cpp/c-handle-exception/) interacts with polymorphic hierarchies for resource safety. The [C++ Data Structures and STL](/languages/cpp/data-structures-stl/) article is also worth reading alongside this one: how you store and own polymorphic objects in collections directly shapes both correctness and performance.
