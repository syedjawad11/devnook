---
title: "Lists in React: Rendering Arrays with map() and Keys"
description: "Render lists in React with map() and the key prop. Covers dynamic arrays, nested lists, conditional rendering, and key-related bugs to avoid."
category: "languages"
language: "react"
concept: "lists-rendering"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [react, lists-rendering, jsx, array-map, keys]
related_posts: []
related_tools: []
linkAnchors:
  - "lists in react"
  - "react list rendering"
  - "render array react"
published_date: "2026-07-11"
og_image: "/og/languages/react/lists-rendering.png"
word_count_target: 2027
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "Lists in React: Rendering Arrays with map() and Keys",
    "description": "Render lists in React with map() and the key prop. Covers dynamic arrays, nested lists, conditional rendering, and key-related bugs to avoid.",
    "datePublished": "2026-07-11",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/react/lists-rendering/",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Why does React need a key prop when rendering lists?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "React uses the key prop to identify which items changed, were added, or were removed during re-renders. Without keys, React matches list elements by position, which breaks when items reorder or are inserted mid-list. With stable keys, React surgically updates only the items that actually changed, keeping performance and component state correct."
        }
      },
      {
        "@type": "Question",
        "name": "Can I use the array index as a key in React?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Using the array index works for static, non-reorderable lists. For anything that sorts, filters, prepends, or removes items, index-based keys cause React to associate the wrong DOM node with each item after the array changes. UI state such as input values, focus, or checkbox state ends up on the wrong item. Use a stable unique identifier from your data instead."
        }
      },
      {
        "@type": "Question",
        "name": "How do I render a list of objects in React?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Call Array.map() on your array and return a JSX element for each object. Add a key prop to the outermost element returned by map(), using a stable unique field like id. React renders the resulting array of JSX elements as sibling nodes in the DOM."
        }
      }
    ]
  }
  </script>
---

Rendering lists in React is one of those patterns you'll use every day — product catalogues, comment feeds, notification streams, and navigation menus all reduce to the same core problem: take an array of data, turn each item into a UI element, and let React keep the DOM in sync as the data changes.

React doesn't have a special list directive. Lists in React are just JavaScript arrays of JSX elements. That simplicity is intentional, but it means you need to understand two things clearly: how `Array.map()` maps data to JSX, and why the `key` prop is not optional. This article covers both, from the simplest working example through to the gotchas that cause real bugs in production.

## Rendering Lists in React with map()

The fundamental pattern for lists in React is `Array.map()`. You call `map()` on your data array, return a JSX element per item, and React renders the resulting array as sibling nodes in the DOM.

Here is the simplest possible version:

```jsx
const fruits = ['Apple', 'Banana', 'Cherry'];

function FruitList() {
  return (
    <ul>
      {fruits.map((fruit) => (
        <li key={fruit}>{fruit}</li>
      ))}
    </ul>
  );
}
```

The `map()` call executes once per item. Each iteration returns a `<li>` element. React receives an array of `<li>` elements and renders them all. The `key` prop on `<li>` is required — React logs a warning without it, and the reconciliation bugs that follow are subtle enough to cost real debugging time.

For the JavaScript mechanics behind `map()`, `filter()`, and `reduce()` — which you'll chain frequently when building list components — the [JavaScript Array Methods guide](/languages/javascript/array-methods/) covers them in depth.

## How React Uses the key Prop: Reconciliation

Understanding why `key` matters requires understanding what React does when it re-renders a list.

React maintains a virtual DOM — a lightweight JavaScript representation of the real DOM. When state or props change, React builds a new virtual DOM tree and diffs it against the old one. Only the differences get applied to the actual DOM. This process is called reconciliation, and it's why React is fast.

For lists, the diffing algorithm needs to match each element in the new array to an element in the old array. Without keys, it matches by position: new element 0 matches old element 0, new element 1 matches old element 1, and so on.

