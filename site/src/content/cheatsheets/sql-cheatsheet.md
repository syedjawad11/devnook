---
title: "SQL Cheat Sheet: Queries, Joins, Aggregates"
description: "Master sql queries with this SQL cheatsheet: SELECT, WHERE, JOINs, GROUP BY, window functions, CTEs, and DML — with runnable copy-paste examples."
category: cheatsheets
subcategory: "Reference"
template_id: "cheatsheet-v1"
tags: [sql, sql-queries, database, joins, aggregate-functions]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-07-01"
og_image: "/og/cheatsheets/sql-cheatsheet.png"
actual_word_count: 1924
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": [\n    \"TechArticle\",\n    \"FAQPage\"\n  ],\n  \"headline\": \"SQL Cheat Sheet: Queries, Joins, Aggregates\",\n  \"description\": \"Master sql queries with this SQL cheatsheet: SELECT, WHERE, JOINs, GROUP BY, window functions, CTEs, and DML — with runnable copy-paste examples.\",\n  \"datePublished\": \"2026-07-01\",\n  \"author\": {\n    \"@type\": \"Organization\",\n    \"name\": \"DevNook\"\n  },\n  \"publisher\": {\n    \"@type\": \"Organization\",\n    \"name\": \"DevNook\",\n    \"url\": \"https://devnook.dev\"\n  },\n  \"url\": \"https://devnook.dev/cheatsheets/sql-cheatsheet/\",\n  \"mainEntity\": [\n    {\n      \"@type\": \"Question\",\n      \"name\": \"What is the difference between WHERE and HAVING in SQL?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"WHERE filters rows before grouping; HAVING filters groups after GROUP BY. Use WHERE for row-level conditions and HAVING for aggregate conditions like HAVING COUNT(*) > 5.\"\n      }\n    },\n    {\n      \"@type\": \"Question\",\n      \"name\": \"What is the difference between INNER JOIN and LEFT JOIN?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"INNER JOIN returns only rows with a match in both tables. LEFT JOIN returns all rows from the left table, with NULLs for columns from the right table where no match exists.\"\n      }\n    },\n    {\n      \"@type\": \"Question\",\n      \"name\": \"What are window functions in SQL?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"Window functions compute results across a set of related rows without collapsing them. Common examples include ROW_NUMBER(), RANK(), and SUM() OVER (PARTITION BY ...).\"\n      }\n    }\n  ]\n}\n</script>"
---
SQL is the standard language for working with relational databases, and being fluent in sql queries is one of the most transferable skills a backend developer can build. This cheatsheet covers the commands you'll reach for most often — from basic SELECT statements through aggregates, JOINs, window functions, and data modification. Every snippet runs on PostgreSQL, MySQL, and SQLite unless noted.

If you're deciding between SQL and NoSQL storage, the [SQL vs NoSQL comparison](/blog/sql-vs-nosql-differences-examples/) covers the trade-offs in depth.

## SQL Queries: SELECT, WHERE, and Filtering

Every sql query starts with SELECT. The clause after FROM names the table; WHERE restricts which rows come back.

```sql
-- Basic SELECT: retrieve specific columns
SELECT first_name, last_name, email
FROM users
WHERE status = 'active'
ORDER BY last_name ASC
LIMIT 50;
```

### SELECT Modifiers

| Modifier | Effect |
|---|---|
| `SELECT DISTINCT col` | Remove duplicate values from output |
| `SELECT *` | Return all columns (avoid in production queries) |
| `SELECT TOP n` / `LIMIT n` | First n rows — SQL Server / MySQL & PostgreSQL |
| `OFFSET n` | Skip n rows — pair with LIMIT for pagination |

### WHERE Operators

| Operator | Example |
|---|---|
| `=`, `!=` / `<>` | `status = 'active'` |
| `<`, `>`, `<=`, `>=` | `price >= 10.00` |
| `BETWEEN … AND …` | `created_at BETWEEN '2025-01-01' AND '2025-12-31'` |
| `IN (…)` | `country IN ('US', 'CA', 'GB')` |
| `NOT IN (…)` | `role NOT IN ('admin', 'superuser')` |
| `LIKE` | `email LIKE '%@gmail.com'` |
| `IS NULL` / `IS NOT NULL` | `deleted_at IS NULL` |
| `AND`, `OR`, `NOT` | `status = 'active' AND verified = true` |

Wildcards in LIKE: `%` matches any sequence of characters; `_` matches exactly one character. PostgreSQL also supports `ILIKE` for case-insensitive matching.

## JOIN Types: INNER, LEFT, RIGHT, and FULL

Joins combine rows from two or more tables based on a related column. The most common pattern joins on foreign keys — columns that reference a [primary key](/guides/primary-key-in-database/) in another table. Understanding which join type fits your intent keeps the result set correct.

```sql
-- INNER JOIN: only rows matching on both sides
SELECT o.order_id, o.total, u.email
FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE o.status = 'shipped';

-- LEFT JOIN: all orders, NULL for missing user record
SELECT o.order_id, u.email
FROM orders o
LEFT JOIN users u ON o.user_id = u.id;
```

### JOIN Quick Reference

