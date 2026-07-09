---
title: "React Router DOM Explained: Routes, Links, and Params"
description: "Learn react router dom routing from scratch. Set up BrowserRouter, define routes, pass URL params, and navigate your React SPA with confidence."
category: "languages"
language: "react"
concept: "router"
difficulty: "intermediate"
template_id: "lang-v2"
tags: [react, routing, react-router-dom, spa, navigation]
related_posts: []
related_tools: []
linkAnchors:
  - "react router dom"
  - "react router"
  - "routing in react"
published_date: "2026-07-09"
og_image: "/og/languages/react/router.png"
word_count_target: 2315
schema_org: "<script type=\"application/ld+json\">\n{\"@context\": \"https://schema.org\", \"@type\": [\"TechArticle\", \"FAQPage\"], \"headline\": \"React Router DOM Explained: Routes, Links, and Params\", \"description\": \"Learn react router dom routing from scratch. Set up BrowserRouter, define routes, pass URL params, and navigate your React SPA with confidence.\", \"datePublished\": \"2026-07-09\", \"author\": {\"@type\": \"Organization\", \"name\": \"DevNook\"}, \"publisher\": {\"@type\": \"Organization\", \"name\": \"DevNook\", \"url\": \"https://devnook.dev\"}, \"url\": \"https://devnook.dev/languages/react/router/\", \"mainEntity\": [{\"@type\": \"Question\", \"name\": \"What is the difference between BrowserRouter and HashRouter?\", \"acceptedAnswer\": {\"@type\": \"Answer\", \"text\": \"BrowserRouter uses the HTML5 History API to produce clean URLs like /about, while HashRouter uses a URL hash giving URLs like /#/about. BrowserRouter requires server configuration to serve index.html for all paths; HashRouter works on static hosts without extra setup.\"}}, {\"@type\": \"Question\", \"name\": \"How do you pass URL parameters in react-router-dom v6?\", \"acceptedAnswer\": {\"@type\": \"Answer\", \"text\": \"Define the route with a colon-prefixed segment: path='/products/:productId'. Inside the component, call useParams() to retrieve the value: const { productId } = useParams().\"}}, {\"@type\": \"Question\", \"name\": \"Can react-router-dom be used without Redux?\", \"acceptedAnswer\": {\"@type\": \"Answer\", \"text\": \"Yes. React Router is independent of Redux or any global state library. Route params and query strings handle most navigation-related state. A global store only becomes relevant when data must persist across route changes unrelated to the URL.\"}}]}\n</script>"
---

React apps are single-page — one HTML file, one JavaScript bundle, one entry point. But users expect URLs to change when they navigate. They expect the back button to work. They expect that bookmarking `/dashboard` brings them back to the dashboard, not to the homepage. Without routing, a React app has exactly one address. React router dom is the library that gives it the rest.

React Router DOM is the standard routing library for React, built on top of the web's [HTML5 History API](https://developer.mozilla.org/en-US/docs/Web/API/History_API). This guide walks through setting it up, defining routes, handling dynamic URLs, navigating between pages, and avoiding the common traps — starting from a minimal working example and building toward patterns you would find in a real codebase. The [official React Router documentation](https://reactrouter.com/home) covers the full API surface.

## What react-router-dom Does Under the Hood

When a user types a URL in a traditional multi-page app, the browser makes a network request and the server returns a new HTML document. With react-router-dom, none of that happens. The library intercepts navigation events, reads the current URL, and renders a different React component — all without a network round-trip.

The mechanism is the HTML5 History API. `BrowserRouter` wraps your app and listens for `popstate` events, which fire when the user clicks the browser's back or forward buttons, and for programmatic pushes to the history stack. When the URL changes, React Router matches it against your route definitions and re-renders the matched component tree.

Two components form the structure of every react-router-dom setup:

- **`<Routes>`** — a container that evaluates all its `<Route>` children and renders only the one whose `path` matches the current URL.
- **`<Route>`** — pairs a URL pattern (`path`) with a React element (`element`).

