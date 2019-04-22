import { Schema } from './schema'
import { Model } from './model'
import { Property } from './property'
import { PropertyType } from './type'

export type Value = string | Entity
export type Values = Array<Value>

export interface IEntityDatum {
  schema: Schema | string
  properties?: { [prop: string]: Array<Value | IEntityDatum> }
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

  constructor(model: Model, data: IEntityDatum) {
    this.schema = model.getSchema(data.schema)
    this.id = data.id

    if (data.properties) {
      Object.entries(data.properties).forEach(([prop, values]) => {
        values.forEach((value) => {
          this.setProperty(prop, value)
        })
      })
    }
  }

  setProperty(prop: string | Property, value: Value | IEntityDatum | undefined | null): Values {
    const property = this.schema.getProperty(prop)
    const values = this.properties.get(property) || []
    if (value === undefined || value === null) {
      return values
    }
    if (typeof (value) === 'string' && value.trim().length === 0) {
      return values
    }
    if (typeof (value) !== 'string') {
      value = this.schema.model.getEntity(value)
    }
    values.push(value)
    this.properties.set(property, values)
    return values
  }

  hasProperty(prop: string | Property): boolean {
    try {
      const property = this.schema.getProperty(prop)
      return this.properties.has(property)
    } catch {
      return false
    }
  }

  getProperty(prop: string | Property): Values {
    try {
      const property = this.schema.getProperty(prop)
      if (!this.properties.has(property)) {
        return []
      }
      return this.properties.get(property) as Values
    } catch {
      return []
    }
  }

  /**
   * The first value of a property only.
   *
   * @param prop A property name or object
   */
  getFirst(prop: string | Property): Value | null {
    for (let value of this.getProperty(prop)) {
      return value
    }
    return null
  }

  /**
   * List all properties for which this entity has values set. This
   * does not include unset properties.
   */
  getProperties(): Array<Property> {
    return Array.from(this.properties.keys())
  }

  /**
   * Get the designated label for the given entity.
   */
  getCaption(): string | null {
    for (let property of this.getProperties()) {
      if (property.caption) {
        for (let value of this.getProperty(property)) {
          return value as string
        }
      }
    }
    return null
  }

  /**
   * Get all the values of a particular type, irrespective of
   * which property it is associated with.
   */
  getTypeValues(type: string | PropertyType, matchableOnly: boolean = false): Values {
    const propType = this.schema.model.getType(type)
    const values = new Array<Value>()
    for (let property of this.getProperties()) {
      if (!matchableOnly || property.matchable) {
        if (property.type.toString() === propType.toString()) {
          for (let value of this.getProperty(property)) {
            if (values.indexOf(value) === -1) {
              values.push(value)
            }
          }
        }
      }
    }
    return values
  }
}
