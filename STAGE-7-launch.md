# Stage 7 — Launch Day

**Goal:** Run all agents end-to-end to produce a live devnook.dev with 15–20 published posts + 10 working tools. This is the culmination of all prior stages.

**Depends on:** All previous stages (1–6) must be complete and tested  
**Estimated session time:** 1–2 sessions (generation takes time due to LLM calls; some steps can run overnight)  
**Domain:** devnook.dev (registered on Cloudflare, April 2026)

---

## Pre-Launch Checklist

### Environment Setup
- [ ] `GEMINI_API_KEY` set in local `.env`
- [ ] `OPENROUTER_API_KEY` set in local `.env`
- [ ] `GOOGLE_SERVICE_ACCOUNT_JSON` set in local `.env`
- [ ] Python deps installed: `pip install -r agents/requirements.txt`
- [ ] Node.js 20+ installed
- [ ] `wrangler` CLI installed (for Cloudflare Workers): `npm install -g wrangler`
- [ ] Git repo initialized and pushed to GitHub
- [ ] GitHub Secrets configured (GH_PAT, GOOGLE_SERVICE_ACCOUNT_JSON)

### Verify Prior Stages
- [ ] `agents/skills/` has all 6 skill files
- [ ] `agents/content-team/registry.db` exists with schema tables
- [ ] `templates/templates/` has all 22 template files
- [ ] `agents/tools-team/tool-specs/` has at least 10 spec files
- [ ] `agents/dev-team/scaffold.py` exists
- [ ] `agents/tools-team/build-tool.py` exists
- [ ] `agents/content-team/run-pipeline.py` exists
- [ ] `agents/publish/publish.py` exists
- [ ] `.github/workflows/drip-publish.yml` exists

---

## Launch Sequence

### Step 1: Scaffold the Astro Site

```bash
# Generate the full Astro project
python agents/dev-team/scaffold.py

# Install Astro deps
npm install

# Verify it builds
npm run dev
# Check http://localhost:4321 — should show homepage (empty but styled)
```

Expected output:
- `src/` directory populated with all components, layouts, pages
- `npm run dev` starts without errors
- Homepage shows with NavBar, Footer, token-based design

---

### Step 2: Generate the First 10 Tools

```bash
# Generate the first 10 Tier 1 tools (these power the tool-adjacent content strategy)
python agents/tools-team/build-tool.py --spec json-formatter
python agents/tools-team/build-tool.py --spec base64-encoder
python agents/tools-team/build-tool.py --spec url-encoder
python agents/tools-team/build-tool.py --spec regex-tester
python agents/tools-team/build-tool.py --spec uuid-generator
python agents/tools-team/build-tool.py --spec hash-generator
python agents/tools-team/build-tool.py --spec timestamp-converter
python agents/tools-team/build-tool.py --spec case-converter
python agents/tools-team/build-tool.py --spec word-counter
python agents/tools-team/build-tool.py --spec hex-to-rgb

# Or run all Tier 1 at once:
python agents/tools-team/build-tool.py --tier 1

# Verify tools build
npm run build
# Check http://localhost:4321/tools/ — should show 10 tool cards
# Test a tool: http://localhost:4321/tools/json-formatter
```

---

### Step 3: Generate Seed Content (15–20 posts)

Run the content pipeline targeting high-priority keywords for launch.

**Option A: Automated pipeline**
```bash
# Run full pipeline (keyword → planner → writer → seo → qa → staging)
python agents/content-team/run-pipeline.py --steps all

# Check what's staged
ls content-staging/
sqlite3 agents/content-team/registry.db \
  "SELECT slug, category, opportunity_score FROM posts WHERE status='staged' ORDER BY opportunity_score DESC LIMIT 20;"
```

**Option B: Targeted seed content** (recommended for launch quality)

Manually queue the 20 highest-value posts by inserting directly into registry.db:

