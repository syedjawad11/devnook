import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

interface SearchItem {
  title: string;
  description: string;
  slug: string;
  category: string;
  url: string;
  tags?: string[];
  language?: string;
}

export const GET: APIRoute = async () => {
  const items: SearchItem[] = [];

  // Collect language posts
  const languagePosts = await getCollection('languages');
  for (const post of languagePosts) {
    items.push({
      title: post.data.title,
      description: post.data.description,
      slug: post.slug,
      category: 'languages',
      url: `/languages/${post.data.language}/${post.data.concept}`,
      tags: post.data.tags || [],
      language: post.data.language,
    });
  }

  // Collect guides
  const guides = await getCollection('guides');
  for (const guide of guides) {
    items.push({
      title: guide.data.title,
      description: guide.data.description,
      slug: guide.slug,
      category: 'guides',
      url: `/guides/${guide.slug}`,
      tags: guide.data.tags || [],
    });
  }

  // Collect cheatsheets
  const cheatsheets = await getCollection('cheatsheets');
  for (const sheet of cheatsheets) {
    items.push({
      title: sheet.data.title,
      description: sheet.data.description,
      slug: sheet.slug,
      category: 'cheatsheets',
      url: `/cheatsheets/${sheet.slug}`,
      tags: sheet.data.tags || [],
      language: sheet.data.language,
    });
  }

  // Collect blog posts
  const blogPosts = await getCollection('blog');
  for (const post of blogPosts) {
    items.push({
      title: post.data.title,
      description: post.data.description,
      slug: post.slug,
      category: 'blog',
      url: `/blog/${post.slug}`,
      tags: post.data.tags || [],
    });
  }

  // Collect tools
  const tools = await getCollection('tools');
  for (const tool of tools) {
    items.push({
      title: tool.data.title,
      description: tool.data.description,
      slug: tool.slug,
      category: 'tools',
      url: `/tools/${tool.data.tool_slug || tool.slug}`,
      tags: tool.data.tags || [],
    });
  }

  return new Response(JSON.stringify(items), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};