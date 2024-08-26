import { Schema } from './schema'
import { PropertyType } from './type'

export interface IPropertyDatum {
  name: string
  qname: string
  label: string
  type: string
  description?: string
  maxLength?: number
  format?: string
  stub?: boolean
  hidden?: boolean
  matchable?: boolean
  deprecated?: boolean
  range?: string | null
  reverse?: string
}

/**
 * Definition of a property, with relevant metadata for type,
 * labels and other useful criteria.
 */
export class Property {
  public readonly schema: Schema
  public readonly name: string
  public readonly qname: string
  public readonly label: string
  public readonly type: PropertyType
  public readonly hidden: boolean
  public readonly matchable: boolean
  public readonly deprecated: boolean
  public readonly description: string | null
  public readonly format: string | null
  public readonly stub: boolean
  public readonly maxLength: number
  public readonly hasReverse: boolean
  public readonly hasRange: boolean
  private readonly range: string | null
  private readonly reverse: string | null

  constructor(schema: Schema, property: IPropertyDatum) {
    this.schema = schema
    this.name = property.name
    this.qname = property.qname
    this.label = property.label || property.name
    this.hidden = !!property.hidden
    this.description = property.description || null
    this.format = property.format || null
    this.stub = !!property.stub
    this.maxLength = property.maxLength || 0
    this.matchable = !!property.matchable
    this.deprecated = !!property.deprecated
    this.range = property.range || null
    this.reverse = property.reverse || null
    this.type = schema.model.getType(property.type)
    this.hasRange = this.range !== null
    this.hasReverse = this.range !== null && this.reverse !== null
  }

  getRange(): Schema {
    return this.schema.model.getSchema(this.range)
  }

  getReverse(): Property {
    if (this.range === null || this.reverse === null) {
      throw new Error("This property has no reverse")
    }
    return this.getRange().getProperty(this.reverse)
  }

  static isProperty = (item: Property | undefined): item is Property => {
    return !!item
  }

  toString(): string {
    return this.qname
  }
}
