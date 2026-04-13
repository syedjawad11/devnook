#!/usr/bin/env python3
"""
DevNook Tools Team — build-tool.py
Reads a tool spec JSON and generates 3 files per tool:
1. src/components/tools/{slug}.astro  — interactive UI component
2. src/pages/tools/{slug}.astro        — tool page
3. src/content/tools/{slug}.md         — SEO explainer (200–300 words)

All tools are client-side only. No Cloudflare Workers, no API calls.

Usage:
  python agents/tools-team/build-tool.py --spec json-formatter
  python agents/tools-team/build-tool.py --all
  python agents/tools-team/build-tool.py --batch 1
  python agents/tools-team/build-tool.py --list
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import date
from dotenv import load_dotenv

# Ensure project root is in sys.path so `agents.utils` resolves correctly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

from agents.utils.llm_router import route

SKILLS_DIR = PROJECT_ROOT / "agents" / "skills"
SPECS_DIR = PROJECT_ROOT / "agents" / "tools-team" / "tool-specs"

# Load skill files once at startup
TOOL_CONVENTIONS = (SKILLS_DIR / "tool-build-patterns.md").read_text(encoding="utf-8")
ASTRO_CONVENTIONS = (SKILLS_DIR / "astro-conventions.md").read_text(encoding="utf-8")
SEO_RULES = (SKILLS_DIR / "seo-writing-rules.md").read_text(encoding="utf-8")
BRAND_VOICE = (SKILLS_DIR / "devnook-brand-voice.md").read_text(encoding="utf-8")

SYSTEM_PROMPT = f"""You are an expert developer building tools for devnook.dev — a developer resource site.

ASTRO CONVENTIONS:
{ASTRO_CONVENTIONS}

TOOL BUILD PATTERNS:
{TOOL_CONVENTIONS}

SEO RULES:
{SEO_RULES}

BRAND VOICE:
{BRAND_VOICE}

CRITICAL RULES:
- Return ONLY the file content — no markdown fences, no explanations
- All JavaScript must be vanilla JS (no React, Vue, Svelte, etc.)
- Use CSS custom properties from tokens.css (--color-*, --space-*, --font-*)
- Every interactive element needs aria-labels
- All tools must work 100% client-side — zero external HTTP requests
"""


# ---------------------------------------------------------------------------
# Spec loader
# ---------------------------------------------------------------------------

def load_spec(slug: str) -> dict:
    spec_path = SPECS_DIR / f"{slug}.json"
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec not found: {spec_path}")
    return json.loads(spec_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_tool_component(spec: dict) -> str:
    controls_json = json.dumps(spec.get("controls", []), indent=2)
    features_json = json.dumps(spec.get("features", []), indent=2)

    prompt = f"""Generate the Astro component file `src/components/tools/{spec['slug']}.astro` for this tool:

Tool name: {spec['name']}
Slug: {spec['slug']}
Description: {spec['description']}
Category: {spec['category']}
Input label: {spec.get('input_label', 'Input')}
Output label: {spec.get('output_label', 'Output')}

Features:
{features_json}

Controls:
{controls_json}

Requirements:
- Vanilla JavaScript only (no frameworks)
- Mobile-responsive layout using CSS custom properties
- Accessible: aria-labels on all controls, aria-live="polite" on status messages
- Copy-to-clipboard button with visual feedback ("Copied!" for 2 seconds)
- Clear/reset button
- Error handling: show user-friendly error messages in a visible error div
- All logic inside a <script> tag (no external JS files)
- Wrap all JS in a self-invoking function or use DOMContentLoaded
- Use semantic HTML (textarea, button, select, label elements)

Return ONLY the .astro file content. No markdown fences. No explanation."""

    result = route("tool_builder", SYSTEM_PROMPT, prompt, max_tokens=4000)
    return result.text


def generate_tool_page(spec: dict) -> str:
    prompt = f"""Generate the Astro page `src/pages/tools/{spec['slug']}.astro` for devnook.dev.

Tool slug: {spec['slug']}
Tool name: {spec['name']}
Description: {spec['description']}
Primary keyword: {spec['primary_keyword']}
Related tools: {', '.join(spec.get('related_tools', []))}