| Join Type | Returns |
|---|---|
| `INNER JOIN` | Only rows with a match in both tables |
| `LEFT JOIN` (or `LEFT OUTER JOIN`) | All left-side rows plus matched right rows; NULL where no right match |
| `RIGHT JOIN` | All right-side rows plus matched left rows |
| `FULL OUTER JOIN` | All rows from both sides; NULLs for non-matches |
| `CROSS JOIN` | Every combination of both tables (Cartesian product) |
| `SELF JOIN` | A table joined to itself — useful for hierarchical or adjacency data |

For worked examples and edge cases of the CROSS JOIN type, see the [CROSS JOIN guide](/guides/what-is-cross-join-in-sql/).

### Multi-Table Joins

You can chain JOINs. The planner processes them left to right:

```sql
SELECT o.order_id, u.email, p.name AS product_name
FROM orders o
INNER JOIN users u ON o.user_id = u.id
INNER JOIN order_items oi ON oi.order_id = o.order_id
INNER JOIN products p ON p.id = oi.product_id
WHERE o.status = 'completed';
```

## GROUP BY and Aggregate Functions

GROUP BY collapses rows that share the same column value into a single output row, letting aggregate functions summarise each group.

```sql
-- Orders per customer — only customers with more than 5 orders
SELECT user_id,
       COUNT(*) AS order_count,
       SUM(total) AS revenue,
       AVG(total) AS avg_order_value
FROM orders
WHERE status != 'cancelled'
GROUP BY user_id
HAVING COUNT(*) > 5
ORDER BY revenue DESC;
```

WHERE filters rows before grouping. HAVING filters groups after aggregation — it is the only place you can filter on aggregate results. You cannot reference a SELECT alias inside HAVING; use the full aggregate expression instead.

### Aggregate Function Reference

| Function | Description |
|---|---|
| `COUNT(*)` | Count all rows in the group |
| `COUNT(col)` | Count non-NULL values in col |
| `COUNT(DISTINCT col)` | Count unique non-NULL values |
| `SUM(col)` | Sum of all values |
| `AVG(col)` | Mean average, excluding NULLs |
| `MIN(col)` / `MAX(col)` | Smallest or largest value |
| `STRING_AGG(col, ',')` | Concatenate strings across a group (PostgreSQL) |
| `GROUP_CONCAT(col)` | Concatenate strings across a group (MySQL, SQLite) |

