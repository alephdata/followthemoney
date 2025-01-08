import { defineConfig } from 'astro/config';
import theme, { injectComponent } from 'astro-theme-docs';
import explorerLinks from './src/plugins/explorerLinks.mjs';
import referenceLinks from './src/plugins/referenceLinks.mjs';

export default defineConfig({
  scopedStyleStrategy: 'where',
  integrations: [theme({
    mdxPlugins: [
      explorerLinks(),
      referenceLinks(),
      injectComponent('SchemaLink', '@components/explorer/SchemaLink.astro'),
      injectComponent('PropertyTypeLink', '@components/explorer/PropertyTypeLink.astro'),
      injectComponent('ReferenceLink', '@components/common/ReferenceLink.astro'),
    ],
  })],
});
