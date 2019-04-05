import { Schema, ISchemaDatum } from './schema'
import { Entity, IEntityDatum } from './entity'
import { PropertyType, IPropertyTypeDatum } from './type'
import uuid from 'uuid/v4';


export interface IModelDatum {
  schemata: { [name: string]: ISchemaDatum }
  types: { [name: string]: IPropertyTypeDatum }
}

export class Model {
  public readonly schemata: { [x: string]: Schema | undefined } = {}
  public readonly types: { [x: string]: PropertyType } = {}

  constructor(config: IModelDatum) {
    this.types = {}
    Object.entries(config.types).forEach(
      ([typeName, typeData]) => {
        this.types[typeName] = new PropertyType(typeName, typeData)
      }
    )

    this.schemata = {}
    Object.entries(config.schemata).forEach(
      ([schemaName, schema]) => {
        this.schemata[schemaName] = new Schema(this, schemaName, schema)
      }
    )
  }

  getSchema(schemaName: string | null | undefined | Schema): Schema {
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

  getType(typeName: string): PropertyType {
    return this.types[typeName]
  }

  /**
   * Convert a raw JSON object to an entity proxy.
   * 
   * @param raw entity source data
   */
  getEntity(raw: IEntityDatum | Entity): Entity {
    if (raw instanceof Entity) {
      return raw
    } else {
      return new Entity(this, raw)
    }
  }

  /**
   * Make a new object with the given schema, and generate a random ID for
   * it.
   * 
   * @param schema Schema name or object
   */
  createEntity(schema: string | Schema): Entity {
    return this.getEntity({
      id: uuid(),
      schema: schema,
      properties: {}
    })
  }
}

