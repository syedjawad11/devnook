---
title: "What Is a Cross Join in SQL? Examples Explained"
description: "Learn what is cross join in SQL, how it generates a Cartesian product, when to use it, and see practical examples in MySQL, PostgreSQL, and more."
category: guides
subcategory: "Web Concepts"
template_id: blog-v5
tags: [sql, database, joins, cross-join, cartesian-product]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-06-04"
og_image: "/og/guides/what-is-cross-join-in-sql.png"
actual_word_count: 3518
schema_org: "<script type=\"application/ld+json\">\n{\"@context\":\"https://schema.org\",\"@type\":[\"BlogPosting\",\"FAQPage\"],\"headline\":\"What Is a Cross Join in SQL? Examples Explained\",\"description\":\"Learn what is cross join in SQL, how it generates a Cartesian product, when to use it, and see practical examples in MySQL, PostgreSQL, and more.\",\"datePublished\":\"2026-06-04\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/guides/what-is-cross-join-in-sql/\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"What does CROSS JOIN return if one table is empty?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"If either input table has zero rows, the cross join returns zero rows. The Cartesian product of any set and an empty set is always empty.\"}},{\"@type\":\"Question\",\"name\":\"Is CROSS JOIN the same as a FULL OUTER JOIN?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"No. FULL OUTER JOIN returns at most rows_A + rows_B rows, using NULLs for missing matches. CROSS JOIN returns rows_A x rows_B rows with no NULLs.\"}},{\"@type\":\"Question\",\"name\":\"When should I use a CROSS JOIN in SQL?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Use CROSS JOIN when your requirement is genuinely all combinations of two sets: generating product variants, building reporting scaffolds, seeding test data, or computing round-robin tournament fixtures.\"}}]}\n</script>"
---
A cross join in SQL is one of those features that looks dangerous at first — and for good reason. Run it without understanding what you are asking for and you will end up with a result set that brings your database to its knees. Use it intentionally and it solves a class of problems that no other join type handles cleanly.

This guide explains what is cross join in SQL, walks through the mechanics with real examples, shows you when the pattern is the right tool, and covers exactly when to reach for something else instead.

## What Is a Cross Join in SQL?

A cross join produces the **Cartesian product** of two tables. That means every row from the first table is paired with every row from the second table — no condition, no filtering, no matching column required. If table A has M rows and table B has N rows, the result set has exactly M × N rows.

The name "Cartesian product" comes from René Descartes, the 17th-century mathematician who developed the coordinate plane. The mathematical operation and the SQL join share the same core idea: take every element from one set and combine it with every element of another. Every possible pairing is produced, without exception.

Here is the simplest possible demonstration. Suppose you have two tiny tables — one with three shirt sizes and one with two colours:

```sql
-- shirt_sizes: XS, M, XL
-- shirt_colors: Red, Blue
SELECT s.size_label, c.color_name
FROM shirt_sizes s
CROSS JOIN shirt_colors c;
```

With 3 sizes and 2 colours, this query returns exactly 6 rows:

| size_label | color_name |
|------------|------------|
| XS         | Red        |
| XS         | Blue       |
| M          | Red        |
| M          | Blue       |
| XL         | Red        |
| XL         | Blue       |

No ON clause. No WHERE condition. No shared key. Every size is paired with every colour, unconditionally. The join produces all possible combinations and nothing else.

This behaviour is fundamentally different from every other join type in SQL. INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL JOIN all filter or match rows using a condition — typically a shared foreign key. Cross join ignores keys entirely. It is not combining rows that relate to each other; it is combining every row with every other row, whether they have anything in common or not.

### The math: result size grows multiplicatively

If you cross join a 100-row table with a 100-row table, you get 10,000 rows. Cross join a 1,000-row table with a 1,000-row table and you are looking at one million rows. Join two tables with 10,000 rows each and the output is 100 million rows.

This growth is not a theoretical concern. Accidental cross joins — where a developer forgets a WHERE clause or a JOIN condition — are among the most common causes of query timeouts and database incidents in production. The query optimiser cannot save you here: a cross join produces its full output before any outer filtering runs. Understanding [SQL vs NoSQL: Key Differences Explained With Examples](/blog/sql-vs-nosql-differences-examples) helps put joins in context — joins are a defining feature of relational databases, and the cross join is the join that strips all relationship logic away.