```sql
-- The 20 seed posts that cover all content rings and establish authority
INSERT INTO posts (slug, title, description, category, language, concept, template_id, keyword, opportunity_score, status) VALUES

-- Ring 1: Tool-adjacent (highest conversion)
('json-formatter-guide', 'JSON Formatter Online: Format, Validate & Minify JSON Free', 'Format and validate JSON instantly. Our free online JSON formatter catches syntax errors and beautifies messy JSON in one click.', 'guides', NULL, NULL, 'guide-v2', 'json formatter online', 95, 'queued'),
('base64-decode-online', 'Base64 Decode & Encode Online — Free Tool + Guide', 'Decode or encode Base64 strings instantly in your browser. Learn what Base64 is and why developers use it.', 'guides', NULL, NULL, 'guide-v2', 'base64 decode online', 92, 'queued'),
('regex-tester-guide', 'Regex Tester: Test Regular Expressions Online with Explanation', 'Test regular expressions interactively. Get real-time matches, group captures, and plain-English explanations.', 'guides', NULL, NULL, 'guide-v2', 'regex tester online', 90, 'queued'),

-- Ring 2: Web dev fundamentals
('what-is-rest-api', 'What is a REST API? A Complete Guide for Developers', 'REST APIs power the modern web. Learn what REST means, how HTTP methods work, and how to design clean API endpoints.', 'guides', NULL, NULL, 'guide-v1', 'what is REST API', 88, 'queued'),
('what-is-jwt', 'What is JWT? JSON Web Tokens Explained with Examples', 'JWTs are the industry standard for stateless authentication. Understand the header, payload, signature — and when not to use JWT.', 'guides', NULL, NULL, 'guide-v1', 'what is JWT', 86, 'queued'),
('http-status-codes-guide', 'HTTP Status Codes: Complete Reference (200, 301, 404, 500...)', 'Every HTTP status code explained with real-world examples. Bookmark this as your definitive HTTP reference.', 'guides', NULL, NULL, 'guide-v4', 'HTTP status codes', 84, 'queued'),

-- Ring 3: Language concepts (Python — highest volume)
('python-list-comprehensions', 'Python List Comprehensions: Syntax, Examples & When to Use Them', 'List comprehensions are one of Python''s most powerful features. Learn the syntax, nested comprehensions, and filtering with real examples.', 'languages', 'python', 'list-comprehensions', 'lang-v3', 'python list comprehensions', 85, 'queued'),
('python-decorators', 'Python Decorators Explained: A Practical Guide with Examples', 'Decorators modify function behavior without changing the function itself. Learn @property, @staticmethod, and how to write your own.', 'languages', 'python', 'decorators', 'lang-v2', 'python decorators', 83, 'queued'),
('python-async-await', 'Python Async/Await: Complete Guide to Asynchronous Programming', 'Async Python lets you run I/O-bound tasks concurrently. Learn async def, await, asyncio.gather(), and when async actually helps.', 'languages', 'python', 'async-await', 'lang-v1', 'python async await', 82, 'queued'),

-- JavaScript
('javascript-promises', 'JavaScript Promises Explained: then(), catch(), and async/await', 'Promises replaced callback hell. Understand the Promise lifecycle, chaining, error handling, and how async/await simplifies it all.', 'languages', 'javascript', 'promises', 'lang-v3', 'javascript promises', 84, 'queued'),
('javascript-closures', 'JavaScript Closures: What They Are and Why They Matter', 'Closures are fundamental to JavaScript. Learn how functions remember their surrounding scope and why this is useful.', 'languages', 'javascript', 'closures', 'lang-v1', 'javascript closures', 82, 'queued'),
('javascript-array-methods', 'JavaScript Array Methods: map(), filter(), reduce() and More', 'Master the functional array methods that make JavaScript elegant. Real examples with map, filter, reduce, find, and flatMap.', 'languages', 'javascript', 'array-methods', 'lang-v3', 'javascript array methods', 81, 'queued'),

-- TypeScript
('typescript-interfaces-vs-types', 'TypeScript: interface vs type — What''s the Difference?', 'Both interface and type define object shapes in TypeScript, but they''re not identical. Learn when to use each one.', 'languages', 'typescript', 'interfaces-vs-types', 'lang-v1', 'typescript interface vs type', 83, 'queued'),

-- Cross-language (Ring 3 bonus)
('sorting-algorithms-comparison', 'Sorting Algorithms Explained: Python, JS, Go, and Java Side by Side', 'Quick sort, merge sort, bubble sort — implemented in 4 languages. Understand O(n log n) vs O(n²) with visual complexity tables.', 'blog', NULL, NULL, 'blog-v1', 'sorting algorithms comparison', 80, 'queued'),

-- Cheat Sheets
('python-string-methods-cheatsheet', 'Python String Methods Cheat Sheet: split, join, replace, format & More', 'Every Python string method with syntax and examples. The only string reference you''ll need.', 'cheatsheets', 'python', 'string-methods', 'cheatsheet-v2', 'python string methods cheatsheet', 87, 'queued'),
('javascript-array-cheatsheet', 'JavaScript Array Methods Cheat Sheet: Quick Reference Guide', 'All JavaScript array methods at a glance. Includes ES6+ methods with examples and return values.', 'cheatsheets', 'javascript', 'array-methods', 'cheatsheet-v1', 'javascript array cheatsheet', 85, 'queued'),

-- AI/comparison bonus
('chatgpt-vs-gemini-for-developers', 'ChatGPT vs Gemini for Developers: Which AI Wins in 2025?', 'We tested both on real developer tasks: code generation, debugging, documentation, and API quality. Here''s the honest verdict.', 'blog', NULL, NULL, 'blog-v1', 'ChatGPT vs Gemini for developers', 78, 'queued'),

-- Go (expanding languages)
('golang-goroutines-explained', 'Go Goroutines Explained: Concurrency Made Simple', 'Goroutines are Go''s secret weapon for concurrent code. Learn go keyword, channels, WaitGroups, and when goroutines beat threads.', 'languages', 'go', 'goroutines', 'lang-v1', 'golang goroutines', 80, 'queued'),

-- Tool explainers (auto-generated by build-tool.py, but adding manually for launch)
('what-is-base64', 'What is Base64 Encoding? Why Developers Use It', 'Base64 converts binary data to ASCII text for safe transport over text-based protocols. Learn why email, APIs, and JWTs all use it.', 'guides', NULL, NULL, 'guide-v2', 'what is base64', 89, 'queued'),
('unix-timestamp-explained', 'Unix Timestamp: What It Is and How to Convert It', 'Unix timestamps count seconds since January 1, 1970. Learn why developers use them, and how to convert timestamps in any language.', 'guides', NULL, NULL, 'guide-v2', 'unix timestamp', 86, 'queued');
```

