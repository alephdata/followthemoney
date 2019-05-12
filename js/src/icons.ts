import icons from './generated/icons.json'
import { Schema } from './schema'

interface IIconStorage {
  [iconName:string]: string[]
}

export const IconRegistry = {
  storage: icons as IIconStorage,

  getIcon(iconName: string): string[] {
    return this.storage[iconName];
  },

  getSchemaIcon(schema: Schema): string[] {
    const iconName = schema.name.toLowerCase()
    return this.getIcon(iconName) || this.getIcon('info')
  }
}
