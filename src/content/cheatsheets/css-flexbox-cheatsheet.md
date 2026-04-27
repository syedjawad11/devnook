---
title: "CSS Flexbox Cheat Sheet"
description: "Master CSS Flexbox with this cheat sheet covering flex container and flex item properties, alignment, ordering, and responsive layout patterns with examples."
category: cheatsheets
template_id: cheatsheet-v1
tags: [css, flexbox, layout, frontend, cheatsheet, responsive-design]
related_posts: []
related_tools: []
published_date: "2026-04-25"
og_image: "/og/cheatsheets/css-flexbox-cheatsheet.png"
downloadable: true
content_type: editorial
---

# CSS Flexbox Cheat Sheet

CSS Flexbox is a one-dimensional layout model that lets you distribute space and align items in a container along a single axis. This reference covers every property — for both the flex container and flex items — with values, defaults, and usage examples.

## Enabling Flexbox

```css
.container {
  display: flex;        /* block-level flex container */
  display: inline-flex; /* inline-level flex container */
}
```

All direct children of a flex container automatically become **flex items**.

## Flex Container Properties

These properties are applied to the parent element (`display: flex`).

### Flex Direction & Wrapping

| Property | Values | Default | Description |
|----------|--------|---------|-------------|
| `flex-direction` | `row` \| `row-reverse` \| `column` \| `column-reverse` | `row` | Sets the main axis direction |
| `flex-wrap` | `nowrap` \| `wrap` \| `wrap-reverse` | `nowrap` | Controls whether items wrap to new lines |
| `flex-flow` | `<direction> <wrap>` | `row nowrap` | Shorthand for `flex-direction` + `flex-wrap` |

```css
.container {
  flex-direction: row;         /* left → right */
  flex-direction: column;      /* top → bottom */
  flex-direction: row-reverse; /* right → left */

  flex-wrap: wrap;             /* items wrap onto multiple lines */
  flex-flow: row wrap;         /* shorthand equivalent */
}
```

### Alignment: Main Axis (justify-content)

`justify-content` aligns items along the **main axis** (set by `flex-direction`).

| Value | Description |
|-------|-------------|
| `flex-start` | Pack items at the start (default) |
| `flex-end` | Pack items at the end |
| `center` | Center items along the main axis |
| `space-between` | Equal gaps between items; no gap at edges |
| `space-around` | Equal spacing around each item |
| `space-evenly` | Equal spacing between items and edges |

```css
.container {
  justify-content: space-between; /* nav links spread across full width */
  justify-content: center;        /* centered button group */
}
```

### Alignment: Cross Axis (align-items & align-content)

| Property | Values | Default | Description |
|----------|--------|---------|-------------|
| `align-items` | `stretch` \| `flex-start` \| `flex-end` \| `center` \| `baseline` | `stretch` | Aligns items along the **cross axis** for a single line |
| `align-content` | `stretch` \| `flex-start` \| `flex-end` \| `center` \| `space-between` \| `space-around` \| `space-evenly` | `stretch` | Aligns **multiple lines** of items (only applies when `flex-wrap: wrap`) |

```css
.container {
  align-items: center;          /* vertically center items in a row */
  align-items: flex-start;      /* align to top of cross axis */

  /* Multi-line layout */
  flex-wrap: wrap;
  align-content: space-between; /* distribute rows with space between */
}
```

### Gap

| Property | Description |
|----------|-------------|
| `gap: <value>` | Space between flex items (row and column) |
| `row-gap: <value>` | Space between rows (wrapped layouts) |
| `column-gap: <value>` | Space between columns |

```css
.container {
  gap: 16px;            /* 16px between all items */
  gap: 16px 24px;       /* 16px row gap, 24px column gap */
}
```

## Flex Item Properties

These properties are applied to the **children** of a flex container.

### Sizing: flex-grow, flex-shrink, flex-basis

| Property | Default | Description |
|----------|---------|-------------|
| `flex-grow` | `0` | How much an item grows relative to siblings when space is available |
| `flex-shrink` | `1` | How much an item shrinks relative to siblings when space is tight |
| `flex-basis` | `auto` | The initial main-size of the item before growing/shrinking |
| `flex` | `0 1 auto` | Shorthand for `flex-grow flex-shrink flex-basis` |

```css
/* Common flex shorthand patterns */
.item { flex: 1; }       /* flex: 1 1 0% — grow equally, shrink equally */
.item { flex: auto; }    /* flex: 1 1 auto — grow and shrink from natural size */
.item { flex: none; }    /* flex: 0 0 auto — don't grow or shrink */

/* Three-column equal layout */
.col { flex: 1; }

/* Sidebar + main content */
.sidebar { flex: 0 0 250px; }  /* fixed 250px, never flex */
.main    { flex: 1; }          /* takes remaining space */
```

### Individual Alignment (align-self)

`align-self` overrides `align-items` for a single item.

| Value | Description |
|-------|-------------|
| `auto` | Inherit from `align-items` (default) |
| `flex-start` | Align to start of cross axis |
| `flex-end` | Align to end of cross axis |
| `center` | Center on cross axis |
| `stretch` | Stretch to fill cross axis |
| `baseline` | Align to text baseline |

```css
.container {
  align-items: flex-start; /* all items top-aligned */
}

.special-item {
  align-self: center; /* this item centered, overrides parent */
}
```

### Order

```css
.item { order: 0; }   /* default — source order */
.item { order: -1; }  /* move item before all order:0 siblings */
.item { order: 1; }   /* move item after all order:0 siblings */
```

`order` only affects visual order; DOM order (and accessibility reading order) is unchanged.

## Common Flexbox Layout Patterns

### Centered Content (horizontal + vertical)

```css
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
```

### Navigation Bar

```css
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

.navbar .logo { flex: 0 0 auto; }
.navbar .nav-links { display: flex; gap: 16px; }
.navbar .cta { margin-left: auto; }
```

### Responsive Card Grid

```css
.cards {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.card {
  flex: 1 1 280px;  /* grow/shrink but minimum 280px wide */
  max-width: 400px;
}
```

### Sticky Footer Layout

```css
body {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1; /* pushes footer to bottom */
}
```

## Quick-Reference Summary

| Need | Property + Value |
|------|-----------------|
| Horizontal center | `justify-content: center` |
| Vertical center | `align-items: center` |
| Full center | both of the above |
| Equal columns | `flex: 1` on each child |
| Fixed sidebar | `flex: 0 0 <width>` on sidebar, `flex: 1` on main |
| Wrap items | `flex-wrap: wrap` |
| Reverse order | `flex-direction: row-reverse` |
| Push one item to end | `margin-left: auto` on that item |
| Space links evenly | `justify-content: space-between` |
| Stack vertically | `flex-direction: column` |

Flexbox handles the vast majority of one-dimensional layout needs. For grid-based two-dimensional layouts, pair this reference with a CSS Grid cheatsheet. Explore the full [DevNook cheatsheets hub](/cheatsheets/) for more quick references, including the [JavaScript Array Methods Cheat Sheet](/cheatsheets/javascript-array-cheatsheet) for front-end development. Check the [guides hub](/guides/) for deeper walkthroughs, and visit [DevNook tools](/tools/) for utilities to speed up your development workflow.
