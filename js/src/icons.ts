import icons from '../generated/icons.json'
import { Schema } from './schema'

interface IIconStorage {
  [iconName:string] : string[]
}
/*
* getSchema(schemaName: string | null | undefined | Schema): Schema {
    if (schemaName === null || schemaName === undefined) {
      throw new Error('Invalid schema.')
    }
    if (schemaName instanceof Schema) {
      return schemaName
    }
    const schema = this.schemata[schemaName];
    if (schema === undefined) {
      throw new Error('No such schema: ' + schemaName)
    }
    return schema;
  }
  *
* */
export const IconRegistry = {
  storage:icons as IIconStorage,
  getIcon(iconName:string){
    return this.storage[iconName];
  },
  iconForSchema(schemaName: string | null | undefined | Schema){
    if (schemaName === null || schemaName === undefined) {
      throw new Error('Invalid schema.')
    }
    if (schemaName instanceof Schema) {
      return this.getIcon(schemaName.name)
    }
    return this.getIcon(schemaName)
  }
}