React Router v6 — the current major version — introduced several breaking changes from v5. The most significant: `<Switch>` became `<Routes>`, the `component` prop became `element`, and route matching is now best-match-first rather than first-match-first. This article covers v6 (react-router-dom@6) throughout.

## Installing and Wiring Up BrowserRouter

Install the package from npm:

```bash
npm install react-router-dom
```

To enable routing, wrap your application in `BrowserRouter`. In a Vite or Create React App project, modify your entry point file:

```jsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
```

`BrowserRouter` must be an ancestor of every component that uses Router hooks or the `<Link>` component. Rendering a `<Link>` outside a `BrowserRouter` throws a context error at runtime — this is one of the more confusing errors for developers who are new to React Router.

There is also `HashRouter`, which appends `#` to the URL, producing `/#/about` instead of `/about`. It works on static file hosts that cannot be configured to serve `index.html` for all paths. The trade-offs: uglier URLs, no server-side rendering support, and some analytics tools handle hash-based URLs differently. Prefer `BrowserRouter` on any modern host and configure your server to redirect all paths to `index.html`. Fall back to `HashRouter` only when you have no server configuration control at all.

## Defining Your First Routes

Once `BrowserRouter` wraps your tree, define routes in any component rendered inside it — typically in `App.jsx`:

```jsx
import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import DashboardPage from './pages/DashboardPage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
```

The `path="*"` catch-all renders when no other route matches — that is your 404 page, a regular React component you design and style yourself. API calls inside route components may return HTTP error codes; the [HTTP Status Codes guide](/guides/http-status-codes-guide/) covers what each code means and how to handle them in your fetch logic.

The `element` prop takes a JSX element (`element={<HomePage />}`), not a component reference (`element={HomePage}`). This is the v6 API; v5 used `component={HomePage}`. Passing a component reference instead of a JSX element is silent — React Router v6 renders nothing without throwing, which makes this a frustrating bug to track down.

## Navigating Between Pages with Link and NavLink

Never use a plain `<a href="/about">` inside a React Router app. A standard anchor tag causes a full browser navigation — the page reloads, JavaScript state is cleared, and the app re-initializes from scratch. `<Link>` provides the same visual result without the reload:

```jsx
import { Link, NavLink } from 'react-router-dom';

function SiteNav() {
  return (
    <nav>
      <NavLink
        to="/"
        end
        className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
      >
        Home
      </NavLink>
      <NavLink
        to="/about"
        className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
      >
        About
      </NavLink>
      <Link to="/dashboard" className="nav-link">Dashboard</Link>
    </nav>
  );
}
```

`NavLink` is a superset of `<Link>`. Its `className` and `style` props accept a callback that receives an `isActive` boolean, letting you style the link for the currently active route. The `end` prop on the root route (`/`) is important: without it, the root NavLink is considered active on every URL, because every URL starts with `/`.

Use `<Link>` for links where active styling doesn't matter — footer links, back-navigation buttons, or links to unrelated sections. Use `<NavLink>` for primary navigation where highlighting the current page is part of the design.

## Dynamic Routes and URL Parameters

Most apps include routes like `/users/42` or `/articles/react-router-guide`. React Router handles these with colon-prefixed URL segments:

```jsx
// Route definitions
<Route path="/products/:productId" element={<ProductPage />} />
<Route path="/blog/:category/:postSlug" element={<BlogPostPage />} />
```

Inside the component, `useParams()` retrieves the current URL's values for those segments:

```jsx
import { useParams } from 'react-router-dom';

function ProductPage() {
  const { productId } = useParams();

  return (
    <article>
      <h2>Product #{productId}</h2>
      <p>
        Fetch product details from your API using <code>{productId}</code> as the query key.
      </p>
    </article>
  );
}
```

