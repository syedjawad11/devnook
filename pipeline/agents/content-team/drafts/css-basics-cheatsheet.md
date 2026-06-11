---
title: "CSS Border Cheat Sheet: Selectors and Properties"
description: "CSS border properties, selectors, the box model, colors, flexbox, and pseudo-classes covered in one quick-reference cheat sheet for web developers."
category: cheatsheets
template_id: cheatsheet-v1
tags: [css, css-border, selectors, web-development, css-properties]
related_posts: []
related_tools: []
published_date: "2026-06-11"
og_image: "/og/cheatsheets/css-basics-cheatsheet.png"
downloadable: true
---

CSS border declarations, selectors, and the box model are the building blocks of every stylesheet you write. This cheat sheet gathers the properties you reach for most often — from border syntax and selector patterns to colors, typography, flexbox shorthand, and pseudo-classes — so you can stay in your editor instead of hunting through docs.

## CSS Border Properties

The `border` shorthand combines width, style, and color in a single declaration. Each side can also be targeted individually when you need to override just one edge, and `border-radius` rounds corners without affecting the layout of surrounding elements.

| Property | Values | Example |
|---|---|---|
| `border` | `width style color` | `border: 1px solid #ccc` |
| `border-width` | `px`, `em`, `thin`, `medium`, `thick` | `border-width: 2px` |
| `border-style` | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `none` | `border-style: dashed` |
| `border-color` | Any color value | `border-color: #333` |
| `border-radius` | Length, `%` | `border-radius: 8px` |
| `border-top` | Shorthand for one side | `border-top: 2px dashed red` |
| `border-right` | Shorthand for one side | `border-right: none` |
| `border-bottom` | Shorthand for one side | `border-bottom: 1px solid #e2e8f0` |
| `border-left` | Shorthand for one side | `border-left: 4px solid #3b82f6` |
| `outline` | `width style color` | `outline: 2px solid blue` |
| `box-shadow` | `x y blur spread color` | `box-shadow: 0 2px 4px rgba(0,0,0,.15)` |

```css
/* Card with rounded border */
.card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 24px;
}

/* Accent left border — sidebar callout pattern */
.callout {
  border: none;
  border-left: 4px solid #3b82f6;
  padding-left: 16px;
  background-color: #eff6ff;
}

/* Circle via border-radius */
.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid #6366f1;
}

/* Focus ring — does not shift layout */
button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
```

`outline` differs from `border` in one key way: it does not participate in the box model and never shifts surrounding elements. Use `outline` for focus rings, where visible feedback is needed without layout side effects. Use `border` when the visual boundary should contribute to the element's total size and spacing.

