---
title: "React Multi Select: Dropdowns and Controlled Inputs"
description: "Build a react multi select input with controlled state and live filtering. Covers dropdowns, multi-select, and form integration for React components."
category: "languages"
language: "react"
concept: "select"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [react, select, multi-select, forms, dropdown]
related_posts: []
related_tools: []
linkAnchors:
  - "react multi select"
  - "react select"
  - "multi-select dropdown"
published_date: "2026-07-13"
og_image: "/og/languages/react/select.png"
word_count_target: 2320
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["TechArticle", "FAQPage"],
    "headline": "React Multi Select: Dropdowns and Controlled Inputs",
    "description": "Build a react multi select input with controlled state and live filtering. Covers dropdowns, multi-select, and form integration for React components.",
    "datePublished": "2026-07-13",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/languages/react/select/",
    "mainEntity": [
      {"@type": "Question", "name": "How do I read all selected values from a React multi select?", "acceptedAnswer": {"@type": "Answer", "text": "Use Array.from(e.target.selectedOptions).map(o => o.value) inside your onChange handler. This returns a plain array of selected values you can store in state."}},
      {"@type": "Question", "name": "Can I pre-select options in a React multi select?", "acceptedAnswer": {"@type": "Answer", "text": "Yes — initialize your useState array with the values you want pre-selected. Pass the array as the value prop and React marks matching options as selected on mount."}},
      {"@type": "Question", "name": "When should I use react-select instead of a native select element?", "acceptedAnswer": {"@type": "Answer", "text": "Use react-select for search-as-you-type filtering, async option loading, custom option rendering, or dismissable chip-style selection. For simple dropdowns with a fixed list, the native select multiple is lighter and accessible by default."}}
    ]
  }
  </script>
---

You are building a product filter page and the designer hands you a wireframe: a dropdown where users pick multiple categories, type to search, and deselect individual choices. A native `<select multiple>` almost works — until someone on mobile says the UI is unusable, and a teammate points out there is no clean way to read the full selected state without digging into the DOM. This is where understanding react multi select patterns pays off.

This post covers how React's controlled component model applies to select inputs, how to build a react multi select from scratch, how to add live filtering, when to reach for a library, and three traps that catch developers at every skill level.

## React Multi Select and the Controlled Component Model

React treats all form elements — including `<select>` — through the lens of controlled components. You pass a `value` prop and an `onChange` handler; React owns the displayed selection and updates it only when your handler calls `setState`.

The alternative is an uncontrolled `<select>`, where the DOM manages its own internal state and you read it via a ref. Uncontrolled elements work for simple cases but create friction when you need to read, reset, or validate the selection from outside the element — for example, clearing all chosen items when the user clicks a "Reset filters" button.

For a react multi select specifically, the controlled model is almost always the right choice. You need to know what is selected at any moment: to disable a confirm button until at least one item is chosen, to sync the count shown in a badge, or to validate before submission. The controlled pattern gives you that state as a plain JavaScript array at all times.

The native `<select>` element, documented in full on [MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/select), supports a `multiple` attribute that enables multi-selection. React wraps this behaviour cleanly — you provide the array of selected values, React marks the matching `<option>` elements as selected, and your `onChange` handler updates the array on each interaction.

## A Basic Controlled Select

Start with a single-value dropdown before adding the `multiple` attribute. This makes the controlled model concrete before you layer on complexity.

```jsx
import { useState } from 'react';

const FRUIT_OPTIONS = ['Apple', 'Banana', 'Cherry', 'Durian', 'Elderberry'];

function FruitPicker() {
  const [selected, setSelected] = useState('');

  return (
    <div>
      <label htmlFor="fruit-select">Pick a fruit</label>
      <select
        id="fruit-select"
        value={selected}
        onChange={e => setSelected(e.target.value)}
      >
        <option value="">-- Select --</option>
        {FRUIT_OPTIONS.map(fruit => (
          <option key={fruit} value={fruit}>{fruit}</option>
        ))}
      </select>
      {selected && <p>You picked: {selected}</p>}
    </div>
  );
}
```

