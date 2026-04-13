# DevNook — Brand Voice & Writing Style

## Brand Identity
DevNook is a **developer resource site**, not a blog. The tone is professional, direct, and genuinely helpful. We respect the reader's time and intelligence.

## Target Audience
- **Primary**: Mid-level developers (2–5 years experience) who want quick, reliable reference
- **Secondary**: Beginners who are searching for clear explanations
- **Never talk down** to the reader. Assume they know the basics of their language.
- **Never over-explain** basics that any developer knows (what a variable is, etc.)

## Tone
- Direct and confident, not hedging ("This will", not "This might")
- Conversational but not casual (no slang, no "Let's dive in!", no "Buckle up!")
- No filler phrases: banned list below
- Technically precise — correct over simple when the distinction matters

## Banned Phrases (QA will flag these)
- "Let's dive in"
- "Buckle up"
- "In this article, we will..."
- "Without further ado"
- "It's worth noting that"
- "In conclusion" / "To summarize" / "In summary"
- "At the end of the day"
- "Game-changer"
- "Leverage" (as a verb)
- Excessive exclamation marks (max 1 per post, ideally 0)

## Opening Paragraphs
- First sentence: state the answer or frame the problem — do NOT start with a question
- Wrong: "Have you ever wondered how Python handles list comprehensions?"
- Right: "Python list comprehensions let you build lists in a single line using a compact, readable syntax."
- Keep under 3 sentences. Get to the code/content fast.

## Code Examples
- Always real, working code (not pseudocode)
- Include output/result in a comment or separate block when helpful
- Python: use f-strings, not `.format()` or `%s` (unless the post is specifically about those)
- JavaScript: use `const`/`let`, not `var`; arrow functions preferred
- Add a brief comment explaining non-obvious lines
- For comparison posts: show equivalent code in both languages side by side

## Explanatory Style
- Explain concepts by showing them in code first, then explaining why it works
- Use bullet lists for features/characteristics; use numbered lists only for steps
- Max 3 bullet points before breaking into H3 subsections
- Tables: use for comparisons, parameter references, type listings

## Closing Paragraphs
- DO: Point to related content ("For more on X, see our guide to Y")
- DO: Summarize the key takeaway in one sentence
- DON'T: Add "I hope this helped!" or "Happy coding!" type sign-offs

## Post Formatting Checklist
- [ ] No banned phrases
- [ ] First paragraph under 3 sentences with direct opening
- [ ] Code blocks have language tags
- [ ] At least 3 internal links with descriptive anchor text
- [ ] Heading hierarchy is H1 → H2 → H3 (no skipping)
- [ ] Meta description is 140–160 chars
