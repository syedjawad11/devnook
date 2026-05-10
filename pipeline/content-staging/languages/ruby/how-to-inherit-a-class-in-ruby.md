---
title: "How to Inherit a Class in Ruby? — A Complete Guide"
description: "Learn how to use class inheritance in Ruby to share behavior and avoid code duplication. Understand super, method overriding, and inheritance chains."
category: languages
language: "ruby"
concept: "inherit-a-class"
difficulty: "intermediate"
template_id: "lang-v2"
tags: ["ruby", "inherit-a-class", "oop", "inheritance"]
related_tools: []
related_posts: []
published_date: "2026-05-10"
og_image: "/og/languages/ruby/inherit-a-class.png"
---

When building object-oriented applications, developers frequently encounter situations where multiple data structures require identical functional capabilities. Knowing how to inherit a class in ruby is critical to solving this fundamental architectural challenge. Without proper inheritance structures, codebases quickly become bloated, difficult to maintain, and highly susceptible to synchronization errors when updating shared logic.

## The Problem

Consider a system designed to manage different types of employees within a company. A typical early-stage approach involves creating discrete, independent classes for each specific role. While this works initially, it rapidly degenerates as the system scales and common behaviors must be implemented across all role types.

```ruby
# A naive approach with severe code duplication
class Manager
  def initialize(name, salary)
    @name = name
    @salary = salary
  end

  def process_payroll
    puts "Processing payroll for #{@name} in the amount of $#{@salary}."
  end

  def approve_timesheets
    puts "#{@name} is approving timesheets."
  end
end

class Developer
  def initialize(name, salary)
    @name = name
    @salary = salary
  end

  def process_payroll
    puts "Processing payroll for #{@name} in the amount of $#{@salary}." # Duplicated logic!
  end

  def write_code
    puts "#{@name} is writing code."
  end
end
```

The approach above represents a significant architectural failure because the initialization logic and the `process_payroll` method are entirely duplicated across the `Manager` and `Developer` classes. If the payroll processing logic needs to change—for example, to include tax calculations—the developer must manually locate and update every single class that implements this method. This approach simply does not scale, violates the Don't Repeat Yourself principle, and is highly error-prone in production environments.

## The Ruby Solution: Inherit a Class

The direct solution to this structural problem is class inheritance. Inheritance allows a new class (the subclass) to acquire the properties and methods of an existing class (the superclass). By extracting the shared behavior into a common superclass, we establish a hierarchical relationship that eliminates duplication and centralizes shared logic.

```ruby
# The corrected version using the inheritance operator '<'
class Employee
  def initialize(name, salary)
    @name = name
    @salary = salary
  end

  def process_payroll
    puts "Processing payroll for #{@name} in the amount of $#{@salary}."
  end
end

class Manager < Employee # Manager inherits from Employee
  def approve_timesheets
    puts "#{@name} is approving timesheets."
  end
end

class Developer < Employee # Developer inherits from Employee
  def write_code
    puts "#{@name} is writing code."
  end
end

dev = Developer.new("Alice", 90000)
dev.process_payroll # Method inherited from Employee
dev.write_code      # Method specific to Developer
```

By utilizing the `<` syntax, we declare that both `Manager` and `Developer` inherit from the `Employee` superclass. All initialization logic and the `process_payroll` method are now defined in exactly one location. The subclasses automatically receive these capabilities without any further code. Furthermore, the subclasses are free to define their own specific behaviors, such as `approve_timesheets` or `write_code`, which remain isolated from each other. This structural change guarantees that any future modifications to payroll processing will automatically propagate to all employee types seamlessly.

## How Inherit a Class Works in Ruby

The mechanics of class inheritance in Ruby revolve around a concept known as single inheritance. A subclass in Ruby can only have one direct superclass. This design decision intentionally avoids the extreme complexity and ambiguity that arises from multiple inheritance systems (often referred to as the Diamond Problem). When a subclass is defined using the `<` operator, Ruby establishes an internal pointer linking the subclass to its superclass.

When a method is called on an object, Ruby executes a precise algorithm known as the method lookup path. The interpreter first inspects the object's singleton class, then the class the object was instantiated from. If the method is not found there, the interpreter follows the inheritance pointer to the superclass and searches there. This process continues up the hierarchy until the method is found or until it reaches the top of the hierarchy (usually the `BasicObject` class), at which point a `NoMethodError` is raised.

