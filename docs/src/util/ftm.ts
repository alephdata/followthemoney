import defaultModel from '../../../js/src/defaultModel.json';
import { Model, Schema } from '@alephdata/followthemoney';

export const model = new Model(defaultModel);

export function getInheritanceAdjacency(
  schema: Schema
): Array<[Schema, Schema]> {
  const tuples: Array<[Schema, Schema]> = [];

  // Get all parent schemata
  const queue: Array<Schema> = [];
  const visited: Set<Schema> = new Set();
  queue.push(schema);

  while (queue.length > 0) {
    const child = queue.shift();
    visited.add(child);

    for (const parent of child.getExtends()) {
      tuples.push([child, parent]);

      if (!visited.has(parent) && !queue.includes(parent)) {
        queue.push(parent);
      }
    }
  }

  // Get first level child schemata
  for (const child of model.getSchemata()) {
    if (child.getExtends().includes(schema)) {
      tuples.push([child, schema]);
    }
  }

  return tuples;
}
