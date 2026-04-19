---
actual_word_count: 1464
category: blog
description: Quick sort, merge sort, bubble sort — implemented in 4 languages. Understand
  O(n log n) vs O(n²) with visual complexity tables.
og_image: /og/blog/sorting-algorithms-comparison.png
published_date: '2026-04-13'
related_content: []
related_posts:
- /languages/javascript/array-methods
related_tools: []
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\"\
  ,\n  \"@type\": \"BlogPosting\",\n  \"headline\": \"Sorting Algorithms Explained:\
  \ Python, JS, Go, and Java Side by Side\",\n  \"description\": \"Quick sort, merge\
  \ sort, bubble sort — implemented in 4 languages. Understand O(n log n) vs O(n²)\
  \ with visual complexity tables.\",\n  \"datePublished\": \"2026-04-13\",\n  \"\
  author\": {\"@type\": \"Organization\", \"name\": \"DevNook\"},\n  \"publisher\"\
  : {\"@type\": \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"\
  },\n  \"url\": \"https://devnook.dev/blog/\"\n}\n</script>"
tags:
- sorting-algorithms
- python
- javascript
- go
- java
- complexity
template_id: blog-v1
title: 'Sorting Algorithms Explained: Python, JS, Go, and Java Side by Side'
---

Sorting algorithms comparison is one of the first computer science topics developers encounter, yet understanding the practical performance differences between quick sort, merge sort, and bubble sort across languages remains valuable throughout your career. This guide implements the three most common sorting algorithms in Python, [JavaScript](/languages/javascript), Go, and Java to show syntax patterns, built-in alternatives, and when time complexity matters.

## TL;DR — Which Sorting Algorithm Should You Use?

Use your language's built-in sort for production code unless you have a specific reason not to. All four languages implement optimized hybrid algorithms (Timsort in [Python](/languages/python), merge-insertion in V8 JavaScript, pattern-defeating quicksort in Go, dual-pivot quicksort in Java) that outperform hand-rolled implementations. Write custom sorts only for educational purposes, specialized data structures, or when you need guaranteed worst-case performance.

| | Quick Sort | Merge Sort | Bubble Sort |
|---|---|---|---|
| Best for | General-purpose sorting when average case matters | Guaranteed O(n log n), stable sort required | Teaching, tiny datasets only |
| Time complexity (avg) | O(n log n) | O(n log n) | O(n²) |
| Time complexity (worst) | O(n²) | O(n log n) | O(n²) |
| Space complexity | O(log n) | O(n) | O(1) |
| Stable | No | Yes | Yes |

## What is Quick Sort?

Quick sort is a divide-and-conquer algorithm that selects a pivot element, partitions the array around it (smaller elements left, larger right), then recursively sorts the partitions. Developed by Tony Hoare in 1959, it became popular because its average-case O(n log n) performance and in-place sorting made it practical for memory-constrained systems. Modern implementations use randomized pivot selection or median-of-three to avoid O(n²) worst case on sorted input.

## What is Merge Sort?

Merge sort splits the array in half recursively until single-element subarrays remain, then merges them back in sorted order. Its guaranteed O(n log n) worst-case performance and stability (preserves relative order of equal elements) make it ideal when consistency matters more than space. Python's Timsort is a merge sort variant optimized for real-world data with partial ordering.

## What is Bubble Sort?

Bubble sort repeatedly steps through the array, compares adjacent elements, and swaps them if out of order. The largest unsorted element "bubbles" to its position each pass. With O(n²) time complexity, it's inefficient for anything beyond teaching or datasets under 10 elements. Its only practical advantage is O(1) space complexity and simplicity.

## Key Differences

### Time Complexity Under Different Conditions

Quick sort averages O(n log n) but degrades to O(n²) when the pivot consistently lands at an extreme (sorted or reverse-sorted input with naive pivot selection). Merge sort maintains O(n log n) regardless of input ordering. Bubble sort always performs O(n²) comparisons unless you add early termination when no swaps occur.

For 10,000 random integers, quick sort typically completes in 2-3ms, merge sort in 3-4ms, and bubble sort in 200-300ms on modern hardware. The difference compounds exponentially: at 100,000 elements, bubble sort takes 20+ seconds while quick sort and merge sort remain under 50ms.

### Memory Usage

Quick sort sorts in-place with O(log n) stack space for recursion depth. Merge sort requires O(n) auxiliary space to hold the merged subarrays. Bubble sort uses O(1) additional space. For embedded systems or memory-constrained environments, quick sort's space efficiency matters. For datasets that fit comfortably in RAM, merge sort's stability often outweighs the memory cost.

### Stability

Merge sort and bubble sort preserve the relative order of equal elements (stable). Quick sort does not, unless you implement a more complex partitioning scheme. Stability matters when sorting objects by multiple keys — if you sort by last name then first name, a stable sort keeps "Smith, Alice" before "Smith, Bob" from the first sort.

### Built-In Language Implementations

