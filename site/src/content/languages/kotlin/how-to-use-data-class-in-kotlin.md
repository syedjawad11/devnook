---
category: languages
concept: data-class
linkAnchors:
  - "kotlin data class"
  - "data class"
description: Discover how to cleanly model object structures and state using Kotlin's
  Data Classes to eradicate extensive boilerplate and boilerplate property methods.
difficulty: beginner
language: kotlin
og_image: /og/languages/kotlin/data-class.png
published_date: '2026-06-11'
related_posts:
- /languages/kotlin/classes
- /languages/kotlin/null-safety
related_tools: []
tags:
- kotlin
- data-class
- oop
- architecture
actual_word_count: 2350
template_id: lang-v2
title: How to Use Data Classes in Kotlin?
word_count_target: 1500
---

## The Problem

When building rigorous applications such as an Android App or Spring Boot microservice, developers frequently create classes whose sole purpose is strictly holding data state (POJOs in [Java](/languages/java/)). If you use standard structures, you face an avalanche of required boilerplate generation just to ensure the objects behave efficiently.

```kotlin
// A standard class requires massive amounts of manual method overriding
class User(val name: String, val age: Int) {
    
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as User
        if (name != other.name) return false
        if (age != other.age) return false
        return true
    }

    override fun hashCode(): Int = name.hashCode() * 31 + age

    override fun toString(): String = "User(name=$name, age=$age)"
}
```

Creating basic identity, logging outputs (`toString()`), and equality rules (`equals()`) necessitates manually wiring decades-old architecture. The problem compounds as attributes change—if you add an `email` field to the object above, you must meticulously remember to update equality structures or risk catastrophic bugs related to sets and copying.

The maintenance burden compounds in team environments. When a junior developer adds a new field and forgets to update `equals()`, two `User` objects that should be considered identical silently fail equality checks. Sets and Maps built on that class start producing wrong results — bugs that are notoriously hard to trace because the faulty logic is buried in manually written boilerplate, not in the business logic where developers look first. [Java](/languages/java/) developers who have worked through this pain tend to reach for libraries like Lombok's `@Data` annotation; Kotlin solves it at the language level instead.

## The Kotlin Solution: Data Classes

Kotlin aggressively addresses this class bloat issue via the implementation of the `data` keyword. By placing this single keyword before your class declaration, you instruct the Kotlin compiler to automatically generate all the necessary utility methods directly from the constructor's scoped variables.

```kotlin
// The exact same functionality achieved instantly with a Data Class
data class User(val name: String, val age: Int)

val userA = User("Alice", 25)
val userB = User("Alice", 25)

// The compiler generated toString() and equals() automatically!
println(userA) // Output: User(name=Alice, age=25)
println(userA == userB) // Output: true
```

The `data class` takes control of the architecture, automatically deriving `equals()`, `hashCode()`, `toString()`, and `copy()` logic behind the scenes using only the properties explicitly written within the primary constructor.

The brevity is not just cosmetic. Because the compiler generates `equals()` from the constructor parameters, the equality contract stays in sync automatically: add an `email` field to the constructor and the compiler's generated `equals()` immediately incorporates it. There is no manual update step and no risk of forgetting. The `copy()` function is equally valuable — it enables the immutable-update pattern that functional programming and modern state management (think Redux reducers or Kotlin Flow) rely on heavily. You get a modified snapshot without touching the original.

## How Data Classes Work in Kotlin

When the Kotlin compiler compiles a `data class` down into JVM bytecode, it inspects every single `val` or `var` parameter declared inside the primary constructor parenthesis. It then weaves synthesized companion implementations representing robust structural equivalences into the compiled `.class` architecture.

If you subsequently perform the structural equality operator (`==`) between two identical instances of `User`, Kotlin knows to unpack the evaluation logic. It skips reference identity and sequentially checks if `userA.name == userB.name` and then `userA.age == userB.age`. 

To facilitate object destructing, the compiler also synthesizes `componentN()` functions corresponding directly to the properties declaration order.

The `hashCode()` implementation follows the standard contract: objects that are `equals()` must have identical hash codes. The compiler achieves this by combining the hash codes of each constructor property using a prime multiplier chain, the same algorithm `Objects.hash()` uses in Java. This means data classes integrate seamlessly with `HashSet`, `HashMap`, and any collection that relies on hash bucketing — you never encounter the classic bug where an object is added to a `HashSet` and then cannot be found because a manually written `hashCode()` was inconsistent with `equals()`.

## Going Further — Real-World Patterns

