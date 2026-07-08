---
title: "Building React UI Components: JSX, Props, and State"
description: "Master React UI components: learn JSX syntax, props, and state with practical examples for building reusable and composable React applications."
category: "languages"
language: "react"
concept: "components"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [react, components, jsx, props, state]
related_posts: []
related_tools: []
linkAnchors:
  - "react ui components"
  - "react components"
  - "jsx components"
published_date: "2026-07-08"
og_image: "/og/languages/react/components.png"
word_count_target: 2079
schema_org: "<script type=\"application/ld+json\">\n{\"@context\":\"https://schema.org\",\"@type\":[\"TechArticle\",\"FAQPage\"],\"headline\":\"Building React UI Components: JSX, Props, and State\",\"description\":\"Master React UI components: learn JSX syntax, props, and state with practical examples for building reusable and composable React applications.\",\"datePublished\":\"2026-07-08\",\"author\":{\"@type\":\"Organization\",\"name\":\"DevNook\"},\"publisher\":{\"@type\":\"Organization\",\"name\":\"DevNook\",\"url\":\"https://devnook.dev\"},\"url\":\"https://devnook.dev/languages/react/components/\",\"mainEntity\":[{\"@type\":\"Question\",\"name\":\"What is a React component?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"A React component is a JavaScript function that accepts an optional props object and returns JSX describing what should appear on screen. Every piece of UI in a React application is built from components, either written by the developer or imported from a library.\"}},{\"@type\":\"Question\",\"name\":\"What is the difference between props and state in React?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Props are data passed from a parent component to a child and are strictly read-only from the child's perspective. State is data the component owns and manages internally using useState. Calling the state setter triggers a re-render; props change only when the parent passes new values.\"}},{\"@type\":\"Question\",\"name\":\"Can a React component return multiple elements?\",\"acceptedAnswer\":{\"@type\":\"Answer\",\"text\":\"Yes, but they need a single root. Use a div when you want a DOM node, or a React Fragment written as empty angle brackets to group elements without adding anything to the DOM. Fragments are especially useful inside table structures or flex containers.\"}}]}\n</script>"
---
Think of a React application the way you'd think of a furniture showroom. The showroom is assembled from individual pieces — chairs, tables, lamps — each designed independently and available in multiple configurations. React UI components work the same way: self-contained pieces of UI that you slot together into pages, pass data between, and reuse across your application.

This model is why large teams can build complex UIs without stepping on each other. Each component owns its own structure, appearance, and behavior. You compose them like building blocks, send data down through props, and let each piece manage its own state when needed.

What follows covers React UI components from the ground up — JSX syntax, props, state, and composition patterns with runnable code at every step.

## React UI Components: What They Are and How They Render

A React UI component is a JavaScript function that returns JSX. The function describes what should appear on screen, and React handles translating that description into DOM elements.

```jsx
function WelcomeBanner() {
  return (
    <div className="banner">
      <h2>Welcome to DevNook</h2>
      <p>Developer tools and references, all in one place.</p>
    </div>
  );
}
```

When React encounters `<WelcomeBanner />`, it calls this function, receives the JSX tree, and converts it into actual DOM nodes. The function runs every time the component re-renders — which is why keeping the render body pure (no side effects inside it) leads to predictable, debuggable behavior.

React's model follows unidirectional data flow: data moves down from parent to child via props, and events bubble up from child to parent via callback props. Understanding this direction early saves considerable debugging time.