`productId` is always a string, even when the underlying value is numeric. Convert it explicitly with `Number(productId)` or `parseInt(productId, 10)` before arithmetic or passing it to a typed function. When building URLs that include special characters or encoded segments, the [url-encoder tool](/tools/url-encoder/) lets you test encodings interactively.

Multiple parameters work the same way. The path `/teams/:teamId/members/:memberId` produces both keys from a single `useParams()` call: `const { teamId, memberId } = useParams()`.

### Query strings with useSearchParams

Query strings — the `?key=value` part of a URL — are separate from path params and handled with `useSearchParams`:

```jsx
import { useSearchParams } from 'react-router-dom';

function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const page = Number(searchParams.get('page') || '1');

  return (
    <div>
      <input
        value={query}
        onChange={e => setSearchParams({ q: e.target.value, page: '1' })}
        placeholder="Search..."
      />
      <p>Page {page} of results for: <strong>{query}</strong></p>
      <button onClick={() => setSearchParams({ q: query, page: String(page + 1) })}>
        Next page
      </button>
    </div>
  );
}
```

`useSearchParams` behaves like `useState` for the URL query string. Calling `setSearchParams` pushes a new history entry, making the search state bookmarkable and back-button-safe without any additional setup. Both the query text and page number live in the URL — a user can share a link to page 3 of their results and that exact state is reproduced.

## Programmatic Navigation with useNavigate

Sometimes navigation happens in response to code rather than a user click — after form submission, after an API response, or when a guard condition fails. `useNavigate` handles this:

```jsx
import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const navigate = useNavigate();

  async function handleLogin(credentials) {
    const result = await loginUser(credentials);
    if (result.success) {
      navigate('/dashboard', { replace: true });
    } else {
      navigate('/login/error');
    }
  }

  return <LoginForm onSubmit={handleLogin} />;
}
```

`navigate('/dashboard')` pushes a new history entry — the back button returns to the previous page. `navigate('/dashboard', { replace: true })` replaces the current entry instead of pushing a new one. After a successful login, `replace: true` prevents the back button from returning the user to the login form, which would be confusing. `navigate(-1)` goes back one step; `navigate(1)` goes forward.

Understanding how async functions resolve in JavaScript is useful here. The [async/await in JavaScript](/languages/javascript/async-await/) guide covers the mechanics, and [JavaScript Promises](/languages/javascript/promises/) explains the underlying model that `async/await` builds on.

## Nested Routes and Shared Layouts

React Router v6 supports nested route definitions that map directly to nested component layouts. The outer route renders a shared shell; inner routes render into an `<Outlet>` placeholder inside that shell:

```jsx
import { Outlet, NavLink } from 'react-router-dom';

function DashboardLayout() {
  return (
    <div className="dashboard-shell">
      <aside className="sidebar">
        <NavLink to="analytics" end>Analytics</NavLink>
        <NavLink to="settings">Settings</NavLink>
        <NavLink to="billing">Billing</NavLink>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
```

```jsx
// Route tree in App.jsx
<Route path="/dashboard" element={<DashboardLayout />}>
  <Route index element={<DashboardHomePage />} />
  <Route path="analytics" element={<AnalyticsPage />} />
  <Route path="settings" element={<SettingsPage />} />
  <Route path="billing" element={<BillingPage />} />
</Route>
```

The URL `/dashboard/analytics` renders `DashboardLayout` with `AnalyticsPage` inside its `<Outlet>`. Navigating to `/dashboard/settings` keeps the layout shell mounted and swaps only the inner component — headers, sidebars, and any layout-level data stay in memory without refetching. The `index` route renders when the path is exactly `/dashboard`.

Nested layouts work well because they reflect the structure of your UI directly. Components at the layout level receive props and manage state that all child routes can share through context or props. The [React Components guide](/languages/react/components/) covers how component composition and props work in depth — the same patterns apply to how you structure layout-level and route-level components.

## Where This Can Bite You