Then run the writing pipeline on these specific posts:
```bash
python agents/content-team/run-pipeline.py --steps writer,seo,qa,staging
```

---

### Step 4: Update the Astro Site with Content Stats

```bash
python agents/dev-team/update.py
```

This adds language hubs for Python, JavaScript, TypeScript, Go.

---

### Step 5: Test the Full Build

```bash
npm run build

# Check key pages:
# http://localhost:4321/ → Homepage with post/tool counts
# http://localhost:4321/tools/ → 10 tools listed
# http://localhost:4321/languages/python/ → Python hub
# http://localhost:4321/languages/javascript/ → JavaScript hub
# http://localhost:4321/guides/what-is-rest-api → Guide page
# http://localhost:4321/cheatsheets/python-string-methods-cheatsheet → Cheat sheet

# Run Lighthouse
npx lighthouse http://localhost:4321 --output html --output-path ./lighthouse-report.html
# Target: Performance ≥ 90, SEO ≥ 95, Best Practices ≥ 95, Accessibility ≥ 85
```

---

### Step 6: Publish Seed Content

**Option A: Local publish (immediate)**
```bash
# Publish all staged content at once for launch day
python agents/publish/publish.py --count 20

# Commit and push
git add .
git commit -m "feat: launch devnook.dev — 20 posts + 10 tools"
git push origin main
```

