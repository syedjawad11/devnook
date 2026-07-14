---
title: "React Table: Sorting, Filtering, and Infinite Scroll"
description: "React table components explained: build sortable, filterable data grids from scratch or with TanStack Table. Includes infinite scroll patterns and key gotchas."
category: "languages"
language: "react"
concept: "table"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [react, table, tanstack-table, infinite-scroll, data-grid]
related_posts: []
related_tools: []
linkAnchors:
  - "react table"
  - "react data table"
  - "react table component"
published_date: "2026-07-14"
og_image: "/og/languages/react/table.png"
word_count_target: 2352
schema_org: "<script type=\"application/ld+json\">\n{\"@context\":\"https://schema.org\",\"@type\":[\"TechArticle\",\"FAQPage\"],\"headline\":\"React Table: Sorting, Filtering, and Infinite Scroll\",\"description\":\"React table components explained: build sortable, filterable data grids from scratch or with TanStack Table. Includes infinite scroll patterns and key gotchas.\",\"datePublished\":\"2026-07-14\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/languages/react/table/\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"What is the best React table library?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"TanStack Table is the most widely adopted headless React table library, offering sorting, filtering, pagination, and virtualization without imposing any UI. For a batteries-included option with built-in styling, AG Grid Community edition is a common alternative.\"}},{\"@type\":\"Question\",\"name\":\"How do I add pagination to a React table?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"With TanStack Table, add getPaginationRowModel() to your useReactTable call and navigate with table.nextPage() and table.previousPage(). For a manual approach, keep a currentPage integer in state and slice your data array: data.slice((currentPage - 1) * pageSize, currentPage * pageSize).\"}},{\"@type\":\"Question\",\"name\":\"How does TanStack Table v8 differ from react-table v7?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"TanStack Table v8 is a complete rewrite with a framework-agnostic core and a thin React adapter. The v7 plugin system is gone. Column definitions are TypeScript-first, and the monolithic useTable hook is replaced by useReactTable with explicit row model opt-ins.\"}}]}\n</script>"
---

Building a react table is one of the most common tasks in React development. Whether your data is a list of users, a product catalog, or a paginated API response, a table gives users a way to scan, compare, and act on structured information. This article walks through three approaches: building a table from plain HTML elements and React state, adding sorting and filtering with TanStack Table, and implementing infinite scroll for datasets that grow as users scroll.

## What Is a React Table Component?

