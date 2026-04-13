import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://devnook.dev',
  output: 'static',
  integrations: [],
  image: {
    service: {
      entrypoint: 'astro/assets/services/noop'
    }
  },
  markdown: {
    shikiConfig: {
      theme: 'github-dark',
      wrap: true
    }
  }
});