Another vital mechanic is the `super` keyword. When a subclass overrides a method defined in its superclass, it completely masks the original implementation. However, the subclass can invoke the original, overridden method by calling `super` within its own method definition. `super` automatically forwards all arguments passed to the subclass method up to the superclass method, enabling the subclass to augment, rather than entirely replace, the parent behavior.

## Going Further — Real-World Patterns

In production systems, inheritance is utilized to implement sophisticated design patterns. Recognizing these patterns differentiates a novice from a highly capable software engineer.

**Pattern 1: The Template Method Pattern**

This pattern defines the skeleton of an algorithm in an operation, deferring some steps to subclasses. The superclass controls the overall execution flow, while subclasses provide the specific implementation details for certain steps.

```ruby
class DataImporter
  def import_data
    connect_to_source
    raw_data = fetch_data
    processed_data = parse_data(raw_data)
    save_to_database(processed_data)
  end

  def connect_to_source
    raise NotImplementedError, "Subclasses must implement connect_to_source"
  end

  def fetch_data
    raise NotImplementedError, "Subclasses must implement fetch_data"
  end

  # Default implementations provided by the superclass
  def parse_data(data)
    data.map(&:strip)
  end

  def save_to_database(data)
    puts "Saving #{data.size} records to DB."
  end
end

class CsvImporter < DataImporter
  def connect_to_source
    puts "Opening CSV file stream."
  end

  def fetch_data
    [" row 1 ", " row 2 "]
  end
end

importer = CsvImporter.new
importer.import_data # Executes the algorithm defined in DataImporter
```

The `DataImporter` defines the `import_data` workflow, but explicitly forces subclasses to implement connection and fetching logic by raising `NotImplementedError`. This guarantees a consistent execution order while allowing infinite flexibility in data source types.

**Pattern 2: Augmenting Initialization with Super**

Subclasses frequently require their own specific initialization parameters in addition to those required by the superclass. Utilizing `super` allows the subclass to initialize its unique state while correctly delegating the base initialization to the parent.

```ruby
class Vehicle
  attr_reader :wheels

  def initialize(wheels)
    @wheels = wheels
  end
end

class Truck < Vehicle
  attr_reader :cargo_capacity

  def initialize(wheels, cargo_capacity)
    super(wheels) # Delegates the wheels assignment to Vehicle
    @cargo_capacity = cargo_capacity # Handles subclass specific state
  end
end

semi = Truck.new(18, 40000)
puts semi.wheels # Outputs 18
```

This pattern prevents the subclass from needing to understand the internal initialization mechanics of the superclass, ensuring strong encapsulation and clean separation of concerns within the object hierarchy.

## What to Watch Out For

A primary danger associated with inheritance is the creation of unnecessarily deep hierarchies, often referred to as the Yo-Yo problem. When an inheritance chain spans five or six levels, understanding the behavior of a subclass requires a developer to constantly navigate up and down the chain to trace method definitions and state changes. This severely degrades maintainability and increases cognitive load. Inheritance hierarchies should remain as shallow as functionally possible.

Additionally, developers must be extremely careful when overriding methods. If a subclass overrides a method that the superclass depends on for its internal logic, the subclass might inadvertently break the superclass's functionality. This violates the Liskov Substitution Principle. To prevent this, developers must thoroughly understand the superclass implementation before overriding its public interface, and should generally favor composition over inheritance when behavior sharing is required without an explicit "is-a" conceptual relationship.

## Under the Hood: Performance & Mechanics

At runtime, navigating the inheritance chain incurs a performance cost. Every time a method is invoked, Ruby must theoretically traverse the ancestor chain to locate the executable code. To prevent this from becoming a catastrophic performance bottleneck, the Ruby Virtual Machine implements aggressive method caching mechanisms. 

When a method is called for the first time, Ruby traverses the hierarchy, locates the method, and stores a pointer to it in a specialized cache associated with the calling class. Subsequent calls to that method bypass the hierarchy traversal entirely and execute directly via the cached pointer. This achieves O(1) time complexity for method resolution under normal circumstances. 

