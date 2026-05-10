---
title: "How to Format Strings in Kotlin? String Templates Explained"
description: "Learn how to format strings in Kotlin efficiently using string templates, String.format(), and multi-line strings to solve common formatting problems."
category: "languages"
language: "kotlin"
concept: "format-string"
difficulty: "beginner"
template_id: "lang-v2"
tags: ["kotlin", "format-string", "strings", "templates"]
related_tools: []
related_posts: []
published_date: "2026-05-10"
og_image: "/og/languages/kotlin/format-string.png"
---

## The Problem

A common source of frustration for developers, especially those transitioning from older languages, is constructing readable strings that include variable data. When you need to build a string by combining static text with dynamic values, the naive approach is to use the `+` operator for string concatenation.

```kotlin
// Naive string concatenation - hard to read and error-prone
val userName = "Alice"
val orderCount = 5
val totalCost = 120.50

// Building the string requires multiple + operators and quotes
val summaryMessage = "User " + userName + " has placed " + orderCount + " orders for a total of $" + totalCost + "."
```

While this code functions, it is exceptionally tedious to write and read. As the string grows in complexity, managing the opening and closing quotes, along with the numerous `+` signs, becomes highly error-prone. This approach obfuscates the intended structure of the output string, making maintenance difficult and increasing the likelihood of syntax errors.

## The Kotlin Solution: String Templates

To resolve this issue, Kotlin introduces String Templates. This feature allows you to embed variables and expressions directly inside string literals, creating a much more natural and readable syntax. It eliminates the need for manual concatenation, significantly improving code clarity.

```kotlin
// Using Kotlin String Templates for clean, readable formatting
val userName = "Alice"
val orderCount = 5
val totalCost = 120.50

// Variables are embedded directly using the $ prefix
val summaryMessage = "User $userName has placed $orderCount orders for a total of $$totalCost."
```

By prefixing a variable name with the `$` symbol, the Kotlin compiler automatically interpolates its value into the string. This makes the code concise and explicitly shows the structure of the resulting text. Notice how the structure of `summaryMessage` now exactly mirrors the final output, improving readability and developer productivity.

## How String Templates Work in Kotlin

When you use string templates to figure out how to format string in kotlin, the compiler translates this elegant syntax into highly optimized bytecode. Under the hood, Kotlin does not repeatedly allocate new string objects for every concatenation, which would be inefficient. Instead, it utilizes `StringBuilder` operations (or similar optimized JVM instructions depending on the compiler version) to construct the final string.

The syntax rules are straightforward. For simple variable references, you just use `$variableName`. However, if you need to evaluate a more complex expression, access a property of an object, or call a function, you must enclose the expression in curly braces: `${expression}`. The compiler evaluates the expression within the braces, calls the `toString()` method on the result, and inserts that value into the final string. This powerful mechanism allows for dynamic text generation directly within the string literal.

## Going Further — Real-World Patterns

While string templates are ideal for simple interpolation, real-world development often demands specific formatting rules, such as aligning numbers, controlling decimal precision, or generating complex multi-line text structures.

**Pattern 1: Formatting Numbers and Dates**

When you need precise control over the output format, such as restricting a floating-point number to two decimal places, you should utilize the `String.format()` method. This function leverages standard Java format specifiers.

```kotlin
val piValue = 3.14159265
val formattedPi = String.format("Pi rounded to two decimals: %.2f", piValue)
// Result: Pi rounded to two decimals: 3.14

val invoiceId = 42
val paddedInvoice = String.format("Invoice #%05d", invoiceId)
// Result: Invoice #00042
```

The `String.format()` method is indispensable when string templates alone cannot enforce the necessary presentation rules, particularly for numerical data or locale-specific formatting.

**Pattern 2: Multi-line Raw Strings**

For SQL queries, JSON payloads, or extensive text blocks, Kotlin provides raw strings enclosed in triple quotes (`"""`). Raw strings can span multiple lines without requiring explicit newline characters (`\n`). To maintain proper indentation in your code without affecting the final string, combine raw strings with the `trimIndent()` or `trimMargin()` functions.

```kotlin
val tableName = "users"
val sqlQuery = """
    SELECT id, username, email 
    FROM $tableName 
    WHERE active = true
""".trimIndent()
```

The `.trimIndent()` function removes the common minimal indentation across all lines, keeping the source code neat while ensuring the actual string content is correctly formatted without excessive leading spaces.

## What to Watch Out For

A primary gotcha involves escaping the `$` symbol. Because `$` indicates the start of a template expression, you must escape it if you want to output a literal dollar sign. In standard string literals, you cannot use a simple backslash (`\$`). Instead, you must embed the literal character within an expression: `${'$'}`. This is a frequent point of confusion for beginners.

