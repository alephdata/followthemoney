import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";
import mdx from '@astrojs/mdx';
import injectComponents from './src/plugins/injectComponents.ts';

export default defineConfig({
  integrations: [
    tailwind(),
    mdx({
      remarkPlugins: [
        injectComponents({
          Callout: '@components/content/Callout.astro',
        }),
      ],
    }),
  ],
});
