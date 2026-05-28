---
title: "How to Do Class Inheritance in C++? A Complete Guide"
description: "Learn how class inheritance works in C++: syntax, access specifiers, virtual functions, and real-world patterns with clear code examples."
category: "languages"
language: "cpp"
concept: "class-inheritance"
linkAnchors:
  - "cpp class inheritance"
  - "class inheritance"
  - "c++ inheritance"
difficulty: "intermediate"
template_id: "lang-v5"
tags: ["cpp", "class-inheritance", "oop", "virtual-functions", "polymorphism"]
related_tools: []
related_posts: []
published_date: "2026-05-09"
og_image: "/og/languages/cpp/class-inheritance.png"
---

Class inheritance is one of the cornerstones of object-oriented programming in C++. Whether you're modeling a game character hierarchy, designing a plugin system, or building reusable library components, understanding how to correctly set up base and derived classes — along with access control, virtual dispatch, and construction order — separates maintainable code from brittle spaghetti. This guide walks through every layer of C++ class inheritance with concrete, production-relevant examples.

## What Is Class Inheritance in C++?

In C++, class inheritance allows a **derived class** to acquire the member variables and member functions of a **base class**, establishing an "is-a" relationship between them. A `Dog` is-a `Animal`; a `Button` is-a `Widget`. C++ supports single inheritance (one base), multiple inheritance (many bases), multilevel inheritance (chains), and hierarchical inheritance (multiple derived from one base). Inheritance promotes code reuse and enables polymorphic behaviour through virtual dispatch.

## Basic Syntax

The minimal syntax for declaring a base and derived class uses the colon notation with an access specifier:

```cpp
#include <iostream>
#include <string>

// Base class
class Animal {
public:
    std::string name;

    Animal(const std::string& n) : name(n) {}

    void speak() const {
        std::cout << name << " makes a sound.\n";
    }
};

// Derived class — public inheritance
class Dog : public Animal {
public:
    Dog(const std::string& n) : Animal(n) {}  // delegate to base ctor

    void fetch() const {
        std::cout << name << " fetches the ball!\n";
    }
};

int main() {
    Dog d("Rex");
    d.speak();   // inherited from Animal
    d.fetch();   // Dog's own method
}
```

The `: public Animal` notation after `Dog` means `Dog` inherits all `public` and `protected` members of `Animal` with the same access level. The `Animal(n)` call in `Dog`'s initialiser list explicitly invokes the base constructor — in C++ this is **mandatory** whenever the base class has no default constructor. Using `public` inheritance preserves the "is-a" relationship visible to the rest of the program; `private` or `protected` inheritance hides it and is used for implementation-only reuse.

## Access Specifiers in Inheritance

C++ gives you three inheritance modes, each controlling how the base's member visibility is re-exported by the derived class:

| Base member | `public` inheritance | `protected` inheritance | `private` inheritance |
|-------------|---------------------|------------------------|-----------------------|
| `public`    | `public` in derived | `protected` in derived | `private` in derived  |
| `protected` | `protected`         | `protected`            | `private`             |
| `private`   | inaccessible        | inaccessible           | inaccessible          |

**Public inheritance** (`class Dog : public Animal`) is the standard "is-a" model. External code can call inherited `public` methods on a `Dog` object, and a `Dog*` can implicitly convert to `Animal*`.

**Protected inheritance** demotes the base's public interface to `protected`, meaning subclasses of `Dog` can still access it but external client code cannot. This is used rarely.

**Private inheritance** is essentially "implemented-in-terms-of": all base members become `private` in the derived class. No implicit base-pointer conversion occurs. It is useful as an alternative to composition when you need to override virtual functions of the base but don't want to expose the base interface.

```cpp
class Engine {};

class Car : private Engine {  // Car is NOT an Engine publicly
    // uses Engine internals; clients don't know
};
```

## Constructors and Destructors in Derived Classes

Construction and destruction order is a critical detail that catches many developers off guard. The base class constructor always runs first, and the base class destructor always runs last:

