---
title: "Collapsible HTML Tags, Attributes and Elements Reference"
description: "Collapsible HTML with <details> and <summary> explained, plus a reference for essential HTML tags, attributes, and semantic elements every developer needs."
category: guides
content_type: editorial
template_id: guide-v2
tags: [html, html-tags, html-attributes, collapsible-html, semantic-html]
related_posts: []
related_tools: []
published_date: "2026-06-10"
og_image: "/og/guides/html-reference-guide.png"
word_count_target: 2500
actual_word_count: 3324
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["Article", "FAQPage"],
    "headline": "Collapsible HTML Tags, Attributes and Elements Reference",
    "description": "Collapsible HTML with <details> and <summary> explained, plus a reference for essential HTML tags, attributes, and semantic elements every developer needs.",
    "datePublished": "2026-06-10",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/guides/html-reference-guide/",
    "mainEntity": [
      {"@type": "Question", "name": "What is collapsible HTML and how do I create it?", "acceptedAnswer": {"@type": "Answer", "text": "Collapsible HTML uses the <details> element as the container and <summary> as the clickable heading. No JavaScript required — the browser handles the toggle natively."}},
      {"@type": "Question", "name": "What is the difference between <strong> and <b> in HTML?", "acceptedAnswer": {"@type": "Answer", "text": "<strong> signals semantic importance to screen readers. <b> is purely visual bold without implying importance. Use <strong> when the emphasis affects meaning."}},
      {"@type": "Question", "name": "When should I use <article> versus <section> in HTML?", "acceptedAnswer": {"@type": "Answer", "text": "Use <article> for self-contained content that makes sense in isolation. Use <section> for thematically grouped content within a page that requires context from the surrounding page."}}
    ]
  }
  </script>
---

Collapsible HTML sections let you show and hide content without writing any JavaScript — the `<details>` and `<summary>` elements handle that natively in every modern browser. This reference covers collapsible HTML fully, then walks through the tags, attributes, and semantic elements you'll use most when building web pages. Whether you're adding a FAQ accordion, marking up navigation, or putting together a contact form, you'll find the syntax and context you need here.

## Collapsible HTML: The `<details>` and `<summary>` Elements

The `<details>` element creates a disclosure widget: a block of content that starts collapsed and expands when a user clicks it. The `<summary>` element provides the clickable heading. Both are supported across all major browsers without any polyfill or JavaScript dependency.

Here's the minimal working structure:

```html
<details>
  <summary>Show installation instructions</summary>
  <p>Run <code>npm install</code> from your project root directory.</p>
</details>
```

The `<summary>` tag must be the first child of `<details>`. If you omit it, browsers display a default label — usually "Details". Everything after `<summary>` is the collapsible content: it can contain paragraphs, lists, code blocks, images, tables, or even nested `<details>` elements.

### The `open` Attribute

By default the content inside `<details>` is hidden. Add the `open` attribute to start it expanded:

```html
<details open>
  <summary>Prerequisites</summary>
  <ul>
    <li>Node.js 18 or higher</li>
    <li>npm or yarn installed globally</li>
    <li>A code editor</li>
  </ul>
</details>
```

`open` is a boolean attribute — its presence means open, its absence means closed. You can read or set it with JavaScript when you need programmatic control:

```javascript
const disclosureEl = document.querySelector('details#prerequisites');

// Expand it
disclosureEl.open = true;

// Collapse it
disclosureEl.open = false;

// Toggle
disclosureEl.open = !disclosureEl.open;
```

### Listening to State Changes with `toggle`

The `<details>` element fires a `toggle` event whenever its state changes. Use this event to track interactions, trigger animations, or keep multiple collapsible sections in sync:

```javascript
const detailsEl = document.querySelector('details.faq-item');

detailsEl.addEventListener('toggle', () => {
  const state = detailsEl.open ? 'opened' : 'closed';
  analytics.track('faq_disclosure', { state });
});
```

### Styling Collapsible HTML

