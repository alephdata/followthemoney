import { Schema } from './schema'
import { Model } from './model'
import { Property } from './property'
import { PropertyType } from './type'

export type Value = string | Entity
export type Values = Array<Value>
export type EntityProperties = { [prop: string]: Array<Value | IEntityDatum> }

export interface IEntityDatum {
  schema: Schema | string
  properties?: EntityProperties
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
    for (const value of this.getProperty(prop)) {
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
   * Copy the properties from a given entity that match the local
   * schema to this entity.
   */
  copyProperties(entity: Entity): void {
    entity.getProperties().forEach((prop) => {
      if (this.schema.hasProperty(prop)) {
        const localProp = this.schema.getProperty(prop.name)
        if (localProp.qname === prop.qname) {
          entity.getProperty(prop).forEach((value) => {
            this.setProperty(localProp, value)
          })
        }
      }
    })
  }

  /**
   * Get the designated label for the given entity.
   */
  getCaption(): string {
    for (const property of this.schema.caption) {
      for (const value of this.getProperty(property)) {
        return value as string
      }
    }
    return this.schema.label
  }

  /**
   * Set the designated label as the first caption prop for the given entity.
   */
  setCaption(value: string): void {
    const captionProperties = this.schema.caption
    if (captionProperties && captionProperties.length > 0) {
      this.setProperty(captionProperties[0], value)
    }
  }

  /**
   * Get the designated label for the given entity.
   */
  getEdgeCaption(): string {
    const captions = this.schema.edge ? this.schema.edge.caption : []
    for (const property of captions) {
      for (const value of this.getProperty(property)) {
        return value as string
      }
    }
    return this.schema.label
  }

  /**
   * Get all the values of a particular type, irrespective of
   * which property it is associated with.
   */
  getTypeValues(type: string | PropertyType, matchableOnly = false): Values {
    const propType = this.schema.model.getType(type)
    const values = new Array<Value>()
    for (const property of this.getProperties()) {
      if (!matchableOnly || property.matchable) {
        if (property.type.toString() === propType.toString()) {
          for (const value of this.getProperty(property)) {
            if (values.indexOf(value) === -1) {
              values.push(value)
            }
          }
        }
      }
    }
    return values
  }

  /**
   * Serialise the entity to a plain JSON object, suitable for feeding to the
   * JSON.stringify() call.
   */
  toJSON(): IEntityDatum {
    const properties: EntityProperties = {}
    this.properties.forEach((values, prop) => {
      properties[prop.name] = values.map((value) =>
        Entity.isEntity(value) ? (value as Entity).toJSON() : value
      )
    })
    return {
      id: this.id,
      schema: this.schema.name,
      properties: properties
    }
  }

  /**
   * Make a copy of the entity with no shared object identity.
   */
  clone(): Entity {
    return Entity.fromJSON(this.schema.model, this.toJSON())
  }

  /**
   * Shortcut helper function.
   *
   * @param model active FollowTheMoney model
   * @param data the raw blob, which must match IEntityDatum
   */
  static fromJSON(model: Model, data: any): Entity { // eslint-disable-line
    return model.getEntity(data)
  }

  static isEntity(value: Value): boolean {
    return typeof (value) !== 'string'
  }
}
