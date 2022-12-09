import { defineConfig } from 'astro/config';
import theme, { injectComponent } from 'astro-theme-docs';
import explorerLinks from './src/plugins/explorerLinks.mjs';

export default defineConfig({
  integrations: [theme({
    mdxPlugins: [
      explorerLinks(),
      injectComponent('SchemaLink', '@components/explorer/SchemaLink.astro'),
      injectComponent('PropertyTypeLink', '@components/explorer/PropertyTypeLink.astro'),
    ],
  })],
});
