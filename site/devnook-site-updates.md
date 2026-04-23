# DevNook Site Updates — Brief for Claude Code

## 🎯 Prompt for Claude Code

> You are working on **devnook.dev**, an Astro-based static site deployed on Cloudflare Pages. I need you to make four changes described below. Before editing anything:
>
> 1. Read the project structure and identify where the hero section, footer component, and `src/pages/` directory live.
> 2. Match the existing code style, frontmatter conventions, layout imports, and Tailwind/CSS classes already used on the site — do **not** introduce new patterns.
> 3. For the two new pages (About, Cookie Policy), reuse whatever base layout the existing static pages use (e.g. the same Layout component and meta setup as the homepage or blog index).
> 4. After making all changes, run the dev server and verify the site still builds cleanly with no warnings or 404s. Then commit each change as a separate, clearly-scoped commit.
>
> The four changes are listed in order below. Follow them top to bottom.

---

## Change 1 — Replace the hero tagline

**Where:** Homepage hero section (likely `src/pages/index.astro` or a `Hero.astro` component).

**Find this text:**

```
Free browser-based tools, language guides, and quick-reference cheat sheets. No ads, no tracking, just the information you need.
```

**Replace with (primary choice):**

```
Free browser-based tools, language guides, and quick-reference cheat sheets. Fast, distraction-free, and built for developers who ship.
```

