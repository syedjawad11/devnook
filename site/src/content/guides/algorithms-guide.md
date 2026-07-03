---
title: "Luhn Algorithm, TSP, and Greedy: A Practical Guide"
description: "Luhn algorithm validates credit cards before any API call. Learn TSP, greedy strategies, and Python examples for three classic algorithm problems."
category: guides
subcategory: "Reference"
template_id: "guide-v2"
tags: [algorithms, luhn-algorithm, greedy, travelling-salesman, computer-science]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-07-03"
og_image: "/og/guides/algorithms-guide.png"
actual_word_count: 3242
schema_org: "<script type=\"application/ld+json\">\n{\"@context\":\"https://schema.org\",\"@type\":[\"Article\",\"FAQPage\"],\"headline\":\"Luhn Algorithm, TSP, and Greedy: A Practical Guide\",\"description\":\"Luhn algorithm validates credit cards before any API call. Learn TSP, greedy strategies, and Python examples for three classic algorithm problems.\",\"datePublished\":\"2026-07-03\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/guides/algorithms-guide/\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"How does the Luhn algorithm detect typos in card numbers?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"The Luhn algorithm catches single-digit errors and most adjacent transpositions. When any digit changes, the weighted sum changes and no longer divides evenly by 10. The one case it misses is transposing two identical adjacent digits, which produces no change in the sum.\"}},{\"@type\":\"Question\",\"name\":\"Is the travelling salesman problem ever solved exactly?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"For small inputs under 20 cities, yes. The Held-Karp dynamic programming algorithm solves TSP exactly in O(n squared times 2 to the n). For large inputs with hundreds or thousands of cities, exact solutions are not practical and heuristics such as nearest-neighbour or simulated annealing are used instead.\"}},{\"@type\":\"Question\",\"name\":\"When should you use a greedy algorithm instead of dynamic programming?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Use greedy when the problem has the greedy choice property and optimal substructure, meaning local optimal choices always produce a global optimum. Greedy is faster and simpler. Use dynamic programming when overlapping subproblems exist but the greedy choice property does not hold, such as 0 slash 1 knapsack or edit distance.\"}}]}\n</script>"
---

The **Luhn algorithm** feels almost too simple for how much work it does. A single arithmetic formula — no databases, no network calls — decides whether a credit card number is structurally valid before any further processing. That makes it a useful starting point for thinking about algorithm design: a small, precise rule solving a real problem at massive scale.

This guide covers three algorithm families worth understanding: the **Luhn algorithm** for check-digit validation, the travelling salesman problem as a canonical example of combinatorial hardness, and greedy strategies as a class of approaches that trade optimality guarantees for practical speed. Each belongs to a different algorithmic regime, and recognising which regime a new problem falls into is one of the most transferable skills in software engineering.

## How the Luhn Algorithm Validates Card Numbers

