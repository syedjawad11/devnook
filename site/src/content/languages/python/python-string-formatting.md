---
title: "Python String Formatting: f-strings, format() & %"
description: "Learn Python string formatting from scratch: f-strings, the format() method, and the % operator, with simple, beginner-friendly examples you can run today."
category: "languages"
language: "python"
concept: "string-formatting"
difficulty: "intermediate"
template_id: "lang-programmatic-v1"
tags: ["python", "string-formatting", "f-strings", "format-method", "string-interpolation"]
related_posts: []
related_tools: []
linkAnchors:
  - "python string formatting"
  - "f-strings"
  - "format method"
published_date: "2026-05-30"
og_image: "/og/languages/python/string-formatting.png"
word_count_target: 2050
---

Imagine you are writing a program that greets a user by name and shows their account balance: something like `Hello Maria, your balance is $1,234.56`. The name and the balance live in variables, and they change for every user. So how do you slot those changing values into a fixed sentence, with the dollar sign, the comma, and exactly two decimal places? That is the everyday job of Python string formatting, and it is one of the first genuinely useful skills you pick up as a Python beginner.

This guide starts from the very beginning. We will explain what string formatting actually is, why plain text-joining falls apart quickly, and then build up — one small step at a time — through f-strings, the `format()` method, and the older `%` operator.

## What Is Python String Formatting?

A *string* is simply text: a sequence of characters like `"hello"` or `"$1,234.56"`. Most of the text your program shows is not fixed in advance — it depends on data such as a username, a price, or today's date. Python string formatting is the technique of building a piece of text by inserting values into a template and deciding how each value should look.

Think of it like a fill-in-the-blanks form. You write a sentence with gaps:

```
Hello ____, your balance is $____.
```

Then you tell Python which value goes in each gap. Formatting goes one step further than just filling the gap, though: it also lets you control the *appearance* of each value — rounding a number to two decimals, adding thousands separators, or lining text up into columns. You describe the result you want, and Python produces the finished string.

## Why Not Just Add Strings Together?

When you first learn Python, the obvious way to combine text is the `+` operator:

```python
name = "Maria"
greeting = "Hello " + name
print(greeting)   # Hello Maria
```

This works fine for two pieces of text. The trouble starts the moment you mix in a number:

```python
balance = 1234.56
print("Hello " + name + ", your balance is " + balance)   # fails: can't concatenate float to str (TypeError)
```

Python refuses to glue a number directly onto text, so you have to wrap it in `str()`:

```python
print("Hello " + name + ", your balance is $" + str(balance))   # -> Hello Maria, your balance is $1234.56
```

It runs now, but look at the result: `$1234.56` has no comma, and if the number had been `1234.5` it would show `$1234.5` instead of `$1234.50`. Controlling decimals or alignment this way is painful, and the line is already cluttered with quotation marks and plus signs. (If a value might be missing or the wrong type, you also end up reaching for [error handling](/languages/python/error-handling/) just to keep the program from crashing.) String formatting exists to make all of this clean and readable.

## f-strings: The Modern, Readable Way

Python 3.6 introduced *formatted string literals*, almost always called **f-strings**, and for new code they are the recommended approach. You put the letter `f` right before the opening quote, then write your variables inside curly braces `{}` directly where they belong in the sentence:

```python
name = "Maria"
balance = 1234.56
print(f"Hello {name}, your balance is ${balance}")   # -> Hello Maria, your balance is $1234.56
```

Notice how much easier this is to read than the `+` version — the variables sit exactly where they appear in the output, so you can see the final sentence at a glance. There is no `str()` call either; the f-string converts the number to text automatically.

The braces are not limited to plain variable names. Any Python *expression* works inside them, which means you can do arithmetic, call methods, or look things up without leaving the string:

```python
name = "alex"
age = 30
print(f"{name.upper()} will be {age + 1} next year")   # -> ALEX will be 31 next year
```

For most everyday tasks, that is all you need. The next step is learning how to control the way each value looks.

## Formatting Numbers: Decimals, Commas, and Percentages

