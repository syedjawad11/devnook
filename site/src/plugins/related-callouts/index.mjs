import fs from 'node:fs';
import path from 'node:path';
import fg from 'fast-glob';
import matter from 'gray-matter';

const WORD_THRESHOLD = 500;
const MAX_CALLOUTS = 3;

const LEAD_IN_PHRASES = [
  'Worth reading next:',
  'On a related note:',
  'Related deep-dive:',
  'A helpful companion piece:',
  'More on this subject:',
  'Want to dig deeper? See our guide to',
  'We explored this in more depth in our guide to',
  'For a complete walkthrough, see',
];

let postIndexCache = null;
let postIndexCacheKey = null;

function defaultUrlBuilder({ filePath, frontmatter, contentDir }) {
  if (frontmatter.language && frontmatter.concept) {
    return `/languages/${String(frontmatter.language).toLowerCase()}/${String(frontmatter.concept).toLowerCase()}/`;
  }
  if (frontmatter.permalink) return frontmatter.permalink;
  if (frontmatter.url) return frontmatter.url;
  let rel = path.relative(contentDir, filePath)
    .replace(/\.(md|mdx)$/i, '')
    .replace(/[\\/]index$/, '');
  if (frontmatter.slug) {
    const dir = path.dirname(rel);
    rel = (dir === '.' || dir === '') ? frontmatter.slug : `${dir}/${frontmatter.slug}`;
  }
  return '/' + rel.split(path.sep).join('/').replace(/^\/+|\/+$/g, '') + '/';
}

async function buildPostIndex(options) {
  const { contentDir, urlBuilder, verbose } = options;
  const absContentDir = path.resolve(process.cwd(), contentDir);

  if (!fs.existsSync(absContentDir)) {
    console.warn(`[related-callouts] Content directory not found: ${absContentDir}`);
    return [];
  }

  const files = await fg('**/*.{md,mdx}', {
    cwd: absContentDir,
    absolute: true,
    dot: false,
  });

  const posts = [];

  for (const filePath of files) {
    const relParts = path.relative(absContentDir, filePath).split(path.sep);
    if (relParts[0] === 'tools') continue;

    let parsed;
    try {
      parsed = matter(fs.readFileSync(filePath, 'utf-8'));
    } catch (err) {
      console.warn(`[related-callouts] Failed to read ${filePath}: ${err.message}`);
      continue;
    }

    const fm = parsed.data || {};
    if (fm.draft === true) continue;
    if (!fm.title) continue;

    let url;
    try {
      url = urlBuilder({ filePath, frontmatter: fm, contentDir: absContentDir });
    } catch (err) {
      console.warn(`[related-callouts] urlBuilder threw for ${filePath}: ${err.message}`);
      continue;
    }

    posts.push({
      filePath,
      url,
      title: String(fm.title),
      category: String(fm.category || ''),
      language: String(fm.language || ''),
      tags: Array.isArray(fm.tags) ? fm.tags.map(String) : [],
      published_date: String(fm.published_date || ''),
    });
  }

  if (verbose) {
    console.log(`[related-callouts] Built post index: ${posts.length} posts from ${files.length} files`);
  }

  return posts;
}

function scorePost(post, currentFm) {
  let s = 0;
  const currentLanguage = String(currentFm.language || '');
  const currentCategory = String(currentFm.category || '');
  const currentTags = Array.isArray(currentFm.tags) ? currentFm.tags.map(String) : [];

  if (currentLanguage && post.language === currentLanguage) s += 3;
  if (currentCategory && post.category === currentCategory) s += 2;
  for (const tag of post.tags) {
    if (currentTags.includes(tag)) s += 1;
  }
  return s;
}

function estimateWordCount(tree) {
  let charCount = 0;
  function walk(node) {
    if (node.type === 'text') charCount += node.value.length;
    if (node.children) {
      for (const child of node.children) walk(child);
    }
  }
  walk(tree);
  return charCount / 5.5;
}