Position-based matching breaks immediately when items move. Consider a task list sorted by priority. The user completes the top task; it moves to the bottom. Without keys, React sees that every element changed — the top now has different text, the second item moved up — and updates every DOM node in the list. With a stable `key` per task (the task's `id`), React sees that one item moved to the bottom and the others shifted up. It moves the DOM node rather than re-creating it.

The performance difference matters for long lists, but the correctness difference is what causes genuine bugs. Any stateful child component in the list — an open dropdown, an input mid-edit, a focused element — stores its state in the component instance. When React matches the wrong instance to the wrong position, that state appears on the wrong item. The user types in one text field and the value appears in a different row.

## A Minimal Product List Component

Start with a stateless component that renders a plain array of objects:

```jsx
const products = [
  { id: 1, name: 'Mechanical Keyboard', price: 129 },
  { id: 2, name: 'USB-C Hub', price: 49 },
  { id: 3, name: 'Monitor Stand', price: 79 },
];

function ProductList() {
  return (
    <ul className="product-list">
      {products.map((product) => (
        <li key={product.id}>
          {product.name} — ${product.price}
        </li>
      ))}
    </ul>
  );
}
```

`product.id` is a stable, unique identifier. It won't change if the array reorders, and it won't collide with another item's id. This is the right key for this data.

The [React Components guide](/languages/react/components/) covers how components like this receive data via props, manage their own state, and compose into larger trees — the full picture of how list components fit into a React application.

## Extracting Items into a Separate Component

In practice, list items are rarely rendered inline. Extract the per-item rendering into its own component:

```jsx
function ProductItem({ product }) {
  return (
    <li className="product-item">
      <span className="product-name">{product.name}</span>
      <span className="product-price">${product.price}</span>
    </li>
  );
}

function ProductList({ products }) {
  return (
    <ul className="product-list">
      {products.map((product) => (
        <ProductItem key={product.id} product={product} />
      ))}
    </ul>
  );
}
```

The `key` goes on the element returned by `map()` — here that is `<ProductItem>`, not the `<li>` inside it. The key lives at the list level, not inside the component. Importantly, you cannot read `props.key` inside `ProductItem` — React reserves it. If you need the id inside the component (for a delete button, for example), pass it as a separate explicit prop: `<ProductItem key={product.id} id={product.id} product={product} />`.

## Handling Empty States and Loading Conditions

Real list components need to handle three states beyond the happy path: loading, error, and empty. Handle these with early returns before the `map()` call:

```jsx
function ProductList({ products, isLoading, error }) {
  if (isLoading) {
    return <p className="status-message">Loading products...</p>;
  }

  if (error) {
    return <p className="status-message error">Failed to load: {error.message}</p>;
  }

  if (products.length === 0) {
    return <p className="status-message">No products match your filters.</p>;
  }

  return (
    <ul className="product-list">
      {products.map((product) => (
        <ProductItem key={product.id} product={product} />
      ))}
    </ul>
  );
}
```

Returning early keeps the main render path clean and eliminates the most common list crash: calling `.map()` on `undefined`. This happens when an API response hasn't arrived yet and the component tries to map over the initial `undefined` value. The explicit `isLoading` guard prevents it.

When you're debugging data shapes from API responses — figuring out which fields are available to map over — the [JSON formatter tool](/tools/json-formatter/) helps you inspect and validate response JSON before wiring it into a component.

## Nested Lists

Nested lists follow the same map-and-key pattern at each level. Keys are scoped to their sibling array, not globally:

```jsx
const categories = [
  {
    id: 'peripherals',
    label: 'Peripherals',
    items: [
      { id: 101, name: 'Keyboard' },
      { id: 102, name: 'Mouse' },
    ],
  },
  {
    id: 'furniture',
    label: 'Furniture',
    items: [
      { id: 201, name: 'Monitor Stand' },
      { id: 202, name: 'Desk Mat' },
    ],
  },
];

function CategoryList() {
  return (
    <div>
      {categories.map((category) => (
        <section key={category.id}>
          <h3>{category.label}</h3>
          <ul>
            {category.items.map((item) => (
              <li key={item.id}>{item.name}</li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
```

`item.id` only needs to be unique within its `category.items` array — id `101` in `peripherals` and id `101` in `furniture` would not conflict. React reconciles each nested array independently. That said, globally unique IDs (database row IDs, UUIDs) make life easier as components grow.

## Filtering and Sorting Lists

Chain `filter()` before `map()` to render a subset of the array:

```jsx
function AffordableProducts({ products, maxPrice }) {
  return (
    <ul>
      {products
        .filter((product) => product.price <= maxPrice)
        .map((product) => (
          <ProductItem key={product.id} product={product} />
        ))}
    </ul>
  );
}
```

For sorting, create a sorted copy rather than mutating the original array — `Array.sort()` mutates in place, and mutating props is always a bug:

```jsx
const sortedProducts = [...products].sort((a, b) => a.price - b.price);
```

For a quick reference on `filter()`, `reduce()`, `find()`, and the other array methods you'll reach for regularly, the [JavaScript Array Cheat Sheet](/cheatsheets/javascript-array-cheatsheet/) lists them with signatures and examples. And when list items involve inline editing or multi-field forms, [React Hook Form](/languages/react/hook-form/) handles controlled inputs efficiently without re-rendering the entire list on each keystroke.

## Common Mistakes with Lists in React

### Using Array Index as a Key

The index pattern looks harmless and React doesn't throw an error:

```jsx
// Risky for any list that can reorder or filter
{items.map((item, index) => (
  <li key={index}>{item.name}</li>
))}
```

For a static array that never changes order, index keys work. The moment you sort, filter, prepend, or delete items, the indices shift. React keeps the same DOM node at each index position but now associates it with a different item. Any controlled input, checkbox state, or focused element inside the list item follows the DOM node, not the data — so it appears on the wrong row.

Use index only for truly static lists. For everything else, use a field from the data itself.

### Generating Keys at Render Time

```jsx
// Never do this
{items.map((item) => (
  <li key={Math.random()}>{item.name}</li>
))}
```

Every render generates entirely new keys. React sees no stable identity across renders and unmounts then remounts every list item on every state update — destroying all internal state and causing unnecessary DOM churn. Generate IDs when you create data (using `crypto.randomUUID()` or your backend's primary key), store them in state or your data layer, and use them as keys.

### Forgetting the key Entirely

React logs: `Warning: Each child in a list should have a unique "key" prop.` This is a bug report, not a style warning. React falls back to position-based reconciliation without keys, which causes the state-mismatch issues described above. Fix it immediately — don't leave it for later.

## Frequently Asked Questions

### Why does React need a key prop when rendering lists?

React uses `key` to identify which items changed, were added, or were removed during re-renders. Without keys, React matches elements by position, which breaks as soon as items reorder or get inserted mid-list. With stable keys, React surgically updates only the items that actually changed, keeping both performance and component state correct.

### Can I use the array index as a key in React?

Index-based keys work for static, non-reorderable lists. For anything that sorts, filters, prepends, or removes items, index keys cause React to associate the wrong DOM node with each data item after the array changes. Controlled input values, focus, and checkbox state end up on the wrong row. Use a stable unique identifier from your data — a database id, a UUID — instead.

### How do I render a list of objects in React?

Call `Array.map()` on your array and return a JSX element for each object. Add a `key` prop to the outermost element returned by `map()`, drawn from a stable unique field like `id`. React renders the resulting array as sibling nodes. For complex items, extract them into a dedicated component and pass the object as a prop.

### What happens if I don't add a key when rendering a list?

React logs a console warning and falls back to position-based reconciliation. For static lists that never reorder, this causes no visible bugs. For dynamic lists, component state — controlled inputs, open dropdowns, focus — attaches to the wrong element whenever the array changes. Treat the warning as a bug.

### How do I show an empty state when a list has no items?

Check `array.length === 0` before calling `map()` and return a fallback element:

```jsx
if (products.length === 0) {
  return <p>No results. Try adjusting your filters.</p>;
}
return <ul>{products.map(...)}</ul>;
```

You can also inline it with a conditional expression: `{products.length === 0 ? <p>No results</p> : <ul>...</ul>}`.

## Conclusion

Lists in React reduce to two things: `Array.map()` to transform data into JSX, and a stable `key` to tell React which DOM node corresponds to which data item across re-renders. The `key` isn't a formality — it directly controls whether React updates the right node, and whether component state stays attached to the right item.

The practical rules: pull keys from your data (a database id or UUID), not from the array's position. Handle empty and loading states before you call `map()`. Sort and filter by creating a copy of the array, not by mutating it in place.

To go deeper on how these list components fit into a larger application — how they receive props, manage state, and compose together — the [React Components guide](/languages/react/components/) is the natural next step. The official [React documentation on rendering lists](https://react.dev/learn/rendering-lists) also covers the reconciliation algorithm in detail, and [MDN's Array.map() reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map) is worth bookmarking for the JavaScript side.
