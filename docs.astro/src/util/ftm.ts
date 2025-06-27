import defaultModel from '../../../js/src/defaultModel.json';
import { Model, type Schema } from '@alephdata/followthemoney';

export const model = new Model(defaultModel);

type Edges = Array<[Schema, Schema]>;

export function getInheritanceEdges(schemata: Array<Schema>): Edges {
  const nodes = new Set(schemata);
  const edges: Set<string> = new Set();

  for (const node of nodes) {
    for (const parent of node.getExtends()) {
      if (nodes.has(parent)) {
        edges.add([node.name, parent.name].join(':'));
      }
    }
  }

  return Array.from(edges).map((edge) => {
    const [child, parent] = edge.split(':');
    return [model.getSchema(child), model.getSchema(parent)];
  });
}