The `value` prop ties the displayed selection to React state. The `onChange` handler fires every time the user chooses a different option, and `e.target.value` gives you the string value of the selected `<option>`. The `key` prop on each option matters for the same reason it matters when rendering any list — see [React Lists and Rendering: keys and map()](/languages/react/lists-rendering/) for a full treatment of why stable keys prevent subtle rendering bugs when the option list is dynamic.

## Building a React Multi Select Step by Step

Adding `multiple` to a `<select>` lets users pick more than one option, but `e.target.value` now only gives you the most recently clicked item — not the full selection. You need `Array.from(e.target.selectedOptions)` to extract every chosen option.

**Step 1: Switch state to an array**

```jsx
const [selected, setSelected] = useState([]);
```

**Step 2: Extract all selected options in the change handler**

```jsx
function handleChange(e) {
  const picked = Array.from(e.target.selectedOptions).map(opt => opt.value);
  setSelected(picked);
}
```

`e.target.selectedOptions` is an `HTMLOptionsCollection` — an array-like object containing every `<option>` the user currently has highlighted. `Array.from()` turns it into a real array, and `.map(opt => opt.value)` extracts the string values.

**Step 3: Pass the array as the `value` prop**

React compares the array against each `<option>`'s `value` attribute to decide which ones to mark as selected on render.

```jsx
<select
  id="fruit-select"
  multiple
  value={selected}
  onChange={handleChange}
  size={5}
>
  {FRUIT_OPTIONS.map(fruit => (
    <option key={fruit} value={fruit}>{fruit}</option>
  ))}
</select>
```

The `size` attribute controls how many options are visible without scrolling. Without it, most browsers collapse the multi-select into a dropdown that makes multi-selection harder for users to discover.

**Full working component:**

```jsx
import { useState } from 'react';

const FRUIT_OPTIONS = ['Apple', 'Banana', 'Cherry', 'Durian', 'Elderberry'];

function MultiFruitPicker() {
  const [selected, setSelected] = useState([]);

  function handleChange(e) {
    const picked = Array.from(e.target.selectedOptions).map(opt => opt.value);
    setSelected(picked);
  }

  return (
    <div>
      <label htmlFor="multi-fruit">
        Pick fruits (Ctrl/Cmd + click to select multiple)
      </label>
      <select
        id="multi-fruit"
        multiple
        value={selected}
        onChange={handleChange}
        size={5}
      >
        {FRUIT_OPTIONS.map(fruit => (
          <option key={fruit} value={fruit}>{fruit}</option>
        ))}
      </select>
      <p>Selected: {selected.join(', ') || 'none'}</p>
    </div>
  );
}
```

One real-world limitation of the native multi-select: users need to know about Ctrl/Cmd+click to select multiple items. Most non-technical users do not. Adding a label hint helps, but for consumer-facing products with more than a handful of options, a custom checkbox list or a library like react-select tends to be more intuitive.

## Adding a Search Filter

The native multi-select has no built-in search. For any list longer than six or seven options, a text input that narrows the visible choices dramatically improves usability.

```jsx
import { useState } from 'react';

const COUNTRIES = [
  'Australia', 'Brazil', 'Canada', 'Denmark', 'Egypt',
  'Finland', 'Germany', 'Hungary', 'India', 'Japan',
  'Kenya', 'Latvia', 'Mexico', 'Norway', 'Oman',
];

function FilteredMultiSelect() {
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState([]);

  const visible = COUNTRIES.filter(c =>
    c.toLowerCase().includes(search.toLowerCase())
  );

  function handleChange(e) {
    const picked = Array.from(e.target.selectedOptions).map(o => o.value);
    setSelected(picked);
  }

  return (
    <div>
      <input
        type="text"
        placeholder="Search countries..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        aria-label="Filter countries"
      />
      <select
        multiple
        value={selected}
        onChange={handleChange}
        size={7}
        aria-label="Countries multi-select"
      >
        {visible.map(country => (
          <option key={country} value={country}>{country}</option>
        ))}
      </select>
      <p>Selected: {selected.join(', ') || 'none'}</p>
    </div>
  );
}
```