Additionally, developers sometimes overuse complex expressions within string templates. While `${user.getAddress().getZipCode().format()}` is syntactically valid, embedding extensive logic inside a string literal severely degrades readability. Best practices dictate extracting complex calculations into separate variables before referencing them in the template.

## Under the Hood: Performance & Mechanics

Understanding the performance implications of string formatting requires examining the bytecode. When you write a string template like `"Value: $x"`, the Kotlin compiler essentially translates this to `StringBuilder().append("Value: ").append(x).toString()`. This translation ensures that string creation is highly efficient, avoiding the overhead of creating multiple intermediate string objects in the heap.

Comparatively, `String.format()` incurs a slight performance penalty because it must parse the format string at runtime to identify the specifiers before applying the substitutions. String templates, being resolved at compile-time into `StringBuilder` operations, offer superior performance for standard interpolation. Therefore, developers should default to string templates for general concatenation and reserve `String.format()` exclusively for scenarios requiring strict formatting rules.

## Advanced Edge Cases

String formatting behavior can become nuanced when dealing with specific locales or null values.

**Edge Case 1: Locale-Dependent Formatting**

`String.format()` relies on the default system Locale if one is not explicitly provided. This can lead to unexpected behavior; for instance, formatting a decimal number might produce `3.14` in the US but `3,14` in Germany, potentially breaking data serialization.

```kotlin
import java.util.Locale

val value = 1234.56
// Explicitly providing the Locale ensures consistent formatting regardless of the host system
val consistentFormat = String.format(Locale.US, "Value: %.2f", value)
```

Always provide an explicit `Locale` when formatting strings that will be parsed by machines or transmitted over a network.

**Edge Case 2: Null Handling in Templates**

When a variable referenced in a string template is null, Kotlin safely handles it by inserting the literal string `"null"`. This prevents `NullPointerException`s during string construction.

```kotlin
val missingUser: String? = null
// Kotlin safely calls toString() on the null reference
val greeting = "Hello, $missingUser"
// Result: "Hello, null"
```

While safe, displaying `"null"` to an end-user is rarely desirable. You often need to combine templates with the Elvis operator (`?:`) to provide sensible defaults.

## Testing String Formatting in Kotlin

Verifying that strings are formatted correctly is a crucial aspect of unit testing, especially for UI components or reporting modules. Using a framework like JUnit, you can assert that the generated string matches the expected output precisely.

```kotlin
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Assertions.assertEquals
import java.util.Locale

class StringFormattingTest {

    @Test
    fun `test complex string template generation`() {
        val userName = "TestUser"
        val score = 95.5
        
        // Target function logic
        val result = "Player $userName achieved a score of ${String.format(Locale.US, "%.1f", score)}"
        
        val expected = "Player TestUser achieved a score of 95.5"
        assertEquals(expected, result, "The string format did not match the expected structure")
    }
}
```

This test guarantees that both the string template interpolation and the nested `String.format` function execute as anticipated, ensuring stability against future code changes.

## Summary

Mastering how to format string in kotlin centers on utilizing String Templates to create readable and efficient string concatenations. By embedding variables with `$` and expressions with `${}`, you avoid cumbersome `+` operators. For precise numerical or date formatting, `String.format()` remains the standard approach.

## Related

For more advanced language features, explore our guides on Kotlin Coroutines and Kotlin Null Safety. Understanding these concepts alongside string templates will greatly enhance your overall proficiency with the language.

If you are transitioning from Java, take some time to review how Kotlin handles nullability and type inference, as these concepts often intersect with string manipulation. Another great area to study is Kotlin's Extension Functions, which allow you to add custom formatting methods directly to the `String` class, making your string manipulation logic even more reusable across your entire application.

Additionally, digging into the JVM bytecode using tools like `javap` or IntelliJ IDEA's "Show Kotlin Bytecode" feature is highly recommended. It provides a deeper appreciation for the zero-cost abstractions Kotlin offers. Seeing firsthand how your elegant string templates are compiled down to standard `StringBuilder` operations will give you the confidence to use these features extensively without worrying about performance regressions.

Ultimately, understanding how to format string in kotlin effectively is essential for writing clean, idiomatic code. While string templates will handle the vast majority of your formatting needs, mastering `String.format()` ensures you can handle any edge cases involving localization or complex number formatting. By avoiding manual concatenation and embracing these built-in language features, you not only improve readability but also reduce the likelihood of subtle bugs in your text generation logic.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "How to Format Strings in Kotlin? String Templates Explained",
  "description": "Learn how to format strings in Kotlin efficiently using string templates, String.format(), and multi-line strings to solve common formatting problems.",
  "author": {
    "@type": "Person",
    "name": "Expert Developer"
  },
  "publisher": {
    "@type": "Organization",
    "name": "DevPortal"
  },
  "datePublished": "2026-05-10"
}
</script>