The Luhn algorithm — also called the Luhn formula or modulo-10 algorithm — was designed by Hans Peter Luhn at IBM in 1954. Its original purpose was to protect against accidental errors in identification numbers, not to provide cryptographic security. That distinction matters: Luhn is a check-digit scheme. It detects transpositions and single-digit errors with high reliability but offers no resistance to deliberate fraud by anyone who knows how it works. The [Wikipedia article on the Luhn algorithm](https://en.wikipedia.org/wiki/Luhn_algorithm) documents its full range of applications and historical context.

The algorithm runs in five steps:

1. Starting from the rightmost digit (the check digit), move left through the number.
2. Double every second digit you encounter moving left.
3. If doubling a digit produces a result greater than 9, subtract 9 from the result.
4. Sum all the digits — both the unchanged ones and the doubled-and-adjusted ones.
5. If the total is divisible by 10 (total mod 10 equals 0), the number passes the check.

Take the Visa test card number `4532015112830366`. Working right to left, the digits at positions 2, 4, 6, 8 (counting from the right, starting at 1) get doubled. The digit 3 at position 2 becomes 6. The digit 1 at position 4 becomes 2. The digit 1 at position 6 becomes 2. The digit 5 at position 8 becomes 10, which exceeds 9, so subtract 9 to get 1. Sum all the modified and unmodified digits and you get a total divisible by 10 — the number is valid.

The check digit — that rightmost digit — is chosen by card issuers so that this sum always comes out clean for any genuinely issued number. Payment systems use Luhn as the first filter: catch obvious structural errors before spending a network round-trip on a number that cannot possibly be valid. Beyond credit cards, Luhn validates IMEI numbers (mobile device identifiers), National Provider Identifiers in US healthcare, and ISIN securities identifiers. Any long numeric ID with a check digit is worth checking against Luhn.

What Luhn does NOT detect: transpositions of two identical adjacent digits (swapping "44" → "44" changes nothing), and any number deliberately crafted by someone who knows the algorithm. Both are accepted limitations for a scheme designed around accidental errors — typos, transpositions, single key slip.

## Implementing the Luhn Algorithm in Python

The Python implementation maps directly to the five-step description above:

```python
def luhn_check(card_number: str) -> bool:
    """Return True if card_number passes the Luhn algorithm check."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if not digits:
        return False

    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:          # every second position from the right (index 1, 3, 5...)
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit

    return total % 10 == 0


print(luhn_check("4532015112830366"))   # True — known Visa test number
print(luhn_check("4532015112830367"))   # False — last digit changed
print(luhn_check("1234567890123456"))   # False
```

The loop iterates once through the reversed digit list, making this O(n) in both time and space. In practice, card numbers are 13–19 digits, so the entire check completes in microseconds — fast enough to run on every keystroke in a payment form without noticeable delay.

A common companion function is a check-digit generator. Given the first 15 digits of a card number, compute which check digit makes the full number Luhn-valid:

```python
def luhn_generate_check_digit(partial: str) -> int:
    """Return the check digit that completes partial into a Luhn-valid number."""
    for check in range(10):
        if luhn_check(partial + str(check)):
            return check
    raise ValueError("No valid check digit found — input may be malformed")


print(luhn_generate_check_digit("453201511283036"))  # 6
```

This pattern is standard in test data generation for payment workflows. Developers writing integration tests need Luhn-valid card numbers without using real credentials, and this gives them a programmatic way to generate them. Many testing libraries expose a similar function under names like `generate_test_card`.

## The Travelling Salesman Problem: What It Is and Why It Stays Hard

The [travelling salesman problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem) (TSP) asks a deceptively simple question: given a set of cities and the distances between every pair, what is the shortest route that visits each city exactly once and returns to the starting point?

For five cities, a brute-force search checks 12 distinct routes (4! / 2 for a symmetric problem). For 20 cities, the count reaches roughly 60 trillion. For 100 cities, the number of possible routes exceeds the number of atoms in the observable universe. Exact solutions become computationally intractable well before you reach those scales.

TSP is NP-hard. No polynomial-time algorithm is known for it. The best exact methods — branch-and-bound and the Held-Karp dynamic programming algorithm — still scale exponentially. Held-Karp runs in O(n² × 2ⁿ), which is a significant improvement over brute force O(n!), but remains unusable for large inputs. For 25 cities, Held-Karp requires evaluating roughly 800 million subproblems; for 50 cities, the number exceeds the memory capacity of any current computer.

Brute force illustrates why exact TSP is only feasible for small inputs:

```python
from itertools import permutations

def tsp_brute_force(cities: list, distances: dict) -> tuple:
    """Return (minimum_distance, best_route) by checking every permutation."""
    start = cities[0]
    remaining = cities[1:]
    best_distance = float('inf')
    best_route = None

    for perm in permutations(remaining):
        route = [start] + list(perm) + [start]
        total = sum(
            distances[(route[i], route[i + 1])]
            for i in range(len(route) - 1)
        )
        if total < best_distance:
            best_distance = total
            best_route = route

    return best_distance, best_route
```

For five or six cities, this runs comfortably in milliseconds. By 12 cities, you start waiting seconds. By 20, it is unusable on any modern hardware.

The practical value of TSP is as a model for approximation. For logistics routing, PCB manufacturing (finding the shortest drill path across thousands of circuit board holes), telescope scheduling (minimising time spent repositioning between targets), and DNA read assembly, an answer that is 10–15% above optimal and found in milliseconds beats an optimal answer found in hours. The field of combinatorial optimisation has produced a rich toolkit of approximation algorithms, local search methods, and metaheuristics specifically for TSP and related problems.

## Greedy Algorithms: Taking the Best Available Move

A greedy algorithm makes the locally optimal choice at each decision point and never revisits it. No backtracking, no look-ahead, no future consideration — just: "what is the best move available right now?"

Greedy algorithms are fast, typically O(n log n) when paired with a sort and O(n) for the selection phase. They are also straightforward to implement and to reason about. The formal requirements are documented in the [Wikipedia greedy algorithm article](https://en.wikipedia.org/wiki/Greedy_algorithm). The difficulty is proving the approach correct: you need to establish that the problem has two structural properties before greedy is guaranteed to give the right answer.

**Problems where greedy is provably optimal:**

- **Activity selection**: given a set of time intervals, find the maximum number of non-overlapping intervals you can schedule. Always pick the interval with the earliest end time. This is optimal because finishing early leaves the maximum time for future intervals.
- **Huffman coding**: given symbol frequencies, build an optimal prefix-free binary code for lossless data compression. Always merge the two lowest-frequency symbols into a combined node. Optimal by exchange argument — any other choice produces a longer expected code length.
- **Dijkstra's shortest path**: with non-negative edge weights, always relax the unvisited node with the smallest known distance from the source. Correct because revisiting a node through a longer path cannot improve its distance when all edge weights are non-negative.
- **Minimum spanning trees (Kruskal's and Prim's)**: always add the cheapest available edge that does not create a cycle. Both produce a minimum-weight spanning tree, proven by the cut property of MSTs.

**Problems where greedy fails:**

- **0/1 knapsack**: taking the item with the highest value-per-weight ratio first can leave remaining capacity wasted in a way that costs more than selecting a slightly lower ratio item would have. Dynamic programming is required for exact solutions.
- **Coin change with non-standard denominations**: greedy works for standard currency denominations (25¢, 10¢, 5¢, 1¢) because they have a specific mathematical structure, but fails for arbitrary sets like {1, 3, 4} where greedy picks 4 + 1 + 1 = 3 coins for 6 but DP finds 3 + 3 = 2 coins.
- **TSP**: as the section below shows, always going to the nearest city produces reasonable but usually non-optimal tours.

Understanding [Python data structures](/languages/python/data-structures/) like heaps and sorted containers is directly useful when implementing greedy algorithms. Dijkstra's and Prim's MST both rely on a min-heap for the "extract minimum" operation. Python's `heapq` module provides this in O(log n) per operation, which keeps the overall algorithm within O((V + E) log V) for graph problems.

The activity selection proof is worth studying because it is one of the cleanest greedy correctness arguments. Suppose you have intervals sorted by end time and you apply greedy, always selecting the earliest-finishing interval compatible with the current schedule. Claim: this produces the maximum number of non-overlapping intervals. Proof sketch: suppose an optimal solution picks some first interval that ends later than the greedy choice. You can swap the greedy choice in for that first interval — it ends no later, so it cannot conflict with any interval the optimal solution uses next. By induction, greedy produces a schedule as large as any other. The key insight: ending earlier never hurts.

## A Greedy Approach to TSP: Nearest Neighbour

The nearest-neighbour heuristic applies a greedy strategy to TSP: start at any city, always travel to the closest unvisited city, continue until all cities are visited, then return home.

It is not optimal — in adversarially constructed cases, nearest-neighbour can produce tours nearly twice the optimal length. On random instances with uniformly distributed cities, it typically lands within 20–25% of optimal, which is often acceptable for practical problems where computation time matters.

```python
def tsp_nearest_neighbour(cities: list, distances: dict) -> tuple:
    """Greedy nearest-neighbour TSP heuristic. Returns (total_distance, route)."""
    unvisited = set(cities)
    current = cities[0]
    route = [current]
    unvisited.remove(current)
    total_distance = 0

    while unvisited:
        nearest = min(
            unvisited,
            key=lambda c: distances.get((current, c), float('inf'))
        )
        total_distance += distances.get((current, nearest), 0)
        route.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    total_distance += distances.get((current, route[0]), 0)  # return to start
    route.append(route[0])
    return total_distance, route
```

This runs in O(n²): for each of n cities, the `min()` call scans the remaining unvisited set. For a few thousand cities, this is still fast. For tens of thousands of cities, you would replace the linear scan with a spatial data structure such as a k-d tree, reducing each nearest-neighbour query to O(log n).

The nearest-neighbour output is frequently used as an initial solution for more sophisticated refinement steps. The 2-opt local search technique iteratively identifies pairs of edges that, if reversed, reduce total tour length. Starting from a decent greedy tour rather than a random permutation typically produces better 2-opt results in fewer iterations. Simulated annealing and genetic algorithms take a similar approach: begin with a greedy tour, then explore the neighbourhood.

## When Greedy Works and When It Falls Short

Two formal properties determine whether a greedy approach is correct rather than merely fast:

1. **Greedy choice property**: a globally optimal solution can always be constructed by making locally optimal choices — no greedy pick ever forecloses a better global outcome.
2. **Optimal substructure**: the optimal solution to the whole problem contains optimal solutions to its subproblems.

Both are required. Activity selection, Dijkstra, Huffman, and Kruskal's MST possess both. TSP and 0/1 knapsack possess neither (or only the second without the first).

A practical decision framework for choosing algorithm strategy:

| Problem type | Recommended approach | Classic examples |
|---|---|---|
| Greedy choice property holds | Greedy — exact and fast | Activity selection, Dijkstra, Huffman coding, MST |
| Large input, near-optimal acceptable | Greedy heuristic | TSP nearest-neighbour, bin packing first-fit |
| Overlapping subproblems, exact answer needed | Dynamic programming | 0/1 knapsack, edit distance, longest common subsequence |
| Structured search, pruning viable | Branch and bound | Integer programming, exact TSP solvers |
| No polynomial algorithm known, exact required | Exponential algorithms | Held-Karp TSP, subset sum |

The question to ask before writing a greedy solution: "Can I prove that a locally optimal choice never blocks a better global outcome?" If yes, greedy is your fastest correct path. If no, you are writing a heuristic — which may be exactly what you need for a large problem where exact optimisation is impractical, but you should know the difference and benchmark the approximation quality.

## Where These Algorithms Appear in Real Projects

**Luhn validation** runs on every e-commerce checkout in the world. Payment processors validate card numbers client-side before any server request. Stripe.js, Braintree, and similar browser libraries run the Luhn check locally so that a transposed digit never triggers an API round-trip. Beyond payments, the same formula validates IMEI numbers (mobile device identifiers used in telecommunications), US National Provider Identifiers, Canadian Social Insurance Numbers, and ISIN securities identifiers — any long numeric identifier that needs a cheap structural integrity check before further processing.

**TSP variants** appear across engineering domains. PCB manufacturers need the shortest drill path across thousands of holes in a circuit board; shaving milliseconds per board across millions of boards compounds quickly. DNA sequencing uses a related problem called the shortest superstring problem to assemble short DNA reads into longer sequences. Telescope scheduling optimises the order in which a telescope points at targets to minimise mechanical slew time. Google Maps and similar routing engines do not solve TSP exactly — they use hierarchical decomposition, precomputed road networks, and local search heuristics to produce near-optimal routes in under a second for city-scale inputs.

**Greedy strategies** run inside familiar tools. gzip and zlib use Huffman coding (a greedy construction) as their final entropy coding stage. The OSPF routing protocol uses Dijkstra to compute shortest paths between routers. Build systems like Make and Ninja use topological sort — a greedy selection of nodes with no pending dependencies — to determine compilation order. The `diff` command uses a dynamic programming longest-common-subsequence algorithm for line matching, but many surrounding decisions in patch generation are greedy selections.

For a comparative look at sorting and traversal algorithms — the adjacent algorithmic territory — the [sorting algorithms comparison](/blog/sorting-algorithms-comparison/) covers quicksort, mergesort, and heapsort side by side with implementations in Python, JavaScript, Go, and Java. If you need to verify a hash or checksum as part of an integrity workflow, the [DevNook hash generator](/tools/hash-generator/) computes MD5, SHA-1, and SHA-256 directly in the browser without sending data to a server.

## Frequently Asked Questions

### How does the Luhn algorithm detect typos in card numbers?

The Luhn algorithm catches single-digit errors and most adjacent transpositions. When any digit changes, the weighted sum of all digits changes, and the result no longer divides evenly by 10 — the check fails. Swapping two adjacent digits that are different also changes the weighted sum, because the doubled digit changes identity. The one failure case is transposing two identical adjacent digits, such as swapping "44" for "44" — there is nothing to detect. This is an accepted design trade-off: Luhn was built for accidental errors (typing a 5 instead of a 3, reversing "52" to "25"), not adversarial manipulation.

### Is the travelling salesman problem ever solved exactly in practice?

For small inputs — under 15 to 20 cities — yes. The Held-Karp dynamic programming algorithm finds exact solutions in O(n² × 2ⁿ) time, which is tractable for small n and widely used in practice for those scales. For large real-world instances, researchers using the Concorde TSP solver have solved instances with tens of thousands of cities, but doing so required days to weeks of distributed computing time. Practical systems use approximation algorithms with provable quality bounds (the Christofides algorithm guarantees within 1.5× optimal for metric TSP) or heuristics with empirically good quality.

### When should you use a greedy algorithm instead of dynamic programming?

Reach for greedy when you can prove the problem has the greedy choice property and optimal substructure — the two formal tests that guarantee local optimal choices produce a global optimal result. Greedy is typically O(n log n) against O(n²) or worse for dynamic programming, and the code is usually simpler to write and debug. Use dynamic programming when the problem has overlapping subproblems but lacks the greedy choice property: 0/1 knapsack, longest common subsequence, edit distance, and matrix chain multiplication are all cases where greedy produces wrong answers and DP is the correct approach.

### How is greedy different from brute force?

Brute force examines every possible solution and returns the best — guaranteed optimal, but combinatorially expensive. Greedy builds a solution incrementally, making one locally optimal choice per step and never revisiting previous choices. This is O(n log n) to O(n²) depending on the problem, far faster than brute force. The trade-off: greedy may not be optimal unless the problem structure guarantees it. Brute force is always correct; greedy is only correct when the greedy choice property holds.

## Conclusion

The **Luhn algorithm** demonstrates that algorithms do not need to be complex to be valuable. A single modulo operation, applied across a reversed digit list with one doubling rule, produces a reliable structural check that runs on billions of transactions daily without any server-side infrastructure. The travelling salesman problem represents the opposite end of the spectrum: simple to state, computationally intractable to solve exactly at scale, and practically important enough to have generated decades of approximation research. Greedy algorithms sit between the two — for the right problem, they produce exact optimal results faster than any other approach; for the wrong problem, they produce heuristics of varying quality.

The skill these three examples build is the same: recognising algorithmic regime early. Is the problem amenable to a simple formula? Does it have the structure greedy requires? Is it NP-hard, pushing you toward approximation? The earlier you answer those questions, the less time you spend implementing the wrong approach.

For the modulo arithmetic and integer operations that power the Luhn check, the [Python math and numbers guide](/languages/python/math-numbers/) covers operators, built-in functions, and number types with runnable examples. Token-based validation — a conceptually related family where a structured token encodes verifiable claims — is explored in [What is JWT?](/guides/what-is-jwt/), which covers how JSON Web Tokens are constructed, verified, and where they fit alongside checksum-based approaches like Luhn.
