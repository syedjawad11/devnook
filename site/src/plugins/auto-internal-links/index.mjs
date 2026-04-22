/**
 * rehype-auto-internal-links
 *
 * A build-time plugin for Astro that automatically inserts internal links
 * into markdown content based on per-post `linkAnchors` metadata or
 * auto-derived anchors from title + slug (when `autoAnchors: true`).
 *
 * ---------------------------------------------------------------------------
 * Architecture
 * ---------------------------------------------------------------------------
 *   1. At build time, scan every markdown file in the content directory.
 *   2. For each post with `linkAnchors` in frontmatter (or derived anchors
 *      when autoAnchors is enabled), register each anchor phrase pointing to
 *      that post's URL.
 *   3. When processing a post's HTML (HAST), walk the tree and replace the
 *      first matching occurrence of each registered anchor with an <a> tag,
 *      respecting per-page and per-target caps.
 *
 * ---------------------------------------------------------------------------
 * Data model
 * ---------------------------------------------------------------------------
 *   - No database. No runtime state. Everything lives in git.
 *   - Per-post anchors live in frontmatter (explicit wins over auto-derived):
 *       ---
 *       linkAnchors:
 *         - "binary search"
 *         - "bisection algorithm"
 *       ---
 *   - Configuration lives in astro.config.mjs.
 *
 * ---------------------------------------------------------------------------
 * Uninstall
 * ---------------------------------------------------------------------------
 *   Delete the plugin folder and remove the rehypePlugins entry from
 *   astro.config.mjs. The `linkAnchors` fields in frontmatter become
 *   inert (Astro ignores unknown fields). Nothing to clean up anywhere.
 */

import fs from 'node:fs';
import path from 'node:path';
import fg from 'fast-glob';
import matter from 'gray-matter';

// ============================================================================
// DEFAULT OPTIONS
// ============================================================================

const DEFAULT_OPTIONS = {
  // Where to look for markdown files that declare linkAnchors.
  // Path is relative to the project root (where astro.config.mjs lives).
  contentDir: 'src/content',

  // Maximum outgoing links to insert in a single post. 0 = unlimited.
  maxLinksPerPage: 8,

  // Maximum times the same target URL can be linked from one post.
  maxLinksPerTarget: 1,

  // If true, "Binary Search" matches "binary search". Recommended true.
  caseInsensitive: true,

  // HTML elements whose contents are never linked.
  excludeTags: [
    'a', 'code', 'pre', 'kbd', 'samp', 'var',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'script', 'style', 'textarea', 'button',
  ],

  // CSS class names that cause their subtree to be skipped.
  excludeClasses: ['no-auto-link'],

  // Class added to every auto-inserted <a> tag.
  linkClass: 'auto-internal-link',

  // If true, logs what the plugin WOULD link without modifying output.
  dryRun: false,

  // Optional URL builder. Converts a markdown file path + frontmatter into
  // the URL that post lives at on your site.
  urlBuilder: defaultUrlBuilder,

  // Verbose logging during build (anchor index size, per-file summary).
  verbose: false,

  // When true, auto-derive anchor phrases from title + slug for posts that
  // have no explicit `linkAnchors` frontmatter. Explicit linkAnchors always
  // win. For `languages` collection, also registers the bare language name
  // pointing to its index page (once per language).
  autoAnchors: false,
};

// ============================================================================
// DEFAULT URL BUILDER
// ============================================================================

/**
 * Default URL builder. Handles simple Astro content-collection layouts where
 * each .md file maps directly to a URL path.
 */
function defaultUrlBuilder({ filePath, frontmatter, contentDir }) {
  if (frontmatter.permalink) return frontmatter.permalink;
  if (frontmatter.url) return frontmatter.url;

  let rel = path.relative(contentDir, filePath);
  rel = rel.replace(/\.(md|mdx)$/i, '');
  rel = rel.replace(/[\\/]index$/, '');

  if (frontmatter.slug) {
    const dir = path.dirname(rel);
    rel = (dir === '.' || dir === '') ? frontmatter.slug : `${dir}/${frontmatter.slug}`;
  }

  rel = rel.split(path.sep).join('/');
  return '/' + rel.replace(/^\/+|\/+$/g, '') + '/';
}

// ============================================================================
// REGEX HELPERS
// ============================================================================

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Build a Unicode-safe, word-boundary-aware regex for a phrase.
 */
