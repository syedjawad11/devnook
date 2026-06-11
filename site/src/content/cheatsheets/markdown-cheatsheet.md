---
title: "Markdown Cheat Sheet: Complete Reference for Developers"
description: "Markdown cheat sheet with horizontal rule markdown syntax, text formatting, links, tables, code blocks — your complete quick reference for writing docs."
category: cheatsheets
template_id: cheatsheet-v1
tags: [markdown, cheatsheet, documentation, formatting, github]
related_posts: []
related_tools: []
published_date: "2026-06-11"
og_image: "/og/cheatsheets/markdown-cheatsheet.png"
downloadable: true
---

Markdown is the standard format for README files, documentation, GitHub comments, and developer notes. This cheat sheet covers every syntax element — from the horizontal rule markdown separator to advanced tables, code blocks, and extended GitHub Flavored Markdown. Use it as a quick reference while writing docs, blog posts, or wiki pages.

## Horizontal Rule Markdown and Basic Syntax

A horizontal rule in Markdown creates a visual divider between sections. It renders as an `<hr>` element in HTML. Three or more hyphens, asterisks, or underscores on a standalone line produce a horizontal rule.

| Syntax | Result | Notes |
|--------|--------|-------|
| `---` | Horizontal rule | Three hyphens (most common) |
| `***` | Horizontal rule | Three asterisks |
| `___` | Horizontal rule | Three underscores |
| `- - -` | Horizontal rule | Spaced hyphens also valid |
| `# Heading 1` | `<h1>` | Top-level heading |
| `## Heading 2` | `<h2>` | Section heading |
| `### Heading 3` | `<h3>` | Sub-section heading |
| `#### Heading 4` | `<h4>` | Minor heading |

```markdown
# My Document Title

This section introduces the topic.

---

This section continues after a divider.

***

Another section separated by asterisks.
```

**Important:** A horizontal rule markdown separator must sit on its own line, surrounded by blank lines. Placing `---` immediately after a paragraph (with no blank line) causes the paragraph to render as a Setext-style heading instead — a common gotcha. Always add a blank line above and below `---`.

Headings also use `#` characters — one through six, matching `<h1>` through `<h6>`. Only one H1 should appear per document; most static site generators inject the page title as the H1 automatically.

## Text Formatting

Bold, italic, strikethrough, and highlighting apply inline emphasis. Most flavors of Markdown support all four.

| Syntax | Output | Use Case |
|--------|--------|----------|
| `**bold**` | **bold** | Strong emphasis |
| `__bold__` | **bold** | Alternative syntax |
| `*italic*` | *italic* | Soft emphasis, titles |
| `_italic_` | *italic* | Alternative syntax |
| `***bold italic***` | ***bold italic*** | Maximum emphasis |
| `~~strikethrough~~` | ~~strikethrough~~ | Deleted content (GFM) |
| `` `inline code` `` | `inline code` | Filenames, commands, values |
| `> text` | blockquote | Callouts, warnings, quotes |

```markdown
**Bold text** is used for critical information or UI element names.
*Italic text* works for book titles, technical terms, or mild emphasis.
~~Strikethrough~~ indicates deprecated content or corrections.
`code spans` wrap filenames, function names, or short commands inline.

> **Note:** Always add blank lines around blockquotes for consistent
> rendering across parsers.
```

Nested emphasis works in CommonMark: `***bold and italic***` or `**_bold and italic_**`. Avoid mixing `*` and `_` inside the same word — parser behavior varies.

## Links, Images, and References

Markdown links use the `[anchor text](url)` pattern. Images use the same pattern prefixed with `!`.

| Syntax | Use Case |
|--------|----------|
| `[text](url)` | Inline hyperlink |
| `[text](url "title")` | Link with hover tooltip |
| `[text][ref]` | Reference-style link |
| `[ref]: url "title"` | Reference definition (anywhere in file) |
| `![alt text](url)` | Inline image |
| `![alt text][img-ref]` | Reference-style image |
| `<https://url>` | Auto-link (bare URL) |
| `<email@example.com>` | Auto-linked email address |

```markdown
Visit the [CommonMark specification](https://spec.commonmark.org/) for full grammar rules.

Reference-style links keep long paragraphs readable:

Read the [original Markdown syntax guide][md-daring] for historical context.

[md-daring]: https://daringfireball.net/projects/markdown/syntax "John Gruber's original spec"

![Project logo](/images/logo.png "DevNook")
```

Reference-style links define the URL once and reuse the label multiple times — useful in technical documentation with repeated external citations. Markdown link syntax is identical whether you're writing for a static site generator or an API documentation tool. For more cheatsheet references, the [Python String Methods Cheatsheet](/cheatsheets/python-string-methods-cheatsheet) and [JavaScript Array Cheatsheet](/cheatsheets/javascript-array-cheatsheet) use the same linking patterns throughout.

## Lists and Task Checklists

Unordered lists use `-`, `*`, or `+`. Ordered lists use `1.` — Markdown auto-increments the number, so using `1.` for every item makes reordering painless. Nest lists by indenting child items two or four spaces.