```cpp
#include <iostream>

class Base {
public:
    Base()  { std::cout << "Base constructed\n"; }
    virtual ~Base() { std::cout << "Base destroyed\n"; }
};

class Derived : public Base {
public:
    Derived() { std::cout << "Derived constructed\n"; }
    ~Derived() override { std::cout << "Derived destroyed\n"; }
};

int main() {
    Base* obj = new Derived();
    delete obj;
    // Output:
    // Base constructed
    // Derived constructed
    // Derived destroyed  ← only because ~Base is virtual
    // Base destroyed
}
```

**Construction order:** The base class constructor runs first, then the derived class constructor. This guarantees the base sub-object is fully initialised before the derived part builds on top of it.

**Destruction order:** The reverse — the derived destructor runs first, then the base destructor. This mirrors construction so resources are released in the correct sequence.

**Why `virtual` destructors?** Without `virtual ~Base()`, deleting a `Derived` object through a `Base*` invokes only `~Base()`, skipping `~Derived()`. This is undefined behaviour and a classic resource leak. The rule: if a class has any virtual function, make the destructor `virtual` too.

## Virtual Functions and Polymorphism

Virtual functions are the mechanism that makes inheritance truly powerful. They allow a base class pointer or reference to call the correct derived-class implementation at runtime:

```cpp
#include <iostream>
#include <vector>
#include <memory>

class Shape {
public:
    virtual double area() const = 0;   // pure virtual
    virtual void print() const {
        std::cout << "Area: " << area() << "\n";
    }
    virtual ~Shape() = default;
};

class Circle : public Shape {
    double radius_;
public:
    explicit Circle(double r) : radius_(r) {}
    double area() const override { return 3.14159 * radius_ * radius_; }
};

class Rectangle : public Shape {
    double w_, h_;
public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
    double area() const override { return w_ * h_; }
};

int main() {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>(5.0));
    shapes.push_back(std::make_unique<Rectangle>(4.0, 6.0));

    for (const auto& s : shapes)
        s->print();   // correct virtual dispatch at runtime
}
```

**Virtual dispatch** works through the **vtable** (virtual function table): the compiler attaches a hidden pointer (`vptr`) to every polymorphic object. At runtime, calling a virtual function dereferences the `vptr`, finds the correct function pointer for the actual dynamic type, and calls it. This costs one extra pointer dereference per virtual call — negligible in most code, but measurable in tight inner loops.

The **`override` keyword** (C++11) explicitly tells the compiler this method is overriding a base virtual. If the signature doesn't match, you get a compile error instead of silently creating a new non-virtual method. Always use `override`. The **`final` keyword** prevents further overriding of a method or subclassing of an entire class. **Pure virtual functions** (`= 0`) make the class abstract — it cannot be instantiated, only subclassed.

## Multiple Inheritance and the Diamond Problem

C++ is one of the few mainstream languages that supports multiple inheritance. It is powerful but comes with a specific pitfall — the diamond problem:

```cpp
#include <iostream>

class A {
public:
    int value = 42;
    void hello() { std::cout << "A::hello\n"; }
};

class B : virtual public A {};   // virtual inheritance
class C : virtual public A {};   // virtual inheritance

class D : public B, public C {}; // D gets exactly ONE copy of A

int main() {
    D obj;
    obj.hello();         // unambiguous — one A sub-object
    std::cout << obj.value; // 42
}
```

Without `virtual`, `D` would inherit `A` twice — once through `B` and once through `C`. Accessing `obj.value` would be ambiguous and would require writing `obj.B::value` explicitly. **Virtual inheritance** makes the compiler insert only a single shared `A` sub-object in `D`, eliminating the ambiguity. The trade-off is that the object layout becomes more complex and the `vptr` overhead increases slightly. Practical advice: prefer multiple inheritance only for interface mixins — pure abstract classes with no data members. When the diamond pattern involves data, consider composition instead.

## Advanced Edge Cases

**Edge Case 1: Name hiding vs. overriding**

A common trap is assuming that declaring a method with the same name in a derived class overrides all base-class overloads. In fact, it *hides* them:

```cpp
class Base {
public:
    void foo(int x) { std::cout << "Base::foo(int)\n"; }
};

class Derived : public Base {
public:
    void foo() { std::cout << "Derived::foo()\n"; }
    // Base::foo(int) is now HIDDEN, not overloaded
};

int main() {
    Derived d;
    d.foo();      // OK
    // d.foo(1); // ERROR: no matching function
    d.Base::foo(1); // must qualify explicitly
}
```

