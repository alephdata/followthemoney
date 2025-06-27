import path from 'node:path';
import { Schema } from '@alephdata/followthemoney';

export function schemaLink(base?: string = '', schema: Schema) {
  return path.join(base, '/explorer/schemata/', schema.name);
}
