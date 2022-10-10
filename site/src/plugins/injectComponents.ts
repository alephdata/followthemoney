const importNode = (name, path) => ({
  type: 'mdxjsEsm',
  data: {
    estree: {
      type: 'Program',
      body: [
        {
          type: 'ImportDeclaration',
          specifiers: [
            {
              type: 'ImportDefaultSpecifier',
              local: {
                type: 'Identifier',
                name: name,
              },
            },
          ],
          source: {
            type: 'Literal',
            value: path,
          },
        },
      ],
      sourceType: 'module',
      comments: [],
    },
  },
});

export default function injectComponents(components) {
  return () => {
    const imports = Object.entries(components).map(([name, path]) =>
      importNode(name, path)
    );

    return (tree) => {
      tree.children.unshift(...imports);
    };
  };
}