The browser renders a disclosure triangle (▶) by default. You can hide it and apply your own styles using the `::marker` pseudo-element and an `[open]` attribute selector:

```css
details summary {
  cursor: pointer;
  font-weight: 600;
  padding: 0.5rem 0.75rem;
  background: #f5f5f5;
  border-radius: 4px;
  list-style: none;
}

/* Needed for Chrome and Safari */
details summary::-webkit-details-marker {
  display: none;
}

details[open] summary {
  background: #e8f4fd;
  border-bottom: 1px solid #c8e0f4;
}

details > *:not(summary) {
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-top: none;
  border-radius: 0 0 4px 4px;
}
```

For smooth expand/collapse animation, you can pair this with a CSS transition on `max-height`, though the native `<details>` doesn't support `height: auto` transitions directly — a small JavaScript wrapper handles that case.

Collapsible HTML with `<details>` and `<summary>` fits well for FAQ sections, optional code examples, long inline notes, settings panels, and any place you want optional content to stay out of the way by default. For the MDN full reference on the `<details>` element, see the [MDN `<details>` documentation](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details).

---

## Essential HTML Tags: A Practical Reference

Every HTML page is built from a repeating core of high-frequency tags. The tables below cover the elements you'll write on nearly every project, organized by role.

### Document Structure

| Tag | Purpose | Notes |
|-----|---------|-------|
| `<!DOCTYPE html>` | Declares HTML5 mode | Always the first line of any HTML document |
| `<html lang="en">` | Root element | Always set the `lang` attribute |
| `<head>` | Metadata container | Not rendered in the browser viewport |
| `<body>` | Page content | Every visible element goes inside here |
| `<title>` | Browser tab title | 50–60 characters optimal for search appearance |
| `<meta>` | Metadata — charset, viewport, description | Self-closing; no end tag needed |
| `<link>` | External resource — CSS, fonts, canonical | Self-closing |
| `<script>` | JavaScript | Add `defer` or `async` to avoid blocking rendering |
| `<style>` | Inline CSS | Prefer external stylesheets for maintainability |
| `<base>` | Base URL for relative links | At most one per document |

### Text Content

| Tag | Purpose | Notes |
|-----|---------|-------|
| `<p>` | Paragraph | Block element; use CSS margins for spacing |
| `<h1>`–`<h6>` | Headings | One `<h1>` per page; never skip levels |
| `<span>` | Inline container | No semantic meaning; useful for styling hooks |
| `<div>` | Block container | No semantic meaning; used for layout grouping |
| `<br>` | Line break | For intentional breaks in prose, not spacing |
| `<hr>` | Thematic break | Visual separator between distinct topics |
| `<pre>` | Preformatted text | Preserves whitespace and line breaks as typed |
| `<code>` | Inline code | Pair with `<pre>` for multi-line code blocks |
| `<strong>` | Bold + semantic importance | Screen readers may signal importance |
| `<em>` | Italic + semantic emphasis | Signals stress emphasis affecting meaning |
| `<blockquote>` | Extended quotation | Add `cite` attribute with the source URL |
| `<abbr>` | Abbreviation | Use `title` for the expanded form |
| `<kbd>` | Keyboard input | Renders key-like styling by default |
| `<del>` / `<ins>` | Deleted / inserted text | Useful in changelogs and edit tracking |
| `<sub>` / `<sup>` | Subscript / superscript | For chemical formulas and footnote references |

### Lists

| Tag | Purpose | Notes |
|-----|---------|-------|
| `<ul>` | Unordered list | Bullet points; use `list-style-type` to change style |
| `<ol>` | Ordered list | Numbers by default; `type` changes to letters or roman numerals |
| `<li>` | List item | Used inside `<ul>` or `<ol>` only |
| `<dl>` | Description list | For term–definition pairs and metadata tables |
| `<dt>` | Description term | Always a child of `<dl>` |
| `<dd>` | Description details | Always a child of `<dl>`, follows `<dt>` |

