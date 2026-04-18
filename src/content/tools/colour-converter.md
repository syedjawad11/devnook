---
title: Colour Converter — Free Online Tool
description: Convert between HEX, RGB, HSL, and CSS named colours instantly in your browser. No data sent to servers.
category: tools
tool_slug: colour-converter
template_id: tool-exp-v1
tags:
- colour
- color
- hex
- rgb
- hsl
- css
- converter
related_tools:
- meta-tag-generator
- hash-generator
related_content:
- css-colour-guide
- css-variables-explained
published_date: '2026-04-18'
og_image: /og/tools/colour-converter.png
---

## What is the Colour Converter?

The Colour Converter is a free browser-based tool that instantly translates colour values between HEX, RGB, HSL, and CSS named colour formats. Whether you are a web designer working with a brand colour palette or a developer translating design tokens into code, this converter handles all common CSS colour representations with one click.

All conversions happen entirely in your browser — no colour values are sent to any server.

## How to Use the Colour Converter

1. Enter a colour value in any input field: HEX (`#3b82f6`), RGB (`rgb(59, 130, 246)`), HSL (`hsl(217, 91%, 60%)`), or a CSS named colour (`steelblue`)
2. Click **Convert**
3. All other fields update instantly with the equivalent values
4. Use the **Copy** button next to any field to copy that format to your clipboard
5. Click **Clear** to reset all fields

## Colour Format Reference

**HEX** — A six-digit hexadecimal code prefixed with `#`. Shorthand 3-digit codes like `#f0f` are also accepted and expanded automatically.

**RGB** — Red, Green, Blue channels each ranging from 0 to 255. Accepts `rgb(r, g, b)` format.

**HSL** — Hue (0–360°), Saturation (0–100%), Lightness (0–100%). More intuitive for adjusting colour variations — decrease lightness to darken, increase saturation to make colours more vivid.

**CSS Named Colour** — Plain English names like `cornflowerblue` or `tomato`. The converter resolves them by computing the browser's interpreted RGB value.

## Common Use Cases

- **Design-to-code handoff** — Convert Figma HEX values to the HSL format your CSS variables use
- **Accessibility checks** — Use HSL to understand relative lightness and adjust contrast ratios
- **Brand colour consistency** — Keep HEX, RGB, and HSL equivalents in sync across a design system
- **Tailwind CSS configuration** — Convert palette colours from RGB (used in design tools) to HEX (used in `tailwind.config.js`)

## Frequently Asked Questions

**Why does HSL not round-trip perfectly back to the same HEX?**  
Rounding to whole-number HSL values loses fractional precision, so converting HEX → HSL → HEX may produce a one-digit difference. For exact colour preservation, use HEX or RGB.

**Does this tool support alpha/transparency?**  
Not currently. Transparent colours (`rgba`, `hsla`) are not supported — use the HEX, RGB, or HSL formats only.