| Syntax | Output | Notes |
|--------|--------|-------|
| `- item` | Bullet point | Most common |
| `* item` | Bullet point | Alternate |
| `+ item` | Bullet point | Less common |
| `1. item` | Ordered list | Auto-numbered |
| `1) item` | Ordered list | Alternate (GFM) |
| `  - nested` | Indented sub-item | 2 or 4 spaces |
| `- [ ] task` | Unchecked checkbox | GitHub Flavored Markdown |
| `- [x] done` | Checked checkbox | GitHub Flavored Markdown |

```markdown
## Installation

1. Clone the repository
2. Install dependencies
   - Run `npm install`
   - Set environment variables in `.env`
3. Start the development server with `npm run dev`

## Pre-release Checklist

- [x] All unit tests pass
- [x] CHANGELOG updated
- [ ] Version bumped in package.json
- [ ] Production build verified
- [ ] Deployment reviewed
```

Task lists (checkboxes) are a GitHub Flavored Markdown extension. They render as interactive checkboxes in GitHub issues and pull requests — a practical way to track work items inside a repository.

## Code Blocks and Inline Code

Inline code uses a single backtick. For blocks, use triple backticks (fenced code blocks) with an optional language identifier for syntax highlighting.

| Syntax | Use Case |
|--------|----------|
| `` `code` `` | Inline snippet, filenames |
| ```` ```lang ```` | Fenced code block with highlighting |
| ```` ``` ```` | Plain fenced block |
| 4-space indent | Legacy indented code block |

Common language tags: `bash`, `shell`, `python`, `javascript`, `typescript`, `go`, `rust`, `java`, `sql`, `json`, `yaml`, `html`, `css`, `markdown`, `diff`, `plaintext`.

````markdown
Use `npm install` to install packages.

```bash
# Install dependencies and start server
npm install
npm run dev
```

```python
def word_count(text: str) -> int:
    return len(text.split())

print(word_count("hello world"))  # 2
```

```diff
- const old_function = () => {};
+ const newFunction = () => {};
```
````

The `diff` language tag is useful in documentation to show before/after changes. Fenced code blocks render in every major Markdown parser: GitHub, GitLab, VS Code, Obsidian, Notion, and static site generators like Astro, Jekyll, and Hugo.

## Tables and Structured Data

GitHub Flavored Markdown (GFM) tables use pipes `|` to delimit columns and a separator row (`---`) to define the header. Most modern Markdown parsers and documentation platforms support GFM tables.

| Syntax Element | Description |
|----------------|-------------|
| `\| Col \| Col \|` | Table row |
| `\|---\|---\|` | Separator row (required after header) |
| `\|:---\|` | Left-aligned column |
| `\|---:\|` | Right-aligned column |
| `\|:---:\|` | Center-aligned column |

```markdown
| HTTP Status | Meaning          | When to Use                       |
|:-----------:|-----------------|-----------------------------------|
| `200`       | OK               | Successful GET, POST, PUT         |
| `201`       | Created          | Resource created via POST         |
| `400`       | Bad Request      | Invalid client input              |
| `401`       | Unauthorized     | Missing or invalid authentication |
| `404`       | Not Found        | Resource does not exist           |
| `500`       | Internal Error   | Unhandled server exception        |
```

Pipe characters inside table cells must be escaped as `\|`. Column widths in the source do not need to align — the parser handles rendering. For an in-depth reference on HTTP statuses themselves, see the [HTTP Status Codes Guide](/guides/http-status-codes-guide).

For complex layouts with merged cells or nested content, fall back to raw HTML tables — Markdown parsers render inline HTML inside `.md` files.

## Escaping and Special Characters

Some characters have special meaning in Markdown. Prefix them with a backslash `\` to render them literally.

| Character | Name | Escaped Form |
|-----------|------|-------------|
| `\` | Backslash | `\\` |
| `` ` `` | Backtick | `` \` `` |
| `*` | Asterisk | `\*` |
| `_` | Underscore | `\_` |
| `{` `}` | Curly braces | `\{` `\}` |
| `[` `]` | Square brackets | `\[` `\]` |
| `(` `)` | Parentheses | `\(` `\)` |
| `#` | Hash | `\#` |
| `+` `-` `.` `!` | Misc punctuation | `\+` `\-` `\.` `\!` |

```markdown
Use \*asterisks\* when you want literal asterisks, not italics.

Render a literal backtick: \`code\`

Show a bracket without creating a link: \[not a link\]
```

HTML entities also work inside Markdown: `&amp;`, `&lt;`, `&gt;`, `&copy;`, `&nbsp;`. This is useful when writing technical documentation that includes angle brackets or HTML-like content outside of fenced code blocks.

## Conclusion

This Markdown cheat sheet covers the full syntax — from horizontal rule markdown separators and basic headings to tables, task lists, code blocks, and escape sequences. Keep it open while writing README files, wikis, or developer documentation. For the complete Markdown grammar, refer to the [CommonMark specification](https://spec.commonmark.org/).