A React table component renders rows and columns of data using standard HTML table elements — `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, and `<td>` — wrapped in React components that manage data and interactivity through state.

The simplest version is a stateless component that receives an array of objects and maps each object to a table row. A production version adds column definitions, sort state, filter state, and pagination — features that a library like TanStack Table handles through a composable hook API.

Understanding [React components, JSX, and props](/languages/react/components/) is the foundation. Tables extend that model by adding data-driven rendering and user-controlled state (sort direction, filter values, current page).

### Two Approaches at a Glance

| Approach | Best for | Trade-offs |
|---|---|---|
| HTML table + React state | Small datasets, simple displays | Manual sort/filter logic |
| TanStack Table (headless) | Sorting, filtering, pagination, virtualization | Requires reading the API |

Most projects start with the native approach and reach for TanStack Table when the feature requirements grow past what a hand-rolled sort function can comfortably handle.

## How React Renders Tabular Data

React renders table data by mapping over a JavaScript array and producing one JSX element per row. It maintains a virtual DOM tree of the table and reconciles it with the real DOM on each update — patching only the nodes that changed.

For a 500-row table where you update one cell, React does not re-render all 500 rows. It diffs the virtual DOM against the previous snapshot and applies only the changed patches. This is why every row needs a stable, unique `key` prop: React uses those keys to match old rows against new rows during the diff. A missing key forces React to re-render every row on every update; a duplicate key produces incorrect renders where two rows share the same DOM identity.

Table data lives in a `useState` hook (or a global store for shared datasets). Each user interaction — a sort click, a filter input, a page change — triggers a state update, which triggers a re-render of the table with the new data slice or ordering.

## Building a React Table from Scratch

Start with the simplest working version before reaching for a library. This component accepts `columns` and `data` props and renders a plain HTML table:

```jsx
function DataTable({ columns, data }) {
  return (
    <table>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.accessor}>{col.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.id}>
            {columns.map((col) => (
              <td key={col.accessor}>{row[col.accessor]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

Use it with a static dataset:

```jsx
const columns = [
  { header: "Name", accessor: "name" },
  { header: "Email", accessor: "email" },
  { header: "Role", accessor: "role" },
];

const users = [
  { id: 1, name: "Priya Nair", email: "priya@example.com", role: "Admin" },
  { id: 2, name: "Leon Mayer", email: "leon@example.com", role: "Editor" },
  { id: 3, name: "Sana Holt", email: "sana@example.com", role: "Viewer" },
];

export default function UsersPage() {
  return <DataTable columns={columns} data={users} />;
}
```

This renders immediately with no dependencies. Now extend it with sorting:

```jsx
import { useState } from "react";

export default function SortableTable({ columns, data }) {
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState("asc");

  const sorted = sortKey
    ? [...data].sort((a, b) => {
        const val = (v) => (typeof v === "string" ? v.toLowerCase() : v);
        const cmp = val(a[sortKey]) < val(b[sortKey]) ? -1 : val(a[sortKey]) > val(b[sortKey]) ? 1 : 0;
        return sortDir === "asc" ? cmp : -cmp;
      })
    : data;

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <table>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.accessor} onClick={() => handleSort(col.accessor)} style={{ cursor: "pointer" }}>
              {col.header}
              {sortKey === col.accessor ? (sortDir === "asc" ? " ▲" : " ▼") : ""}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {sorted.map((row) => (
          <tr key={row.id}>
            {columns.map((col) => (
              <td key={col.accessor}>{row[col.accessor]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

The key detail: `[...data].sort(...)` creates a copy before sorting. Calling `.sort()` directly on the state array mutates it in place, and React may skip the re-render because the array reference is unchanged. Always sort a copy.

When your data comes from an API, use the [JSON Formatter](/tools/json-formatter/) to inspect the exact shape of the response before mapping it to column accessors. Mismatched keys surface as blank columns rather than errors, which makes them harder to spot.

## React Table with TanStack Table

TanStack Table (the library formerly called `react-table`) is headless: it provides all the sorting, filtering, and pagination logic, but you write the JSX. This lets it work with any CSS framework or design system without fighting a built-in render pipeline.

Install it:

```bash
npm install @tanstack/react-table
```

Here is a complete sortable-and-filterable table:

```jsx
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
} from "@tanstack/react-table";
import { useState, useMemo } from "react";

const users = [
  { id: 1, name: "Priya Nair", email: "priya@example.com", role: "Admin" },
  { id: 2, name: "Leon Mayer", email: "leon@example.com", role: "Editor" },
  { id: 3, name: "Sana Holt", email: "sana@example.com", role: "Viewer" },
  { id: 4, name: "Dev Patel", email: "dev@example.com", role: "Admin" },
  { id: 5, name: "Clara Wu", email: "clara@example.com", role: "Editor" },
];

export default function FilterableTable() {
  const [sorting, setSorting] = useState([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const columns = useMemo(
    () => [
      { accessorKey: "name", header: "Name" },
      { accessorKey: "email", header: "Email" },
      { accessorKey: "role", header: "Role" },
    ],
    []
  );

  const table = useReactTable({
    data: users,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div>
      <input
        value={globalFilter}
        onChange={(e) => setGlobalFilter(e.target.value)}
        placeholder="Search all columns..."
        style={{ marginBottom: "8px", display: "block" }}
      />
      <table>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                  style={{ cursor: "pointer" }}
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                  {header.column.getIsSorted() === "asc"
                    ? " ▲"
                    : header.column.getIsSorted() === "desc"
                    ? " ▼"
                    : ""}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

Clicking any header sorts the table. Clicking again reverses the direction. Typing in the filter input narrows rows across all columns. Each feature is an opt-in row model — add `getPaginationRowModel()` to get pagination without changing anything else.

`useMemo` around column definitions is important: TanStack Table compares column arrays by reference on each render. A new array reference on every render triggers unnecessary recalculations inside the library.

The official [TanStack Table documentation](https://tanstack.com/table/latest/docs/introduction) covers column helper signatures, pinning, virtualization, and the full row model API.

## Adding Infinite Scroll to a React Table

Infinite scroll replaces pagination with continuous loading — new rows appear as the user reaches the bottom. It suits browse-first use cases where users scan rather than navigate to a known page.

The browser's [Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API) handles the detection: a sentinel element sits below the last row, and the observer fires a callback when that element enters the viewport.

```jsx
import { useState, useEffect, useRef, useCallback } from "react";

const PAGE_SIZE = 20;

async function fetchUsers(page) {
  const res = await fetch(`https://api.example.com/users?page=${page}&limit=${PAGE_SIZE}`);
  if (!res.ok) throw new Error(`Failed to fetch page ${page}`);
  return res.json();
}

export default function InfiniteTable() {
  const [rows, setRows] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const sentinelRef = useRef(null);

  const loadPage = useCallback(async (pageNum) => {
    setLoading(true);
    try {
      const newUsers = await fetchUsers(pageNum);
      setRows((prev) => [...prev, ...newUsers]);
      if (newUsers.length < PAGE_SIZE) setHasMore(false);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPage(page);
  }, [page, loadPage]);

  useEffect(() => {
    if (!hasMore) return;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading) {
          setPage((prev) => prev + 1);
        }
      },
      { threshold: 0.1 }
    );
    if (sentinelRef.current) observer.observe(sentinelRef.current);
    return () => observer.disconnect();
  }, [hasMore, loading]);

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((user) => (
            <tr key={user.id}>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>{user.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div ref={sentinelRef} style={{ height: "1px" }} />
      {loading && <p>Loading more rows…</p>}
      {!hasMore && <p>All records loaded.</p>}
    </div>
  );
}
```

The sentinel `<div>` is one pixel tall and invisible. When it scrolls into the viewport the observer fires, increments `page`, and the `loadPage` effect appends the next batch to `rows`. The `hasMore` flag stops fetching when the API returns fewer items than `PAGE_SIZE`.

For very large tables — hundreds of thousands of rows accumulated over many scroll cycles — combine this pattern with row virtualization using TanStack Virtual. Virtualization keeps only the visible rows mounted in the DOM, preventing memory from growing with the total row count.

The key-based row rendering used here follows the same rules as any React list. The [React Lists and Rendering](/languages/react/lists-rendering/) guide covers `key` prop semantics and the common pitfalls of `map()` rendering in detail.

## Common React Table Gotchas

### Trap 1: Array Index as Row Key

```jsx
{users.map((user, index) => (
  <tr key={index}>  {/* avoid this */}
```

When rows are reordered by a sort click, filtered by a search input, or removed by a delete action, index-based keys cause React to match the wrong DOM nodes. The visual result is cells that appear frozen in their original positions. Use a stable identifier from your data — `user.id`, a UUID, or whatever your backend provides.

### Trap 2: Sorting State That Mutates the Original Array

```jsx
// mutates the state reference — React may skip the re-render
users.sort((a, b) => a.name.localeCompare(b.name));
setUsers(users);
```

`Array.sort()` sorts in place and returns the same reference. When you pass that same reference back to `setUsers`, React sees no change and may skip the re-render. Always sort a copy:

```jsx
setUsers([...users].sort((a, b) => a.name.localeCompare(b.name)));
```

### Trap 3: Redefining Columns Inside the Component Body Without `useMemo`

```jsx
export default function MyTable({ data }) {
  // recreated on every render — causes TanStack Table to recalculate unnecessarily
  const columns = [
    { accessorKey: "name", header: "Name" },
    { accessorKey: "email", header: "Email" },
  ];

  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() });
  // ...
}
```

TanStack Table uses referential equality to check whether column definitions changed between renders. Defining `columns` inside the component body without `useMemo` produces a new array reference on every render, triggering internal recalculations every time the parent re-renders — even for unrelated state changes. Wrap column definitions in `useMemo` or move them outside the component entirely.

### Trap 4: Forgetting to Handle Empty State

A table that renders zero rows with no explanation leaves users confused. Check whether the empty state is from loading, from filtering, or from genuinely having no data, and display an appropriate message:

```jsx
if (loading && rows.length === 0) return <p>Loading…</p>;
if (rows.length === 0) return <p>No results match your search.</p>;
```

## Frequently Asked Questions

### What is the best React table library?

TanStack Table is the most widely adopted headless option, offering sorting, filtering, pagination, and virtualization without prescribing any UI. It pairs with TanStack Virtual for large datasets where DOM node count is a concern. If you need a fully styled, out-of-the-box solution, AG Grid Community Edition provides built-in theming, but it imposes its own rendering pipeline that can conflict with custom styling systems. For most React applications, TanStack Table with your own CSS is the right balance of control and convenience.

### How do I add pagination to a React table?

With TanStack Table, add `getPaginationRowModel()` to your `useReactTable` options and navigate pages with `table.nextPage()`, `table.previousPage()`, and `table.setPageIndex(n)`. Read `table.getState().pagination` to display the current page and total page count. For a manual approach without TanStack Table, keep a `currentPage` integer in state and slice your data array before passing it to the table component:

```jsx
const pageSize = 20;
const currentPageData = allData.slice(
  (currentPage - 1) * pageSize,
  currentPage * pageSize
);
```

Render navigation buttons that call `setCurrentPage((p) => p + 1)` and `setCurrentPage((p) => p - 1)`, disabling them when you reach the first or last page.

### How does TanStack Table v8 differ from react-table v7?

TanStack Table v8 is a complete rewrite with a framework-agnostic core. The v7 API centered on a monolithic `useTable` hook with a plugin architecture — you added features like sorting or pagination by passing plugin functions as arguments. In v8, each feature is an explicit row model you opt into (`getSortedRowModel`, `getPaginationRowModel`, and so on), and the React adapter is a thin layer over the same core that drives Vue, Solid, and Svelte versions. The column definition syntax changed significantly: v8 uses `accessorKey` and `accessorFn` instead of v7's string accessor paths, and the render functions use `flexRender` rather than the implicit cell render from v7. Migration requires rewriting column definitions and the render JSX, but the conceptual model — columns, row models, state — maps clearly from one to the other.

## Conclusion

A react table starts as a simple `map()` over an array and grows as interaction requirements grow. Build the basic version with native HTML and React state first — you understand what TanStack Table provides once you have done the work manually. When sorting logic, filter inputs, and pagination controls start to crowd your component, TanStack Table removes that boilerplate without locking you into a specific visual style. For datasets that grow dynamically, the Intersection Observer pattern replaces numbered pagination with continuous loading that feels natural on both desktop and mobile.

From here, explore [React Components](/languages/react/components/) to understand the component model that tables are built on, and [React Lists and Rendering](/languages/react/lists-rendering/) for the key-prop patterns that apply to every dynamic row list. The TanStack Table documentation covers virtualization, column pinning, row selection, and the full row model API.
