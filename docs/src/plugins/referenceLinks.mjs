import path from 'node:path';
import { visit } from 'unist-util-visit';

/*
 * Replaces references like `ref:followthemoney.proxy.EntityProxy` with
 * a link to the Python API docs.
 */
export default function explorerLinks() {
  return () => {
    return (tree) => {
      visit(tree, 'inlineCode', (node, index, parent) => {
        if (!node.value.startsWith('class:')) {
          return;
        }

        const ref = node.value.replace('class:', '');

        const linkNode = {
          type: 'mdxJsxFlowElement',
          name: 'ReferenceLink',
          attributes: [
            {
              type: 'mdxJsxAttribute',
              name: 'ref',
              value: ref,
            },
          ],
        };

        parent.children.splice(index, 1, linkNode);
      });
    };
  };
}
