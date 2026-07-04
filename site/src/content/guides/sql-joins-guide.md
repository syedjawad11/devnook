---
title: "SQL Join Types: INNER, LEFT, RIGHT, FULL and CROSS"
description: "Learn all five SQL join types with clear examples: INNER, LEFT, RIGHT, FULL OUTER, and CROSS joins, when to use each, and common mistakes to avoid."
category: guides
subcategory: "Database & SQL"
template_id: guide-v2
tags: [sql, database, joins, sql-joins, relational-database]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-07-04"
og_image: "/og/guides/sql-joins-guide.png"
actual_word_count: 2978
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["Article", "FAQPage"],
    "headline": "SQL Join Types: INNER, LEFT, RIGHT, FULL and CROSS",
    "description": "Learn all five SQL join types with clear examples: INNER, LEFT, RIGHT, FULL OUTER, and CROSS joins, when to use each, and common mistakes to avoid.",
    "datePublished": "2026-07-04",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/guides/sql-joins-guide/",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between INNER JOIN and LEFT JOIN?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "INNER JOIN returns only rows that have matching values in both tables. LEFT JOIN returns all rows from the left table, plus matching rows from the right table — unmatched right-side rows appear as NULL."
        }
      },
      {
        "@type": "Question",
        "name": "When should you use FULL OUTER JOIN?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Use FULL OUTER JOIN when you need to see all records from both tables, including unmatched rows from either side. Common use cases include data reconciliation, auditing for missing records, and comparing two datasets where gaps in either direction matter."
        }
      },
      {
        "@type": "Question",
        "name": "Can you combine multiple join types in one SQL query?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes. A single SQL query can include multiple JOIN clauses, each with a different join type. For example, you can INNER JOIN an orders table to customers while LEFT JOINing to a promotions table to preserve orders without a promotion code."
        }
      }
    ]
  }
  </script>
---

SQL databases store data across separate tables for good reasons — normalisation avoids duplication and keeps each table focused on one thing. But that same separation means answering almost any real question requires combining tables. That is where join types come in. Every SQL join type has a different rule for which rows make it into the result, and picking the wrong one silently drops data or inflates row counts in ways that are hard to spot until the numbers stop adding up.

This guide covers all five join types — INNER, LEFT, RIGHT, FULL OUTER, and CROSS — with working examples, a comparison table, and clear rules for when to use each one.

## What Are SQL Join Types?

A SQL join combines rows from two or more tables based on a related column — typically a foreign key matching a primary key. The join type determines what happens when rows in one table have no match in the other.

Think of it this way: you have a `customers` table and an `orders` table. Some customers have placed orders. Some haven't. Some orders — edge cases aside — might reference an invalid customer ID. The join type you choose decides whether those unmatched rows appear in the output, and if so, what fills the missing columns.

SQL defines five standard join types:

| Join Type | What it returns |
|-----------|----------------|
| INNER JOIN | Only rows with matches in both tables |
| LEFT JOIN | All rows from the left table; NULLs for unmatched right rows |
| RIGHT JOIN | All rows from the right table; NULLs for unmatched left rows |
| FULL OUTER JOIN | All rows from both tables; NULLs where no match exists |
| CROSS JOIN | Every combination of rows from both tables (Cartesian product) |

The first four are the most commonly used in day-to-day queries. CROSS JOIN serves a narrower set of use cases and requires intentional use — for a full walkthrough of when and why to use it, read [What Is a Cross Join in SQL?](/guides/what-is-cross-join-in-sql/), which covers the edge cases this guide sets aside.

For syntax reference and aggregate function shortcuts, keep the [SQL Cheat Sheet](/cheatsheets/sql-cheatsheet/) nearby while working through examples.

## INNER JOIN: Only Rows That Match on Both Sides

INNER JOIN is the default join behavior in most SQL queries. It returns a row in the result only when the join condition finds a match in both tables.

If a customer has no orders, that customer does not appear. If an order references a non-existent customer ID, that order does not appear either. The result set is strictly the intersection.

```sql
SELECT
    customers.customer_id,
    customers.name,
    orders.order_id,
    orders.total_amount
FROM customers
INNER JOIN orders
    ON customers.customer_id = orders.customer_id;
```

This query returns one row per order, limited to customers who have placed at least one order. A customer with three orders appears three times; a customer with no orders is absent entirely.

### When INNER JOIN Is the Right Choice

INNER JOIN fits whenever you only care about matched data. Pulling a user's purchase history, listing all invoices with their associated client records, joining product details to line items in a cart — these are cases where a missing match means genuinely missing data, and you want the query to reflect that.