To control appearance, you add a colon `:` inside the braces, followed by a short instruction. The most common need is rounding a number to a fixed number of decimal places. The instruction `.2f` means "show this as a float with 2 digits after the decimal point":

```python
balance = 1234.56
print(f"Your balance is ${balance:.2f}")   # Your balance is $1234.56

pi = 3.14159
print(f"Pi is about {pi:.2f}")             # Pi is about 3.14
```

For money, you usually want a thousands separator too. A comma in the instruction adds one, and you can combine it with the decimal rule:

```python
amount = 1234567.891
print(f"${amount:,.2f}")   # $1,234,567.89
```

Percentages are just as easy. The `%` instruction multiplies the number by 100 and adds a `%` sign, and `.1%` keeps one decimal:

```python
rate = 0.0725
print(f"Interest rate: {rate:.2%}")   # Interest rate: 7.25%
print(f"Pass rate: {0.85:.1%}")       # Pass rate: 85.0%
```

Each of these would be awkward with manual string-joining. With formatting, you simply state the format you want after the colon.

## Aligning Text into Neat Columns

The same colon syntax can pad and align values, which is how you turn a loop of data into a tidy table. A number after the colon sets the minimum *width*, and the symbols `<`, `>`, and `^` set the alignment (left, right, and centre):

```python
print(f"{'Name':<10}{'Score':>6}")
print(f"{'Alice':<10}{95:>6}")
print(f"{'Bob':<10}{88:>6}")
```

Output:

```
Name       Score
Alice         95
Bob           88
```

The `<10` left-aligns each name in a 10-character-wide space, and `>6` right-aligns each score in a 6-character space, so the columns line up perfectly. Combine width with a decimal rule for a price list:

```python
products = [("Coffee", 4.5), ("Sandwich", 12.0), ("Cake", 6.75)]
for item, price in products:
    print(f"{item:<12}{price:>8.2f}")
```

```
Coffee          4.50
Sandwich       12.00
Cake            6.75
```

Doing this by counting spaces yourself would be tedious and break the instant someone changed a value. (If you are looping over data to build these rows, a [list comprehension](/languages/python/list-comprehension/) can often produce the list you iterate over in the first place.)

## The Format Specification Mini-Language

Everything after the colon — the `.2f`, `,`, `<10`, `.1%` — belongs to one shared system that Python calls the *format specification mini-language*. You do not need to memorise it; the patterns above cover most real work. The piece worth knowing is the final *type code*, which tells Python how to render the value:

| Code | Meaning | Example | Output |
|------|---------|---------|--------|
| `d` | Whole number | `f"{42:d}"` | `42` |
| `f` | Fixed-point float | `f"{3.14159:.2f}"` | `3.14` |
| `e` | Scientific notation | `f"{1234.5:e}"` | `1.2345e+03` |
| `%` | Percentage | `f"{0.85:.0%}"` | `85%` |
| `x` | Hexadecimal | `f"{255:x}"` | `ff` |
| `b` | Binary | `f"{5:b}"` | `101` |

