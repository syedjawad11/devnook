# DevNook — QA Rejection Criteria

## Automatic Rejection Conditions (fail any = reject)

### Structural Issues
- [ ] Missing required frontmatter field (any field in schema = fail)
- [ ] `title` missing or empty
- [ ] `description` missing, empty, or >160 characters
- [ ] `description` <100 characters (too short for Google)
- [ ] `published_date` missing or invalid format (must be YYYY-MM-DD)
- [ ] `template_id` not in the valid 22-ID list
- [ ] `category` not one of: languages, guides, blog, cheatsheets, tools

### Content Quality
- [ ] Word count below minimum for content type (see seo-writing-rules.md)
- [ ] Zero code blocks in a language post or guide
- [ ] Fewer than 3 internal links
- [ ] More than 8 internal links
- [ ] Any internal link pointing to a non-existent slug in registry.db
- [ ] Contains any banned phrase from devnook-brand-voice.md
- [ ] Title is identical to an existing post in registry.db
- [ ] First 8 words of title match an existing post

### Duplicate Detection
- [ ] Slug already exists in registry.db (exact match = immediate reject)
- [ ] TF-IDF similarity >70% against any approved/staged/published post
- [ ] >40% sentence-level overlap with any existing post

### Technical Issues
- [ ] Frontmatter YAML is invalid/unparseable
- [ ] Any Markdown heading skips a level (H1→H3 without H2 = fail)
- [ ] Code block missing language tag (``` without python/js/etc.)
- [ ] Internal link format incorrect (must start with /)

## Warning Conditions (flag but do not reject)
- Word count between minimum and +10% of minimum (low but acceptable)
- Fewer than 5 internal links (recommend adding more)
- No H3 subsections (acceptable for short posts)
- Title over 65 characters (may truncate in SERPs)
- Meta description between 130–140 chars (tight but ok)

## Similarity Check Implementation
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_similarity(new_content: str, existing_contents: list[str]) -> float:
    """Returns max similarity score (0–1). Reject if > 0.70"""
    if not existing_contents:
        return 0.0
    corpus = existing_contents + [new_content]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    return float(scores.max())
```

## QA Output Format
The QA agent writes a structured result to registry.db for each post:

```json
{
  "slug": "python-list-comprehensions",
  "qa_status": "approved",  // or "rejected" or "warning"
  "qa_timestamp": "2024-01-15T10:30:00Z",
  "word_count": 1247,
  "similarity_score": 0.23,
  "internal_links": 4,
  "rejections": [],
  "warnings": ["title_length: 68 chars"]
}
```

## Registry.db QA Status Update
When a post passes QA: update `status` column to `approved`.
When a post fails QA: update `status` to `rejected`, log reason in `qa_notes` column.
Rejected posts are NOT deleted — they stay in registry.db for pattern analysis.