For the full MDN spec on every border sub-property, see the [MDN CSS border reference](https://developer.mozilla.org/en-US/docs/Web/CSS/border).

---

## CSS Selectors Reference

Selectors determine which elements a rule applies to. Element, class, and ID selectors cover the majority of cases; attribute selectors and combinators handle the rest. Specificity — the scoring system CSS uses when two rules conflict — is the most common source of "why isn't this applying?" bugs.

| Selector | Matches | Example |
|---|---|---|
| `element` | Tag by name | `p { }` |
| `.class` | Elements with class | `.card { }` |
| `#id` | Element with ID | `#nav { }` |
| `*` | All elements | `* { box-sizing: border-box }` |
| `A B` | B anywhere inside A | `nav a { }` |
| `A > B` | B direct child of A | `ul > li { }` |
| `A + B` | B immediately after A | `h2 + p { }` |
| `A ~ B` | All B siblings after A | `h2 ~ p { }` |
| `[attr]` | Has attribute | `input[required] { }` |
| `[attr="val"]` | Exact attribute match | `input[type="text"] { }` |
| `[attr^="val"]` | Attribute starts with value | `a[href^="https"] { }` |
| `[attr$="val"]` | Attribute ends with value | `a[href$=".pdf"] { }` |
| `[attr*="val"]` | Attribute contains value | `a[href*="devnook"] { }` |

```css
/* Descendant vs direct child */
.menu a { color: inherit; }       /* any link inside .menu */
.menu > li { list-style: none; }  /* only top-level list items */

/* Attribute selectors */
input[type="email"] {
  border: 1px solid #94a3b8;
  padding: 8px 12px;
}

/* External link indicator */
a[href^="https"]::after {
  content: " ↗";
  font-size: 0.75em;
  opacity: 0.6;
}

/* Any element carrying a tooltip */
[data-tooltip] {
  position: relative;
  cursor: help;
  text-decoration: underline dotted;
}
```

Specificity scores: inline styles (1-0-0-0) > ID (0-1-0-0) > class, attribute, pseudo-class (0-0-1-0) > element, pseudo-element (0-0-0-1). When a rule isn't applying, compare the specificity scores of both competing selectors — the higher score wins regardless of source order.

---

## Box Model: Spacing and Sizing

Every element in CSS occupies a rectangular box. The box model defines four layers: content, padding, border, and margin. Setting `box-sizing: border-box` globally makes `width` and `height` include padding and border — the behavior most developers expect and the reason every modern reset starts with it.

| Property | Values | Notes |
|---|---|---|
| `box-sizing` | `content-box`, `border-box` | Use `border-box` globally |
| `margin` | Length, `auto`, `%`, `0` | Shorthand: top right bottom left |
| `padding` | Length, `%`, `0` | Same shorthand order as margin |
| `width` | Length, `%`, `auto`, `min-content`, `max-content`, `fit-content` | |
| `height` | Length, `%`, `auto`, `min-content` | |
| `max-width` | Length, `%`, `none` | Common: `1200px` or `90rem` for page wrapper |
| `min-height` | Length, `%`, `0` | |
| `overflow` | `visible`, `hidden`, `scroll`, `auto`, `clip` | |
| `display` | `block`, `inline`, `inline-block`, `flex`, `grid`, `none` | |
| `position` | `static`, `relative`, `absolute`, `fixed`, `sticky` | |
| `z-index` | Integer, `auto` | Only applies to positioned elements |

```css
/* Global reset — include in every project */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Centered page wrapper */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Shorthand: top | right | bottom | left */
.section {
  padding: 48px 24px;    /* 48px top/bottom, 24px left/right */
  margin-bottom: 32px;
}

/* Sticky header */
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}
```

`margin: 0 auto` on a block element with a defined `width` horizontally centers it — this pattern appears on almost every layout wrapper. Vertical centering with `auto` does not work the same way; reach for flexbox `align-items: center` or grid `place-items: center` instead.

---

## Colors, Backgrounds and Typography

CSS accepts five color formats: hex, `rgb()`, `rgba()`, `hsl()`, and named keywords. For design-system work, `hsl()` makes it straightforward to derive tints and shades from a base hue. For overlays and transparency, `rgba()` is the standard choice.

| Property | Values | Notes |
|---|---|---|
| `color` | Hex, rgb, hsl, keyword | Text and foreground color |
| `background-color` | Any color value | Fill color only |
| `background` | Color, image, gradient | Shorthand — covers all background sub-properties |
| `opacity` | `0`–`1` | Affects entire element and its children |
| `font-family` | Font name or stack | Always include a generic fallback |
| `font-size` | `rem`, `em`, `px`, `%`, `vw` | Prefer `rem` for accessibility |
| `font-weight` | `100`–`900`, `bold`, `normal` | |
| `font-style` | `normal`, `italic`, `oblique` | |
| `line-height` | Unitless number, length | `1.5`–`1.7` for readable body copy |
| `letter-spacing` | Length, `normal` | Can be negative for tight headings |
| `text-align` | `left`, `center`, `right`, `justify` | |
| `text-decoration` | `none`, `underline`, `line-through` | |
| `text-transform` | `uppercase`, `lowercase`, `capitalize`, `none` | |
| `white-space` | `normal`, `nowrap`, `pre`, `pre-wrap` | Use `nowrap` for truncation patterns |

```css
:root {
  font-size: 16px;
}

.heading-lg {
  font-size: 2rem;           /* 32px relative to root */
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.025em;
  color: #1a202c;
}

.body-text {
  font-size: 1rem;
  line-height: 1.7;
  color: #4a5568;
}

/* Gradient background */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

/* Semi-transparent overlay */
.overlay {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}
```

Use `rem` units for `font-size` — it respects user browser zoom preferences and accessibility settings. `em` works better for padding and margin on components where spacing should scale proportionally with the local font size, such as button padding.

---

## Flexbox Layout Quick Reference

Flexbox handles one-dimensional layouts — rows or columns. It is the standard tool for navigation bars, card rows, and any pattern that distributes items along a single axis. For a complete property-by-property reference, see the [CSS Flexbox cheatsheet](/cheatsheets/css-flexbox-cheatsheet).

| Property | Values | Notes |
|---|---|---|
| `display: flex` | — | Creates flex container |
| `flex-direction` | `row`, `column`, `row-reverse`, `column-reverse` | Default is `row` |
| `justify-content` | `flex-start`, `flex-end`, `center`, `space-between`, `space-around`, `space-evenly` | Main axis distribution |
| `align-items` | `stretch`, `flex-start`, `flex-end`, `center`, `baseline` | Cross axis alignment |
| `flex-wrap` | `nowrap`, `wrap`, `wrap-reverse` | Default is `nowrap` |
| `gap` | Length | Space between items — replaces old margin hacks |
| `flex-grow` | Number | How much the item grows to fill remaining space |
| `flex-shrink` | Number | How much the item shrinks when space is tight |
| `flex-basis` | Length, `auto`, `content` | Starting size before grow/shrink calculation |
| `flex` | `grow shrink basis` | Shorthand — `flex: 1` equals `1 1 0%` |
| `align-self` | Same as `align-items` | Per-item override of container alignment |
| `order` | Integer | Visual reorder without changing DOM (default 0) |

```css
/* Horizontal navigation bar */
.nav-list {
  display: flex;
  align-items: center;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}

/* Responsive card row that wraps */
.card-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.card-grid > .card {
  flex: 1 1 300px;  /* grow, shrink, minimum width 300px */
}

/* Full-viewport hero with centered content */
.hero-content {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 16px;
  min-height: 100vh;
}
```

Flexbox is one-dimensional — it handles a row or a column at a time. When a layout needs to span rows and columns simultaneously, CSS Grid is the better fit. For a side-by-side breakdown of when each layout model makes sense, the [CSS flexbox vs grid comparison](/blog/css-flexbox-vs-grid) covers the decision points clearly.

---

## Pseudo-classes and Pseudo-elements

Pseudo-classes target elements based on state or position in the DOM tree. Pseudo-elements style a specific part of an element or inject generated content. The distinction matters: pseudo-classes use a single colon (`:hover`), pseudo-elements use a double colon (`::before`).

| Selector | Matches | Common Use |
|---|---|---|
| `:hover` | Mouse over element | Link colors, button lift effects |
| `:focus` | Element has focus | Focus rings |
| `:focus-visible` | Focus from keyboard only | Accessible ring without mouse hover |
| `:active` | Being clicked right now | Button press state |
| `:visited` | Previously clicked link | Link history differentiation |
| `:disabled` | Disabled form control | Dimmed input fields |
| `:checked` | Checked checkbox or radio | Custom toggle component styles |
| `:first-child` | First sibling in parent | List start, remove top margin |
| `:last-child` | Last sibling in parent | Remove last border or margin |
| `:nth-child(n)` | Nth sibling | Zebra-striped table rows |
| `:nth-child(even)` | Even siblings | Alternating row backgrounds |
| `:not(selector)` | Elements NOT matching selector | Exclude specific items |
| `:empty` | No children or text content | Hide empty containers |
| `::before` | Generated content before element | Badges, quote marks, icons |
| `::after` | Generated content after element | Clearfix hack, closing punctuation |
| `::placeholder` | Input placeholder text | Placeholder color and style |
| `::selection` | User-selected text | Custom highlight color |
| `::first-line` | First rendered line of block text | Drop caps, special callouts |

```css
/* Keyboard-only focus ring */
button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Zebra-striped table */
tbody tr:nth-child(even) {
  background-color: #f8fafc;
}

/* Remove last item's bottom border */
.list-item:last-child {
  border-bottom: none;
}

/* Opening quote mark via pseudo-element */
blockquote::before {
  content: '\201C';    /* Unicode left double quotation mark */
  font-size: 3rem;
  line-height: 0;
  vertical-align: -0.4em;
  color: #94a3b8;
}

/* Style sibling label when checkbox is checked */
input[type="checkbox"]:checked + label {
  font-weight: 600;
  color: #3b82f6;
  text-decoration: line-through;
}
```

`:focus-visible` is the modern answer to the old `:focus { outline: none }` anti-pattern. It keeps the focus ring for keyboard navigation while suppressing it for mouse clicks — the behavior most products need without the accessibility regression. Browser support is broad enough to use today without a fallback.

---

## Conclusion

CSS border properties, selectors, and layout rules appear in every project — a single-page reference like this one removes the friction of constant lookups. Once your stylesheet is working, the [CSS minification and performance guide](/guides/css-minification-performance-optimization) covers how to reduce delivery time without changing any visual behavior. For the full property list including browser compatibility tables, the [MDN CSS Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference) remains the most reliable source for edge-case syntax and spec-accurate definitions.
