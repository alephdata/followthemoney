
export interface IPropertyTypeDatum {
    name: string
    group?: string
    label: string
    plural: string
    matchable?: boolean
}

/**
 * A property type, such as a string, email address, phone number,
 * URL or a related entity.
 */
export class PropertyType {
    static ENTITY = 'entity';

    public name: string
    public group?: string | null
    public grouped: boolean
    public label: string
    public plural: string
    public matchable: boolean

    constructor(data: IPropertyTypeDatum) {
        this.name = data.name
        this.group = data.group || null
        this.grouped = data.group !== null
        this.label = data.label
        this.plural = data.plural
        this.matchable = !!data.matchable
    }

    toString(): string {
        return this.name
    }
}