When `Derived` declares a new `foo()`, it hides all `Base::foo` overloads, even those with different signatures. This is name hiding, not overriding — there is no `virtual` involved. Fix it by adding `using Base::foo;` inside `Derived` to restore the hidden overloads into the derived class's scope.

**Edge Case 2: Calling virtual functions in constructors**

During base class construction, the dynamic type of the object is still `Base`, so virtual dispatch resolves to `Base`'s version — not the derived class's:

```cpp
class Base {
public:
    Base() { init(); }          // calls Base::init, not Derived::init
    virtual void init() { std::cout << "Base::init\n"; }
};

class Derived : public Base {
public:
    void init() override { std::cout << "Derived::init\n"; }
};

int main() {
    Derived d;  // prints "Base::init" — surprising!
}
```

The `Derived` part hasn't been constructed yet when `Base`'s constructor runs, so calling `init()` inside the base constructor calls `Base::init` every time. The same logic applies to destructors: when `~Base` runs, the `Derived` part has already been destroyed, so the dynamic type is again `Base`. Never call virtual functions from constructors or destructors if you expect derived-class behaviour.

## Testing Class Inheritance in C++

Google Test (`gtest`) is the de-facto standard for C++ unit testing. Here's how to test an inheritance hierarchy effectively:

```cpp
#include <gtest/gtest.h>
#include <memory>

class Shape {
public:
    virtual double area() const = 0;
    virtual ~Shape() = default;
};

class Circle : public Shape {
    double r_;
public:
    explicit Circle(double r) : r_(r) {}
    double area() const override { return 3.14159 * r_ * r_; }
};

TEST(CircleTest, AreaIsCorrect) {
    Circle c(1.0);
    EXPECT_NEAR(c.area(), 3.14159, 1e-4);
}

TEST(PolymorphismTest, BasePtrDispatchesToDerived) {
    std::unique_ptr<Shape> s = std::make_unique<Circle>(2.0);
    EXPECT_NEAR(s->area(), 12.566, 1e-2);
}

TEST(PolymorphismTest, DerivedIsInstanceOfBase) {
    Circle c(1.0);
    Shape* ptr = &c;                             // implicit upcast
    EXPECT_NE(ptr, nullptr);
    EXPECT_NEAR(ptr->area(), 3.14159, 1e-4);    // dispatches correctly
}
```

Key principles for testing inheritance: test through the interface (`Shape*`) not just the concrete type — this validates polymorphic dispatch. Use `EXPECT_NEAR` for floating-point comparisons instead of `EXPECT_EQ`. Test destructor correctness indirectly by wrapping objects in `unique_ptr` and running under AddressSanitizer (`-fsanitize=address,leak`) to catch resource leaks that occur during virtual destruction. Use GMock's `MOCK_METHOD` to create mock derived classes when the base has side effects you need to isolate.

## Quick Reference

- Syntax: `class Derived : public Base { ... };`
- `public` inheritance → "is-a"; `private` → "implemented-in-terms-of"
- Base constructor always runs **before** derived constructor
- Always make base class destructors `virtual` if the class has any virtual functions
- Use `override` on every overriding method — it catches signature mismatches at compile time
- `= 0` makes a function pure virtual and the class abstract
- Virtual inheritance solves the diamond problem in multiple inheritance
- Never call virtual functions from constructors or destructors

## Next Steps

After mastering class inheritance in C++, explore these closely related topics:

- **Exception Handling in C++** — Every polymorphic system needs robust error handling; exceptions and inheritance interact in important ways, particularly when catching by base class reference. See [How to Catch Errors in C++](/languages/cpp/catch-error/) for a detailed walkthrough.
- **C++ Templates** — Template-based polymorphism (compile-time) versus virtual-based polymorphism (runtime) is a key architectural decision in modern C++.
- **Smart Pointers** — Inheritance through raw pointers is dangerous; `unique_ptr` and `shared_ptr` make ownership semantics explicit and exception-safe.

See the C++ language hub and C++ cheatsheet for a quick reference covering inheritance syntax and related idioms.