function buildRegex(phrase, caseInsensitive) {
  const pattern = `(?<![\\p{L}\\p{N}_])(${escapeRegex(phrase)})(?![\\p{L}\\p{N}_])`;
  return new RegExp(pattern, caseInsensitive ? 'iu' : 'u');
}

// ============================================================================
// AUTO-ANCHOR HELPERS
// ============================================================================

/**
 * Strip common marketing suffixes from post titles so they read naturally as
 * anchor text: "JavaScript Array Methods | DevNook" → "JavaScript Array Methods"
 */
function cleanTitle(title) {
  return title
    .replace(/\s*\|.*$/, '')
    .replace(/\s*-\s*(online tool|free tool|tool)\b.*/i, '')
    .replace(/\s*\([^)]*\)\s*$/, '')
    .trim();
}

/**
 * Convert a kebab-case slug to a human-readable phrase.
 * "javascript-array-methods" → "javascript array methods"
 */
function humanizeSlug(slug) {
  return slug.replace(/-/g, ' ').trim();
}

/**
 * Return true for phrases too short/generic to be useful anchors.
 * Rule: fewer than 2 words AND fewer than 6 characters.
 * Examples filtered: "Go" (2 chars, 1 word), "C" (1 char).
 * Examples kept: "Python" (6 chars), "javascript array" (2 words).
 */
function isTooShort(phrase) {
  const words = phrase.trim().split(/\s+/);
  return words.length < 2 && phrase.length < 6;
}

/**
 * Derive anchor phrases for a post that has no explicit `linkAnchors`.
 * Returns an array of { phrase, targetUrl }.
 */
function deriveAutoAnchors(filePath, fm, url, absContentDir, seenLangUrls) {
  const phrases = [];
  const relParts = path.relative(absContentDir, filePath).split(path.sep);
  const collection = relParts[0];
  const fileBase = path.basename(filePath).replace(/\.(md|mdx)$/i, '');

  // 1. Title-derived anchor
  const rawTitle = typeof fm.title === 'string' ? fm.title : '';
  const cleanedTitle = rawTitle ? cleanTitle(rawTitle) : '';
  if (cleanedTitle && !isTooShort(cleanedTitle)) {
    phrases.push({ phrase: cleanedTitle, targetUrl: url });
  }

  // 2. Humanized slug (skip if identical to cleaned title, case-insensitive)
  const slugPhrase = humanizeSlug(fileBase);
  if (slugPhrase && !isTooShort(slugPhrase)) {
    if (slugPhrase.toLowerCase() !== cleanedTitle.toLowerCase()) {
      phrases.push({ phrase: slugPhrase, targetUrl: url });
    }
  }

  // 3. Language name anchor (languages collection only, once per language)
  if (collection === 'languages' && relParts.length >= 2) {
    const langName = relParts[1];
    if (langName && !isTooShort(langName) && !seenLangUrls.has(langName)) {
      seenLangUrls.add(langName);
      phrases.push({ phrase: langName, targetUrl: `/languages/${langName}/` });
    }
  }

  return phrases;
}

// ============================================================================
// ANCHOR INDEX (built once per build process, cached in module scope)
// ============================================================================

let anchorCache = null;
let anchorCacheKey = null;

/**
 * Scan the content directory and produce a priority-sorted list of anchors.
 *
 * Each anchor is:
 *   { phrase, url, sourceFile, regex, wordCount, charCount }
 *
 * Anchors are sorted longest-first so "binary search tree" is tried before
 * "binary search" before "search".
 */
