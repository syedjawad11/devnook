---
category: blog
content_type: editorial
description: 'CSS Flexbox vs Grid explained: learn the key differences, use cases,
  and when to choose each layout method with practical examples.'
og_image: /og/blog/css-flexbox-vs-grid.png
published_date: '2026-04-20'
related_posts:
- /guides/css-minification-performance-optimization
- /guides/http-status-codes-guide
- /guides/url-encoding-query-parameters-guide
related_tools:
- /tools/html-formatter
tags:
- css
- flexbox
- css-grid
- layout
- web-design
template_id: blog-v1
title: 'CSS Flexbox vs Grid: When to Use Each'
word_count_target: 1500
---

CSS Flexbox and Grid are both layout systems built into modern browsers, but they solve different problems. Flexbox is a one-dimensional layout model — it handles a row or a column. Grid is two-dimensional — it handles rows and columns simultaneously. Choosing the right one isn't always obvious, so here's a direct comparison with real code.

## The Core Difference

Flexbox lays out items along a single axis — either a row (left-to-right) or a column (top-to-bottom). The items can wrap onto new lines, but Flexbox doesn't control alignment between rows.

Grid places items in a defined two-dimensional space. Rows and columns are explicit, and items can span multiple tracks.

A useful mental model: **Flexbox works from the content outward** — you set rules on a container and the items find their own space. **Grid works from the layout inward** — you define the structure first, then place content into it.

## Flexbox: What It Does Well

### Navigation Bars and Toolbars

Flexbox excels at distributing a set of items along a single axis with space control:

```css
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
}

.navbar .logo {
  flex-shrink: 0; /* logo never shrinks */
}

.navbar .nav-links {
  display: flex;
  gap: 24px;
  list-style: none;
}
```

`justify-content: space-between` pushes the logo to the left and the nav links to the right. `align-items: center` vertically centers both. This is exactly what Flexbox is designed for.

### Card Rows with Dynamic Width

When you have a row of cards that should fill available space equally:

```css
.card-row {
  display: flex;
  gap: 16px;
}

.card {
  flex: 1;          /* each card grows equally to fill space */
  min-width: 200px; /* prevents cards from shrinking too far */
}
```

Flexbox handles this cleanly because you're controlling one axis — the horizontal distribution.

### Centering a Single Item

Centering was notoriously difficult in CSS before Flexbox. Now it's two lines:

```css
.container {
  display: flex;
  justify-content: center;
  align-items: center;
}
```

This works for centering modals, hero sections, and loading spinners.

### Flex Properties Reference

| Property | Applied To | Effect |
|----------|-----------|--------|
| `justify-content` | Container | Distributes items along main axis |
| `align-items` | Container | Aligns items along cross axis |
| `flex-wrap` | Container | Allows items to wrap to new lines |
| `flex-grow` | Item | How much an item grows relative to siblings |
| `flex-shrink` | Item | How much an item shrinks when space is tight |
| `flex-basis` | Item | Starting size before grow/shrink applies |
| `order` | Item | Override visual order (doesn't change DOM order) |
| `align-self` | Item | Override cross-axis alignment for one item |

## Grid: What It Does Well

### Page-Level Layout

Grid's two-dimensional control makes it the right tool for overall page structure:

```css
.page {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: 64px 1fr auto;
  grid-template-areas:
    "sidebar header"
    "sidebar main"
    "sidebar footer";
  min-height: 100vh;
}

.sidebar { grid-area: sidebar; }
.header  { grid-area: header; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }
```

The sidebar is 240px fixed; the right column fills remaining space (`1fr`). The header, main content, and footer stack vertically in the right column. This layout requires both row and column control simultaneously — Grid handles it directly; Flexbox would require nested containers.

### Responsive Image Galleries

Grid's `auto-fill` and `minmax()` create responsive grids without media queries:

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}
```

This creates as many columns as fit at minimum 200px width. On a 1200px container that's 6 columns; on 600px it's 3 columns. No [JavaScript](/languages/javascript), no media queries.

### Overlapping Layers

Grid allows multiple items to occupy the same cells, enabling layered designs:

```css
.hero {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 480px;
}

.hero-image,
.hero-text {
  grid-column: 1;
  grid-row: 1; /* both items in the same cell */
}

.hero-text {
  z-index: 1;
  place-self: center;
}
```

This overlays text on an image without absolute positioning. The items stay in normal flow, which plays better with responsive design.

### Dashboard Layouts with Mixed Sizes

```css
.dashboard {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
}

.widget-wide { grid-column: span 8; }
.widget-narrow { grid-column: span 4; }
.widget-full { grid-column: 1 / -1; } /* spans all 12 columns */
```

A 12-column grid lets components claim different widths. Flexbox achieves similar results, but explicit column spans in Grid are more predictable when you need specific proportions.

## When to Use Flexbox vs Grid: Decision Guide

```
Is the layout one-dimensional (a row OR a column)?
  → Yes: Flexbox

Is the layout two-dimensional (rows AND columns)?
  → Yes: Grid

