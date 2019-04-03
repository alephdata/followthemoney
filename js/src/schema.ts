import { IPropertyDatum, Property } from './property'
import { Model } from './model'

interface IEdgeSpecification {
  source: string
  target: string
}

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
  public properties: Map<string, Property> = new Map()

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

  getFeaturedProperties() {
    return this.featured.map(name => this.properties.get(name))
  }

  hasProperty(prop: string | Property): boolean {
    if (prop instanceof Property) {
      return this.properties.has(prop.name)
    }
    return this.properties.has(prop)
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
      return this.properties.get(prop) as Property
    } else {
      throw new Error('Property does not exist: ' + prop)
    }
  }

  isA(schemaName: string) {
    return !!~this.schemata.indexOf(schemaName)
  }

  toString(): string {
    return this.name
  }
}
