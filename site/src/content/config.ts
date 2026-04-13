import { z, defineCollection } from 'astro:content';

const languagesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.literal('languages'),
    language: z.string(),
    concept: z.string(),
    template_id: z.string(),
    tags: z.array(z.string()),
    related_posts: z.array(z.string()),
    related_tools: z.array(z.string()),
    published_date: z.string(),
    og_image: z.string(),
    word_count_target: z.number().optional(),
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
  }),
});

const cheatsheetsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.literal('cheatsheets'),
    language: z.string().optional(),
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
    template_id: z.string(),
    tags: z.array(z.string()),
    related_posts: z.array(z.string()),
    related_tools: z.array(z.string()),
    published_date: z.string(),
    og_image: z.string(),
    word_count_target: z.number().optional(),
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
  }),
});

export const collections = {
  languages: languagesCollection,
  guides: guidesCollection,
  cheatsheets: cheatsheetsCollection,
  blog: blogCollection,
  tools: toolsCollection,
};