According to the [React documentation on components](https://react.dev/learn/your-first-component), components let you split UI into independent, reusable pieces and think about each in isolation — and that isolation is the foundation of how React scales to large applications.

## JSX Syntax: Writing Markup Inside JavaScript

JSX looks like HTML, but it compiles to plain JavaScript. When Babel (or the React transform) processes this:

```jsx
const heading = <h1 className="page-title">Developer Reference</h1>;
```

it produces:

```js
const heading = React.createElement('h1', { className: 'page-title' }, 'Developer Reference');
```

Understanding the compilation step clarifies several JSX rules that trip up beginners.

**Attributes use camelCase.** Because JSX becomes JavaScript, HTML attribute names are renamed: `class` becomes `className`, `for` becomes `htmlFor`, `onclick` becomes `onClick`. Using the HTML form often works but generates warnings and breaks in specific environments.

**JavaScript expressions go inside curly braces.** Any expression — a variable, a ternary, a function call — can be embedded in JSX with `{}`:

```jsx
function StatusBadge({ status, lastSeen }) {
  const label = status === 'online' ? 'Online' : 'Away';

  return (
    <span className={`badge badge-${status}`}>
      {label} — last seen {lastSeen}
    </span>
  );
}
```

**Every return needs a single root element.** JSX expressions must have one top-level element. When adding a real DOM wrapper would break layout — inside a table row, or between flex items — use a React Fragment:

```jsx
function TableRow({ name, department }) {
  return (
    <>
      <td>{name}</td>
      <td>{department}</td>
    </>
  );
}
```

`<></>` compiles to `<React.Fragment>`, grouping the elements without inserting anything into the DOM.

For a thorough reference on JavaScript destructuring — which appears throughout JSX props patterns — see [MDN's destructuring reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring).

## Props: Passing Data to React UI Components

Props are how data moves into a component from its parent. They are read-only by design — a component receives props, reads them, and must never modify them directly.

Props are passed as JSX attributes:

```jsx
<UserCard username="sarah_dev" role="Engineer" avatarSize={48} />
```

And received by the function, typically via destructuring:

```jsx
function UserCard({ username, role, avatarSize }) {
  return (
    <div className="user-card">
      <img
        src={`/avatars/${username}.png`}
        alt={`${username}'s avatar`}
        width={avatarSize}
        height={avatarSize}
      />
      <div className="user-info">
        <strong>{username}</strong>
        <span>{role}</span>
      </div>
    </div>
  );
}
```

Add default parameter values to handle optional props gracefully:

```jsx
function UserCard({ username = 'guest', role = 'Viewer', avatarSize = 40 }) {
  // falls back cleanly when props are missing
}
```

`<UserCard />` now renders without errors — each missing prop uses its default. `<UserCard username="sarah_dev" />` overrides only `username`.

### The children Prop

`children` is a special prop: it receives whatever JSX appears between a component's opening and closing tags.

```jsx
function Panel({ title, children }) {
  return (
    <section className="panel">
      <header className="panel-header">{title}</header>
      <div className="panel-body">{children}</div>
    </section>
  );
}

// Usage:
<Panel title="Quick Reference">
  <p>This content is passed as children.</p>
  <button>See More</button>
</Panel>
```

`Panel` doesn't know what `children` contains — it renders whatever the consumer passes. This pattern underlies layout wrappers, modals, cards, and containers throughout the React ecosystem.

The [React guide to passing props](https://react.dev/learn/passing-props-to-a-component) covers prop spreading, forwarding refs, and handling `children` in depth.

## Props vs State: Key Differences

Before diving into state, here's a comparison that clarifies when each belongs:

| | Props | State |
|---|---|---|
| **Who owns it?** | Parent component | The component itself |
| **Can it change?** | Only when the parent re-renders | Yes — via the setter function |
| **Can the child modify it?** | No — strictly read-only | Yes — via `useState` setter |
| **Triggers re-render?** | When parent passes new values | Yes — on every setter call |
| **Best for** | Configuring a child from outside | Tracking values that change over time |

A component that uses only props is sometimes called stateless. A component that calls `useState` manages its own reactive data. The distinction matters when you're deciding where to put data as the application grows.

## State: Making React UI Components Interactive

State is data that lives inside a component and changes over time. When state changes, React re-renders the component and updates the DOM to reflect the new value.

The `useState` hook declares a state variable inside a functional component:

```jsx
import { useState } from 'react';

function ToggleSwitch({ label }) {
  const [enabled, setEnabled] = useState(false);

  return (
    <div className="toggle-row">
      <span className="toggle-label">{label}</span>
      <button
        className={`toggle ${enabled ? 'toggle-on' : 'toggle-off'}`}
        onClick={() => setEnabled(prev => !prev)}
        aria-pressed={enabled}
      >
        {enabled ? 'On' : 'Off'}
      </button>
    </div>
  );
}
```

`useState(false)` initializes `enabled` to `false`. `setEnabled` is the setter — calling it queues a re-render with the new value. The functional form `prev => !prev` reads the latest state rather than whatever was captured when the event handler was created, which prevents stale-state bugs when React batches updates.

Two patterns that prevent most state bugs:

- **Never mutate state directly.** `enabled = true` does nothing. Only `setEnabled(true)` triggers a re-render.
- **Derive values instead of duplicating state.** If a value can be computed from existing state or props, compute it in the render body — don't create a separate state variable to mirror it.

## Rendering Lists of React UI Components

Rendering a list of items from an array is a pattern you'll write constantly. The [JavaScript `.map()` method](/languages/javascript/array-methods/) is the standard approach — transform each data item into a component:

```jsx
const teamMembers = [
  { id: 1, name: 'Alice Chen', role: 'Frontend' },
  { id: 2, name: 'Bob Okafor', role: 'Backend' },
  { id: 3, name: 'Carol Singh', role: 'DevOps' },
];

