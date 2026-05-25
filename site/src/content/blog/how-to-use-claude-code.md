---
title: "Claude Code: How to Use It for Software Development"
description: "Claude Code is Anthropic's AI coding assistant for the terminal. Learn how to install it, master key commands, and build a faster development workflow."
category: blog
subcategory: "AI & Productivity"
template_id: blog-v5
tags: [claude-code, ai-coding-assistant, anthropic, developer-tools, ai-productivity]
related_posts: []
related_tools: []
related_content: []
featured: false
author: devnook
published_date: "2026-05-24"
og_image: "/og/blog/how-to-use-claude-code.png"
actual_word_count: 2701
schema_org: |
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": ["BlogPosting", "FAQPage"],
    "headline": "Claude Code: How to Use It for Software Development",
    "description": "Claude Code is Anthropic's AI coding assistant for the terminal. Learn how to install it, master key commands, and build a faster development workflow.",
    "datePublished": "2026-05-24",
    "author": {"@type": "Organization", "name": "DevNook"},
    "publisher": {"@type": "Organization", "name": "DevNook", "url": "https://devnook.dev"},
    "url": "https://devnook.dev/blog/how-to-use-claude-code",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "Is Claude Code free to use?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Claude Code is billed per token through the Anthropic API with no flat monthly subscription. A typical interactive session costs between $0.50 and $2.00 depending on the model and context loaded."
        }
      },
      {
        "@type": "Question",
        "name": "Does Claude Code send my code to Anthropic?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes, code included in prompts is sent to Anthropic's API for processing. Under standard API terms, this data is not used to train models. Enterprise agreements with additional data handling guarantees are available."
        }
      },
      {
        "@type": "Question",
        "name": "How does Claude Code handle large codebases?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Claude Code uses search tools to locate relevant files rather than loading the entire repository upfront. The /compact command summarizes long conversations to recover context window space."
        }
      },
      {
        "@type": "Question",
        "name": "Can I use Claude Code in Docker or CI?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes. Set ANTHROPIC_API_KEY as an environment variable, install the npm package, and use --print for non-interactive execution. Add --dangerously-skip-permissions for fully automated CI steps."
        }
      },
      {
        "@type": "Question",
        "name": "What models does Claude Code use?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Claude Code defaults to claude-sonnet-4 for most tasks. Switch to claude-opus-4 for complex reasoning or claude-haiku-4 for fast lookups. Use /model mid-session or set CLAUDE_MODEL to change the default."
        }
      }
    ]
  }
  </script>
---

Claude Code is Anthropic's agentic coding assistant that runs directly in your terminal. Unlike IDE-based tools that offer line-level autocomplete, Claude Code operates at the project level — it reads your files, executes shell commands, writes and edits code, runs your test suite, and commits to git based on natural-language instructions.

This guide covers setup, core commands, and practical workflows so you can integrate Claude Code into your daily development routine. You will learn how to configure project-level context with CLAUDE.md, use it for code review and debugging, extend it with MCP servers, and manage permissions for automated tasks.

## What Is Claude Code and How It Works

Claude Code is a command-line interface built on Anthropic's [Claude](https://www.anthropic.com/claude) model family. You run it from a terminal inside your project directory. Once started, it can read and write files, run shell commands, search your codebase, and make coordinated changes across multiple files — all based on plain-English instructions.

The key difference from tools like GitHub Copilot or Cursor is scope. Copilot autocompletes the line you are writing. Claude Code handles tasks that span the entire project. You describe an outcome — "add input validation to the users endpoint" — and it determines which files to open, what changes to make, and how to verify the result.

Under the hood, Claude Code runs a tool-use loop: receive your prompt → decide which tools to call (Read, Write, Bash, Edit) → execute them → observe results → continue until the task is complete. Every tool call appears in the terminal before execution, giving you full visibility into what is happening.

The permission model gives you control at every level: approve each action individually, pre-approve specific commands, or run fully automated in trusted CI environments.

**Core capabilities:**
- Read and write files anywhere in the project tree
- Run shell commands — npm, pytest, cargo, make, and similar
- Search code with grep and ripgrep
- Create, move, rename, and delete files
- Commit, branch, and push with git
- Connect to external data sources via MCP servers
- Accept images and diagrams as part of prompts

## Installing and Authenticating Claude Code

