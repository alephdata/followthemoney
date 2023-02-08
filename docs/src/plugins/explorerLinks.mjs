import { visit } from 'unist-util-visit';

/*
 * Replaces references like `schema:Company` and `type:identifier`
 * with the `SchemaLink` and `PropertyTypeLink` components.
 */
export default function explorerLinks() {
  return () => {
    return (tree) => {
      visit(tree, 'inlineCode', (node, index, parent) => {
        const isSchemaRef = node.value.startsWith('schema:');
        const isPropertyTypeRef = node.value.startsWith('type:');
        const ref = node.value.replace('schema:', '').replace('type:', '');

        if (!isSchemaRef && !isPropertyTypeRef) {
          return;
        }

        // https://github.com/syntax-tree/mdast-util-mdx-jsx#mdxjsxflowelement
        const linkNode = {
          type: 'mdxJsxFlowElement',
          name: isSchemaRef ? 'SchemaLink' : 'PropertyTypeLink',
          attributes: [
            {
              type: 'mdxJsxAttribute',
              name: isSchemaRef ? 'schema' : 'type',
              value: ref,
            },
          ],
        };

        parent.children.splice(index, 1, linkNode);
      });
    };
  };
}