async function buildAnchorIndex(options) {
  const { contentDir, caseInsensitive, urlBuilder, verbose, autoAnchors } = options;
  const absContentDir = path.resolve(process.cwd(), contentDir);

  if (!fs.existsSync(absContentDir)) {
    console.warn(
      `[auto-internal-links] Content directory not found: ${absContentDir}. ` +
      `No links will be inserted. Check the \`contentDir\` option in astro.config.mjs.`
    );
    return [];
  }

  const files = await fg('**/*.{md,mdx}', {
    cwd: absContentDir,
    absolute: true,
    dot: false,
  });

  const anchors = [];
  const seenPhrases = new Map(); // phrase.toLowerCase() -> first source file
  const seenLangUrls = new Set(); // language names that have claimed their index URL

  for (const filePath of files) {
    let parsed;
    try {
      const raw = fs.readFileSync(filePath, 'utf-8');
      parsed = matter(raw);
    } catch (err) {
      console.warn(`[auto-internal-links] Failed to read ${filePath}: ${err.message}`);
      continue;
    }

    const fm = parsed.data || {};

    if (fm.excludeFromLinking === true) continue;
    if (fm.draft === true) continue;

    const hasExplicitAnchors = Array.isArray(fm.linkAnchors) && fm.linkAnchors.length > 0;
    if (!hasExplicitAnchors && !autoAnchors) continue;

    let url;
    try {
      url = urlBuilder({ filePath, frontmatter: fm, contentDir: absContentDir });
    } catch (err) {
      console.warn(
        `[auto-internal-links] urlBuilder threw for ${filePath}: ${err.message}. Skipping.`
      );
      continue;
    }

    // Determine phrases to register: explicit frontmatter wins over auto-derived.
    let phrasesToRegister;
    if (hasExplicitAnchors) {
      phrasesToRegister = fm.linkAnchors
        .filter(p => typeof p === 'string')
        .map(p => ({ phrase: p.trim(), targetUrl: url }))
        .filter(({ phrase }) => phrase.length > 0);
    } else {
      phrasesToRegister = deriveAutoAnchors(filePath, fm, url, absContentDir, seenLangUrls);
    }

    for (const { phrase, targetUrl } of phrasesToRegister) {
      // Duplicate anchor detection: first file wins, second is warned and ignored.
      const lc = phrase.toLowerCase();
      if (seenPhrases.has(lc)) {
        console.warn(
          `[auto-internal-links] Duplicate anchor "${phrase}" in ${filePath} ` +
          `(first claimed by ${seenPhrases.get(lc)}). Second claim ignored.`
        );
        continue;
      }
      seenPhrases.set(lc, filePath);

      anchors.push({
        phrase,
        url: targetUrl,
        sourceFile: filePath,
        regex: buildRegex(phrase, caseInsensitive),
        wordCount: phrase.split(/\s+/).length,
        charCount: phrase.length,
      });
    }
  }

  // Longest-match-first: sort by word count desc, then char count desc.
  anchors.sort((a, b) => {
    if (b.wordCount !== a.wordCount) return b.wordCount - a.wordCount;
    return b.charCount - a.charCount;
  });

  if (verbose) {
    console.log(
      `[auto-internal-links] Built anchor index: ${anchors.length} anchors ` +
      `from ${files.length} content files`
    );
  }

  return anchors;
}

// ============================================================================
// TREE WALKING & LINK INSERTION
// ============================================================================

/**
 * Test each anchor against a text node's value and return info about the
 * first viable match (respecting caps). Returns null if no match.
 */
function findMatch(textNode, state) {
  if (state.maxLinksPerPage > 0 && state.linkCount >= state.maxLinksPerPage) return null;

  for (const anchor of state.anchors) {
    if (state.maxLinksPerPage > 0 && state.linkCount >= state.maxLinksPerPage) return null;
    if (state.usedAnchors.has(anchor.phrase.toLowerCase())) continue;
    if (state.currentUrl && anchor.url === state.currentUrl) continue;

    if (state.maxLinksPerTarget > 0) {
      const count = state.perTarget.get(anchor.url) || 0;
      if (count >= state.maxLinksPerTarget) continue;
    }

    const match = textNode.value.match(anchor.regex);
    if (!match) continue;

    return { anchor, match };
  }

  return null;
}

/**
 * Commit the state update for a successful link — used in both live and
 * dry-run modes.
 */
function commitLink(anchor, state) {
  state.linkCount++;
  state.usedAnchors.add(anchor.phrase.toLowerCase());
  state.perTarget.set(anchor.url, (state.perTarget.get(anchor.url) || 0) + 1);

  if (state.dryRun) {
    state.dryRunLog.push({
      anchor: anchor.phrase,
      target: anchor.url,
    });
  }
}

/**
 * Build the replacement HAST nodes for a matched text node.
 */
function buildReplacement(textNode, match, anchor, state) {
  const before = textNode.value.slice(0, match.index);
  const matched = match[0];
  const after = textNode.value.slice(match.index + matched.length);

  const linkNode = {
    type: 'element',
    tagName: 'a',
    properties: {
      href: anchor.url,
      className: [state.linkClass],
      'data-auto-link': 'true',
    },
    children: [{ type: 'text', value: matched }],
  };

  const replacement = [];
  if (before) replacement.push({ type: 'text', value: before });
  replacement.push(linkNode);
  if (after) replacement.push({ type: 'text', value: after });

  return replacement;
}