**Alternatives (pick one if the primary doesn't fit the design):**

- `Free browser-based tools, language guides, and quick-reference cheat sheets. Open, fast, and always a keyboard shortcut away.`
- `Free browser-based tools, language guides, and quick-reference cheat sheets. Built by developers, for developers — the reference library that respects your time.`

---

## Change 2 — Replace the footer description

**Where:** Footer component (likely `src/components/Footer.astro` or inside the shared layout).

**Find this text:**

```
Free developer tools, guides, and cheat sheets for the modern web. Built with Astro, deployed on Cloudflare.
```

**Replace with (primary choice):**

```
Free developer tools, guides, and cheat sheets for the modern web. A quiet corner of the internet, built to help you ship better code.
```

**Alternatives:**

- `Free developer tools, guides, and cheat sheets for the modern web. Built by developers, for developers — fast, free, and always will be.`
- `Free developer tools, guides, and cheat sheets for the modern web. Clear references, useful tools, zero fluff.`

---

## Change 3 — Create the About page

**Path:** `src/pages/about.astro` (or `src/pages/about/index.astro` if that matches the existing routing style).

**Link it from:** the footer under a new "Site" or "Company" column, and optionally from the main nav if that fits the design. At minimum, add an `About` link to the footer.

**Page metadata:**

- Title: `About DevNook — Developer Tools & References Built for Speed`
- Description: `DevNook is a free, ad-free library of developer tools, language guides, and cheat sheets. Learn why it exists and what it's for.`
- Canonical: `https://devnook.dev/about/`

**Page content (render as semantic HTML with the site's existing typography styles):**

```markdown
# About DevNook

DevNook is a free, open library of developer tools, language guides, and quick-reference cheat sheets. It exists for one reason: the reference material developers use every day should be fast to load, easy to scan, and free of the noise that fills most of the modern web.

## Why DevNook exists

Every developer has been there. You need to remember the exact syntax for a regex lookahead, or how `Array.prototype.reduce` handles an empty array, or what claims a JWT actually contains. You open a search engine, click the top result, wait for it to load, dismiss a cookie banner, close a newsletter popup, scroll past three ads and a 900-word SEO preamble — and finally find a two-line code snippet.

That friction adds up. DevNook is an attempt to do the opposite: get you to the answer in under ten seconds, on any device, with nothing standing in the way.

## What you'll find here

- **Tools** — browser-based utilities that run entirely on your device. JSON formatting, regex testing, JWT decoding, Base64 encoding, and more. Nothing you paste ever leaves your browser.
- **Language guides** — focused, practical explanations of the features developers reach for most, across Python, JavaScript, TypeScript, Go, Rust, and others.
- **Cheat sheets** — one-page references organised by task, not by API surface. Built for the moment you need them, not for teaching from scratch.
- **Guides** — longer-form articles for topics that genuinely need the space, written without padding.

## The principles behind it

1. **Performance is a feature.** Pages should be usable the moment they load. No layout shift, no blocking scripts, no third-party fonts loading for six seconds.
2. **Content respects your time.** If the answer fits in three lines, the article is three lines.
3. **Privacy is the priority.** Tools run client-side — anything you paste stays in your browser. We use lightweight analytics to understand what's useful, but never for advertising, remarketing, or cross-site tracking.
4. **The web should be readable.** Clean typography, sensible contrast, keyboard-friendly navigation, and dark mode that actually works.
5. **Free means free.** No paywalls, no "pro" tier, no email gates. If a resource is listed on DevNook, you can use it.

```

> **Note for Claude Code:** If the site uses MDX or a content collection for static pages, convert the above into that format. Otherwise, render it as an Astro page with the shared layout and normal prose styling. Keep the headings as `<h1>`, `<h2>`, etc. — don't wrap everything in a single block.

---

## Change 4 — Create the Cookie Policy page

**Path:** `src/pages/cookie-policy.astro` (match routing style of other static pages).

**Link it from:** the footer, alongside any existing legal or site links (e.g. in the bottom row next to the copyright line).

**Page metadata:**

- Title: `Cookie Policy — DevNook`
- Description: `DevNook's cookie policy. We don't use advertising or cross-site tracking. This page explains the cookies and storage we do use.`
- Canonical: `https://devnook.dev/cookie-policy/`
- Optional: add `<meta name="robots" content="index,follow">` — legal pages should still be indexable.

**Page content:**

```markdown
# Cookie Policy

**Last updated:** [INSERT_DATE — Claude Code, please set this to the date the page is added, formatted as "18 April 2026"]

This Cookie Policy explains how DevNook ("we", "us", "devnook.dev") uses cookies and similar technologies when you visit our website. We keep this to an absolute minimum and do not use advertising or cross-site tracking cookies.

## What cookies are

Cookies are small text files stored on your device by your web browser when you visit a website. They are widely used to make websites work, to improve user experience, and — on many sites — to track users across the web for advertising. Similar technologies include `localStorage`, `sessionStorage`, and cookie-free fingerprinting; where relevant, this policy applies to those too.

## Cookies we do not use

DevNook does **not** use any of the following:

- Advertising cookies
- Behavioural or retargeting cookies
- Cross-site tracking cookies
- Social media tracking pixels

We also do not embed third-party scripts whose primary purpose is to profile visitors.

## Cookies and storage we may use

DevNook may use a small number of strictly necessary cookies or browser storage entries, limited to:

- **Theme preference** — if you toggle dark mode, your choice is stored locally in your browser (`localStorage`) so the site remembers it on your next visit. This value never leaves your device.
- **Tool state** — some browser-based tools (e.g. the JSON Formatter, Regex Tester) may store your most recent input locally so it persists if you refresh the page. This data stays in your browser and is never transmitted.
- **Security and infrastructure cookies** set by Cloudflare — our hosting provider — to protect the site from abuse and to serve content efficiently. These are standard for any site on Cloudflare and do not identify you. You can read Cloudflare's own cookie documentation at [cloudflare.com/cookie-policy](https://www.cloudflare.com/cookie-policy/).

None of the above are used for marketing or for building a profile of you.

## Analytics

DevNook uses **Google Analytics** to understand, in aggregate, which pages and tools people use most. This helps us decide what to improve and what to build next.

- The data is aggregated and statistical — we use it to see things like "the JSON Formatter is popular" or "most visitors arrive from search engines", not to identify individual users.
- Google Analytics sets its own cookies (names typically starting with `_ga`) on your device. These are first-party cookies under the devnook.dev domain.
- The data is processed by Google on our behalf. You can read Google's privacy policy at [policies.google.com/privacy](https://policies.google.com/privacy) and learn more about how Google uses data at [policies.google.com/technologies/partner-sites](https://policies.google.com/technologies/partner-sites).
- We do not use Google Analytics for advertising, audience remarketing, or cross-site tracking.

**How to opt out of Google Analytics:**

- Install the official [Google Analytics Opt-out Browser Add-on](https://tools.google.com/dlpage/gaoptout), which works across every site that uses GA.
- Enable "Do Not Track" or tracking-prevention settings in your browser.
- Use a browser or extension that blocks analytics scripts (e.g. Brave, uBlock Origin, Firefox's Enhanced Tracking Protection).

Opting out of analytics has no effect on your ability to use the site — every tool, guide, and cheat sheet will continue to work normally.

## Third-party content

Some pages on DevNook may link out to third-party sites (for example, official language documentation or GitHub repositories). Once you click through, those sites operate under their own cookie and privacy policies, which we do not control. We recommend reviewing the policies of any third-party site you visit.

## How to control cookies

You can control and delete cookies at any time through your browser settings. Every major browser lets you:

- View the cookies currently stored on your device
- Delete individual cookies or all cookies
- Block cookies from specific sites or block them globally
- Use private/incognito mode, which isolates cookies to the current session

```

> **Note for Claude Code:** Please substitute today's date into the `Last updated` line when you create the page. If the site already has an established "legal page" layout with its own title block or prose container, use that component instead of hand-rolling the heading structure.

---

## Summary checklist for Claude Code

- [ ] Hero tagline updated on homepage
- [ ] Footer description updated in shared component
- [ ] `/about/` page created, linked from the footer
- [ ] `/cookie-policy/` page created, linked from the footer
- [ ] Sitemap / RSS / `robots.txt` regenerated if the site's build step requires it
- [ ] `npm run build` (or equivalent) completes with no errors
- [ ] Visually verified in light and dark mode

When done, please summarise exactly which files you changed and which commits you made.
