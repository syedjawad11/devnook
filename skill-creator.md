---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

This skill guides you through creating, testing, and optimizing Claude Code skills (SKILL.md files).

## Workflow Overview

1. **Draft** — Capture user intent and write SKILL.md
2. **Test** — Run test cases and evaluate performance
3. **Review** — Human review of outputs
4. **Improve** — Generalize from feedback, iterate
5. **Optimize** — Tune description for accurate triggering

## Communicating with the User

Adjust technical terminology based on user familiarity:
- "evaluation" and "benchmark" are acceptable baseline terms
- "JSON" and "assertion" require contextual cues before use without explanation

---

## Creating a Skill

### Step 1: Capture Intent
Ask the user:
- What task should this skill handle?
- What are the inputs and outputs?
- When should it trigger (and when should it NOT)?
- What would success look like?

### Step 2: Research
- Look at existing skills for format and style
- Understand the domain well enough to write accurate instructions

### Step 3: Write SKILL.md

Required frontmatter:
```yaml
---
name: skill-name
description: Precise trigger description — when to use and when NOT to use this skill.
---
```

Guidelines for the description:
- Be specific about what triggers the skill
- Include explicit "do NOT use when" conditions
- Use domain-specific language the user would naturally use

The body should contain:
- Clear step-by-step instructions
- Examples where helpful
- Edge cases and exceptions
- Reference to any scripts or tools needed

---

## Running and Evaluating Test Cases

1. Create test prompts that should (and shouldn't) trigger the skill
2. Draft assertions: what should the output contain or avoid?
3. Capture timing and token metrics
4. Grade outputs: does the skill improve results vs. no skill?
5. Launch side-by-side comparison for human review

---

## Improving the Skill

- Generalize from feedback — don't overfit to specific examples
- Keep instructions lean — remove redundancy
- Understand the *why* behind each requirement before changing it
- If a rule seems wrong, ask the user before removing it

---

## Description Optimization

The description field controls when the skill triggers. To optimize:
1. Write 10-20 test prompts that should trigger the skill
2. Write 10-20 prompts that should NOT trigger it
3. Run automated evaluation loop
4. Adjust description wording until accuracy is high

---

## Skill File Structure

```
~/.claude/skills/
  my-skill.md          # Simple single-file skills
  
  my-complex-skill/    # Multi-file skills
    SKILL.md
    reference/
      guide.md
    scripts/
      helper.py
```

For single-purpose skills, a single .md file is sufficient.
For skills with reference material or scripts, use a folder with SKILL.md.