function findH2InsertionPoints(tree) {
  const h2Indices = [];
  const children = tree.children;
  for (let i = 0; i < children.length; i++) {
    if (children[i].type === 'element' && children[i].tagName === 'h2') {
      h2Indices.push(i);
    }
  }

  if (h2Indices.length < 3) return [];

  // Interior H2s: skip first (intro) and last (summary/conclusion)
  const interiorH2s = h2Indices.slice(1, -1);

  // Splice position for each interior H2 = just before the next H2 (end of that section)
  return interiorH2s.map((h2Pos) => {
    const posInAll = h2Indices.indexOf(h2Pos);
    return h2Indices[posInAll + 1];
  });
}

function selectInsertionPoints(points, maxCallouts) {
  if (points.length <= maxCallouts) return points;
  const n = points.length;
  const selected = [];
  for (let i = 0; i < maxCallouts; i++) {
    selected.push(points[Math.round(i * (n - 1) / (maxCallouts - 1))]);
  }
  return selected;
}

function buildCalloutNode(post, phraseIndex) {
  return {
    type: 'element',
    tagName: 'aside',
    properties: {
      className: ['related-callout'],
      'aria-label': 'Related reading',
    },
    children: [
      {
        type: 'element',
        tagName: 'span',
        properties: { className: ['related-callout__icon'], 'aria-hidden': 'true' },
        children: [{ type: 'text', value: '→' }],
      },
      { type: 'text', value: ' ' },
      {
        type: 'element',
        tagName: 'span',
        properties: { className: ['related-callout__lead'] },
        children: [{ type: 'text', value: LEAD_IN_PHRASES[phraseIndex] }],
      },
      { type: 'text', value: ' ' },
      {
        type: 'element',
        tagName: 'a',
        properties: { href: post.url, className: ['related-callout__link'] },
        children: [{ type: 'text', value: post.title }],
      },
    ],
  };
}

export default function rehypeRelatedCallouts(userOptions = {}) {
  const options = {
    contentDir: 'src/content',
    wordThreshold: WORD_THRESHOLD,
    maxCallouts: MAX_CALLOUTS,
    verbose: false,
    urlBuilder: defaultUrlBuilder,
    ...userOptions,
  };

  const cacheKey = options.contentDir;

  return async function transformer(tree, file) {
    if (postIndexCache === null || postIndexCacheKey !== cacheKey) {
      postIndexCache = await buildPostIndex(options);
      postIndexCacheKey = cacheKey;
    }

    if (postIndexCache.length === 0) return;
    if (!file || !file.path) return;

    let currentFm;
    let currentUrl;
    try {
      const parsed = matter(fs.readFileSync(file.path, 'utf-8'));
      currentFm = parsed.data || {};
      currentUrl = options.urlBuilder({
        filePath: file.path,
        frontmatter: currentFm,
        contentDir: path.resolve(process.cwd(), options.contentDir),
      });
    } catch (err) {
      if (options.verbose) {
        console.warn(`[related-callouts] Could not read frontmatter for ${file.path}: ${err.message}`);
      }
      return;
    }

    if (currentFm.excludeRelatedCallouts === true) return;

    if (estimateWordCount(tree) < options.wordThreshold) return;

    const scored = postIndexCache
      .filter(p => p.url !== currentUrl)
      .map(p => ({ ...p, score: scorePost(p, currentFm) }))
      .filter(p => p.score > 0)
      .sort((a, b) => b.score - a.score || b.published_date.localeCompare(a.published_date));

    if (scored.length === 0) return;

    const allPoints = findH2InsertionPoints(tree);
    if (allPoints.length === 0) return;

    const selectedPoints = selectInsertionPoints(allPoints, options.maxCallouts);
    const count = Math.min(selectedPoints.length, scored.length, options.maxCallouts);

    if (count === 0) return;

    const insertions = [];
    for (let i = 0; i < count; i++) {
      insertions.push({ spliceAt: selectedPoints[i], post: scored[i], phraseIndex: i });
    }
    insertions.sort((a, b) => b.spliceAt - a.spliceAt);

    for (const { spliceAt, post, phraseIndex } of insertions) {
      tree.children.splice(spliceAt, 0, buildCalloutNode(post, phraseIndex));
    }

    if (options.verbose) {
      console.log(`[related-callouts] ${currentUrl}: inserted ${count} callout(s)`);
    }
  };
}