Are you centering content inside a container?
  → Flexbox (2 lines: justify-content + align-items)

Do you need items to span across rows or columns?
  → Grid

Is the item count unknown or dynamic?
  → Flexbox (items flow naturally; Grid needs defined tracks)

Is the layout structure page-level (header/sidebar/main)?
  → Grid

Are you building a component (button group, card row, nav)?
  → Flexbox
```

## They Work Together

Flexbox and Grid are not competing tools. The same page typically uses both:

```css
/* Grid handles the page skeleton */
.page {
  display: grid;
  grid-template-columns: 240px 1fr;
  grid-template-rows: 64px 1fr;
}

/* Flexbox handles the navbar inside the header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Grid handles the card grid inside main */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

/* Flexbox handles layout inside each card */
.card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
```

The page skeleton uses Grid; each component within it uses Flexbox. This is the standard pattern in modern CSS codebases.

## Browser Support

Both Flexbox and Grid have excellent browser support — over 97% global coverage for Flexbox and 96%+ for Grid as of 2025. Subgrid (which lets nested grids inherit parent track sizes) reached broad support in late 2023.

The only Grid feature with limited support is `masonry` layout, which is still in the experimental stage and not production-ready.

## Common Mistakes

**Using Flexbox for a 2D grid**: developers often nest flex containers to simulate a grid. This works but requires more markup and loses the alignment guarantees that Grid provides across rows.

**Using Grid for simple horizontal centering**: Grid works here, but Flexbox's `justify-content: center; align-items: center` is shorter and more semantic for this use case.

**Forgetting gap**: both Flexbox and Grid support `gap` (formerly `grid-gap`). Using `margin` on items instead of `gap` on the container creates edge cases at the start and end of rows.

**Not using `fr` units in Grid**: `fr` (fractional unit) is the key to responsive grids. `grid-template-columns: repeat(3, 1fr)` creates three equal columns that scale with the container. Hard-coding pixel values kills the responsiveness.

For keeping your CSS clean and performant after building your layout, see the [CSS Minification guide](/guides/css-minification-performance-optimization). To check and clean your markup, use the [HTML Formatter tool](/tools/html-formatter).

## Responsive Design Patterns

Both Flexbox and Grid handle responsive layouts, but with different approaches.

### Flexbox: Wrap-Based Responsiveness

Flexbox wraps items naturally when space runs out, making it well-suited for components where you don't need to control exact column counts:

```css
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  flex: 0 1 auto; /* don't grow, can shrink, size from content */
  padding: 4px 12px;
  border-radius: 9999px;
}
```

Tags flow into as many rows as needed without any media queries.

### Grid: Controlled Breakpoints

Grid gives you explicit control at each breakpoint:

```css
.article-grid {
  display: grid;
  grid-template-columns: 1fr;   /* mobile: single column */
  gap: 24px;
}

@media (min-width: 640px) {
  .article-grid {
    grid-template-columns: repeat(2, 1fr);  /* tablet: 2 columns */
  }
}

@media (min-width: 1024px) {
  .article-grid {
    grid-template-columns: repeat(3, 1fr);  /* desktop: 3 columns */
  }
}
```

The `repeat(auto-fill, minmax())` pattern shown earlier eliminates media queries entirely for uniform grids:

```css
.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}
```

## Accessibility Considerations

Both layout models affect how content is perceived and navigated by assistive technologies.

**Visual vs DOM order**: CSS Grid (and Flexbox `order`) can place items visually in a different order than the DOM. Screen readers follow DOM order, not visual order. If you use `grid-column`/`grid-row` placement or `order` to reorder items visually, verify that the DOM order makes logical sense when read linearly.

**Focus order**: Keyboard navigation follows DOM order. Reordering items visually with Grid placement can create a confusing tab order for keyboard users. The CSS Working Group recommends keeping DOM order and visual order aligned whenever possible.

## Subgrid

CSS Subgrid (now supported in all major browsers) allows nested grid elements to participate in the parent grid's track definitions. This solves the long-standing problem of aligning content inside cards to each other across a grid:

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.card {
  display: grid;
  grid-row: span 3;
  grid-template-rows: subgrid; /* inherits parent row tracks */
}

/* Now card title, body, and footer align across all cards in the row */
.card-title  { grid-row: 1; }
.card-body   { grid-row: 2; }
.card-footer { grid-row: 3; }
```

Without subgrid, achieving cross-card alignment required JavaScript to equalize heights. Subgrid makes it a pure CSS solution.

## Summary

- Use **Flexbox** for one-dimensional layouts: navbars, button groups, card rows, centering
- Use **Grid** for two-dimensional layouts: page skeletons, galleries, dashboards, overlapping layers
- Use **both together** — Grid for macro layout, Flexbox for micro components
- Neither is universally better; the right choice depends on whether you need one axis or two

For a complete look at encoding URLs in your CSS (background images, `url()` values), see the [URL Encoding guide](/guides/url-encoding-query-parameters-guide).