For the full list of aggregate functions in PostgreSQL, see the [PostgreSQL aggregate functions reference](https://www.postgresql.org/docs/current/functions-aggregate.html).

## Subqueries and Common Table Expressions

A subquery is a SELECT nested inside another statement. A Common Table Expression (CTE) uses the WITH clause to name the subquery upfront, making complex sql queries far easier to read and debug.

```sql
-- Scalar subquery in SELECT
SELECT
  product_id,
  price,
  price - (SELECT AVG(price) FROM products) AS diff_from_avg
FROM products;

-- CTE version of a correlated filter
WITH high_value AS (
  SELECT user_id
  FROM orders
  WHERE total > 500
)
SELECT u.first_name, u.email
FROM users u
INNER JOIN high_value hv ON u.id = hv.user_id;
```

CTEs can be chained — define multiple comma-separated blocks inside a single WITH clause, each able to reference the ones before it. Recursive CTEs (using `WITH RECURSIVE`) walk tree structures like category hierarchies or org charts without any procedural code.

A **correlated subquery** references a column from the outer query and re-executes for every outer row — performance degrades on large tables. Prefer a JOIN or a CTE when you can; they give the query planner more to work with.

## Window Functions

Window functions compute a value for each row based on a set of related rows, without collapsing those rows into a group. They are one of the most useful additions to SQL in the last two decades and are supported by PostgreSQL, MySQL 8+, SQL Server, and SQLite 3.25+. The [SQLite window functions documentation](https://www.sqlite.org/windowfunctions.html) has full syntax details.

```sql
-- Rank customers by total spend within each country
SELECT
  user_id,
  country,
  total_spend,
  RANK() OVER (PARTITION BY country ORDER BY total_spend DESC) AS country_rank,
  SUM(total_spend) OVER (PARTITION BY country) AS country_total,
  ROW_NUMBER() OVER (ORDER BY total_spend DESC) AS global_rank
FROM customer_stats;
```

### Window Function Reference

| Function | Description |
|---|---|
| `ROW_NUMBER()` | Sequential integer — no ties |
| `RANK()` | Rank with gaps on ties (1, 1, 3…) |
| `DENSE_RANK()` | Rank without gaps (1, 1, 2…) |
| `NTILE(n)` | Divide rows into n equal buckets |
| `LAG(col, n)` | Value of col from n rows earlier |
| `LEAD(col, n)` | Value of col from n rows ahead |
| `FIRST_VALUE(col)` | First value in the window frame |
| `LAST_VALUE(col)` | Last value in the window frame |
| `SUM(col) OVER (...)` | Running or partitioned total |
| `AVG(col) OVER (...)` | Running or partitioned average |

`PARTITION BY` divides the window into independent subsets. Omitting it treats the entire result set as one window. `ORDER BY` inside `OVER (...)` defines which rows precede the current row within each partition.

## INSERT, UPDATE, and DELETE

These DML (Data Manipulation Language) statements modify data. Wrap destructive operations in a transaction so you can roll back if something goes wrong.

```sql
-- Insert a single row
INSERT INTO products (name, price, stock)
VALUES ('USB-C Hub', 29.99, 150);

-- Insert multiple rows in one statement
INSERT INTO products (name, price, stock)
VALUES ('HDMI Cable', 9.99, 500),
       ('Webcam', 79.00, 75);

-- Update with a condition (always include WHERE unless intentional)
UPDATE products
SET price = 24.99, updated_at = NOW()
WHERE name = 'USB-C Hub';

-- Delete matching rows
DELETE FROM products
WHERE stock = 0 AND discontinued = true;
```

### Upsert Patterns

PostgreSQL and SQLite support `INSERT … ON CONFLICT` to insert or update in a single statement:

```sql
INSERT INTO user_preferences (user_id, theme)
VALUES (42, 'dark')
ON CONFLICT (user_id) DO UPDATE
  SET theme = EXCLUDED.theme, updated_at = NOW();
```

MySQL uses `INSERT … ON DUPLICATE KEY UPDATE` for the same effect. SQL Server uses `MERGE`.

DELETE is row-by-row and transaction-safe — you can roll it back. TRUNCATE removes all rows by freeing data pages, which is far faster on large tables but cannot be rolled back in MySQL (PostgreSQL allows TRUNCATE inside a transaction).

## Format Your SQL

Before sharing or committing a query, paste it into the [SQL Formatter](/tools/sql-formatter/) to auto-indent and normalise spacing. Consistent formatting surfaces missing WHERE clauses and stray conditions that are easy to miss in dense sql queries.

## Indexes and Query Performance

The speed of sql queries on large tables depends on [SQL indexes](/guides/what-are-indexes-in-sql/). An index is a separate data structure the database maintains so it can find rows without scanning the entire table.

Practical indexing rules:
- Index columns used in WHERE, JOIN ON, and ORDER BY clauses that run frequently.
- Always index foreign key columns — unindexed FK joins are among the most common performance problems in production schemas.
- Avoid indexing low-cardinality columns (boolean flags, status columns with 2–3 distinct values) — the planner typically ignores those indexes.
- Use `EXPLAIN ANALYZE` (PostgreSQL) or `EXPLAIN` (MySQL) to see whether queries are hitting an index or falling through to a full table scan.

For the complete SQL command syntax, the [PostgreSQL SQL commands reference](https://www.postgresql.org/docs/current/sql-commands.html) and the [MySQL 8.0 SQL statements guide](https://dev.mysql.com/doc/refman/8.0/en/sql-statements.html) are the authoritative sources.

## Frequently Asked Questions

### What is the difference between WHERE and HAVING in SQL?

WHERE filters individual rows before GROUP BY runs; HAVING filters the grouped results afterward. You can only filter on aggregate function results (COUNT, SUM, AVG, etc.) inside HAVING, not WHERE. You also cannot reference SELECT column aliases in WHERE — the alias does not exist yet at that stage of query execution. Use HAVING only when the condition depends on an aggregate value.

### What is the difference between INNER JOIN and LEFT JOIN?

INNER JOIN returns only rows where there is a matching row in both tables — left-side rows with no corresponding right-side row are excluded entirely. LEFT JOIN returns every row from the left table, with NULL substituted for columns from the right table wherever no match exists. Use INNER JOIN when the relationship is required; use LEFT JOIN when you need all records from the primary table regardless of whether a related record exists on the other side.

### What are window functions in SQL?

Window functions compute a value for each row based on a set of related rows (the window) without collapsing those rows into a single grouped output. The `OVER (...)` clause defines the window — `PARTITION BY` creates independent subsets, `ORDER BY` inside OVER determines row ordering within each partition. ROW_NUMBER, RANK, LAG, LEAD, and running aggregates such as `SUM() OVER (...)` are the most commonly used. They are available in PostgreSQL, MySQL 8+, SQL Server, and SQLite 3.25+.

### What is the difference between DELETE and TRUNCATE?

DELETE removes rows matching a WHERE condition (or all rows without one) and logs each deletion individually, making it fully transaction-safe. TRUNCATE removes all rows by freeing data pages without logging individual row deletions — much faster on large tables, but not reversible in MySQL. PostgreSQL supports TRUNCATE inside a transaction. Use DELETE when you need a WHERE condition, want rollback safety, or need triggers to fire. Use TRUNCATE when you need to empty a large table as quickly as possible.

## Conclusion

SQL queries are the foundation of working with relational data. The patterns here — SELECT with filtering, JOIN types, GROUP BY with aggregates, window functions, and DML statements — cover the majority of what you'll write day to day. When sql queries get complex, CTEs keep them readable. When they get slow, run `EXPLAIN` and consult the [SQL indexes guide](/guides/what-are-indexes-in-sql/) for optimisation strategies. Keep the [SQL Formatter](/tools/sql-formatter/) open to maintain consistent style across your codebase.
