---
category: languages
concept: data-class
description: Discover how to cleanly model object structures and state using Kotlin's
  Data Classes to eradicate extensive boilerplate and boilerplate property methods.
difficulty: beginner
language: kotlin
og_image: /og/languages/kotlin/data-class.png
published_date: '2026-04-16'
related_posts:
- /languages/kotlin/classes
- /languages/kotlin/null-safety
related_tools: []
tags:
- kotlin
- data-class
- oop
- architecture
template_id: lang-v2
title: How to Use Data Classes in Kotlin?
word_count_target: 1500
---

# How to Use Data Classes in Kotlin?

## The Problem

When building rigorous applications such as an Android App or Spring Boot microservice, developers frequently create classes whose sole purpose is strictly holding data state (POJOs in [Java](/languages/java)). If you use standard structures, you face an avalanche of required boilerplate generation just to ensure the objects behave efficiently.

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

## How Data Classes Work in Kotlin

When the Kotlin compiler compiles a `data class` down into JVM bytecode, it inspects every single `val` or `var` parameter declared inside the primary constructor parenthesis. It then weaves synthesized companion implementations representing robust structural equivalences into the compiled `.class` architecture.

If you subsequently perform the structural equality operator (`==`) between two identical instances of `User`, Kotlin knows to unpack the evaluation logic. It skips reference identity and sequentially checks if `userA.name == userB.name` and then `userA.age == userB.age`. 

To facilitate object destructing, the compiler also synthesizes `componentN()` functions corresponding directly to the properties declaration order.

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

## Under the Hood: Performance & Mechanics

Data classes fundamentally remain absolutely standard OOP instances compiled toward JVM Bytecode structures. They maintain identical memory allocation heaps and Garbage Collector lifecycles compared to regular Kotlin instances.

The performance edge resides essentially in compilation guarantees concerning algorithm operations. Hash computations automatically mirror highly optimized mathematical operations scaling exponentially per prime-numbers arrays without requiring developer interventions. This keeps collections arrays such as `HashSet` or `HashMap` structures scaling rapidly while relying effectively on optimal collision thresholds.

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

## Testing Data Classes in Kotlin

Data Classes streamline testing assertions immensely because test frameworks easily leverage automatically generated object state equivalence configurations without additional verifications.

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
