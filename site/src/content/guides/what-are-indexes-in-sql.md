---
title: What Are Indexes in SQL? A Complete Guide
description: What are indexes in SQL? Learn how database indexes work, which types
  exist, when to use them, and how to create indexes that make queries faster.
category: guides
subcategory: Web Concepts
template_id: blog-v5
tags:
- sql
- database
- performance
- query-optimization
- indexes
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: '2026-06-06'
og_image: /og/guides/what-are-indexes-in-sql.png
actual_word_count: 2831
schema_org: '<script type="application/ld+json">

  {"@context":"https://schema.org","@type":["BlogPosting","FAQPage"],"headline":"What
  Are Indexes in SQL? A Complete Guide","description":"What are indexes in SQL? Learn
  how database indexes work, which types exist, when to use them, and how to create
  indexes that make queries faster.","datePublished":"2026-06-06","author":{"@type":"Organization","name":"DevNook"},"publisher":{"@type":"Organization","name":"DevNook","url":"https://devnook.dev"},"url":"https://devnook.dev/guides/what-are-indexes-in-sql/","mainEntity":[{"@type":"Question","name":"What
  is an index in SQL?","acceptedAnswer":{"@type":"Answer","text":"An index in SQL
  is a data structure the database engine maintains to make data retrieval faster.
  Instead of scanning every row, the database uses the index to jump directly to matching
  rows."}},{"@type":"Question","name":"Does adding an index always improve query performance?","acceptedAnswer":{"@type":"Answer","text":"No.
  Indexes speed up reads but add overhead to write operations. On small tables or
  low-cardinality columns, the overhead may outweigh the benefit."}},{"@type":"Question","name":"What
  is the difference between a clustered and non-clustered index?","acceptedAnswer":{"@type":"Answer","text":"A
  clustered index determines the physical order of rows on disk and a table can have
  only one. A non-clustered index is a separate structure with pointers to table rows
  and a table can have many."}}]}

  </script>'
---
What are indexes in SQL? The short answer: a separate data structure the database engine keeps alongside your table to make certain queries dramatically faster. Without one, the database reads every row to answer a query — even when you only want one matching record. With an index on the right column, that search becomes a direct lookup. This guide explains how SQL indexes work mechanically, what types exist, when to create them, and where they actually slow you down.

## What Are Indexes in SQL

An index in SQL is a data structure built from one or more columns of a table. The database engine maintains it automatically as data changes. The index stores the values from those columns in a sorted, searchable form — along with pointers back to the full rows in the original table.

The simplest analogy is a book index. A 600-page book contains all the content; the index at the back lets you find any page about "transactions" without reading every page. The index trades storage space for the ability to look things up faster. In the database, the trade-off is the same: space and write overhead in exchange for faster reads.

Here is a concrete scenario. You have an `orders` table with five million rows. A query filtering by `customer_id` without an index triggers a full table scan — five million row reads. With an index on `customer_id`, the database walks a tree structure a few levels deep and retrieves only the matching rows. The difference in execution time is often three orders of magnitude.

### Indexes and Primary Keys

Every table with a [primary key](/guides/primary-key-in-database/) gets an index on that column automatically. Primary key lookups are the most common database operation, so all major SQL engines create the index when the primary key is defined. When you write `WHERE id = 42`, you are almost certainly hitting that automatic index.

What you define manually are indexes on other columns — foreign keys, frequently filtered fields, columns used in `ORDER BY`, columns used in `JOIN` conditions. These are explicit choices, and each one carries a real cost.

## How SQL Indexes Work Under the Hood

Most SQL databases use a B-tree — a balanced tree structure — as the underlying mechanism for standard indexes. Understanding how a B-tree works makes it easier to predict which queries an index will help.

A B-tree stores indexed values in sorted order, arranged as a hierarchy of nodes. The root node covers the full range of values in the indexed column. Child nodes cover progressively narrower ranges. Leaf nodes, at the bottom of the tree, contain the actual index entries — the column value plus a pointer to the location of the corresponding row in the table.

When the database engine receives a query like `WHERE email = 'alice@example.com'`, it traverses the B-tree:

1. Start at the root node and compare the search value against the node's boundary values
2. Follow the branch that covers the target value
3. Repeat at each successive level, narrowing the range
4. At the leaf node, read the row pointer and fetch the full row

For a table with one million rows, this traversal typically takes 3 to 4 comparisons because B-trees stay shallow. Tree height grows as O(log n), so doubling the row count adds at most one extra level to traverse. The [database index overview on Wikipedia](https://en.wikipedia.org/wiki/Database_index) covers additional structures beyond B-trees, including hash indexes for equality-only lookups and R-trees used for spatial data.

### Range Queries and Sorting

B-trees handle range queries efficiently because leaf nodes are ordered and linked in a chain. A query like `WHERE created_at BETWEEN '2025-01-01' AND '2025-06-30'` locates the start of the range in O(log n) time, then reads forward through adjacent leaf nodes. No full table scan needed.

Queries with `ORDER BY` on an indexed column also benefit: the database can return rows already sorted from the index rather than sorting the entire result set in memory. On large result sets, eliminating that sort step saves significant time.

### How the Query Planner Decides

The database does not always use an index even when one exists. The query planner estimates the cost of a full table scan versus an index lookup and picks the cheaper option. If a query matches a large fraction of the table's rows — typically more than 15 to 20 percent — the planner often prefers a sequential scan. Sequential reads are faster than the random I/O caused by following index pointers to scattered row locations.

Inspect the planner's decision with `EXPLAIN`:

```sql
EXPLAIN SELECT * FROM orders WHERE customer_id = 1042;
```

The output shows `Seq Scan` for a full scan or `Index Scan` for an index-driven lookup. Running `EXPLAIN ANALYZE` executes the query and shows actual timing data alongside the plan. Always verify the plan after adding an index — a new index does not guarantee the planner will use it.

## Types of SQL Indexes

SQL databases support several index types, each optimised for different access patterns.

| Index Type | Description | Best Use Case |
|---|---|---|
| **Clustered** | Rows physically stored in index key order | Primary key lookups (usually auto-created) |
| **Non-clustered** | Separate structure with row pointers | Filter columns, foreign keys |
| **Unique** | Enforces uniqueness, also serves as an index | Email, username, SKU columns |
| **Composite** | Multi-column index | Queries filtering or sorting on multiple columns |
| **Full-text** | Tokenises text for word-level search | Article bodies, product descriptions |
| **Partial** | Indexes only rows matching a condition | Sparse data, specific status value subsets |
| **Covering** | Index contains all columns a query reads | High-frequency reporting queries |

### Clustered vs. Non-Clustered

A clustered index dictates the physical order of rows in the table. Because rows are stored in sorted order by the index key, looking up a value in the clustered index retrieves the row directly — no additional pointer fetch required. A table can have exactly one clustered index. In most databases, the primary key becomes the clustered index automatically.

A non-clustered index is stored separately from the table data. After finding the target key in the non-clustered index, the engine follows a row locator pointer to fetch the full row. A table can have many non-clustered indexes. That extra pointer step, sometimes called a key lookup or RID lookup, is fast but adds overhead compared to a direct clustered seek.

### Composite Indexes and the Leftmost Prefix Rule

A composite index spans multiple columns in a defined order:

```sql
CREATE INDEX idx_orders_customer_date ON orders (customer_id, created_at);
```

This index supports queries filtering on `customer_id` alone, or on `customer_id AND created_at` together — but not on `created_at` alone. The database can only use a composite index starting from the leftmost column and moving right. Defining composite indexes with columns in the wrong order for your query patterns is one of the most common indexing mistakes developers make.

### Partial Indexes

Partial indexes include only rows matching a specified condition. PostgreSQL and SQLite support them natively:

```sql
CREATE INDEX idx_orders_pending
ON orders (created_at)
WHERE status = 'pending';
```

If 95 percent of orders are fulfilled and only 5 percent are pending, this index is far smaller and faster than a full index on `created_at`. It is precisely scoped to the query pattern that needs it. MySQL does not support partial indexes; use a composite index or table partitioning instead.

### Covering Indexes

A covering index includes every column a particular query reads, so the engine never follows the row pointer back to the main table:

```sql
-- Query needs customer_id, order_status, and total_amount
CREATE INDEX idx_orders_covering
ON orders (customer_id, order_status, total_amount);

-- This query reads entirely from the index
SELECT order_status, SUM(total_amount)
FROM orders
WHERE customer_id = 1042
GROUP BY order_status;
```

When the index contains all referenced columns, the planner marks it a covering index and returns results directly from the index structure. On frequently-run reports or dashboards, this eliminates the most expensive part of the query.

## Creating and Managing Indexes

### Basic CREATE INDEX Syntax

The syntax is consistent across PostgreSQL, MySQL, and SQLite:

```sql
-- Single-column index
CREATE INDEX idx_users_email ON users (email);

-- Unique index (enforces uniqueness and enables fast lookups)
CREATE UNIQUE INDEX idx_users_email_unique ON users (email);

-- Composite index
CREATE INDEX idx_orders_customer_status ON orders (customer_id, status);

-- Remove an index
DROP INDEX idx_users_email;
```

In PostgreSQL, adding an index to a large production table blocks write operations for the duration of the build — potentially minutes on a busy table. Use `CREATE INDEX CONCURRENTLY` to avoid that lock:

```sql
CREATE INDEX CONCURRENTLY idx_products_category_id ON products (category_id);
```

The `CONCURRENTLY` option takes longer but does not block inserts or updates during the build. MySQL handles this with its online DDL feature from version 5.6 onward. The [MySQL index documentation](https://dev.mysql.com/doc/refman/8.0/en/mysql-indexes.html) covers the available locking modes. For PostgreSQL-specific index types including GIN and GiST for full-text and geometric data, the [PostgreSQL indexes reference](https://www.postgresql.org/docs/current/indexes.html) is the authoritative source.

### Verifying the Index Is Being Used

After creating an index, verify the planner actually uses it:

```sql
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE customer_id = 1042
ORDER BY created_at DESC;
```

Look for `Index Scan` or `Index Only Scan` in the output. If you still see `Seq Scan`, the index is not being used. Common reasons: the table is too small, the query is not selective enough, or the index columns do not match the query pattern. The `Actual Time` lines in `EXPLAIN ANALYZE` output show where time is spent before and after adding the index.

### Finding Tables That Need Indexes

PostgreSQL's statistics views reveal where sequential scans are happening at scale:

```sql
SELECT relname AS table_name,
       seq_scan,
       idx_scan,
       n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE n_live_tup > 10000
ORDER BY seq_scan DESC
LIMIT 15;
```

Tables with high `seq_scan` counts and low `idx_scan` counts on large row counts are the first candidates for new indexes. Reviewing this data regularly catches missing indexes before they become production performance problems.

## Index Performance and Trade-offs

### Reads vs. Writes

Every index on a table adds overhead to INSERT, UPDATE, and DELETE operations. Inserting a row requires updating every index that covers the table. A table with eight indexes requires eight index maintenance operations per insert, on top of the table write itself.

For append-heavy workloads — event logs, clickstream tables, sensor data — indexing heavily will measurably reduce write throughput. The asymmetry is the key design insight: reads benefit from many indexes, writes suffer from them. On read-heavy tables such as product catalogues, user profiles, and reference data, adding well-chosen indexes pays off quickly. On write-heavy tables, fewer indexes with careful selection is the better approach.

### Cardinality and Selectivity

Index selectivity measures how many distinct values a column contains relative to the total row count. A column with many distinct values — email addresses, UUIDs, order reference numbers — has high selectivity. An index lookup on such a column returns a tiny fraction of rows, which is exactly when B-tree traversal earns its cost.

A column with few distinct values — a boolean, a status field with three options — has low selectivity. Filtering `WHERE is_active = true` might return 70 percent of all rows. The query planner will often skip the index and scan the table sequentially, because sequential reads are faster than random I/O for large result sets. Low selectivity alone on a column is a strong signal to reconsider whether a standard index on that column is worth creating.

### Index Bloat

B-tree indexes accumulate dead entries as rows are updated and deleted. In PostgreSQL this is called bloat: the physical index file grows larger than necessary, which slows scans and wastes disk space. Running `VACUUM` periodically cleans dead tuples from both the table and its indexes. For heavily-updated tables, periodic `REINDEX` rebuilds the index from scratch and reclaims wasted space. MySQL's InnoDB engine handles some of this automatically through background page merging, but monitoring index sizes on high-churn tables is still good operational practice.

### When Not to Create an Index

Not every table or column benefits from an index. Skip it when:

**The table is small.** For tables with fewer than a few thousand rows, the query planner typically prefers a sequential scan even when an index exists. Index traversal plus random row fetch adds more time than reading a small table in one sequential pass.

**The column has very low cardinality used alone.** A boolean flag or a status column with three values filtered on its own rarely benefits from an index. Use a partial index to target a specific high-value subset, or combine the column with a more selective column in a composite index.

**The column changes on every write.** If a column is updated frequently, index maintenance adds constant write cost. Evaluate whether the read benefit justifies it, or whether restructuring the data model would be more effective.

**You are loading data in bulk.** Dropping indexes before a bulk load and rebuilding them afterward is a standard performance pattern. Building the index once from loaded data is faster than maintaining it incrementally through thousands or millions of individual inserts.

When [choosing between SQL and NoSQL databases](/blog/sql-vs-nosql-differences-examples/), indexing control is one factor that favours relational databases: SQL engines give you precise per-column index control with full query planner visibility, while many document stores apply indexing more automatically with less tuning surface.

## Frequently Asked Questions

### What is an index in SQL?

An index in SQL is a data structure the database engine maintains alongside a table to speed up data retrieval. Rather than reading every row to find matching records, the database uses the index to jump directly to the relevant rows. The most common underlying structure is a B-tree, which supports equality lookups, range queries, and sorted results efficiently. Indexes consume additional storage and add write overhead, so they are most valuable on large tables with selective query patterns.

### Does adding an index always improve query performance?

No. Indexes improve read performance for selective queries on high-cardinality columns. On small tables, a full sequential scan is often faster than the overhead of index traversal plus random row fetch. On write-heavy tables, maintaining multiple indexes slows every insert and update. The only reliable way to know whether an index helps is to compare `EXPLAIN ANALYZE` output before and after adding it — the planner may still choose a sequential scan if it estimates that is cheaper.

### What is the difference between a clustered and non-clustered index?

A clustered index controls the physical order of rows stored on disk. A table can have exactly one clustered index, and it is typically the primary key. A non-clustered index is a separate data structure that stores indexed values with row pointers. A table can have many non-clustered indexes. Lookups on a clustered key are faster because the full row is retrieved directly from the index without an additional pointer follow.

### How do I know which columns to index?

Focus on columns that appear in `WHERE` clauses, `JOIN` conditions, and `ORDER BY` clauses. Use `EXPLAIN ANALYZE` to find queries doing sequential scans on large tables. Prioritise high-cardinality columns where the index will be selective. Foreign key columns on the child side of a relationship are nearly always worth indexing — omitting them causes slow join performance. Avoid indexing every column; each index adds write overhead that compounds across all write operations on the table.

### What is a composite index and when should I use one?

A composite index covers multiple columns in a specified order. Use one when a query consistently filters or sorts on a combination of columns. The leftmost prefix rule applies: an index on `(customer_id, created_at)` helps queries filtering on `customer_id` alone or both columns together, but not on `created_at` alone. Define column order based on which single-column filter appears most frequently. Understanding multi-table query patterns, including operations like [cross joins in SQL](/guides/what-is-cross-join-in-sql/), helps clarify which column combinations are worth covering.

## Conclusion

Understanding what are indexes in SQL is the foundation of database performance tuning. An index is the database engine's shortcut from a query condition to matching rows — built on a B-tree structure that makes lookups O(log n) instead of O(n). Clustered indexes control the physical row order on disk; non-clustered indexes are separate structures with row pointers. Composite indexes follow the leftmost prefix rule and must be defined with actual query patterns in mind. Every index adds write overhead, so create them deliberately based on `EXPLAIN ANALYZE` output rather than instinct.

For a closely related concept, the [primary key in a database](/guides/primary-key-in-database/) is automatically indexed in every SQL engine — understanding that connection clarifies why clustered index lookups are fast and how primary key design shapes overall query performance.