Claude Code is distributed as an npm package and requires Node.js 18 or higher. The official package is available at [npmjs.com/@anthropic-ai/claude-code](https://www.npmjs.com/package/@anthropic-ai/claude-code).

Install it globally:

```bash
npm install -g @anthropic-ai/claude-code
```

If you use a Node version manager, confirm the right version first:

```bash
nvm use 20
npm install -g @anthropic-ai/claude-code
claude --version
```

**Authentication options:**

The simplest path is OAuth login via your Claude.ai account. Run `claude` for the first time and a browser window opens automatically:

```bash
claude
# Browser opens for OAuth — complete the login and return to the terminal
```

For server environments or CI, authenticate via API key instead:

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
claude
```

The API key method bypasses browser authentication entirely and works in headless environments. The [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) covers enterprise key setup, team billing, and usage limit configuration in detail.

**Platform notes:**
- macOS and Linux: works out of the box after installation
- Windows: WSL2 with Ubuntu 22.04 LTS gives the most reliable experience
- Docker: pass `ANTHROPIC_API_KEY` as an environment variable in the container definition

## Your First Session: Core Workflow

Navigate to a project and start Claude Code:

```bash
cd ~/projects/my-api
claude
```

Claude Code scans the directory structure and is ready for instructions. A useful first prompt:

```
> Give me an overview of this project — stack, entry point, and key modules.
```

It reads `package.json`, `README.md`, and top-level source files, then returns a concise summary. From there, give it a real task:

```
> The POST /orders endpoint is not validating the quantity field.
> Add a check: quantity must be a positive integer. Return a 400 error if not.
```

Claude Code will:
1. Find the route handler in your source files
2. Show the planned change as a diff
3. Ask for your approval before writing
4. Apply the edit and confirm completion

This approval loop is on by default. Every tool call — file read, file write, bash command — appears in the terminal before execution. You can approve, skip, or abort at any step.

For multi-step tasks, Claude Code chains tool calls automatically. Ask it to write tests, run them, and fix failures — it handles the entire loop without prompting between steps unless a destructive action requires explicit approval.

Non-interactive mode is essential for scripted usage:

```bash
# Code review via stdin
claude --print "Review this function for security issues:" < src/auth.js

# Single prompt, exits immediately with output to stdout
claude --print "List all TODO comments in this project and prioritize them."
```

The `--print` flag runs one prompt, prints the result to stdout, and exits. This integrates cleanly into shell scripts, pre-commit hooks, and automated review workflows without requiring a persistent session.

## Slash Commands and Keyboard Shortcuts

Claude Code's slash commands control session behavior and access features that plain prompts cannot reach:

| Command | What it does |
|---------|--------------|
| `/help` | Show all available commands and shortcuts |
| `/clear` | Clear conversation history to reduce token usage |
| `/model` | Switch between claude-sonnet, claude-opus, claude-haiku |
| `/review` | Code review of the current git diff |
| `/compact` | Summarize long conversations to free context window space |
| `/status` | Show token count, model in use, and session info |
| `/permissions` | View and adjust auto-approval settings mid-session |
| `/init` | Generate a CLAUDE.md starter file for the current project |
| `/exit` | End the session cleanly |

Keyboard shortcuts that matter in practice:
- `Ctrl+C` — interrupt the current tool call and return to the prompt (the session stays open)
- `Ctrl+L` — clear the terminal screen without affecting conversation history
- Up/Down arrows — cycle through previous prompts
- `Tab` — autocomplete file paths and command arguments

The `/model` command is particularly useful in long sessions. Use claude-haiku-4 for fast file searches and summaries, switch to claude-opus-4 for complex architectural reasoning — all without restarting the session and losing your conversation context.

## CLAUDE.md: Project-Level Context

`CLAUDE.md` is a markdown file at the root of your project that Claude Code reads automatically at the start of every session. It encodes project-specific knowledge — stack details, coding conventions, build commands, and off-limits areas — so you never have to repeat yourself.

Generate a starter file with `/init`:

```bash
claude
> /init
```

Claude Code reads your config files and directory structure, then writes a draft. Edit it to match your team's actual conventions. A well-structured `CLAUDE.md` for a Node.js API:

```markdown
# My API — Claude Session Context

## Stack
- Node.js 20 + Express 4.18
- PostgreSQL 15 via pg driver (connection pool in db/pool.js)
- Jest 29 for unit and integration tests

## Dev Commands
- `npm run dev` — start server on port 3000 with hot reload
- `npm test` — run full test suite
- `npm run test:unit` — unit tests only (faster feedback loop)
- `npm run lint` — ESLint check

## Architecture
- Routes in src/routes/ — one file per resource
- Business logic in src/services/
- All DB access goes through src/repositories/
- Never write SQL directly in route handlers

## Conventions
- Async/await only — no callbacks or raw .then() chains
- Validate all inputs with zod schemas in src/validators/
- Use typed errors from src/errors.js, not plain string throws
- Never commit console.log — use the logger in src/logger.js

## Off-limits
- Do not modify db/migrations/ without an explicit instruction
- Do not touch src/middleware/auth.js without flagging it first
```

With a detailed `CLAUDE.md`, Claude Code treats every session like a developer who already knows the codebase. It will not suggest patterns that violate your conventions, reach into off-limits directories, or use tools your team has moved away from.

The file also serves as living documentation for new team members. When the `CLAUDE.md` reflects current reality — not aspirational architecture — it stays useful for both Claude and humans.

## Using Claude Code for Real Development Tasks

### Code Review

After pulling changes from a colleague:

```
> Review the last 3 commits. Summarize what changed and flag any security,
> performance, or logic issues.
```

Claude Code reads the diff, traces it through affected call sites, and returns structured feedback. For targeted reviews:

```bash
git diff main...feature/new-auth | claude --print "Review this diff for security issues."
```

API changes frequently introduce subtle error-handling mistakes. The [HTTP status codes guide](/guides/http-status-codes-guide) is useful background when checking whether responses — 400 vs 422, 401 vs 403 — are mapped correctly across a changed endpoint.

### Debugging

Describe the symptom, not a guess at the cause:

```
> The app crashes with a TypeError when a user logs in via Google OAuth.
> The error is in the server logs. Find the root cause and propose a fix.
```

Claude Code reads the stack trace, follows the call chain to the source, and proposes a targeted fix. For auth-specific issues, understanding token structure helps — our guide on [what is JWT](/guides/what-is-jwt) explains the payload format and common parsing failures that appear frequently in OAuth debug sessions.

For race conditions, describe the triggering conditions:

```
> This endpoint only fails when two requests hit it simultaneously.
> Find the race condition in src/orders.js and fix it.
```

### Writing and Running Tests

```
> Write Jest tests for applyDiscount() in src/pricing.js.
> Cover: zero discount, 100% discount, negative input, non-numeric input.
> Run them and fix any failures before stopping.
```

Claude Code writes the tests, runs `npm test`, and iterates until the suite is green. If the function itself has a bug that the new tests expose, it fixes the function — not just the tests.

### Refactoring

```
> Refactor src/auth.js to replace all promise chains with async/await.
> Keep all function signatures unchanged. Run the tests afterward.
```

Multi-file refactors are where Claude Code outpaces line-level tools. It tracks how changes in one file affect callers in other files, runs the test suite to catch regressions, and only stops when the tests pass.

### Git Workflows

```
> Create branch feature/rate-limiting. Add rate limiting middleware to all
> API routes with 100 requests per minute per IP. Write tests and commit.
```

Claude Code creates the branch, implements the feature, runs the tests, and commits with a descriptive message — end to end from a single instruction. The [Git Commands Cheat Sheet](/cheatsheets/git-commands-cheatsheet) covers the underlying git operations it runs on your behalf if you need to verify or modify the git state manually.

## MCP Servers: Connecting External Tools

Model Context Protocol (MCP) servers extend Claude Code with live data sources and external APIs. Once configured, you query them through natural language — no context switching to a database client or API explorer required.

Configure servers in `.claude/settings.json`:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-postgres",
               "postgresql://localhost:5432/mydb"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_yourtoken"
      }
    }
  }
}
```

With this configuration active, inside a Claude Code session:

```
> Pull the 5 most recent GitHub issues labeled bug and rank them by severity.
```

```
> Query the database: show all orders from the last 7 days that haven't shipped yet.
```

The [Model Context Protocol specification](https://modelcontextprotocol.io/introduction) documents official server implementations for Postgres, GitHub, Slack, Notion, and the filesystem, along with the protocol for building custom servers.

Common MCP use cases:
- **Database MCP**: Run live queries mid-session without switching to a separate client
- **GitHub MCP**: Read issue descriptions and PR review comments directly in the conversation
- **Filesystem MCP**: Access specific directories outside the current project root
- **Custom MCP**: Wrap any internal REST API or data source your team maintains

MCP servers are the main mechanism for connecting Claude Code to company-specific tooling — internal ticketing systems, proprietary databases, deployment APIs — without writing custom integrations or copy-pasting data into the chat.

## Claude Code vs Other AI Coding Tools

| Feature | Claude Code | GitHub Copilot | Cursor | Windsurf |
|---------|-------------|----------------|--------|----------|
| Terminal-based | Yes | No | No | No |
| Multi-file editing | Yes | Partial | Yes | Yes |
| Runs shell commands | Yes | No | Limited | Limited |
| Full git integration | Yes | No | Partial | Partial |
| MCP server support | Yes | No | No | No |
| Works without an IDE | Yes | No | No | No |
| CI / non-interactive mode | Yes | No | No | No |
| Free tier | No | Yes | Yes | Yes |

Claude Code's differentiated position is terminal access and shell integration. It is the right choice when you need a tool that coordinates your full development toolchain — running builds, tests, linters, and deployment scripts alongside code edits. For a comparison of AI chat tools used in browser-based workflows, see [ChatGPT vs Gemini for Developers](/blog/chatgpt-vs-gemini-for-developers).

## Configuring Permissions and Safe Usage

By default, Claude Code requests approval before writing files, running shell commands, and making git commits. Pre-approving common read-only operations reduces interruptions while keeping guardrails on writes.

In `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Bash(npm test)",
      "Bash(npm run lint)",
      "Bash(npm run build)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(grep*)"
    ],
    "deny": [
      "Bash(rm -rf*)",
      "Bash(curl*)",
      "Bash(wget*)"
    ]
  }
}
```

This setup lets Claude Code read freely and run your standard scripts without asking, but still requires approval for file writes and git commits. The `deny` list blocks destructive shell patterns regardless of any `allow` entries.

For fully-automated use in CI — where there is no human to approve actions — use the `--dangerously-skip-permissions` flag. Restrict this to isolated container environments that have no access to production credentials or infrastructure.

You can also adjust permissions mid-session without restarting by using the `/permissions` slash command.

## Frequently Asked Questions

**Is Claude Code free to use?**
Claude Code is billed per token through the Anthropic API with no flat monthly subscription. You pay for actual usage. A typical interactive session costs between $0.50 and $2.00 depending on which model is active and how many files are loaded into context. Anthropic's pricing page lists current per-token rates for each model tier.

**Does Claude Code send my code to Anthropic?**
Yes, code included in prompts is sent to Anthropic's API for processing. Under standard API terms, this data is not used to train models. Anthropic offers enterprise agreements with stricter data handling guarantees for teams operating under compliance requirements.

**How does Claude Code handle large codebases?**
Claude Code uses search tools — grep, find, ripgrep — to locate relevant files rather than loading the entire repository at once. The `/compact` command summarizes long conversations to recover context window space during extended sessions. For large monorepos, running Claude Code from a specific subdirectory with a focused `CLAUDE.md` scoped to that module consistently gives better results than starting from the repo root.

**Can I use Claude Code in Docker or CI?**
Yes. Set `ANTHROPIC_API_KEY` as an environment variable, install the npm package in the container or CI runner, and use `--print` for non-interactive execution. Add `--dangerously-skip-permissions` for fully automated CI steps where no human approval is possible.

**What models does Claude Code use?**
Claude Code defaults to claude-sonnet-4 for most coding tasks. Switch to claude-opus-4 for complex architectural reasoning or claude-haiku-4 for fast lookups and summaries. Use the `/model` slash command mid-session to switch, or set the `CLAUDE_MODEL` environment variable to change the default for all future sessions.

## Conclusion

Claude Code brings AI assistance out of the IDE and into the terminal, where it has direct access to your full development toolchain. Install it with `npm install -g @anthropic-ai/claude-code`, write a `CLAUDE.md` that captures your project conventions, and give it a real task — a code review, a failing test, a multi-file refactor. The setup takes minutes. The result is a tool that handles the mechanical, multi-step work so you can stay focused on decisions that need actual judgment.
