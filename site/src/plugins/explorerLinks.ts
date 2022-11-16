import { visit } from 'unist-util-visit'

const jsxNode = (component, attributes) => {
  return {
    type: 'mdxJsxFlowElement',
    name: component,
    attributes: Object.entries(attributes).map(
      ([name, value]) => ({ type: 'mdxJsxAttribute', name, value })
    ),
  };
};

export default function explorerLinks() {
  return (tree) => {
    visit(tree, 'link', (node, index, parent) => {
      const isSchemaLink = node.url.startsWith('schema://');
      const isPropertyTypeLink = node.url.startsWith('type://');
      const ref = node.url.replace('schema://', '').replace('type://', '');

      if (!isSchemaLink && !isPropertyTypeLink) {
        return;
      }

      const component = isSchemaLink
        ? 'SchemaLink'
        : 'PropertyTypeLink';

      const attrs = {
        [isSchemaLink ? 'schema' : 'type']: ref,
      };

      if (node.children.length > 0) {
        attrs.children = node.children;
      }

      parent.children.splice(index, 1, jsxNode(component, attrs));
    });
  };
};
