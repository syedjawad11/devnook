# DevNook — Content Schema

## Content Types & Template IDs

### Language Posts (`/languages/{lang}/{concept}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| lang-v1 | Definition First | Terminology, what-is questions |
| lang-v2 | Problem First | How-to, debugging topics |
| lang-v3 | Code First | Syntax, operators, built-ins |
| lang-v4 | Concept Across Languages | Cross-language comparisons |
| lang-v5 | Tutorial/Build-Along | Step-by-step project posts |

### Guides (`/guides/{slug}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| guide-v1 | Encyclopedia | Deep reference topics |
| guide-v2 | Quick Answer + Deep Dive | FAQ-style topics |
| guide-v3 | Problem → Solution | Debugging, troubleshooting |
| guide-v4 | Reference Card | Cheat-sheet style guides |

### Blog Posts (`/blog/{slug}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| blog-v1 | Head-to-Head Comparison | X vs Y posts |
| blog-v2 | Use-Case Driven Comparison | "When to use X vs Y" |
| blog-v3 | Listicle | Top N lists |
| blog-v4 | Deep-Dive Editorial | Opinion/analysis pieces |
| blog-v5 | How-To Tutorial | Practical walkthroughs |

### Cheat Sheets (`/cheatsheets/{subject}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| cheatsheet-v1 | Syntax Reference | Language syntax, operators |
| cheatsheet-v2 | Task-Oriented | "How do I..." reference |
| cheatsheet-v3 | Tiered Beginner→Advanced | Skill-level progression |
| cheatsheet-v4 | Two-Column Comparison | Side-by-side reference |

### Tool Explainers (`/tools/{slug}`)
| Template ID | Name | Best for |
|-------------|------|----------|
| tool-exp-v1 | What + Why + How | General tool pages |
| tool-exp-v2 | Problem First | Pain-point-led pages |
| tool-exp-v3 | Feature Focused | Feature-rich tools |
| tool-exp-v4 | FAQ Style | Common-question-heavy tools |

Template files are at: `templates/templates/{type}/{template-id}.md`

## Frontmatter Schemas

### Language Post
```yaml
---
title: "How to {concept} in {Language}"
description: "{1–2 sentence description targeting primary keyword, under 160 chars}"
category: languages
language: python  # lowercase slug
concept: list-comprehensions  # kebab-case
template_id: lang-v1
tags: [python, list-comprehension, functional-programming]
related_posts:
  - /languages/python/generators
  - /languages/python/lambda-functions
related_tools:
  - /tools/python-repl
published_date: "YYYY-MM-DD"
og_image: "/og/languages/{lang}/{concept}.png"
word_count_target: 1200  # minimum
---
```

### Guide
```yaml
---
title: "{Topic}: A Complete Guide"
description: "{description under 160 chars}"
category: guides
template_id: guide-v1
tags: [tag1, tag2, tag3]
related_posts:
  - /languages/python/...
related_tools:
  - /tools/...
published_date: "YYYY-MM-DD"
og_image: "/og/guides/{slug}.png"
word_count_target: 1800
---
```

### Blog Post
```yaml
---
title: "{title}"
description: "{description}"
category: blog
template_id: blog-v1
tags: [tag1, tag2]
related_posts: []
related_tools: []
published_date: "YYYY-MM-DD"
og_image: "/og/blog/{slug}.png"
word_count_target: 1500
---
```

### Cheat Sheet
```yaml
---
title: "{Language/Topic} Cheat Sheet"
description: "{description}"
category: cheatsheets
language: python  # if applicable
template_id: cheatsheet-v1
tags: [tag1, tag2]
related_posts: []
related_tools: []
published_date: "YYYY-MM-DD"
og_image: "/og/cheatsheets/{subject}.png"
downloadable: true
---
```

### Tool Explainer
```yaml
---
title: "{Tool Name} — Free Online Tool"
description: "{description}"
category: tools
tool_slug: json-formatter
template_id: tool-exp-v1
tags: [tag1, tag2]
related_tools: []
related_content: []
published_date: "YYYY-MM-DD"
og_image: "/og/tools/{slug}.png"
word_count_target: 600
---
```

## Post Status Flow

```
discovered → queued → drafted → optimized → approved → staged → published
```

- `discovered`: keyword found, not yet planned
- `queued`: assigned template and language, ready for writing
- `drafted`: writer agent output exists, not yet SEO-optimized
- `optimized`: SEO optimizer has processed it
- `approved`: QA agent passed it
- `staged`: file moved to /content-staging/
- `published`: drip publisher moved it to /src/content/ and deployed

## Target Languages (Ring 3)
python, javascript, typescript, go, rust, java, csharp, php, ruby, swift, kotlin, cpp

## Content Volume Targets
- Ring 1 (tool-adjacent): ~80 posts
- Ring 2 (web dev fundamentals): ~200 posts
- Ring 3 (language concepts): ~600+ posts (50 concepts × 12 languages)
- Bonus (AI/comparison/editorial): ~200 posts
- **Total target: 1,000+ posts**