You can even pad these. `f"{5:08b}"` produces `00000101` — binary, padded with zeros to a width of 8. The full set of options lives in the [official Python format specification](https://docs.python.org/3/library/string.html#format-specification-mini-language-spec), but the table above is enough for the vast majority of programs.

## The format() Method and the % Operator

f-strings are the modern default, but you will run into two older styles when reading existing code, so it helps to recognise them.

The **`str.format()` method** came before f-strings (it works all the way back to Python 2.6). You leave empty `{}` placeholders in the string and pass the values into `.format()`:

```python
print("{} costs ${}".format("Coffee", 4.5))      # Coffee costs $4.5
print("{0} {1} {0}".format("ho", "hey"))         # ho hey ho  (reuse by index)
print("{product}: ${price}".format(product="Tea", price=3.0))  # Tea: $3.0
```

The colon mini-language works here too — `"{:,.2f}".format(amount)` behaves exactly like the f-string version. The one place `.format()` still shines is when the template and the data are separate, such as a template you define once and reuse with many values:

```python
row = "{name:<10}{score:>6}"
print(row.format(name="Alice", score=95))
print(row.format(name="Bob", score=88))
```

The **`%` operator** is the oldest style, inherited from the C language. You will mostly meet it in older code:

```python
name = "Maria"
balance = 1234.56
print("Hello %s, your balance is $%.2f" % (name, balance))   # -> Hello Maria, your balance is $1234.56
```

Here `%s` means "insert a string" and `%.2f` means "insert a float with 2 decimals". It works, but it is harder to read and easy to get wrong, so prefer f-strings for anything new.

## Which Method Should You Use?

For a beginner, the short answer is: **use f-strings**. They are the most readable, the fastest, and the style you will see most in modern tutorials and codebases. Reach for the others only for the specific reasons below.

| Feature | f-string | `.format()` | `%` operator |
|---------|----------|-------------|--------------|
| Readability | Excellent | Good | Fair |
| Speed | Fastest | Slower | Slower |
| Python version | 3.6+ | 2.6+ | All |
| Inline expressions | Yes | No | No |
| Reusable template | No | Yes | Yes |

Use **f-strings** for almost everything. Drop to **`.format()`** when you need one template applied to many rows of data. Treat the **`%` operator** as read-only knowledge for maintaining older programs.

## Common Beginner Mistakes

A few small slips trip up nearly everyone learning Python string formatting. Knowing them in advance saves a lot of confused debugging.

```python
name = "Sam"
print("Hello {name}")    # prints: Hello {name}  (bug — the f is missing)
print(f"Hello {name}")   # prints: Hello Sam     (correct)

print(f"{{not a variable}}")   # prints: {not a variable}  (doubled braces = literal)

print("%s and %s" % ("a",))    # raises IndexError: not enough arguments
```

The first one is by far the most common: if your output shows the variable *name* in curly braces instead of its value, you forgot the `f` prefix. The second matters when you write JSON or other text that genuinely needs `{` and `}` characters — double them so Python knows they are literal, not placeholders.

## Frequently Asked Questions

### What is the difference between f-strings and the format() method?

f-strings embed your variables directly inside the string where they will appear, which makes them short and easy to read. The `format()` method keeps the template separate from the data, which is handy when you want to reuse one template with many values. Both use the same colon-based formatting rules, so what you learn for one transfers to the other.

### Why is my f-string printing the variable name instead of its value?

You almost certainly forgot the `f` prefix. `"Hello {name}"` prints the literal text `Hello {name}`, while `f"Hello {name}"` substitutes the variable's value. This is the single most common beginner mistake with Python string formatting.

### How do I show a number with two decimal places?

Add `:.2f` inside the braces: `f"{price:.2f}"`. For money with a thousands separator, use `f"${price:,.2f}"`, which turns `1234567.89` into `$1,234,567.89`.

### Can I use f-strings in older versions of Python?

f-strings need Python 3.6 or newer. If you must support Python 3.5 or earlier, use the `format()` method or the `%` operator instead — `.format()` is the safest portable choice across versions.

### Which string formatting method is fastest?

f-strings are the fastest because Python compiles them straight into efficient instructions that build the string directly, without the extra function call that `.format()` makes. For loops that run many times, f-strings are the best choice.

## Wrapping Up

Python string formatting turns scattered variables into clean, readable text, and you now have the whole picture: f-strings for almost everything, the `format()` method when you need a reusable template, and the `%` operator for understanding older code. The colon-based mini-language — `.2f`, `,`, `<10`, `.1%` — is shared across all three, so learning it once pays off everywhere.

The fastest way to make it stick is to use it. Take one place in your own code where you join text with `+` and `str()`, and rewrite it as an f-string — perhaps a message you print, or a line you write to a file (see [Python file handling](/languages/python/file-handling/) if you are saving output). The readability improvement is immediate, and the syntax becomes second nature far quicker by doing than by reading. For every formatting option Python supports, the [official documentation on f-strings](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals) is the reference to keep nearby.
