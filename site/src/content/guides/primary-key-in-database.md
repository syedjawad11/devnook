---
title: What Is a Primary Key in a Database?
description: What is the primary key in a database? A primary key uniquely identifies every row in a table. Learn types, best practices, and SQL examples.
category: guides
subcategory: Architecture
template_id: blog-v5
tags:
- primary-key
- database
- sql
- relational-database
- data-modeling
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: '2026-06-01'
og_image: /og/guides/primary-key-in-database.png
actual_word_count: 3196
schema_org: "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": [\n    \"BlogPosting\",\n    \"FAQPage\"\n  ],\n  \"headline\": \"What Is a Primary Key in a Database?\",\n  \"description\": \"What is the primary key in a database? A primary key uniquely identifies every row in a table. Learn types, best practices, and SQL examples.\",\n  \"datePublished\": \"2026-06-01\",\n  \"author\": {\n    \"@type\": \"Organization\",\n    \"name\": \"DevNook\"\n  },\n  \"publisher\": {\n    \"@type\": \"Organization\",\n    \"name\": \"DevNook\",\n    \"url\": \"https://devnook.dev\"\n  },\n  \"url\": \"https://devnook.dev/guides/primary-key-in-database\",\n  \"mainEntity\": [\n    {\n      \"@type\": \"Question\",\n      \"name\": \"Can a table have more than one primary key?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"No. A table can have at most one primary key constraint. You can add UNIQUE constraints on other columns, but only one column set can be declared PRIMARY KEY.\"\n      }\n    },\n    {\n      \"@type\": \"Question\",\n      \"name\": \"Can the primary key be NULL?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"No. The PRIMARY KEY constraint automatically implies NOT NULL. You cannot insert a row with a NULL primary key value.\"\n      }\n    },\n    {\n      \"@type\": \"Question\",\n      \"name\": \"What happens if you try to insert a duplicate primary key?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"The database rejects the insert with a constraint violation error, such as duplicate key value violates unique constraint in PostgreSQL.\"\n      }\n    }\n  ]\n}\n</script>"
---
A primary key is one of the most fundamental concepts in relational databases. Every table needs a reliable way to identify each row without ambiguity — and the primary key is that mechanism. Understanding what is the primary key in a database matters whether you are designing your first schema, reviewing a legacy codebase, or debugging a data integrity error in a production system. This guide covers what primary keys are, how they work, the main types available, how they differ from foreign keys, and how to choose the right one for your use case.

## What Is a Primary Key in a Database?

A primary key is a column — or set of columns — in a database table that uniquely identifies each row. Two rules apply without exception:

1. **Uniqueness**: No two rows can share the same primary key value.
2. **Non-null**: A primary key column can never contain NULL.

Think of it as a permanent identification number assigned to every record in a table. Every user in a `users` table, every product in a `products` table, every transaction in an `orders` table gets one. No two rows share the same number, and no row exists without one.

Here is the simplest illustration — a `users` table with three rows:

| user_id | name    | email               |
|---------|---------|---------------------|
| 1       | Alice   | alice@example.com   |
| 2       | Bob     | bob@example.com     |
| 3       | Charlie | charlie@example.com |

The `user_id` column is the primary key. Every row has a distinct value, and no row has `user_id = NULL`. That is all a primary key is at its core: a column that unambiguously identifies each record.

When you declare a primary key, the database automatically builds a unique index on that column. This index is what makes lookups by primary key exceptionally fast. Instead of scanning every row in the table, the database uses the index structure — typically a B-tree — to locate the target record in O(log n) time. For a table with one million rows, finding any single row by primary key requires at most 20 comparisons.

In SQL, you declare a primary key in the `CREATE TABLE` statement. The [PostgreSQL documentation on constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) covers the complete syntax:

```sql
CREATE TABLE users (
    user_id   INT          NOT NULL,
    name      VARCHAR(100) NOT NULL,
    email     VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_id)
);
```

The `PRIMARY KEY` constraint tells the database to enforce uniqueness and NOT NULL on `user_id`. Any `INSERT` or `UPDATE` that would violate either rule is immediately rejected with a constraint violation error.

## Why Every Table Needs a Primary Key

Without a primary key, a relational table has a fundamental problem: rows can become indistinguishable. If two rows contain identical data across every column, the database has no way to address one without affecting the other. Updates, deletes, and foreign key relationships all become unreliable.

Consider an `orders` table with no primary key:

| customer_name | product | quantity |
|---------------|---------|----------|
| Alice         | Laptop  | 1        |
| Alice         | Laptop  | 1        |

If Alice returns one laptop, which row do you delete? There is no answer the database can give with confidence. A primary key prevents this class of problem entirely.

Beyond uniqueness enforcement, primary keys serve three additional purposes in a relational database:

**Referential integrity**: Foreign keys in other tables point to primary key values. An `orders` table typically has a `user_id` column referencing `users.user_id`, creating a verified, enforced link between a customer and their orders. Without a primary key to reference, this relationship cannot be expressed correctly. Our comparison of [SQL vs NoSQL differences](/blog/sql-vs-nosql-differences-examples) explains how this kind of structured reference is the defining feature that separates relational from document databases.

**Query performance**: The automatic index on the primary key makes `WHERE user_id = 42` one of the fastest operations in a relational database. Lookups by primary key bypass full table scans entirely, regardless of how many rows the table contains.

**Framework compatibility**: Application frameworks — Django ORM, Hibernate, Active Record, Prisma, SQLAlchemy — assume every table has a primary key. They use it to track object identity in memory, generate efficient UPDATE and DELETE statements, and implement lazy loading in associations. A table without a primary key forces workarounds that add complexity and introduce subtle bugs.

Most databases recommend declaring a primary key on every table. MySQL's InnoDB storage engine physically organizes rows around the primary key. If you do not declare one, InnoDB creates a hidden internal key that is invisible to your application, undebugable, and wasteful of storage.

## Types of Primary Keys

Not all primary keys are the same. There are three main approaches, each with distinct trade-offs.

### Natural Keys

A natural key uses a column that already exists in the data and carries real-world meaning outside the database. Social security numbers, ISBN codes, email addresses, and two-letter country codes are common examples.

**When they work**: The value is stable, guaranteed unique, and universally recognized. Country codes — `US`, `DE`, `JP` — are a rare case where a natural key genuinely works: they are defined by the [ISO 3166-1 international standard](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), never change, and every external system already uses them.

**When they fail**: Most real-world data fails the stability test over time. Email addresses change when users switch providers. Phone numbers are reassigned. ISBN codes migrated from 10 to 13 digits. Any natural key that can change or be reassigned will eventually break the foreign key references pointing to it. Updating a primary key value requires cascading changes through every related table — an expensive, risky operation. For most application tables, natural keys create more problems than they solve.

### Surrogate Keys

A surrogate key is an artificial identifier with no business meaning — generated solely to identify rows. Auto-incrementing integers and UUIDs are the two dominant forms.

**Auto-increment integers** are the most widely used surrogate key. The database generates them automatically (`SERIAL` in PostgreSQL, `AUTO_INCREMENT` in MySQL). They are compact (4–8 bytes), inserted in sequential order, fast to index and join, and easy to read in debugging sessions and SQL logs. The downside: they are predictable. Exposing `user_id=42` in a URL reveals how many users you have and makes ID enumeration possible.

**UUIDs** (Universally Unique Identifiers) are 128-bit pseudo-random values. They are globally unique — two independent servers can generate records simultaneously that will never collide when merged. This matters for distributed systems and applications that synchronize data across devices or regions. The concept of globally unique identifiers also appears in authentication: [JSON Web Tokens](/guides/what-is-jwt) rely on unique, unguessable values for exactly this reason. The trade-offs for UUIDs: they are larger (16 bytes vs 4 bytes for an `INT`), harder to read in debug output, and random insertion order can fragment B-tree indexes in MySQL InnoDB at very high write rates.

**Auto-increment INT vs UUID — at a glance**:

| Property | Auto-increment INT | UUID |
|----------|-------------------|------|
| Storage size | 4–8 bytes | 16 bytes |
| Human-readable | Yes | Opaque |
| Sequential insert | Yes | No (random) |
| Global uniqueness | Per-table only | Yes |
| Enumerable from URL | Yes | No |
| InnoDB write efficiency | Optimal | Degrades at scale |
| Best use case | Single-server apps | Distributed / multi-node |

### Composite Keys

A composite key uses two or more columns together as the primary key. Neither column is unique on its own, but the combination is.

A `course_enrollments` table is the canonical example. A student can enroll in many courses. A course can have many students. But a student can only enroll in a given course once:

```sql
CREATE TABLE course_enrollments (
    student_id  INT       NOT NULL,
    course_id   INT       NOT NULL,
    enrolled_at TIMESTAMP NOT NULL,
    PRIMARY KEY (student_id, course_id)
);
```

The combination of `student_id` and `course_id` is unique across all rows, making it a valid composite primary key. Composite keys are well-suited to junction tables in many-to-many relationships. They are less practical for general application tables because any table referencing the junction must carry both columns as its foreign key.

## Primary Keys vs Foreign Keys

Primary keys and foreign keys work together. A primary key identifies rows within one table. A foreign key in another table references those primary key values, creating an enforced link between records across tables.

```sql
CREATE TABLE users (
    user_id   INT          NOT NULL AUTO_INCREMENT,
    name      VARCHAR(100) NOT NULL,
    email     VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE orders (
    order_id    INT       NOT NULL AUTO_INCREMENT,
    user_id     INT       NOT NULL,
    total_cents INT       NOT NULL,
    placed_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

The `orders.user_id` column is a foreign key referencing `users.user_id`. The database enforces referential integrity: any `INSERT` into `orders` with a `user_id` that does not exist in `users` is rejected. The `ON DELETE` rule determines what happens when a user is deleted — options include `CASCADE` (delete their orders too), `SET NULL` (clear the reference), or `RESTRICT` (block the delete if orders exist).

This enforcement is what makes relational databases *relational*. Data is stored once and referenced by ID. A user's name and email live in exactly one row in `users`. Every order references that row by its primary key. When you query across both tables:

```sql
SELECT u.name, u.email, o.order_id, o.total_cents
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.user_id = 42;
```

The database uses the primary key index on `users` and the index on `orders.user_id` to execute this join efficiently. Both sides of the join condition are indexed, enabling fast index-to-index lookups without scanning either table in full.

## Creating and Querying Primary Keys in SQL

Here are the main SQL patterns you will use when working with primary keys day to day.

**Auto-increment primary key — PostgreSQL:**

```sql
CREATE TABLE products (
    product_id   SERIAL       PRIMARY KEY,
    name         VARCHAR(200) NOT NULL,
    price_cents  INT          NOT NULL CHECK (price_cents > 0),
    created_at   TIMESTAMP    NOT NULL DEFAULT NOW()
);
```

`SERIAL` is shorthand: PostgreSQL creates a sequence object and sets the column default to `nextval(sequence)`. Equivalent to `INT NOT NULL DEFAULT nextval(...)`. In MySQL, use `INT NOT NULL AUTO_INCREMENT PRIMARY KEY` instead.

**UUID primary key — PostgreSQL 13+:**

```sql
CREATE TABLE api_keys (
    key_id      UUID      DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     INT       NOT NULL REFERENCES users(user_id),
    label       TEXT      NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at  TIMESTAMP
);
```

`gen_random_uuid()` generates a cryptographically random UUID for each new row. This is appropriate for anything that should not be guessable from adjacent values. Note that [Unix timestamps](/guides/unix-timestamp-explained) are an alternative when you need time-ordered identifiers — they are sortable by creation time, unlike random UUIDs.

**Adding a primary key to an existing table:**

```sql
ALTER TABLE legacy_data ADD PRIMARY KEY (record_id);
```

Be aware that `ALTER TABLE` to add a primary key acquires a full table lock in most databases. For large production tables, this operation should be planned for a maintenance window or handled through a more careful online migration.

**Querying primary key metadata — PostgreSQL:**

```sql
SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
   AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;
```

## How Databases Store Primary Keys Internally

Understanding what the database does with a primary key under the hood helps explain why key choice affects real performance at scale.

**InnoDB (MySQL/MariaDB) — clustered index**: InnoDB physically stores all table rows in primary key order. Rows with `user_id = 1`, `2`, `3` sit adjacent on disk. Range scans by primary key — reading rows 100 through 200 — read a contiguous block of disk pages, which is very fast. The consequence is that inserting rows with non-sequential primary keys (such as random UUIDs) forces InnoDB to split B-tree pages to insert values in the middle of the sorted structure. At high insert rates on large tables, this page fragmentation degrades write throughput. The MySQL documentation on [InnoDB index types](https://dev.mysql.com/doc/refman/8.0/en/innodb-index-types.html) explains the clustered vs secondary index distinction in detail.

**PostgreSQL — heap + B-tree index**: PostgreSQL stores rows in insertion order in a heap. The primary key creates a separate B-tree index alongside the heap. Because physical row placement is not tied to the key value, UUID primary keys have much less fragmentation impact in PostgreSQL than in InnoDB. The B-tree index simply stores `(key_value, heap_page_location)` pairs, and random insertion order only shuffles those pairs in the index, not the heap.

**B-tree complexity**: Both systems use B-tree indexes for primary keys by default. A balanced B-tree guarantees O(log n) lookup time regardless of insert order. This is the same algorithmic foundation covered in [sorting algorithms](/blog/sorting-algorithms-comparison): the tree's balanced structure ensures the path from root to any leaf is at most log₂(n) levels. For a table with 10 million rows, locating a row by primary key takes at most 24 comparisons.

## How to Choose the Right Primary Key

With types and internals covered, here is practical guidance for making the right choice for your application.

**Default to auto-increment integers for most tables.** For application tables — `users`, `products`, `posts`, `comments`, `invoices` — an auto-incrementing integer is the correct default. It is compact, sequentially inserted (optimal for InnoDB), well-supported by every ORM and migration tool, and easy to read in SQL shells and logs. Unless you have a specific requirement that integers cannot meet, reach for `SERIAL` in PostgreSQL or `AUTO_INCREMENT` in MySQL.

**Use UUIDs when you have distributed systems or need to hide row counts.** If your application writes to multiple database nodes, replicates data across regions, syncs between devices, or will ever merge records from separate databases, UUIDs prevent the collision that sequential integers cannot avoid. They also prevent users from guessing adjacent IDs in API responses and URLs. The extra storage cost — 12 bytes per row compared to `INT` — is a reasonable trade for correctness in distributed architectures.

**Do not use mutable, user-controlled data as a primary key.** Email addresses, usernames, phone numbers, and any value a user can change are poor primary key choices. When a primary key value changes, every foreign key reference pointing to it must be updated — a cascading, expensive, error-prone operation. Surrogate keys solve this cleanly: the user's email can change freely without touching any relational link.

**Use composite keys for pure junction tables.** A table whose only purpose is to record a many-to-many relationship — `user_roles`, `post_tags`, `order_items` — often does not need a surrogate key. The combination of its two foreign key columns is naturally unique and serves well as a composite primary key.

**Keep key columns narrow.** Every foreign key referencing your primary key stores a copy of it. An `INT` (4 bytes) means each child row carries 4 bytes for the reference. A `BIGINT` (8 bytes), a UUID (16 bytes). Over millions of rows across multiple child tables, narrower keys mean less storage, smaller indexes, and better buffer cache utilization. Use `INT` until you expect more than 2 billion rows in the parent table; upgrade to `BIGINT` if that threshold is realistic.

**Plan before production.** Changing a primary key type after data is live — from `INT` to `UUID`, or from a natural key to a surrogate — is costly. It requires migrating the column, rewriting foreign key constraints, updating application code, and invalidating caches. When a later API endpoint returns a [409 Conflict](/guides/http-status-codes-guide) due to a duplicate key error at scale, migrating to UUIDs retroactively is far harder than choosing them upfront.

## Frequently Asked Questions

### Can a table have more than one primary key?

No. A table can have at most one primary key constraint — that is a hard rule in the SQL standard and enforced by every major relational database. What confuses many people is that a table *can* have multiple `UNIQUE` constraints: other columns where no two rows may share the same value. But only one column (or set of columns) can be designated `PRIMARY KEY`. If your table has several candidate keys — multiple columns that could each uniquely identify a row — choose the most stable and commonly joined one as the primary key, and add `UNIQUE NOT NULL` constraints on the others.

### Can the primary key be NULL?

No. The `PRIMARY KEY` constraint automatically implies `NOT NULL`. You cannot declare a nullable column as a primary key, and you cannot insert or update a row where the primary key value is NULL. This is by design: a key that can be absent provides no reliable identity. If you need to represent records whose identity is not yet assigned, use a different pattern — a nullable `external_id` column alongside a non-nullable surrogate key, or a separate staging table.

### What happens if you try to insert a duplicate primary key?

The database immediately rejects the insert with a constraint violation error. In PostgreSQL: `ERROR: duplicate key value violates unique constraint "users_pkey"`. In MySQL: `ERROR 1062 (23000): Duplicate entry '42' for key 'PRIMARY'`. Application code should handle this explicitly. PostgreSQL offers `INSERT ... ON CONFLICT DO NOTHING` or `ON CONFLICT DO UPDATE` for upsert behavior. MySQL offers `INSERT ... ON DUPLICATE KEY UPDATE`. Using these constructs is safer than a check-then-insert sequence, which is not atomic and can fail under concurrent load.

### What is the difference between a primary key and a unique index?

Both enforce that no two rows share the same value. The differences: a table can have only one primary key but multiple unique indexes; primary key columns cannot be NULL, while columns with unique indexes can contain NULL (and most databases allow multiple NULLs in the same column since NULL is not equal to NULL); only the primary key serves as the default target for foreign key references; and in MySQL InnoDB, the primary key is the clustered index — the physical storage order of the table — while unique indexes are secondary structures.

### Should I always use UUIDs instead of integers?

Not by default. UUIDs solve a specific problem: preventing ID collisions across independent, uncoordinated systems. For a standard web application backed by a single database, sequential integers are faster to insert, cheaper to store, and simpler to debug. The decision to use UUIDs should be driven by a concrete requirement — distributed writes, cross-system data merging, or security-sensitive ID exposure — rather than as a default choice. If you are unsure, start with integers and migrate to UUIDs only when the requirement arises.

## Conclusion

The primary key is the foundation of reliable relational data: the guarantee that every row has an unambiguous identity, that relationships between tables are verifiable, and that lookups are fast. Understanding what is the primary key in a database — how the three types compare, how InnoDB and PostgreSQL store them differently, how they relate to foreign keys, and how to choose between integers and UUIDs — gives you the foundation to design schemas that hold up under both correctness requirements and production load. Start with auto-increment integers for most tables, reach for UUIDs when your architecture genuinely requires global uniqueness, and always declare a primary key before your table reaches production.
