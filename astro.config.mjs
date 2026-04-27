import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import path from 'node:path';
import rehypeAutoInternalLinks from './src/plugins/auto-internal-links/index.mjs';
import rehypeRelatedCallouts from './src/plugins/related-callouts/index.mjs';

// Languages collection routes via frontmatter.language + frontmatter.concept,
// not the filename. All other collections use the standard file-path mapping.
function devnookUrlBuilder({ filePath, frontmatter, contentDir }) {
  if (frontmatter.language && frontmatter.concept) {
    const lang = String(frontmatter.language).toLowerCase();
    const concept = String(frontmatter.concept).toLowerCase();
    return `/languages/${lang}/${concept}/`;
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

export default defineConfig({
  site: 'https://devnook.dev',
  output: 'static',
  integrations: [sitemap()],
  image: {
    service: {
      entrypoint: 'astro/assets/services/noop'
    }
  },
  markdown: {
    shikiConfig: {
      theme: 'github-dark',
      wrap: true
    },
    rehypePlugins: [
      [rehypeAutoInternalLinks, {
        contentDir: 'src/content',
        autoAnchors: true,
        maxLinksPerPage: 8,
        maxLinksPerTarget: 1,
        dryRun: false,
        verbose: true,
        urlBuilder: devnookUrlBuilder,
      }],
      [rehypeRelatedCallouts, {
        contentDir: 'src/content',
        wordThreshold: 500,
        maxCallouts: 3,
        verbose: true,
        urlBuilder: devnookUrlBuilder,
      }],
    ],
  }
});