function TeamList() {
  return (
    <ul className="team-list">
      {teamMembers.map(member => (
        <li key={member.id} className="team-member">
          <strong>{member.name}</strong> — {member.role}
        </li>
      ))}
    </ul>
  );
}
```

The `key` prop is required when rendering lists. React uses it to track which items changed, were added, or were removed between renders. Always use a stable, unique identifier from your data — the array index causes bugs when the list can reorder, because React may incorrectly reuse DOM nodes.

When working with API responses that feed component lists, the [JSON Formatter tool](/tools/json-formatter/) is useful for verifying data structure before writing the components that consume it.

## Component Composition: Building Large UIs from Small Pieces

The real productivity gain of React comes from composing small, focused components into larger structures. A `Dashboard` might render a `Header`, a `Sidebar`, and a `MainFeed` — each of which renders its own smaller pieces:

```jsx
function Dashboard({ user }) {
  return (
    <div className="dashboard">
      <Header username={user.name} notifications={user.notifications} />
      <Sidebar navItems={user.navItems} />
      <MainFeed posts={user.feed} />
    </div>
  );
}
```

Each child component handles a single responsibility and knows nothing about its siblings. `Header` doesn't care about `Sidebar`, and neither knows anything about `Dashboard`. This isolation makes each component independently testable and replaceable without touching the rest.

A pattern worth adopting early: separate data-fetching components from display components. A `PostListContainer` fetches from an API; a `PostList` just receives a `posts` array as a prop and renders it. The display component becomes reusable with any data source, and you can swap the fetching strategy without touching the UI layer.

When your components call external APIs, understanding [HTTP headers](/guides/http-headers-guide/) — particularly `Content-Type`, `Authorization`, and CORS behavior — becomes relevant as soon as you connect to real backends.

## Where React UI Components Break: Common Mistakes

**Forgetting the key prop in lists.** React logs a warning, but the real cost is silent bugs: without stable keys, React may reuse DOM nodes incorrectly during list updates, causing form inputs to display values from the wrong item after a reorder.

**Prop drilling too deep.** Passing a prop through five intermediate components to reach one leaf that needs it signals that data is in the wrong place. React Context, or a small state manager like Zustand, is the better tool when many components across the tree need the same data.

**Mutating props.** Props belong to the parent. If a child needs to modify data, it should manage a local copy in state, or call a function prop to ask the parent to update it:

```jsx
// Wrong: mutating the array passed as a prop
function BadList({ items }) {
  items.push({ id: 99, name: 'Extra' }); // modifies the parent's array
  return <ul>{items.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
}

// Right: derive a new array, leave the prop untouched
function GoodList({ items }) {
  const displayItems = [...items, { id: 99, name: 'Extra' }];
  return <ul>{displayItems.map(i => <li key={i.id}>{i.name}</li>)}</ul>;
}
```

React event handlers frequently rely on [JavaScript closures](/languages/javascript/closures/) to capture values from the enclosing scope — which is why `onClick={() => handleDelete(item.id)}` correctly captures `item.id` even though the handler executes later.

When components load data asynchronously, [JavaScript Promises](/languages/javascript/promises/) are the foundation underlying every async pattern in React — from `useEffect` with `fetch` to data-fetching libraries like React Query and SWR.

## Frequently Asked Questions

### What is a React component?

A React component is a JavaScript function that accepts an optional props object and returns JSX describing what should appear on screen. Every piece of UI in a React application — buttons, forms, cards, sidebars, navigation bars, entire pages — is built from components, either written by the developer or imported from a library like Material UI or shadcn.

### What is the difference between props and state in React?

Props are data passed from a parent component to a child — strictly read-only from the child's perspective. State is data the component owns and manages internally using `useState`. Calling the state setter triggers a re-render of the component and any descendants that depend on the changed value. Props change only when the parent re-renders with different values.

### Can a React component return multiple elements?

Yes, but they need a single root element. Group siblings in a `<div>` when you want an actual DOM node, or use a React Fragment (`<></>`) to group elements without inserting anything into the DOM. Fragments are especially useful inside table structures or flex containers where an extra wrapper element would break the layout.

### When should a component be broken into smaller components?

Break a component when part of it could be reused elsewhere, or when it handles more than one clear responsibility. A useful test: can you describe what this component does in a single sentence? If it takes two clauses to explain it, consider splitting. A 150-line component with one clear job is fine; a 60-line component juggling three unrelated concerns should be split.

## Conclusion

React UI components are the foundation of every React application — from a single interactive button to a complete multi-page product. JSX gives you an expressive syntax for describing structure, props provide a clean channel for passing data down the tree, state makes components reactive to user interactions and data changes, and composition lets you build large, maintainable UIs from small focused pieces.

Once React UI components feel solid, the natural next steps are routing between views with React Router and handling complex form interactions — both build directly on the component model and prop patterns covered here.