Requirements:
- Import and use ToolLayout from '@layouts/ToolLayout.astro'
- Import the tool component from '@components/tools/{spec['slug']}.astro'
- Include JSON-LD schema.org SoftwareApplication structured data
- Pass title, description, and slug props to ToolLayout
- Show the tool component prominently
- Include a "Related Tools" section with links if related_tools is not empty
- The page should be self-contained (no extra fetches)

Return ONLY the .astro file content. No markdown fences. No explanation."""

    result = route("tool_builder", SYSTEM_PROMPT, prompt, max_tokens=2000)
    return result.text


def generate_seo_explainer(spec: dict) -> str:
    today = date.today().isoformat()
    features_str = "\n".join(f"- {f}" for f in spec.get("features", []))
    keywords_str = ", ".join(spec.get("seo_keywords", []))
    related_tools_str = ", ".join(spec.get("related_tools", []))

    prompt = f"""Write the SEO explainer Markdown file `src/content/tools/{spec['slug']}.md` for devnook.dev.

Tool: {spec['name']}
Slug: {spec['slug']}
Description: {spec['description']}
Primary keyword: {spec['primary_keyword']}
SEO keywords: {keywords_str}
Related tools: {related_tools_str}
Published date: {today}
Template: {spec.get('template_id', 'tool-exp-v1')}

Features:
{features_str}

Requirements:
- Start with YAML frontmatter: title, description, publishedDate, primaryKeyword, seoKeywords (array), relatedTools (array), template, tier: "client-side"
- Body: 200–300 words
- Structure: What is [tool name] → How to use it → When to use it → FAQ (2–3 questions)
- Naturally use the primary keyword 2–3 times
- Use H2 for section headers
- Write in the devnook brand voice: direct, developer-friendly, no fluff
- End with a brief CTA linking to the tool

Return ONLY the Markdown file content. No code fences. No explanation."""

    result = route("tool_builder", SYSTEM_PROMPT, prompt, max_tokens=2000)
    return result.text


# ---------------------------------------------------------------------------
# File writer
# ---------------------------------------------------------------------------

def write_file(rel_path: str, content: str):
    full_path = PROJECT_ROOT / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"  [ok] {rel_path}")


# ---------------------------------------------------------------------------
# Build orchestrator
# ---------------------------------------------------------------------------

def build_tool(slug: str):
    print(f"\n-> Building: {slug}")
    spec = load_spec(slug)

    write_file(f"src/components/tools/{slug}.astro", generate_tool_component(spec))
    write_file(f"src/content/tools/{slug}.md", generate_seo_explainer(spec))
    write_file(f"src/pages/tools/{slug}.astro", generate_tool_page(spec))

    print(f"  Done: {spec['name']}".encode("ascii", errors="replace").decode("ascii"))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="DevNook build-tool.py — generate tool files from spec JSON"
    )
    parser.add_argument("--spec", metavar="SLUG", help="Build a single tool by slug")
    parser.add_argument("--all", action="store_true", help="Build all tool specs")
    parser.add_argument("--batch", type=int, choices=[1, 2, 3, 4], help="Build all tools in a specific batch")
    parser.add_argument("--list", action="store_true", help="List all available specs")
    args = parser.parse_args()

    if args.list:
        specs = sorted(SPECS_DIR.glob("*.json"))
        print(f"Found {len(specs)} specs:")
        for s in specs:
            data = json.loads(s.read_text(encoding="utf-8"))
            batch = data.get("batch", "?")
            print(f"  [batch {batch}] {data['slug']} — {data['name']}")
        return

    if args.spec:
        build_tool(args.spec)
        return

    if args.all or args.batch:
        specs = sorted(SPECS_DIR.glob("*.json"))
        selected = []
        for spec_file in specs:
            data = json.loads(spec_file.read_text(encoding="utf-8"))
            if args.batch and data.get("batch") != args.batch:
                continue
            selected.append(data["slug"])

        print(f"Building {len(selected)} tools...")
        failed = []
        for slug in selected:
            try:
                build_tool(slug)
            except Exception as e:
                print(f"  [error] {slug}: {e}")
                failed.append(slug)

        print(f"\nDone. {len(selected) - len(failed)}/{len(selected)} built successfully.")
        if failed:
            print(f"Failed: {', '.join(failed)}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