### Links and Media

| Tag | Purpose | Notes |
|-----|---------|-------|
| `<a>` | Hyperlink | `href`, `target="_blank"`, `rel` |
| `<img>` | Image | Self-closing; `alt` required; use `loading="lazy"` below the fold |
| `<video>` | Video player | Wrap `<source>` children for multiple formats |
| `<audio>` | Audio player | Same `<source>` pattern as `<video>` |
| `<picture>` | Responsive images | Wraps `<source>` elements + fallback `<img>` |
| `<figure>` | Media with optional caption | Pair with `<figcaption>` |
| `<figcaption>` | Caption for a `<figure>` | Can precede or follow the media element |
| `<canvas>` | 2D drawing surface | Requires JavaScript to draw |
| `<svg>` | Inline vector graphic | Scales without quality loss at any size |
| `<iframe>` | Embedded page | Use `sandbox` attribute for untrusted content |

For the full elements reference with browser compatibility data, the [MDN HTML elements reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Element) covers every tag in the specification.

---

## HTML Attributes Reference

Attributes modify element behavior and provide machine-readable context. Global attributes apply to every HTML element. Per-element attributes only work on specific tags.

### Global Attributes

| Attribute | Value | Description |
|-----------|-------|-------------|
| `id` | Unique string | CSS target, JavaScript handle, anchor fragment |
| `class` | Space-separated list | CSS and JavaScript targeting |
| `style` | CSS declarations | Inline styles; prefer external CSS for maintainability |
| `lang` | BCP 47 language tag | `en`, `fr`, `zh-Hant`; overrides the document language |
| `dir` | `ltr` or `rtl` | Text flow direction |
| `title` | String | Tooltip text shown on hover |
| `hidden` | Boolean | Hides element from rendering; keeps it in the DOM |
| `tabindex` | Integer | Keyboard focus order; `-1` removes from tab sequence |
| `data-*` | Custom string | Custom data attached directly to elements |
| `aria-*` | ARIA value | Accessibility state and properties |
| `role` | ARIA role | Semantic role for screen readers |
| `contenteditable` | `true` or `false` | Makes element editable in place |
| `draggable` | `true` or `false` | Enables HTML5 drag-and-drop on this element |
| `autofocus` | Boolean | Focus this element on page load (one per page) |
| `translate` | `yes` or `no` | Whether translation services should translate the text |

### Link Attributes Worth Knowing

The `<a>` element's `rel` attribute controls how browsers and search engines treat the link. Two values matter most in practice:

```html
<!-- Opens in a new tab and prevents tabnapping -->
<a
  href="https://developer.mozilla.org/en-US/docs/Web/HTML/Element"
  target="_blank"
  rel="noopener noreferrer">
  MDN HTML elements reference
</a>
```

`rel="noopener"` prevents the opened page from accessing `window.opener`, blocking a class of phishing attack. `rel="noreferrer"` also suppresses the `Referer` header. Always add both when using `target="_blank"`.

For images, `alt` is required on every `<img>` element. An empty `alt=""` tells screen readers to skip the image — use it for decorative images only. Omitting `alt` entirely causes screen readers to announce the filename:

```html
<!-- Informative image: describe what it shows -->
<img
  src="/screenshots/collapsible-section-open.png"
  alt="HTML details element expanded, showing a nested unordered list"
  width="720"
  height="400"
  loading="lazy">

<!-- Decorative image: empty alt skips it in screen readers -->
<img src="/ui/decorative-wave.svg" alt="" role="presentation">
```

The `loading="lazy"` attribute defers loading until the image nears the viewport — a free performance improvement for images below the fold. This complements techniques in our [HTML minification and compression guide](/guides/html-minification-compression-guide), which covers reducing HTML file size before delivery.

---

## Semantic HTML: Structuring Pages With Meaning

Semantic elements describe the role of their content, not just how it looks. Screen readers, search crawlers, and browser reading modes all use these signals to understand page structure — without parsing CSS class names.