**Forgetting `end` on the root NavLink.** Without `end`, the NavLink for `"/"` is active on every URL because every URL starts with `/`. The result is a navigation bar where "Home" appears highlighted on the About page, the Dashboard, and everywhere else. Add `end` to any `NavLink` whose path is a prefix of other routes.

```jsx
// Broken: Home is highlighted everywhere
<NavLink to="/">Home</NavLink>

// Correct
<NavLink to="/" end>Home</NavLink>
```

**Calling router hooks outside the Router context.** `useParams`, `useNavigate`, and `useSearchParams` all require the Router context from `BrowserRouter`. Calling them in a component rendered above `<BrowserRouter>` — or in a unit test that doesn't wrap with a Router — throws a context error. In tests, wrap with `MemoryRouter`:

```jsx
import { MemoryRouter } from 'react-router-dom';

render(
  <MemoryRouter initialEntries={['/products/42']}>
    <ProductPage />
  </MemoryRouter>
);
```

`MemoryRouter` keeps history in memory rather than the browser URL bar, making it well-suited for tests and Storybook stories.

**Server not configured for direct URL access.** With `BrowserRouter`, navigating to `https://yourapp.com/about` directly (or refreshing on that page) sends a real HTTP request to your server for the path `/about`. If the server returns a 404 because no file exists there, the app fails to load. On Nginx, add `try_files $uri /index.html;`; on Netlify add a `_redirects` file with `/* /index.html 200`; on Vercel add a `rewrites` rule in `vercel.json`. `HashRouter` sidesteps this entirely, since the server always receives a request for `/`.

## Frequently Asked Questions

### What is the difference between BrowserRouter and HashRouter?

`BrowserRouter` uses the HTML5 History API to produce clean URLs like `/about`. Direct access or a hard reload on `/about` sends a real HTTP request for that path — your server must serve `index.html` in response, or the user sees a server 404. `HashRouter` uses a URL hash, producing `/#/about`. Since the hash is not sent to the server, the server always receives a request for `/` and no configuration is required. Use `BrowserRouter` on any host where you can add a rewrite rule (virtually all modern platforms); fall back to `HashRouter` only on constrained static hosts.

### How do you pass URL parameters in react-router-dom v6?

Define the route with a colon-prefixed path segment: `<Route path="/products/:productId" element={<ProductPage />} />`. Inside the component, call `useParams()`: `const { productId } = useParams()`. Multiple parameters in one path all come back from a single `useParams()` call as separate keys. All values are strings — convert numeric IDs explicitly with `Number()` or `parseInt()`.

### Can react-router-dom be used without Redux?

Yes. React Router is completely independent of Redux or any global state library. Route parameters and query strings cover most navigation-related state needs without any additional tooling. When data must persist across route changes in a way that shouldn't live in the URL — authentication tokens, a shopping cart, user preferences — React context or a lightweight store like Zustand works well alongside React Router, but nothing about the router itself requires a state manager.

### How do you handle 404 pages in react-router-dom?

Add a catch-all route at the end of your `<Routes>` block using `path="*"`. React Router tries each route in definition order; the wildcard matches any URL that nothing else claimed. The element for that route is a regular React component — style it the same way as the rest of your app, include the main navigation, and add links to popular pages. The user stays in the app and can navigate out without needing the back button.

## Conclusion

React router dom solves a structural mismatch: React renders UI, but the web navigates by URL. The library bridges the two — `BrowserRouter` hooks into the History API, `<Routes>` and `<Route>` map URL patterns to components, `<Link>` navigates without reloading, and `useParams` extracts dynamic segments. Nested routes with `<Outlet>` extend this into full layout systems that keep shared structure mounted as inner content changes.

The natural next step from here is [React Components](/languages/react/components/), which covers how JSX, props, and component composition work — understanding that directly informs how you structure what each route renders. As your route tree grows, look at `React.lazy` and `Suspense` for lazy-loading route bundles, which keeps the initial page load fast regardless of how many routes you add.