**Pattern 1: The `.copy()` Modification Pipeline**

Because data stability and immutability are highly prioritized in modern programming, `val` properties are immensely preferred. Instead of mutating a `var` property on a `data class`, creating modified duplicates using the built-in `.copy()` functionality guarantees concurrency safety.

```kotlin
data class ServerConfig(val host: String, val port: Int, val isSecure: Boolean)

val defaultServer = ServerConfig("127.0.0.1", 8080, false)

// Clone the object, mutating only the provided parameters gracefully
val secureServer = defaultServer.copy(port = 443, isSecure = true)

println(secureServer) 
// Output: ServerConfig(host=127.0.0.1, port=443, isSecure=true)
```

This pattern shines in multi-step configuration builders and event-sourcing systems. Rather than passing a mutable config object through a chain of functions that each modify it, you pass an immutable `data class` and each step returns a `.copy()` with its specific changes applied. The result is that every intermediate state is a distinct, inspectable object — you can log the before and after of each transformation without any defensive cloning.

**Pattern 2: Object Destructuring Assignment**

The generated `componentN()` functionalities inherently unlock destructuring syntax, allowing you to instantly disassemble a `data class` into distinct functional variables perfectly ordered.

```kotlin
data class Coordinates(val x: Double, val y: Double)

val target = Coordinates(52.12, -3.10)

// Extract properties cleanly into their own scope bindings
val (latitude, longitude) = target

println("Lat is $latitude") // Output: Lat is 52.12
```

## What to Watch Out For

**Primary Constructor Only:** 
Data Classes solely utilize properties definitively outlined in the primary `()` constructor for utility generation. If you establish a variable inside the actual class body `{ }`, it completely avoids `toString()`, `equals()`, and `hashCode()` participation. 

**Inheritance Limitations:**
You cannot explicitly declare a `data class` as `open`, `abstract`, `sealed`, or `inner`. While a `data class` can implement robust interfaces or extend abstract parent hierarchies, you cannot extend one `data class` from another `data class`. This rigidly restricts inheritance misuse concerning automatic equivalence evaluations.

**Null Sensitivity in equals():**
Because the generated `equals()` is structurally derived from constructor properties, it is sensitive to nullability. If a property is declared as `String?`, then a `null` value and a non-null value will never be considered equal, even if you might expect them to be in some domain logic. This is the correct behavior in almost every case, but it is worth being deliberate about nullable properties in data classes that participate in equality comparisons — particularly in persistence layers where a missing field from a database row arrives as `null`.

## Under the Hood: Performance & Mechanics

Data classes fundamentally remain absolutely standard OOP instances compiled toward JVM Bytecode structures. They maintain identical memory allocation heaps and Garbage Collector lifecycles compared to regular Kotlin instances.

The performance edge resides essentially in compilation guarantees concerning algorithm operations. Hash computations automatically mirror highly optimized mathematical operations scaling exponentially per prime-numbers arrays without requiring developer interventions. This keeps collections arrays such as `HashSet` or `HashMap` structures scaling rapidly while relying effectively on optimal collision thresholds.

Memory-wise, each `data class` instance is a standard heap-allocated JVM object. The JVM does not cache or deduplicate instances — calling `copy()` always allocates a new object. If your hot path constructs thousands of small data class instances per second, consider using object pools or value classes (introduced in Kotlin 1.5) for single-property wrappers. Value classes are compiled to unboxed primitives on the JVM, eliminating allocation entirely for the single-property case.

## Data Classes vs Regular Classes — When to Use Each

The choice between `data class` and `class` is straightforward when you frame it around identity vs. structure. A regular `class` is the right choice when two instances that hold the same data should still be considered different objects — a `Thread`, a `DatabaseConnection`, or a `UIController` each has meaningful identity beyond its fields. Two database connections to the same host are not interchangeable; they represent distinct resources.

A `data class` is the right choice when two instances that hold the same field values should be considered equivalent — a `Point`, a `Money` amount, a `UserProfile` snapshot, an API response DTO. These are pure values: what they contain is what they are.

A useful heuristic: if you would ever write `if (a === b)` to check reference equality as a meaningful business condition, use a regular `class`. If the only equality that matters is structural (`a == b`), use a `data class`. DTOs, event payloads, value objects in domain-driven design, and API response models are almost always `data class` candidates.

## Advanced Edge Cases

**Edge Case 1: Customizing equals() Behaviours**

