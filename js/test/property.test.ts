import { Property, Model } from '../src'
import modelData from '../src/defaultModel.json'


describe('ftm/Property class', () => {
  let property: Property
  beforeEach(() => {
    const model = new Model(modelData)
    const schema = model.getSchema('Thing')
    property = new Property(schema, modelData.schemata.Thing.properties.address)
  })
  const requiredProperties = ['name', 'label', 'type']

  requiredProperties.forEach(propertyName => {
    it(`should have property ${propertyName}`, () => {
      expect(property).toHaveProperty(propertyName)
      expect(Reflect.get(property, propertyName)).not.toBeUndefined()
    })
  })
})