There is a behaviour decision embedded here: when the search filter removes an option from the visible list, that option remains in `selected` state. On form submit, you get the full set of chosen values including hidden ones. If you want filtering to deselect hidden items instead, add a `useEffect` that reconciles `selected` against `visible` whenever `search` changes:

```jsx
useEffect(() => {
  setSelected(prev => prev.filter(v => visible.includes(v)));
}, [search]);
```

When your options come from an API, format the response as a JSON array like `[{"value": "au", "label": "Australia"}]` before mapping it into `<option>` elements. The [JSON Formatter](/tools/json-formatter/) is handy for inspecting and validating API response payloads during development — paste the raw response to check the structure before writing your mapping code.

## Integrating with React Forms

A controlled `<select multiple>` inside a standard HTML `<form>` submits all selected values correctly when the element carries a `name` attribute. Reading them back after submission uses `FormData.getAll()`:

```jsx
function handleSubmit(e) {
  e.preventDefault();
  const data = new FormData(e.target);
  const chosen = data.getAll('countries'); // returns string[]
  console.log('Submitted:', chosen);
}

// In JSX:
<form onSubmit={handleSubmit}>
  <select name="countries" multiple value={selected} onChange={handleChange}>
    {/* options */}
  </select>
  <button type="submit">Apply filters</button>
</form>
```

For validation, conditional visibility, and multi-step flows, [React Hook Form: Forms and Validation](/languages/react/hook-form/) integrates cleanly with a controlled multi-select. You register the field with `register('countries')`, read its current value with `watch('countries')`, and attach validation rules like `{ validate: v => v.length > 0 || 'Select at least one country' }` without manual event wiring.

## When to Use the react-select Library

