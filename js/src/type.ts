
export interface IPropertyTypeDatum {
    group?: string
    label?: string
    plural?: string | null
    matchable?: boolean
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
    public matchable: boolean
    public isEntity: boolean;

    constructor(name: string, data: IPropertyTypeDatum) {
        this.name = name
        this.label = data.label || name
        this.plural = data.plural || this.label
        this.group = data.group || null
        this.grouped = data.group !== undefined
        this.matchable = !!data.matchable
        this.isEntity = name === PropertyType.ENTITY;
    }

    toString(): string {
        return this.name
    }

}