/**
 * Walk the HAST tree, inserting links where appropriate.
 *
 * Manual walker (not unist-util-visit) because we modify the tree during
 * traversal and need fine-grained control over iteration.
 */
function processTree(tree, state) {
  function walk(node) {
    if (state.maxLinksPerPage > 0 && state.linkCount >= state.maxLinksPerPage) return;
    if (!node || !node.children) return;

    if (node.type === 'element') {
      if (state.excludeTags.includes(node.tagName)) return;

      const classProp = node.properties && node.properties.className;
      const classList = Array.isArray(classProp)
        ? classProp
        : (typeof classProp === 'string' ? classProp.split(/\s+/) : []);
      if (classList.some((c) => state.excludeClasses.includes(c))) return;
    }

    let i = 0;
    while (i < node.children.length) {
      if (state.maxLinksPerPage > 0 && state.linkCount >= state.maxLinksPerPage) return;
      const child = node.children[i];

      if (child.type === 'text') {
        const found = findMatch(child, state);
        if (found) {
          commitLink(found.anchor, state);

          if (state.dryRun) {
            i += 1;
          } else {
            const replacement = buildReplacement(child, found.match, found.anchor, state);
            node.children.splice(i, 1, ...replacement);
            if (replacement[0].type === 'element') {
              i += 1;
            }
          }
        } else {
          i += 1;
        }
      } else if (child.type === 'element' || child.type === 'root') {
        walk(child);
        i += 1;
      } else {
        i += 1;
      }
    }
  }

  walk(tree);
}

// ============================================================================
// PLUGIN ENTRY POINT
// ============================================================================

export default function rehypeAutoInternalLinks(userOptions = {}) {
  const options = { ...DEFAULT_OPTIONS, ...userOptions };

  const cacheKey = JSON.stringify({
    contentDir: options.contentDir,
    caseInsensitive: options.caseInsensitive,
    autoAnchors: !!options.autoAnchors,
  });

  return async function transformer(tree, file) {
    if (anchorCache === null || anchorCacheKey !== cacheKey) {
      anchorCache = await buildAnchorIndex(options);
      anchorCacheKey = cacheKey;
    }

    if (anchorCache.length === 0) return;

    let currentUrl = null;
    let currentFmExcluded = false;

    if (file && file.path) {
      try {
        const raw = fs.readFileSync(file.path, 'utf-8');
        const parsed = matter(raw);
        currentUrl = options.urlBuilder({
          filePath: file.path,
          frontmatter: parsed.data || {},
          contentDir: path.resolve(process.cwd(), options.contentDir),
        });
        currentFmExcluded = parsed.data && parsed.data.excludeFromLinking === true;
      } catch (err) {
        if (options.verbose) {
          console.warn(
            `[auto-internal-links] Could not read frontmatter for ${file.path}: ${err.message}`
          );
        }
      }
    }

    if (currentFmExcluded) return;

    const state = {
      anchors: anchorCache,
      currentUrl,
      linkCount: 0,
      usedAnchors: new Set(),
      perTarget: new Map(),
      maxLinksPerPage: options.maxLinksPerPage,
      maxLinksPerTarget: options.maxLinksPerTarget,
      excludeTags: options.excludeTags,
      excludeClasses: options.excludeClasses,
      linkClass: options.linkClass,
      dryRun: options.dryRun,
      dryRunLog: [],
    };

    processTree(tree, state);

    if (options.dryRun && state.dryRunLog.length > 0) {
      console.log(`[auto-internal-links] DRY RUN — ${currentUrl || file.path}`);
      for (const entry of state.dryRunLog) {
        console.log(`  "${entry.anchor}" -> ${entry.target}`);
      }
    } else if (options.verbose && state.linkCount > 0) {
      console.log(
        `[auto-internal-links] ${currentUrl || file.path}: ` +
        `inserted ${state.linkCount} link${state.linkCount === 1 ? '' : 's'}`
      );
    }
  };
}

/**
 * Clear the cached anchor index. Useful for tests or watch-mode setups
 * where you want to force a rebuild.
 */
export function clearAnchorCache() {
  anchorCache = null;
  anchorCacheKey = null;
}