It is the most common join type precisely because most reporting and display queries are built around matched relationships. In a well-designed relational schema, foreign keys enforce these relationships, so unmatched rows represent an exception rather than a normal state.

### Chaining Multiple INNER JOINs

You can combine conditions in the `ON` clause with `AND`, and chain as many joins as your schema requires:

```sql
SELECT
    employees.name,
    projects.project_name,
    assignments.role
FROM employees
INNER JOIN assignments
    ON employees.employee_id = assignments.employee_id
    AND assignments.status = 'active'
INNER JOIN projects
    ON assignments.project_id = projects.project_id;
```

This joins three tables, but only for active assignments. Each added INNER JOIN narrows the result to rows with valid matches across all the joined tables — the query planner handles ordering for performance.

## LEFT JOIN: Preserve All Rows from the Left Table

LEFT JOIN (also written as LEFT OUTER JOIN — the keyword OUTER is optional in all major databases) returns every row from the left table, plus matching rows from the right table. Where no match exists in the right table, those columns are filled with NULL.

```sql
SELECT
    customers.customer_id,
    customers.name,
    orders.order_id,
    orders.total_amount
FROM customers
LEFT JOIN orders
    ON customers.customer_id = orders.customer_id;
```

Every customer appears in the result. Customers with orders get those order columns populated. Customers with no orders get NULL for `order_id` and `total_amount`.

### Finding Unmatched Rows with LEFT JOIN

The NULL-filled rows are often the whole point. A common pattern combines LEFT JOIN with a WHERE clause that filters for NULL on the right-side key — effectively an anti-join that surfaces rows with no match:

```sql
SELECT customers.customer_id, customers.name
FROM customers
LEFT JOIN orders
    ON customers.customer_id = orders.customer_id
WHERE orders.order_id IS NULL;
```

This returns customers who have never placed an order. The pattern is reliable, readable, and works across PostgreSQL, MySQL, SQLite, and SQL Server. It shows up constantly in churn analysis, re-engagement campaigns, and data quality checks.

### "Left" Refers to Position in the Query

The "left" table is whichever table appears in the FROM clause — before the JOIN keyword. The "right" table is the one named in the JOIN clause. Knowing this matters when chaining multiple joins: each new LEFT JOIN adds a right table while preserving the full left-side result set from the previous join step.

## RIGHT JOIN: Preserve All Rows from the Right Table

RIGHT JOIN is the mirror image of LEFT JOIN. Every row from the right table appears in the result; unmatched left-side rows produce NULL.

```sql
SELECT
    customers.customer_id,
    customers.name,
    orders.order_id,
    orders.total_amount
FROM customers
RIGHT JOIN orders
    ON customers.customer_id = orders.customer_id;
```

Every order appears in the result. If an order's customer ID doesn't match any customer record, the customer columns fill with NULL — which can indicate a referential integrity problem worth investigating before it affects reports.

### RIGHT JOIN vs LEFT JOIN

RIGHT JOIN is used far less often than LEFT JOIN, and for a practical reason: any RIGHT JOIN can be rewritten as a LEFT JOIN by swapping the table order. Most SQL developers prefer LEFT JOIN because it reads more naturally — the table you need to preserve comes first in the query.

```sql
-- These two queries return identical results
SELECT * FROM customers RIGHT JOIN orders ON customers.customer_id = orders.customer_id;
SELECT * FROM orders LEFT JOIN customers ON orders.customer_id = customers.customer_id;
```

Some teams enforce a style guide that bans RIGHT JOIN and rewrites everything as LEFT JOIN for consistency. That is a defensible choice. RIGHT JOIN occasionally reads more clearly when the "source of truth" table is already positioned on the right side of a long query, but it is never strictly necessary.

## FULL OUTER JOIN: All Rows from Both Tables

FULL OUTER JOIN (also written as FULL JOIN) returns all rows from both tables. Where a match exists, columns from both sides are populated. Where no match exists on either side, the non-matching columns are NULL.

```sql
SELECT
    customers.customer_id,
    customers.name,
    orders.order_id,
    orders.total_amount
FROM customers
FULL OUTER JOIN orders
    ON customers.customer_id = orders.customer_id;
```

The result includes three categories of rows:

- Customers with matching orders (all columns populated)
- Customers with no orders (order columns are NULL)
- Orders with no matching customer (customer columns are NULL)

### When FULL OUTER JOIN Makes Sense

FULL OUTER JOIN fits data reconciliation tasks where gaps in either direction matter. Comparing two systems that should contain the same records — a CRM and a billing platform, for example — and needing to surface everything that differs or is missing from either side. It also appears in ETL validation, sync audits, and migration checks where you need a complete picture before declaring the transfer clean.