The native `<select multiple>` covers straightforward requirements, but it has real limits. The [react-select](https://react-select.com/) library addresses the gaps with:

- **Search-as-you-type** directly inside the dropdown — no separate input required
- **Async option loading** — fetch options from an endpoint as the user types, with built-in loading states
- **Tag-style chips** — selected items appear as dismissable badges above the input, familiar from tools like GitHub's label picker
- **Custom option rendering** — render avatars, descriptions, or grouped sections inside each option row
- **Keyboard navigation and ARIA** — full accessibility support built in, including `aria-activedescendant` and role announcements

```jsx
import Select from 'react-select';
import { useState } from 'react';

const countryOptions = [
  { value: 'au', label: 'Australia' },
  { value: 'br', label: 'Brazil' },
  { value: 'ca', label: 'Canada' },
  { value: 'dk', label: 'Denmark' },
];

function CountryPicker() {
  const [picked, setPicked] = useState([]);

  return (
    <Select
      isMulti
      options={countryOptions}
      value={picked}
      onChange={setPicked}
      placeholder="Select countries..."
      aria-label="Country multi-select"
    />
  );
}
```

`isMulti` enables multi-selection. The `onChange` callback receives the full array of selected option objects — `[{value: 'au', label: 'Australia'}, ...]` — rather than raw strings. Adjust your submit logic to pull `.value` from each entry when you need bare values.

When not to reach for react-select: if the dropdown has fewer than ten options with no search requirement and standard browser styling, the native `<select>` is the right call. It is zero-dependency, accessible by default, and familiar to all browsers. react-select adds roughly 25 KB gzipped to your bundle. For a three-option settings form, that weight is not justified. For a product filter with 200+ searchable options and dismissable chips, it earns its keep.

The controlled component model that makes react-select composable with your application — including how `value`, `onChange`, and props flow between parent and child — is covered in depth in [React Components: JSX, Props, and State](/languages/react/components/).

## Three Pitfalls That Will Trip You Up

### Trap 1: Passing `value` without `onChange`

```jsx
// Broken — React treats this as read-only and warns in the console
<select value={selectedItems} multiple>
  {/* options */}
</select>

// Correct — always pair value with onChange
<select value={selectedItems} multiple onChange={handleChange}>
  {/* options */}
</select>
```

Providing `value` without `onChange` makes React treat the input as read-only. Users can click options but the display never changes. If you genuinely want an uncontrolled select with a one-time starting value, use `defaultValue` instead of `value` — that signals to React that the DOM can manage its own state.

### Trap 2: Using `e.target.value` for multi-select

```jsx
// Broken — returns only the last clicked option as a single string
function handleChange(e) {
  setSelected(e.target.value); // string, not array
}

// Correct — collect all currently selected options
function handleChange(e) {
  const vals = Array.from(e.target.selectedOptions).map(o => o.value);
  setSelected(vals);
}
```

`e.target.value` on a `<select multiple>` gives you a single string — the value of the option that was clicked most recently. `e.target.selectedOptions` gives the full active selection. This is the most common bug in react multi select implementations, and it surfaces as "only one option stays selected no matter what."

### Trap 3: Using array index as the option key

```jsx
// Risky — index keys cause incorrect selection state when options reorder or filter
{options.map((opt, i) => (
  <option key={i} value={opt.value}>{opt.label}</option>
))}

// Correct — use a stable, unique identifier
{options.map(opt => (
  <option key={opt.value} value={opt.value}>{opt.label}</option>
))}
```

When the option list can change — after a search filter or when async results arrive — React uses `key` to match old DOM nodes to new ones. Index keys make React think an option that shifted position is a completely different element, leading to mis-highlighted options and stale labels. Always key by a stable, unique field from your data.

## Frequently Asked Questions

### How do I read all selected values from a React multi select?

Use `Array.from(e.target.selectedOptions).map(o => o.value)` inside your `onChange` handler. `e.target.selectedOptions` is an `HTMLOptionsCollection` containing every option the user currently has highlighted. Converting it with `Array.from` and mapping `.value` gives you a plain string array you can store with `useState`.

### Can I pre-select options in a React multi select?

Yes — initialize the `useState` array with the values you want selected on mount: `useState(['Brazil', 'Canada'])`. React compares the array against each `<option>`'s `value` attribute and marks the matches as selected. The comparison is case-sensitive and exact, so the strings in state must match the `value` attributes precisely.

### How do I reset a React multi select to no selection?

Set state back to an empty array: `setSelected([])`. Because the select is controlled, React immediately re-renders with no options highlighted. Avoid relying on a native `<input type="reset">` — that resets the DOM value but not your React state, leaving the component in an inconsistent state until the next interaction.

### Should I use react-select or the native select for multi-select?

Use the native `<select multiple>` when requirements are simple: a fixed list, no search, default browser styling. Use react-select when you need search-as-you-type, async option loading, dismissable chip UI, or custom option rendering. The native select is zero-dependency and keyboard-accessible by default; react-select adds bundle weight but saves significant work for complex selection UIs.

## Conclusion

React multi select inputs follow the same controlled component pattern as every other form element in React — state lives in `useState`, the `value` prop reflects that state, and `onChange` updates it. The practical difference from a single select is using `Array.from(e.target.selectedOptions)` to extract the full set of chosen values rather than reading `e.target.value`.

From there, search filtering is a matter of deriving a `visible` array from your full option list and deciding whether filtering should also deselect hidden items. For advanced use cases — async data, dismissable tags, custom option layouts — react-select handles those patterns cleanly without requiring you to build them from scratch.

To deepen your understanding of how React components wire together via props and state, read [React Components: JSX, Props, and State](/languages/react/components/) — the pillar for the React section on DevNook. For adding validation, required-field checks, and submission handling to your react multi select, [React Hook Form: Forms and Validation](/languages/react/hook-form/) covers the full integration without manual event wiring.