Here are the landmark and content-sectioning elements and when to reach for each:

| Element | Use when... | Don't use when... |
|---------|-------------|-------------------|
| `<header>` | Introducing a page or section — site logo, main nav, hero | Wrapping all page content |
| `<nav>` | A set of navigation links | Every group of links; use it for primary and secondary nav only |
| `<main>` | The primary, unique content area | There's more than one per page |
| `<article>` | Self-contained content that makes sense standalone — post, news item, comment | Content that requires surrounding context |
| `<section>` | Thematically grouped content that needs a heading | Content with no clear thematic grouping (use `<div>`) |
| `<aside>` | Content tangentially related to main content — sidebar, callout, related links | Primary content of the page |
| `<footer>` | Closing content for the page or its ancestor section | Just any bottom-aligned div |
| `<time>` | A date, time, or duration | Other text that happens to mention time loosely |
| `<address>` | Contact information for the nearest `<article>` or page author | Physical addresses unrelated to the document author |
| `<mark>` | Highlighted text, typically search result matches | Generic emphasis (use `<em>` or `<strong>`) |
| `<dialog>` | A dialog box or modal | Content that should always be visible |
| `<details>` | Collapsible disclosure content | Content that should always be visible |

A well-structured article page using these together:

```html
<body>
  <header>
    <nav aria-label="Site navigation">
      <a href="/">DevNook</a>
      <a href="/guides/">Guides</a>
      <a href="/cheatsheets/">Cheatsheets</a>
    </nav>
  </header>

  <main>
    <article>
      <header>
        <h1>Getting Started with Collapsible HTML</h1>
        <time datetime="2026-06-10">June 10, 2026</time>
      </header>

      <section>
        <h2>The &lt;details&gt; Element</h2>
        <p>Use <code>&lt;details&gt;</code> to create expand-on-click sections without JavaScript.</p>

        <details>
          <summary>See a complete working example</summary>
          <pre><code class="language-html">&lt;details&gt;
  &lt;summary&gt;Advanced options&lt;/summary&gt;
  &lt;p&gt;Configure timeout, retries, and proxy settings here.&lt;/p&gt;
&lt;/details&gt;</code></pre>
        </details>
      </section>

      <aside>
        <p>Working on layout? The
          <a href="/blog/css-flexbox-vs-grid">CSS Flexbox vs. Grid comparison</a>
          explains which model to reach for.
        </p>
      </aside>
    </article>
  </main>

  <footer>
    <p>&copy; 2026 DevNook</p>
  </footer>
</body>
```

The rule of thumb: use the semantic element when the role matters to accessibility or SEO; use `<div>` or `<span>` when you only need a layout or styling hook.

---

## HTML Forms: Input Types and Validation Attributes

Forms collect user input. The `<form>` element's `action` and `method` attributes control the submission target and HTTP method. Pairing form elements with correct `<label>` associations keeps forms accessible and usable.

```html
<form action="/contact" method="post">
  <label for="visitor-name">Name</label>
  <input
    type="text"
    id="visitor-name"
    name="visitor_name"
    required
    minlength="2"
    maxlength="80"
    autocomplete="name">

  <label for="visitor-email">Email address</label>
  <input
    type="email"
    id="visitor-email"
    name="visitor_email"
    required
    autocomplete="email">

  <label for="visitor-message">Message</label>
  <textarea
    id="visitor-message"
    name="message"
    rows="5"
    minlength="20"
    maxlength="2000">
  </textarea>

  <button type="submit">Send message</button>
</form>
```

### Input Types Reference

HTML5 input types activate browser-native validation and contextual mobile keyboards automatically:

| `type` value | Purpose | Key attributes |
|--------------|---------|----------------|
| `text` | General single-line text | Default when type is unspecified |
| `email` | Email address | Validates format; mobile keyboard shows `@` key |
| `password` | Masked input | Browser may offer to save and autofill |
| `number` | Numeric input | `min`, `max`, `step` |
| `tel` | Telephone number | Mobile shows dial pad; no format validation |
| `url` | URL | Validates that it starts with a scheme |
| `date` | Date picker | Returns `YYYY-MM-DD`; native UI varies by OS |
| `time` | Time picker | Returns `HH:MM`; local time, no timezone |
| `datetime-local` | Date and time picker | Local time; no timezone information |
| `range` | Slider control | `min`, `max`, `step`, `value` |
| `checkbox` | Boolean toggle | Use `checked` attribute for default-on state |
| `radio` | Single selection from a group | Same `name` value groups radio inputs together |
| `file` | File upload | `accept` filters by type; `multiple` allows several files |
| `hidden` | Not rendered to user | Submits a fixed value with the form |
| `submit` | Submits the form | Or use `<button type="submit">` for more control |
| `reset` | Resets all fields to defaults | Rarely useful; can frustrate users who click it by mistake |
| `search` | Search field | Browser may add a clear button |
| `color` | Color picker | Returns a lowercase hex string like `#3a7bd5` |
| `month` | Month and year picker | Returns `YYYY-MM` |

### Form Validation Attributes

Native browser validation runs before submission without requiring JavaScript:

| Attribute | Applies to | What it does |
|-----------|-----------|--------------|
| `required` | input, select, textarea | Field must not be empty at submit time |
| `minlength` | text-type inputs, textarea | Minimum character count |
| `maxlength` | text-type inputs, textarea | Maximum character count (hard limit in some browsers) |
| `min` | number, date, range, time | Minimum allowed value |
| `max` | number, date, range, time | Maximum allowed value |
| `step` | number, range, date, time | Valid increment for the value |
| `pattern` | text-type inputs | A regex the value must match fully |
| `novalidate` | `<form>` element | Disables native validation for the entire form |
| `formnovalidate` | submit button | Disables validation for that specific button only |
| `autocomplete` | form, input | `on`, `off`, or a named token like `email` or `new-password` |
| `placeholder` | text-type inputs | Hint text shown when the field is empty |
| `readonly` | input, textarea | Displayed but not editable; still submitted |
| `disabled` | input, select, textarea, button | Not interactive and not included in form submission |

Form validation errors and the HTTP responses they produce are connected — the [HTTP status codes guide](/guides/http-status-codes-guide) covers the `400`, `422`, and `200` response codes you'll encounter when processing form submissions server-side.

---

## Common HTML Mistakes That Break Silently

These mistakes won't crash your page — browsers fix them silently — but they surface as accessibility failures, layout bugs, or SEO penalties.

**Missing `alt` on meaningful images.** Every `<img>` carrying visual information needs a descriptive `alt`. Empty `alt=""` is correct only for decorative images. Omitting the attribute entirely causes screen readers to read out the filename. Write `alt` text that describes the image's purpose, not its appearance: "Chart showing monthly revenue Q1–Q4 2025" beats "revenue chart".

**Using `<br>` for layout spacing.** `<br>` creates a line break within text content — it's correct in addresses and poetry. Using `<br><br>` to add space between elements is a layout concern: handle it with CSS `margin` or `padding`.

**Missing `for`/`id` pairing on labels.** Without this association, screen readers can't tell which label belongs to which field, and clicking the label doesn't focus the input:

```html
<!-- Wrong: label and input are not associated -->
<label>Email</label>
<input type="email" name="email">

<!-- Right: clicking the label focuses the input -->
<label for="contact-email">Email</label>
<input type="email" id="contact-email" name="email">
```

**Scripts in `<head>` without `defer`.** A `<script src="app.js">` in `<head>` blocks HTML parsing until the script downloads and executes. Add `defer` to let HTML continue parsing while the script downloads:

```html
<head>
  <meta charset="UTF-8">
  <title>My App</title>
  <!-- Downloads in parallel; executes after DOM is ready -->
  <script src="app.js" defer></script>
</head>
```

