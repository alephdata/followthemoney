import { IPropertyDatum, Property } from './property'
import { Model } from './model'

interface IEdgeSpecification {
  source: string
  target: string
}

export type SchemaSpec = string | null | undefined | Schema;

export interface ISchemaDatum {
  label: string
  plural: string
  schemata: string[]
  extends: string[]
  required?: boolean
  abstract?: boolean
  matchable?: boolean
  description?: string
  edge?: IEdgeSpecification
  featured?: string[]
  properties: {
    [x: string]: IPropertyDatum
  }
}

export class Schema {
  static readonly THING = 'Thing'
  static readonly DOCUMENT = 'Document'

  public readonly model: Model
  public readonly name: string
  public readonly label: string
  public readonly plural: string
  public readonly abstract: boolean
  public readonly matchable: boolean
  public readonly description: string | null
  public readonly featured: string[]
  public readonly schemata: string[]
  public readonly extends: string[]
  public readonly edge?: IEdgeSpecification
  public readonly isEdge: boolean
  private properties: Map<string, Property> = new Map()

  constructor(model: Model, schemaName: string, config: ISchemaDatum) {
    this.model = model
    this.name = schemaName
    this.label = config.label || this.name;
    this.plural = config.plural || this.label;
    this.schemata = config.schemata
    this.extends = config.extends
    this.featured = config.featured || new Array()
    this.abstract = !!config.abstract
    this.matchable = !!config.matchable
    this.description = config.description || null
    this.isEdge = !!config.edge
    this.edge = config.edge

    Object.entries(config.properties).forEach(
      ([propertyName, property]) => {
        this.properties.set(propertyName, new Property(this, property))
      }
    )
  }

  isThing(): boolean {
    return this.isA(Schema.THING)
  }

  isDocument(): boolean {
    return this.isA(Schema.DOCUMENT)
  }

  getExtends(): Array<Schema> {
    return this.extends.map(name => this.model.getSchema(name))
  }

  getProperties(): Map<string, Property> {
    const properties = new Map<string, Property>()
    this.getExtends().forEach((schema) => {
      schema.getProperties().forEach((prop, name) => {
        properties.set(name, prop)
      })
    })
    this.properties.forEach((prop, name) => {
      properties.set(name, prop)
    })
    return properties
  }

  getFeaturedProperties() {
    return this.featured.map(name => this.getProperty(name))
  }

  hasProperty(prop: string | Property): boolean {
    if (prop instanceof Property) {
      return this.getProperties().has(prop.name)
    }
    return this.getProperties().has(prop)
  }

  /**
   * Get the value of a property. If it's not defined, return an
   * empty array. If it's not a valid property, raise an error.
   * 
   * @param prop name or Property
   */
  getProperty(prop: string | Property): Property {
    if (prop instanceof Property) {
      return prop
    }
    if (this.hasProperty(prop)) {
      return this.getProperties().get(prop) as Property
    } else {
      throw new Error('Property does not exist: ' + prop)
    }
  }

  isA(schema: SchemaSpec) {
    try {
      schema = this.model.getSchema(schema)
      return !!~this.schemata.indexOf(schema.name)
    } catch (error) {
      return false;
    }
  }

  isAny(schemata: Array<SchemaSpec>) {
    for (let schema of schemata) {
      if (this.isA(schema)) {
        return true;
      }
    }
    return false;
  }

  toString(): string {
    return this.name
  }
}