**Option B: GitHub Actions manual trigger**
- Go to GitHub → Actions → "On-Demand Publish (Launch Day)"
- Click "Run workflow"
- Set count: 20, category: all
- This auto-commits and pushes, triggering Cloudflare deploy

---

### Step 7: Cloudflare Pages First Deploy

Cloudflare Pages should auto-deploy on the push from Step 6.

**If first deploy:** Set up Cloudflare Pages in the dashboard:
1. Go to Cloudflare Dashboard → Pages → Create a project
2. Connect GitHub repository
3. Build settings:
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Node.js version: 20
4. Add environment variable: `NODE_VERSION=20`
5. Deploy

---

### Step 8: Submit Sitemap to Google Search Console

1. Go to search.google.com/search-console
2. Add property: `devnook.dev`
3. Verify ownership (use the Cloudflare Pages verification method)
4. Go to Sitemaps → Submit: `https://devnook.dev/sitemap-index.xml`
5. Request indexing for the homepage: URL Inspection → Request Indexing

---

### Step 9: AdSense Setup (Manual — no automation)

1. Go to google.com/adsense → Create account
2. Add site: devnook.dev
3. Add AdSense verification meta tag to `src/layouts/BaseLayout.astro`
4. Submit for review
5. Once approved, add auto-ads script to BaseLayout
6. Wait 2–4 weeks for site review (Google requires some content history)

**Note:** AdSense typically approves sites with:
- At least 15–20 posts
- Privacy Policy and Terms pages
- Real, original content
- No copyright violations

Create these pages before applying:
- `src/pages/privacy-policy.astro`
- `src/pages/terms.astro`
- `src/pages/about.astro`

---

### Step 10: Post-Launch Monitoring

```bash
# Check Cloudflare Pages deploy status
wrangler pages deployment list devnook

# Check what's published vs staged
sqlite3 agents/content-team/registry.db \
  "SELECT status, COUNT(*) FROM posts GROUP BY status;"

# Verify GSC is receiving data (may take 24–48 hours)
# Go to: search.google.com/search-console → Coverage → check indexed pages
```

---

## Post-Launch: Weekly Pipeline Routine

Every week, run the full pipeline to keep content coming:

```bash
# Run on your local machine, ~1 hour
python agents/content-team/run-pipeline.py --steps all

# Check results
sqlite3 agents/content-team/registry.db \
  "SELECT COUNT(*) FROM posts WHERE status='staged';"

# GitHub Actions will drip-publish at 08:00 UTC daily automatically
```

Adjust publishing velocity by editing the `--count` argument in `.github/workflows/drip-publish.yml`:
- Month 1: `--count 2` (60/month)
- Month 2: `--count 3` (90/month)
- Month 3+: `--count 6` (180/month)

---

## Launch Day Success Metrics

- [ ] `https://devnook.dev` is live and loads in < 2 seconds
- [ ] 15+ posts accessible
- [ ] 10+ tools working (test each one manually)
- [ ] Sitemap submitted to Google Search Console
- [ ] No 404 errors on internal links (run `npx broken-link-checker https://devnook.dev`)
- [ ] Lighthouse scores: Performance ≥ 90, SEO ≥ 95
- [ ] GitHub Actions drip publisher runs at 08:00 UTC without errors
- [ ] `content-staging/` has 30+ posts ready for the next 2 weeks of drip
- [ ] AdSense application submitted

---

## Ongoing Operations After Launch

| Task | Frequency | How |
|------|-----------|-----|
| Run content pipeline | Weekly | `python run-pipeline.py --steps all` |
| Build more tools | Monthly | `python build-tool.py --spec {slug}` |
| Update language hubs | After pipeline run | `python update.py` |
| Review QA rejections | Weekly | Check registry.db rejected posts |
| Monitor GSC | Weekly | search.google.com/search-console |
| Check AdSense | Monthly | adsense.google.com |
| Increase publishing velocity | Monthly | Edit drip-publish.yml `--count` |
