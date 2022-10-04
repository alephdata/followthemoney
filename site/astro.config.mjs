import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";
import alpine from '@astrojs/alpinejs';
import mdx from '@astrojs/mdx';

export default defineConfig({
  integrations: [
    tailwind(),
    alpine(),
    mdx(),
  ],
});
