import { z, defineCollection } from 'astro:content';

const LANGUAGE_ENUM = ['python','javascript','typescript','go','rust','java','csharp','php','ruby','swift','kotlin','cpp'] as const;

const languagesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.literal('languages'),
    language: z.enum(LANGUAGE_ENUM),
    concept: z.string().regex(/^[a-z0-9-]+$/, 'concept must be lowercase kebab-case'),
    template_id: z.string(),
    tags: z.array(z.string()),
    related_posts: z.array(z.string()),
    related_tools: z.array(z.string()),
    published_date: z.string(),
    og_image: z.string(),
    word_count_target: z.number().optional(),
    linkAnchors: z.array(z.string()).optional(),
  }),
});

const guidesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.literal('guides'),
    template_id: z.string(),
    tags: z.array(z.string()),
    related_posts: z.array(z.string()),
    related_tools: z.array(z.string()),
    published_date: z.string(),
    og_image: z.string(),
    word_count_target: z.number().optional(),
    linkAnchors: z.array(z.string()).optional(),
  }),
});

const cheatsheetsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.literal('cheatsheets'),
    language: z.enum(LANGUAGE_ENUM).optional(),
    template_id: z.string(),
    tags: z.array(z.string()),
    related_posts: z.array(z.string()),
    related_tools: z.array(z.string()),
    published_date: z.string(),
    og_image: z.string(),
    downloadable: z.boolean().optional(),
  }),
});

const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.literal('blog'),
    subcategory: z.string().optional(),
    template_id: z.string(),
    tags: z.array(z.string()),
    related_posts: z.array(z.string()),
    related_tools: z.array(z.string()),
    published_date: z.string(),
    og_image: z.string(),
    word_count_target: z.number().optional(),
    linkAnchors: z.array(z.string()).optional(),
  }),
});

const toolsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.literal('tools'),
    tool_slug: z.string(),
    template_id: z.string(),
    tags: z.array(z.string()),
    related_tools: z.array(z.string()),
    related_content: z.array(z.string()),
    published_date: z.string(),
    og_image: z.string(),
    word_count_target: z.number().optional(),
    faqs: z.array(z.object({
      question: z.string(),
      answer: z.string(),
    })).optional(),
  }),
});

export const collections = {
  languages: languagesCollection,
  guides: guidesCollection,
  cheatsheets: cheatsheetsCollection,
  blog: blogCollection,
  tools: toolsCollection,
};