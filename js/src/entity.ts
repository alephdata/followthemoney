import { Schema } from './schema'
import { Model } from './model'
import { Property } from './property'

export type Value = string | Entity
export type Values = Array<Value>

export interface IEntityDatum {
  schema: Schema | string
  properties: { [prop: string]: Array<Value | IEntityDatum> }
  id: string
}

/**
 * An entity proxy which provides simplified access to the
 * properties and schema associated with an entity.
 */
export class Entity {
  public id: string
  public properties: Map<Property, Values> = new Map()
  public readonly schema: Schema
  public readonly raw: any

  constructor(model: Model, data: IEntityDatum) {
    this.schema = model.getSchema(data.schema)
    this.id = data.id
    this.raw = data

    Object.entries(data.properties).forEach(([prop, values]) => {
      values.forEach((value) => {
        this.setProperty(prop, value)
      })
    })
  }

  setProperty(prop: string | Property, value: Value | IEntityDatum): Values {
    const property = this.schema.getProperty(prop)
    if (typeof(value) !== 'string') {
      value = this.schema.model.getEntity(value)
    }
    const values = this.properties.get(property) || []
    values.push(value)
    this.properties.set(property, values)
    return values
  }

  hasProperty(prop: string | Property): boolean {
    const property = this.schema.getProperty(prop)
    return this.properties.has(property)
  }

  getProperty(prop: string | Property): Values {
    const property = this.schema.getProperty(prop)
    if(!this.properties.has(property)) {
      return []
    }
    return this.properties.get(property) as Values
  }

  /** 
   * List all properties for which this entity has values set. This 
   * does not include unset properties.
   */
  getProperties(): Array<Property> {
    return Array.from(this.properties.keys())
  }

  toString(): string {
    return this.schema.name + this.id
  }
}