However, this caching mechanism has hidden costs. Whenever a class hierarchy is modified at runtime—for example, if a method is dynamically added to a superclass or a module is included—Ruby must invalidate the global method cache. This cache invalidation forces the virtual machine to discard all previously optimized method lookups across the entire application, causing a temporary but severe performance degradation until the caches are rebuilt. Therefore, dynamically modifying deep inheritance hierarchies during high-load production operations should be strictly avoided.

## Advanced Edge Cases

Ruby's implementation contains highly specific edge cases that demand careful attention, particularly regarding class-level state and the top-level object hierarchy.

**Edge Case 1: Class Variable Sharing**

Class variables, denoted by `@@`, exhibit notoriously problematic behavior within inheritance hierarchies. Unlike class instance variables, class variables are shared across the entire inheritance tree, meaning a modification by a subclass will alter the state for the superclass and all other subclasses simultaneously.

```ruby
class Parent
  @@config = "default"

  def self.config
    @@config
  end
end

class ChildA < Parent
  @@config = "modified by A"
end

class ChildB < Parent
end

puts Parent.config # Outputs: "modified by A"
puts ChildB.config # Outputs: "modified by A"
```

The underlying reason for this behavior is that Ruby treats class variables as fundamentally bound to the lexical scope of the highest class in the hierarchy where they are defined. `ChildA` does not create its own copy of `@@config`; it directly mutates the shared variable belonging to `Parent`. This global mutation effect causes unpredictable state corruption in complex systems, leading most professional developers to utilize class instance variables (`@config` defined on the class itself) instead.

**Edge Case 2: Inheriting from BasicObject**

By default, all Ruby classes inherit from `Object`, which includes the `Kernel` module, providing essential methods like `puts`, `raise`, and `require`. However, Ruby permits inheriting directly from `BasicObject`, which is the absolute root of the hierarchy and is completely devoid of these standard methods.

```ruby
class BlankSlate < BasicObject
  def method_missing(name, *args)
    ::Kernel.puts "Intercepted call to #{name}"
  end
end

obj = BlankSlate.new
# obj.puts "hello" # This would cause a NoMethodError!
obj.arbitrary_method # Outputs: Intercepted call to arbitrary_method
```

This edge case is utilized primarily when constructing Proxy objects or dynamic delegates. Because a `BasicObject` lacks almost all standard methods, it guarantees that virtually any method call will trigger the `method_missing` hook rather than accidentally resolving to a built-in method. While powerful, working within a `BasicObject` subclass requires explicitly utilizing top-level namespace resolution (like `::Kernel`) to access standard functionality, severely complicating basic operations.

## Testing Inherit a Class in Ruby

When testing inheritance hierarchies, it is vital to verify both the subclass-specific behavior and the integration with the inherited behavior without duplicating test logic. The RSpec testing framework provides shared examples specifically to solve this problem.

```ruby
# Testing implementation using RSpec shared examples
RSpec.shared_examples "an employee" do
  it "can process payroll" do
    expect { subject.process_payroll }.to output(/Processing payroll/).to_stdout
  end
end

RSpec.describe Developer do
  let(:subject) { Developer.new("Alice", 90000) }

  # Test inherited behavior using the shared example
  it_behaves_like "an employee"

  # Test specific subclass behavior in isolation
  it "can write code" do
    expect { subject.write_code }.to output(/writing code/).to_stdout
  end
end
```

The mechanism detailed above guarantees that any class claiming to inherit from the base employee structure genuinely implements the required interfaces. By utilizing shared examples, we abstract the testing logic for the superclass behavior. When we describe the `Developer` class, we simply include the shared example, instantly verifying the inherited behavior. This ensures that the test suite remains DRY and maintains strict alignment with the architectural design of the application.

## Summary

The challenge of redundant code and synchronized updates across multiple data structures is a critical issue in software engineering. Knowing how to inherit a class in ruby completely resolves this by allowing developers to extract common logic into a centralized superclass. By understanding method lookup paths, utilizing the super keyword for behavioral augmentation, and remaining vigilant against deep hierarchical complexity, you can architect robust, scalable systems. For a practical complement to these patterns, see how [JSON parsing in Ruby](/languages/ruby/parse-json/) applies similar object-oriented techniques when working with external data sources.
