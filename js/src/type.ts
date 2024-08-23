
export interface IPropertyTypeDatum {
  group?: string
  label?: string
  description?: string
  maxLength?: number
  plural?: string | null
  matchable?: boolean,
  pivot?: boolean,
  values?: { [name: string]: string }
}

/**
 * A property type, such as a string, email address, phone number,
 * URL or a related entity.
 */
export class PropertyType {
  static ENTITY = 'entity';

  public name: string
  public group: string | null
  public grouped: boolean
  public label: string
  public plural: string
  public description: string | null
  public maxLength: number
  public matchable: boolean
  public pivot: boolean
  public values: Map<string, string>
  public isEntity: boolean

  constructor(name: string, data: IPropertyTypeDatum) {
    this.name = name
    this.label = data.label || name
    this.description = data.description || null
    this.maxLength = data.maxLength || 0
    this.plural = data.plural || this.label
    this.group = data.group || null
    this.grouped = data.group !== undefined
    this.matchable = !!data.matchable
    this.pivot = !!data.pivot
    this.isEntity = name === PropertyType.ENTITY
    this.values = new Map<string, string>()

    if (data.values) {
      Object.entries(data.values).forEach(([value, label]) => {
        this.values.set(value, label)
      })
    }
  }

  getLabel(value: string | undefined | null): string {
      if (!value) {
          return ''
      }
      return this.values.get(value) || value
  }

  toString(): string {
    return this.name
  }
}