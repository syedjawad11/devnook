import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async ({ site }) => {
  if (!site) {
    return new Response('Site URL not configured', { status: 500 });
  }

  const baseUrl = site.origin;

  // Get all content collections
  const [languages, guides, blog, cheatsheets, tools] = await Promise.all([
    getCollection('languages'),
    getCollection('guides'),
    getCollection('blog'),
    getCollection('cheatsheets'),
    getCollection('tools'),
  ]);

  // Calculate total URLs per sitemap (max 50,000 per sitemap spec, we'll use 10,000 for safety)
  const maxUrlsPerSitemap = 10000;

  // Count static pages
  const staticPages = [
    '/',
    '/languages',
    '/guides',
    '/blog',
    '/cheatsheets',
    '/tools',
    '/about',
    '/privacy',
    '/terms',
  ];

  // Count language hub pages
  const languageSlugs = new Set(languages.map(post => post.data.language));
  const languageHubCount = languageSlugs.size;

  // Total dynamic URLs
  const totalUrls = 
    staticPages.length +
    languageHubCount +
    languages.length +
    guides.length +
    blog.length +
    cheatsheets.length +
    tools.length;

  const sitemapCount = Math.ceil(totalUrls / maxUrlsPerSitemap);

  // Generate sitemap index XML
  const sitemaps = Array.from({ length: sitemapCount }, (_, i) => {
    const sitemapNum = i + 1;
    const lastmod = new Date().toISOString();
    
    return `  <sitemap>
    <loc>${baseUrl}/sitemap-${sitemapNum}.xml</loc>
    <lastmod>${lastmod}</lastmod>
  </sitemap>`;
  }).join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemaps}
</sitemapindex>`;

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};