**Using `<table>` for page layout.** Tables are for tabular data — rows and columns with a meaningful relationship. Using them to control visual layout breaks the reading order for screen readers and makes responsive design very difficult. Use CSS Flexbox or Grid instead, as covered in the [CSS Flexbox vs. Grid guide](/blog/css-flexbox-vs-grid).

**Skipping heading levels.** Going from `<h2>` to `<h4>` breaks the document outline used by screen readers to navigate pages. Each level should represent a true hierarchical step in your content structure.

---

## Frequently Asked Questions

### What is collapsible HTML and how do I create it?

Collapsible HTML refers to content that can be shown or hidden by user interaction. The native HTML approach uses the `<details>` element as the container and `<summary>` as the clickable heading. Add a `<details>` block to your page, put a `<summary>` as its first child — that's the visible toggle — then add your collapsible content after the summary tag. No JavaScript or CSS is required for the basic toggle. Add the `open` attribute to `<details>` to start it expanded on page load. The behavior works in all major browsers and degrades gracefully in environments that don't support it by showing all content by default.

### What is the difference between `<strong>` and `<b>` in HTML?

`<strong>` and `<b>` both render bold text visually, but they carry different semantic weight. `<strong>` marks text as important — screen readers may change their intonation to signal it, and it affects how the content is interpreted in contexts like text-to-speech. `<b>` is for stylistic bold that doesn't imply importance: product names, technical terms, or keywords in search results. The same distinction applies between `<em>` (stress emphasis that affects meaning, analogous to how you'd say the word aloud) and `<i>` (offset text like book titles, technical terms, or foreign words).

### When should I use `<article>` versus `<section>` in HTML?

Use `<article>` when the content makes sense on its own — a blog post, a news item, a product card, a user comment. You could syndicate it to an RSS feed or embed it on a different page and it would still be coherent. Use `<section>` for a thematically grouped block within a page that requires surrounding context to make sense. An `<article>` can contain multiple `<section>` elements. A `<section>` should not contain multiple unrelated `<article>` elements. When neither fits cleanly, a `<div>` is appropriate — it adds no incorrect semantics.

### What does `defer` do on a `<script>` tag and when should I use `async`?

`defer` downloads the script in parallel with HTML parsing, then executes it after parsing is complete but before the `DOMContentLoaded` event. Multiple deferred scripts execute in document order. `async` also downloads in parallel, but executes as soon as the download finishes — potentially interrupting HTML parsing and without preserving order. Use `defer` for scripts that interact with the DOM or need to run after other scripts. Use `async` for independent scripts that don't depend on DOM state, like third-party analytics or ad tags. For scripts placed at the end of `<body>`, neither attribute is necessary — the DOM is already parsed by the time they run — though `defer` in `<head>` is generally the better pattern.

### What is the `data-*` attribute in HTML and when should I use it?

`data-*` attributes store custom data on HTML elements without inventing non-standard attributes. Replace the `*` with a lowercase name: `data-product-id`, `data-theme`, `data-section-index`. Values are always strings. JavaScript reads them via `element.dataset.productId` — the attribute name after `data-` converted to camelCase. They're useful for passing server-rendered data to client scripts, marking elements for JavaScript behavior, and storing metadata without adding invisible DOM nodes. They're not suited for large or frequently changing data — a JavaScript variable, a `fetch()` call, or a structured data store handles those cases better.

---

## Conclusion

Collapsible HTML through `<details>` and `<summary>` removes the need for JavaScript toggle logic across a wide range of disclosure patterns — FAQ sections, optional code previews, settings panels. Paired with the semantic structure, attribute patterns, and HTML5 form controls in this reference, you have the core vocabulary for building accessible, well-structured web pages. To reduce the size of your HTML output before deploying, see the [HTML minification and compression guide](/guides/html-minification-compression-guide). For page layout decisions once your markup is solid, the [CSS Flexbox vs. Grid comparison](/blog/css-flexbox-vs-grid) explains which model to reach for.
