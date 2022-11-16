import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";
import mdx from '@astrojs/mdx';
import injectComponents from './src/plugins/injectComponents.ts';
import explorerLinks from './src/plugins/explorerLinks.ts';

export default defineConfig({
  integrations: [
    tailwind(),
    mdx({
      remarkPlugins: [
        injectComponents({
          Callout: '@components/content/Callout.astro',
          LinkCard: '@components/content/LinkCard.astro',
          SchemaLink: '@components/explorer/SchemaLink.astro',
          PropertyTypeLink: '@components/explorer/PropertyTypeLink.astro',
        }),
        explorerLinks,
      ],
    }),
  ],
});