## How Cross Joins Differ from Other SQL Join Types

Every join type in SQL takes two input tables. What separates them is how they decide which rows appear in the output.

**INNER JOIN** returns only rows where the join condition is true — typically where a foreign key in one table matches a primary key in the other. Rows with no match are excluded from both sides.

**LEFT JOIN** (also called LEFT OUTER JOIN) returns all rows from the left table, plus matching rows from the right. Where a left-table row has no match, the right-side columns are NULL.

**RIGHT JOIN** is the mirror: all rows from the right table, plus matching rows from the left, with NULLs filling in missing left-side values.

**FULL JOIN** (FULL OUTER JOIN) combines both outer joins: all rows from both tables, with NULLs wherever no match exists on either side.

**CROSS JOIN** operates differently from all of them. It accepts no ON or USING clause. Every row from the left table is combined with every row from the right table, producing all possible pairs — no filtering, no matching, no NULLs.

| Join Type  | Condition Required? | NULLs in Result? | Result Row Count     |
|------------|---------------------|------------------|----------------------|
| INNER JOIN | Yes (ON clause)     | No               | <= smaller input table |
| LEFT JOIN  | Yes (ON clause)     | Right side only  | Equal to left table  |
| RIGHT JOIN | Yes (ON clause)     | Left side only   | Equal to right table |
| FULL JOIN  | Yes (ON clause)     | Both sides       | <= rows_A + rows_B   |
| CROSS JOIN | No                  | No               | Exactly M x N rows   |

One edge case worth understanding: a CROSS JOIN with a WHERE clause that filters on columns from both tables can produce the same output as an INNER JOIN. These two queries are logically equivalent:

```sql
-- Cross join with filter — same result as the INNER JOIN below
SELECT o.order_id, c.customer_name
FROM orders o
CROSS JOIN customers c
WHERE o.customer_id = c.customer_id;

-- INNER JOIN — the explicit, optimiser-friendly version
SELECT o.order_id, c.customer_name
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id;
```

The INNER JOIN version is always preferable for conditional matching. It communicates intent clearly and gives the query optimiser better guidance for index usage. According to the [PostgreSQL documentation on table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html), CROSS JOIN is syntactically equivalent to `INNER JOIN ON TRUE` — a join condition that is always satisfied, producing the full Cartesian product.


## Cross Join Syntax Across Database Platforms

The ANSI SQL standard syntax is consistent across all major database platforms:

```sql
SELECT column_list
FROM table_a
CROSS JOIN table_b;
```

Two alternative syntaxes produce identical results but are less explicit about intent:

```sql
-- Implicit cross join: comma-separated tables in the FROM clause
SELECT column_list
FROM table_a, table_b;

-- INNER JOIN with an always-true condition (avoid this form)
SELECT column_list
FROM table_a
INNER JOIN table_b ON 1 = 1;
```

The comma syntax predates the ANSI JOIN keywords and works in every major SQL database. Most modern style guides discourage it because it is visually indistinguishable from a query with an accidentally missing WHERE clause. The `INNER JOIN ON 1 = 1` form is technically valid but reads as a workaround.