There are rare situations where you require a `data class` functionality architecture, but one field fundamentally represents an arbitrary cache unsuited for equivalence assertions. While discouraged, you can meticulously override synthetically generated data logics by manually declaring them.

```kotlin
data class NetworkResponse(val id: Int, val payload: String) {
    var queryTimeInMillis: Long = 0    // Note: This is inside the body, excluded from equals()!
    
    // Explicit override supersedes the automatic generation
    override fun toString(): String {
         return "[$id]: $payload"
    }
}
```

**Edge Case 2: Encompassing Arrays Issues**

If your `data class` embraces an `Array<T>` property parameter, the compiler utilizes the default `Array.equals()` behavior which tests referencing object memory, not underlying contents logic. 

```kotlin
// This will behave unpredictably regarding identity equality!
data class Batch(val items: Array<String>) {
    // You MUST fundamentally override logic utilizing contentEquals() 
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as Batch
        if (!items.contentEquals(other.items)) return false
        return true
    }
    // (hashCode() must also use items.contentHashCode())
}
```
*Recommendation*: Fundamentally replace `Array` configurations with immutable `List<T>` properties; they assert value-level equality autonomously.

## Data Classes and Kotlin Serialization

Data classes integrate directly with the official `kotlinx.serialization` library. Add the `@Serializable` annotation and the compiler plugin generates `encode`/`decode` logic from the same constructor properties that drive `equals()` and `copy()`.

```kotlin
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class ApiResponse(val status: String, val count: Int, val items: List<String>)

val json = Json.encodeToString(ApiResponse("ok", 2, listOf("alpha", "beta")))
// Output: {"status":"ok","count":2,"items":["alpha","beta"]}

val decoded = Json.decodeFromString<ApiResponse>(json)
println(decoded.status) // "ok"
```

Because the serialization contract is derived from the constructor, adding or removing a field automatically updates the serialized format — no separate schema definition required. Use `@SerialName("snake_case")` on properties when the JSON field name differs from the Kotlin property name, and `@Required` to enforce that a key must be present during deserialization. This tight coupling between the data model and its wire format is one reason data classes are the default choice for Kotlin API clients and server-side response models.

## Java Interop: `@JvmRecord`

Since Kotlin 1.5, you can annotate a data class with `@JvmRecord` to compile it as a Java record on the JVM. This matters when your Kotlin code must integrate with Java libraries or frameworks that perform reflection-based introspection on record types — Spring, Jackson, Hibernate, and jOOQ all have dedicated handling for Java records.

```kotlin
@JvmRecord
data class Point(val x: Double, val y: Double)
```

The resulting bytecode is a proper Java record: Java callers can use the `x()` and `y()` accessor methods that the record specification defines, and frameworks that look for `RecordComponent` annotations during deserialization will recognize the class correctly. Constraints apply: all properties must be `val` (immutable), declared only in the primary constructor, with no superclass other than `Any`. For pure-Kotlin codebases with no Java interop requirement, `@JvmRecord` provides no benefit — the standard data class bytecode is already optimal for Kotlin callers.

## Testing Data Classes in Kotlin

Data Classes streamline testing assertions immensely because test frameworks easily leverage automatically generated object state equivalence configurations without additional verifications. You can compare two instances directly with `assertEquals` — no custom comparator or `assertThat().usingRecursiveComparison()` ceremony needed, because structural equality is already the default behavior.

```kotlin
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

class DataClassTest {
    @Test
    fun `ensures copy manipulation preserves untouched configuration targets`() {
        val original = User("Batman", 40)
        val agingBatman = original.copy(age = 45)
        
        // Assertions seamlessly check object states via data class powers
        assertEquals("Batman", agingBatman.name)
        assertEquals(45, agingBatman.age)
    }
}
```

## Summary

The Data Class resolves deep OOP bloat requirements natively in Kotlin architectures. Assigning the `data` prefix before a class generates `hashCode()`, `toString()`, `copy()`, and `equals()` instantly, relying completely on the strictly declared properties existing within the primary constructor map. With robust features permitting structured declarations and immutability cloning behaviors, data classes function elegantly to encapsulate information strictly.

Reach for `data class` whenever a type's identity is defined by the values it holds — DTOs, event payloads, configuration snapshots, and domain value objects all fit this mold. Reserve plain `class` for objects with meaningful reference identity, mutable state managed across a lifecycle, or deep inheritance hierarchies. When in doubt, start with `data class`: it gives you structural equality, a human-readable `toString()`, and safe copying for free, and you can always step back to a regular `class` if the constraints become limiting.
