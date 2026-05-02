---
title: Diff Checker — Free Online Tool
description: Compare two text blocks side-by-side and see differences highlighted line by line. Free browser-based diff viewer.
category: tools
tool_slug: diff-viewer
template_id: tool-exp-v1
tags:
- diff
- diff checker
- text comparison
- code review
- change detection
related_tools:
- markdown-to-html
- html-formatter
related_content:
- git-diff-explained
- code-review-best-practices
published_date: '2026-04-18'
og_image: /og/tools/diff-viewer.png
---

## What is the Diff Checker?

The Diff Checker is a free browser-based tool that compares two text blocks and highlights every addition, deletion, and unchanged line. Paste your original and changed text, click **Compare**, and see a colour-coded visual diff in either side-by-side or unified view.

All comparison happens locally in your browser using a Longest Common Subsequence (LCS) algorithm — the same core technique used by `git diff`. No text is sent to any server.

## How to Use the Diff Checker

1. Paste your **original text** in the left input
2. Paste your **changed text** in the right input
3. Click **Compare**
4. Switch between **Side by side** and **Unified** views using the View selector
5. Use **Swap** to reverse original and changed, then compare again
6. Click **Clear** to reset both inputs

## View Modes

**Side by side** — Shows the original on the left and the modified version on the right. Deletions are highlighted on the left, additions on the right, making it easy to see what was removed and what was added at the same position.

**Unified** — Shows a single stream of lines with `–` for deleted lines and `+` for added lines. Useful for a compact view of changes in shorter files.

## Common Use Cases

- **Code review** — Compare a function or [HTML template](/tools/html-formatter) before and after refactoring to spot unintended changes
- **Config diffs** — Check what changed between two versions of a `.env` or YAML file
- **Document revisions** — See what was changed between two drafts of a specification, a README, or any [Markdown](/tools/markdown-to-html) file
- **Debugging** — Compare two API responses to find unexpected differences in output

## Frequently Asked Questions

**Is this tool useful for binary files or images?**  
No. The Diff Checker is designed for plain text. Binary content will produce unreadable or misleading output.

**How large can the input text be?**  
The tool runs in your browser's JavaScript engine. Very large inputs (tens of thousands of lines) may be slow because LCS computation is O(n×m) in the worst case. For very large diffs, a command-line tool like `git diff` or `diff` will be faster.

**Can I diff JSON or code with syntax highlighting?**  
Not currently — output is plain text with line-level colour coding. Syntax highlighting is not supported in this version.

For tracking code changes over time, the [Git Commands Cheat Sheet](/cheatsheets/git-commands-cheatsheet) covers the essential diff and log commands.