Python uses Timsort (merge sort + insertion sort hybrid), JavaScript V8 uses Timsort as of 2018, Go uses pattern-defeating quicksort (quick sort variant), and [Java](/languages/java) uses dual-pivot quicksort for primitives and Timsort for objects. None use pure merge sort or naive quick sort because hybrid approaches perform better on real data.

## Code Comparison — Quick Sort in Four Languages

**Python**
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]  # median-of-three better for real use
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# Example
nums = [3, 6, 8, 10, 1, 2, 1]
print(quicksort(nums))  # [1, 1, 2, 3, 6, 8, 10]
```

**JavaScript**
```javascript
function quicksort(arr) {
    if (arr.length <= 1) return arr;
    const pivot = arr[Math.floor(arr.length / 2)];
    const left = arr.filter(x => x < pivot);
    const middle = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);
    return [...quicksort(left), ...middle, ...quicksort(right)];
}

// Example
const nums = [3, 6, 8, 10, 1, 2, 1];
console.log(quicksort(nums));  // [1, 1, 2, 3, 6, 8, 10]
```

**[Go](/languages/go)**
```go
func quicksort(arr []int) []int {
    if len(arr) <= 1 {
        return arr
    }
    pivot := arr[len(arr)/2]
    var left, middle, right []int
    for _, x := range arr {
        if x < pivot {
            left = append(left, x)
        } else if x == pivot {
            middle = append(middle, x)
        } else {
            right = append(right, x)
        }
    }
    return append(append(quicksort(left), middle...), quicksort(right)...)
}

// Example
nums := []int{3, 6, 8, 10, 1, 2, 1}
fmt.Println(quicksort(nums))  // [1 1 2 3 6 8 10]
```

**Java**
```java
public static List<Integer> quicksort(List<Integer> arr) {
    if (arr.size() <= 1) return arr;
    int pivot = arr.get(arr.size() / 2);
    List<Integer> left = new ArrayList<>();
    List<Integer> middle = new ArrayList<>();
    List<Integer> right = new ArrayList<>();
    
    for (int x : arr) {
        if (x < pivot) left.add(x);
        else if (x == pivot) middle.add(x);
        else right.add(x);
    }
    
    List<Integer> result = new ArrayList<>(quicksort(left));
    result.addAll(middle);
    result.addAll(quicksort(right));
    return result;
}

// Example
List<Integer> nums = Arrays.asList(3, 6, 8, 10, 1, 2, 1);
System.out.println(quicksort(nums));  // [1, 1, 2, 3, 6, 8, 10]
```

Python and JavaScript implementations are most concise due to list comprehensions and filter methods. Go requires explicit slice allocation. Java needs the most boilerplate with ArrayList operations. All four create new arrays rather than sorting in-place, trading space for code clarity.

## Code Comparison — Merge Sort in Four Languages

**Python**
```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

**JavaScript**
```javascript
function mergesort(arr) {
    if (arr.length <= 1) return arr;
    const mid = Math.floor(arr.length / 2);
    const left = mergesort(arr.slice(0, mid));
    const right = mergesort(arr.slice(mid));
    return merge(left, right);
}

function merge(left, right) {
    const result = [];
    let i = 0, j = 0;
    while (i < left.length && j < right.length) {
        if (left[i] <= right[j]) {
            result.push(left[i++]);
        } else {
            result.push(right[j++]);
        }
    }
    return result.concat(left.slice(i)).concat(right.slice(j));
}
```

Merge sort requires a separate merge function to combine sorted halves. The merge operation is where stability comes from — the `<=` comparison ensures equal elements from the left array appear before those from the right.

## When to Use Quick Sort

- Average-case performance matters more than worst-case guarantees
- Space is constrained and you can implement in-place partitioning
- Data is randomly distributed or you can randomize the pivot
- Stability is not required

## When to Use Merge Sort

- Guaranteed O(n log n) worst-case time is critical (real-time systems, SLA requirements)
- Stable sort is required (sorting database records by multiple fields)
- Sorting linked lists (merge sort works well without random access)
- External sorting (data larger than RAM, merge sort parallelizes cleanly)

## When to Use Bubble Sort

- Teaching fundamental sorting concepts
- Dataset has fewer than 10 elements
- You need to detect if an array is already sorted with one pass
- Never use in production

## The Verdict

Use your language's built-in sort: `sorted()` in Python, `Array.sort()` in JavaScript, `sort.Slice()` in Go, `Collections.sort()` or `Arrays.sort()` in Java. These implementations are faster, battle-tested, and handle edge cases you'll miss in a custom implementation.

Write custom sorting algorithms to understand recursion, time complexity analysis, and algorithm tradeoffs. Reference the implementations in this guide when learning recursion patterns or studying Big O notation. For production sorting needs, benchmark your language's built-in against specialized libraries if performance profiling shows sorting is a bottleneck.


- Python Recursion: Base Cases and Stack Depth
- Big O Notation: The Complete Guide
- JavaScript Array Methods Cheat Sheet
- Code Formatter Tool