**MySQL and MariaDB** support all three forms. The [MySQL JOIN syntax reference](https://dev.mysql.com/doc/refman/8.0/en/join.html) confirms that a comma-separated table list in the FROM clause is treated as a CROSS JOIN when no condition is supplied.

**PostgreSQL** supports all three forms, with CROSS JOIN as the canonical syntax in its documentation. PostgreSQL treats CROSS JOIN and the comma-separated FROM clause identically in terms of execution plan.

**SQL Server (T-SQL)** supports CROSS JOIN as a standard keyword. The legacy comma syntax works but is flagged by modern T-SQL linters as a potential accidental join.

**SQLite** supports CROSS JOIN and the comma syntax, producing the same execution plan for both.

**Oracle** supports CROSS JOIN from version 9i onward. For older Oracle databases (pre-9i), only the comma syntax was available.

The rule for new code is simple: always use the explicit `CROSS JOIN` keyword. It communicates intent to both the reader and the query planner.


## Practical Cross Join Examples in SQL

### Example 1: Generating all product variants

The most natural use case for cross join is generating every combination of two attribute tables. An e-commerce platform typically stores shirt sizes and colours as separate tables. A cross join produces the full variant matrix in a single query:

```sql
CREATE TABLE shirt_sizes (size_label VARCHAR(10));
INSERT INTO shirt_sizes VALUES ('XS'), ('S'), ('M'), ('L'), ('XL');

CREATE TABLE shirt_colors (color_name VARCHAR(20));
INSERT INTO shirt_colors VALUES ('White'), ('Black'), ('Navy');

SELECT
    s.size_label,
    c.color_name,
    CONCAT(s.size_label, '-', c.color_name) AS sku_variant
FROM shirt_sizes s
CROSS JOIN shirt_colors c
ORDER BY s.size_label, c.color_name;
-- Result: 15 rows (5 sizes x 3 colors)
```

Each row is a unique SKU variant. No row is missing, and no join condition was needed because the relationship IS that every size exists in every colour option. The cross join expresses the requirement directly.

### Example 2: Building a zero-fill reporting scaffold

A frequent reporting problem: the sales table has gaps — some days had no transactions — but the report needs every date in the range, including zero-sale days. A cross join generates the full scaffold before a LEFT JOIN fills in actual data:

```sql
-- Build a scaffold: every product for every month in Q1
WITH months AS (
    SELECT 1 AS month_num UNION ALL
    SELECT 2              UNION ALL
    SELECT 3
),
active_products AS (
    SELECT product_id, product_name
    FROM catalogue
    WHERE is_active = 1
)
SELECT
    p.product_id,
    p.product_name,
    m.month_num,
    COALESCE(s.units_sold, 0) AS units_sold,
    COALESCE(s.revenue, 0.00) AS revenue
FROM active_products p
CROSS JOIN months m
LEFT JOIN monthly_sales s
    ON  s.product_id = p.product_id
    AND s.month_num  = m.month_num
ORDER BY p.product_id, m.month_num;
```

The CROSS JOIN between `active_products` and `months` creates the scaffold — every product for every month. The LEFT JOIN then fills in actual sales figures where they exist, and COALESCE converts NULLs (months with no sales) to zero. This pattern is one of the most practical applications of cross join in business intelligence reporting.

When working with date and time data across different SQL databases, the [Unix Timestamp guide](/guides/unix-timestamp-explained) explains how to convert between SQL date types and epoch integers, which is useful when joining against systems that store timestamps as integer columns.

### Example 3: Seeding test databases

Cross joins generate large, varied test datasets without procedural loops:

```sql
INSERT INTO test_order_log
    (customer_id, customer_email, category_id, category_name, order_ref)
SELECT
    c.customer_id,
    c.customer_email,
    cat.category_id,
    cat.category_name,
    CONCAT('TEST-', c.customer_id, '-', cat.category_id) AS order_ref
FROM test_customers c
CROSS JOIN product_categories cat;
-- 100 test customers x 10 categories = 1,000 test records in one statement
```

With 100 test customers and 10 product categories, this inserts 1,000 test records in a single SQL statement — comprehensive coverage across all customer-category combinations with no looping code required.

### Example 4: Round-robin tournament fixtures

Generating a fixture list where every team plays every other team uses a self-cross-join filtered to remove self-pairings:

```sql
SELECT
    home.team_name AS home_team,
    away.team_name AS away_team
FROM teams home
CROSS JOIN teams away
WHERE home.team_id <> away.team_id
ORDER BY home.team_name, away.team_name;
```

This is one of the cases where adding a WHERE clause to a cross join is appropriate — the problem genuinely requires a self-cross-join filtered to remove a team playing itself. The result is every ordered (home, away) combination with self-pairings excluded.

For well-structured query result data, the [JSON Formatter and Validator guide](/guides/json-formatter-validator-best-practices) covers how to validate and transform SQL query output when your application layer needs structured data.


## When to Use a Cross Join — and When to Avoid It

Cross join is the right tool when the requirement itself is "generate all combinations of two sets." If you can describe what you need as "every X paired with every Y," cross join is almost certainly the correct answer.

**Reach for CROSS JOIN when:**

- Generating product or inventory variants from attribute tables (sizes x colours x materials x regions)
- Building zero-fill reporting scaffolds (all dates x all products, then LEFT JOIN actual data)
- Seeding test databases with comprehensive dimensional coverage
- Computing round-robin tournament fixtures or any all-pairs scheduling problem
- Building multiplication tables or coordinate grids in pure SQL
- Generating a full calendar grid from year x month x day range tables

**Avoid CROSS JOIN when:**

- You meant to write a join condition and forgot. An accidental cross join on production tables can cause a query timeout or an outage. Treat any multi-table FROM clause without an explicit ON condition as a yellow flag in code review.
- Either table can grow unboundedly. A cross join that is perfectly manageable at 50 rows x 20 rows (1,000 rows) becomes a disaster at 50,000 rows x 20,000 rows (one billion rows).
- The relationship between tables has actual logic. If you are joining customers to their orders, use INNER JOIN on customer_id. Cross join ignores the relationship entirely, pairing every customer with every order regardless of ownership.
- You are debugging a slow query and discover a cross join in a subquery or CTE. Missing join conditions in subqueries silently multiply row counts and are one of the most common hidden causes of query slowness.

A practical checkpoint: before running a cross join on non-trivial tables, calculate the expected output row count explicitly. If it exceeds 100,000 rows, verify that downstream operations — GROUP BY, ORDER BY, further joins — can handle that volume efficiently.


## Performance Considerations for Cross Joins

Understanding the performance characteristics of cross join prevents surprises when queries reach production data volumes.

### Output size is always O(M x N)

This is the defining property. For every other join type, selective filtering or indexed lookups keep the output small relative to the inputs. Cross join has no filtering step — it always produces exactly M x N rows. A 10x increase in either input table produces a 10x increase in the output size.

### Index optimisation does not apply to cross join

For INNER JOIN and other conditional joins, the database uses indexes on the join columns to locate matching rows without scanning entire tables. Cross join has no join condition to index. The execution plan will show a full scan of both tables — a nested-loop, hash join, or merge join that processes every row of each input. This is not a bug; it is the expected and unavoidable behaviour for an operation that must produce every combination.

The concern is not the cross join computation itself but whether the M x N output is manageable for whatever the query does downstream: sorting, further joins, aggregation.

### Watch for cross joins hidden in CTEs

A cross join inside a common table expression (CTE) materialises the full Cartesian product before the outer query runs:

```sql
-- Dangerous: implicit cross join materialises 100M rows before WHERE filter
WITH all_combos AS (
    SELECT a.record_id AS a_id, b.record_id AS b_id
    FROM large_table_a, large_table_b  -- implicit cross join
)
SELECT * FROM all_combos WHERE a_id = 42;
```

The WHERE clause on the outer query filters the already-materialised CTE. It does not prevent the full Cartesian product from being computed first. The correct fix pushes the filter inside the CTE:

```sql
-- Correct: filter first, then cross join the smaller result
WITH filtered_a AS (
    SELECT record_id FROM large_table_a WHERE record_id = 42
)
SELECT f.record_id, b.record_id
FROM filtered_a f
CROSS JOIN large_table_b b;
```

### LIMIT does not reduce cross join computation

Adding `LIMIT 100` to a cross join query does not prevent the database from computing all M x N combinations in most execution plans — it discards excess rows after the full product is computed. If you need a sample of combinations, pre-filter the input tables to smaller subsets before cross joining.

### Verify execution plans with EXPLAIN

For any cross join on non-trivial tables, check the execution plan before running against production data:

```sql
-- PostgreSQL and MySQL
EXPLAIN SELECT * FROM product_sizes CROSS JOIN product_colors;

-- Look for: estimated rows = size_count x color_count
```

The [Wikipedia article on SQL joins](https://en.wikipedia.org/wiki/Join_(SQL)) covers how different join algorithms — nested loop, hash join, merge join — apply to different join types, which is useful background for interpreting cross join execution plans.


## Common Mistakes When Using Cross Joins

### Mistake 1: The accidental cross join from a missing join condition

The most common mistake is not an intentional cross join — it is accidentally producing one:

```sql
-- Accidental cross join: no join condition between orders and customers
SELECT o.order_id, c.customer_name
FROM orders o, customers c;
```

Many developers write this intending to join orders to their customers. Without the WHERE condition that matches `o.customer_id = c.customer_id`, the query pairs every order with every customer. In a database with 50,000 orders and 10,000 customers, that is 500 million rows.

Modern SQL linters flag comma-separated multi-table FROM clauses without join conditions. Enabling linting in your SQL editor catches this pattern before it reaches a code review.

### Mistake 2: Underestimating subquery row counts in a cross join

```sql
-- Looks manageable but dangerous if active_promotions subquery returns many rows
SELECT p.product_name, promo.discount_pct
FROM products p
CROSS JOIN (
    SELECT discount_pct FROM promotions WHERE is_active = 1
) promo;
```

If the subquery returns 500 rows instead of the expected 5, the output is 100x larger than anticipated. Always verify subquery row counts with a standalone `SELECT COUNT(*)` before embedding the subquery in a cross join.

### Mistake 3: Cross join instead of self join with a condition

For operations like "find all pairs of employees in the same department," a self join with an explicit ON condition communicates intent and helps the optimiser:

```sql
-- Self join with condition: uses department index, intent is clear
SELECT a.employee_name, b.employee_name
FROM employees a
INNER JOIN employees b
    ON  a.department_id = b.department_id
    AND a.employee_id < b.employee_id;

-- Cross join with WHERE: same result, less readable, less optimiser-friendly
SELECT a.employee_name, b.employee_name
FROM employees a
CROSS JOIN employees b
WHERE a.department_id = b.department_id
  AND a.employee_id < b.employee_id;
```

Both queries return the same rows, but the INNER JOIN version signals to the optimiser that department_id is a join key, enabling index-based lookup rather than full-table combination.


## Frequently Asked Questions

### What does CROSS JOIN return if one table is empty?

If either input table has zero rows, the cross join returns zero rows. The Cartesian product of any set and an empty set is always empty — M x 0 = 0, regardless of M. In practice, this means a cross join on a table that might be empty requires the same guard logic as any query that depends on that table having rows. An empty scaffold table produces an empty report even if all other inputs are fully populated.

### Is CROSS JOIN the same as a FULL OUTER JOIN?

No — these are completely different operations with different outputs. FULL OUTER JOIN returns all rows from both tables, using NULLs to fill in missing matches. On two 10-row tables with no overlapping keys, FULL OUTER JOIN returns 20 rows. CROSS JOIN returns every combination — 10 x 10 = 100 rows on the same two tables. The two joins produce different row counts, different column values, and different semantics. There is no scenario where they produce the same result.

### Can I use CROSS JOIN with more than two tables?

Yes. SQL allows chaining multiple cross joins: `FROM table_a CROSS JOIN table_b CROSS JOIN table_c`. The result is the three-way Cartesian product — every row of A combined with every row of B combined with every row of C. If A, B, and C each have 10 rows, the output is 1,000 rows. Each additional table multiplies the output size by its row count, so multi-table cross joins require especially careful pre-execution size calculation.

### Does CROSS JOIN accept an ON or USING clause?

No. CROSS JOIN does not accept an ON or USING clause in standard SQL. Adding one converts the operation to a conditional join — which is what INNER JOIN with an ON clause already does. In PostgreSQL, adding an ON clause to a CROSS JOIN raises a syntax error. In some older MySQL versions, it silently converts to an INNER JOIN. When you have a join condition, use INNER JOIN explicitly.

### How do I write a cross join in PostgreSQL specifically?

PostgreSQL supports the standard `FROM table_a CROSS JOIN table_b` syntax, as well as the comma syntax `FROM table_a, table_b`. Both produce identical execution plans. The PostgreSQL documentation recommends the explicit CROSS JOIN keyword for readability. Use EXPLAIN to verify the plan:

```sql
EXPLAIN SELECT * FROM product_sizes CROSS JOIN product_colors;
-- Expected: Nested Loop, estimated rows = size_count x color_count
```


## Conclusion

Knowing what is cross join in SQL — that it produces the Cartesian product of two tables with no filtering condition — is the foundation for using it correctly. Cross join is not a mistake or a last resort; it is a precise tool for the specific class of problems that require every possible combination of two sets. Variant generation, reporting scaffolds, test data seeding, and round-robin scheduling are all valid, practical applications.

The danger is accidental use. A cross join with a missing join condition looks identical to a broken INNER JOIN, and on large tables the result set grows explosively. Calculate expected output size before running, verify the execution plan with EXPLAIN on non-trivial tables, and treat comma-separated multi-table FROM clauses without conditions as a mandatory code-review checkpoint.

For broader context on why relational databases are structured around explicit table relationships, the [SQL vs NoSQL: Key Differences Explained With Examples](/blog/sql-vs-nosql-differences-examples) guide covers the architectural reasons that make joins — including cross join — a defining feature of the relational model.