For routine application queries, FULL OUTER JOIN is rarely the right choice. If you find yourself reaching for it in a standard report, revisit the data model — the schema may have normalisation issues that a join can't paper over.

**Database compatibility note:** PostgreSQL supports FULL OUTER JOIN natively. MySQL did not support it until version 8.0; the traditional workaround is a UNION of a LEFT JOIN and a RIGHT JOIN. See the [PostgreSQL joins documentation](https://www.postgresql.org/docs/current/tutorial-join.html) for full syntax and behavior details.

## CROSS JOIN: Cartesian Product of Both Tables

CROSS JOIN produces every possible combination of rows from the two tables. There is no join condition — CROSS JOIN does not match on columns; it multiplies. If the left table has 10 rows and the right table has 5, the result has 50 rows.

```sql
SELECT
    sizes.size_label,
    colors.color_name
FROM sizes
CROSS JOIN colors;
```

For a `sizes` table with Small, Medium, Large and a `colors` table with Red, Blue, Green, this produces nine rows: every size paired with every color. CROSS JOIN has legitimate uses in generating test data, building scheduling grids, and computing combinatorial product sets.

On large tables the row count explodes fast, so CROSS JOIN requires intentional use. The dedicated guide at [What Is a Cross Join in SQL?](/guides/what-is-cross-join-in-sql/) covers the performance limits, MySQL vs PostgreSQL syntax differences, and scenarios where the Cartesian product is genuinely what you want.

## SQL Join Types Side by Side

Here is how the five join types compare using a concrete example. Assume a `customers` table with 5 rows and an `orders` table with 8 rows, where 3 of the 5 customers have at least one order:

| Join Type | Rows in result | Unmatched customers included? | Unmatched orders included? |
|-----------|---------------|-------------------------------|---------------------------|
| INNER JOIN | 8 | No | No |
| LEFT JOIN | ≥ 5 (more if customers have multiple orders) | Yes (NULL order columns) | No |
| RIGHT JOIN | 8 | No | Yes (NULL customer columns) |
| FULL OUTER JOIN | ≥ 10 | Yes | Yes |
| CROSS JOIN | 40 | N/A — all combinations | N/A — all combinations |

The exact row count for LEFT, RIGHT, and FULL JOIN depends on how many customers have multiple orders — a customer with three orders contributes three rows to an INNER or LEFT JOIN result, not one.

The keyword OUTER is optional in LEFT OUTER JOIN, RIGHT OUTER JOIN, and FULL OUTER JOIN. Both forms are valid SQL; the behavior is identical. Most developers drop OUTER for brevity.

## When to Use Which SQL Join Type

Choosing the right join type comes down to one question: which rows do you need to preserve when there is no match?

**Use INNER JOIN when:**
- You only want rows with data on both sides of the join
- Missing matches genuinely mean "not relevant" for this query
- You are reporting on confirmed relationships — completed orders with known customers, active assignments on real projects

**Use LEFT JOIN when:**
- You need all rows from the primary (left) table regardless of whether they match
- You want to flag, count, or audit unmatched rows
- The left table is your source of truth and the right table provides optional enrichment

**Use RIGHT JOIN when:**
- The right table is the one you need to preserve completely
- Rewriting as a LEFT JOIN by swapping table order would make the query harder to follow in context

**Use FULL OUTER JOIN when:**
- You are reconciling two data sources and gaps in either direction matter
- You are validating a sync or migration and need to see what is present in each source independently

**Use CROSS JOIN when:**
- You deliberately need every combination — product option grids, scheduling matrices, test data generation
- You have verified the row count is manageable and the multiplication is the intended result

Before writing a join-heavy query, paste it through the [SQL Formatter](/tools/sql-formatter/) to clean up indentation and make table relationships easier to follow, especially when chaining three or more joins in a single statement.

## Common Mistakes with SQL Join Types

### Moving Filter Conditions to WHERE Instead of ON

When a LEFT JOIN has no match, the right-side columns are NULL — not empty strings or zeros. Filtering with `WHERE right_table.column = 'something'` silently eliminates all the NULL rows, turning the LEFT JOIN into an effective INNER JOIN. If you want to filter right-side data while keeping unmatched left rows, put the condition in the `ON` clause rather than in WHERE.

```sql
-- This drops customers without any shipped orders (silently converts LEFT to INNER):
SELECT * FROM customers
LEFT JOIN orders ON customers.customer_id = orders.customer_id
WHERE orders.status = 'shipped';

-- This keeps all customers; those with no shipped orders appear with NULL order columns:
SELECT * FROM customers
LEFT JOIN orders
    ON customers.customer_id = orders.customer_id
    AND orders.status = 'shipped';
```

This is one of the most common SQL mistakes and one of the hardest to spot — the query runs without error but returns fewer rows than expected.

### Forgetting That Table Order Is Semantically Significant

For INNER JOINs, the order of tables does not affect which rows appear — only query planning, which the optimizer usually handles. But for LEFT and RIGHT JOINs, order is semantically significant. Swapping the left and right tables changes which rows are preserved. That is a correctness issue, not a style preference.

### The Accidental CROSS JOIN

In the older comma-separated FROM syntax, listing two tables without a join condition produces a Cartesian product. Some databases still accept this silently:

```sql
-- Accidental CROSS JOIN — returns every customer paired with every order:
SELECT * FROM customers, orders;

-- Correct INNER JOIN:
SELECT * FROM customers
INNER JOIN orders ON customers.customer_id = orders.customer_id;
```

Always use explicit JOIN syntax with an ON condition. The implicit comma-join form has caused outages when a WHERE clause is accidentally removed during refactoring.

### Duplicate Rows from One-to-Many Relationships

Joining a table that has many rows per key multiplies the left-side rows. A customer with 10 orders produces 10 rows in the join result — the customer's profile data repeats once per order. This is correct behavior, but it surprises developers who run aggregates on the result without accounting for it.

Understanding [primary keys in a database](/guides/primary-key-in-database/) and how they relate across tables is the prerequisite for reasoning about join cardinality correctly. If the duplication is causing problems, the fix is usually an aggregate subquery or a GROUP BY, not a different join type.

If you are working with a performance-sensitive query over large tables, understanding how [SQL indexes](/guides/what-are-indexes-in-sql/) interact with join columns can make the difference between a millisecond query and one that scans millions of rows.

The [MySQL JOIN syntax reference](https://dev.mysql.com/doc/refman/8.0/en/join.html) is the authoritative source for MySQL-specific behavior and syntax edge cases. For the relational algebra underlying join semantics, the [Wikipedia article on SQL joins](https://en.wikipedia.org/wiki/Join_(SQL)) provides a solid theoretical grounding.

## Frequently Asked Questions

### What is the difference between INNER JOIN and LEFT JOIN?

INNER JOIN returns only rows that have matching values in both tables — unmatched rows from either side are excluded entirely. LEFT JOIN returns every row from the left (first) table, filling right-side columns with NULL where no match exists. Choose INNER JOIN when a missing match means the data is irrelevant to your query; choose LEFT JOIN when you need to preserve all left-side rows and treat unmatched rows as valid data points worth keeping in the result.

### When should I use FULL OUTER JOIN?

FULL OUTER JOIN fits when you need to see all records from both tables, including rows that have no match on either side. It is most useful for data reconciliation — comparing two systems that should contain the same records, or auditing a migration to see what is present in one source but missing from another. For standard application queries against a normalised schema, INNER JOIN or LEFT JOIN handles most cases and FULL OUTER JOIN is rarely the right tool.

### Can I combine different join types in a single SQL query?

Yes. A single SQL query can chain multiple JOIN clauses with different join types applied to each one. For example, you can INNER JOIN an orders table to a products table — because orders must reference valid products — while LEFT JOINing to a coupons table, because a coupon is optional. Each JOIN clause specifies its own join type, and the query planner evaluates them in sequence.

### Does JOIN order affect performance?

The query optimizer in PostgreSQL, MySQL, SQL Server, and SQLite can reorder INNER JOINs to find the most efficient execution plan. It cannot safely reorder LEFT, RIGHT, or FULL OUTER JOINs without changing the result, so the optimizer respects the order you write. For large tables, adding indexes on the columns used in ON conditions significantly reduces join cost — the engine reads a compact index rather than scanning entire tables row by row.

## Conclusion

The five SQL join types exist because different questions require different views of your relational data. INNER JOIN is the workhorse — most queries are built around it, retrieving matched relationships from a normalised schema. LEFT JOIN handles the second-most-common case: preserve your primary table and treat the joined data as optional enrichment. RIGHT JOIN is LEFT JOIN with the tables swapped — useful occasionally, but often rewritten as LEFT JOIN for readability. FULL OUTER JOIN is a reconciliation tool, not a daily driver. CROSS JOIN is precise and intentional, used when you genuinely need every combination.

Getting join types right means your row counts match what the data actually contains — no silent drops, no unexpected duplicates. Use the [SQL Formatter](/tools/sql-formatter/) to keep multi-join queries readable, and keep the [SQL Cheat Sheet](/cheatsheets/sql-cheatsheet/) nearby for quick syntax reference as you build.
