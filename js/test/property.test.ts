import { Property, Model, defaultModel } from '../src'


describe('ftm/Property class', () => {
  const model = new Model(defaultModel)
  const schema = model.getSchema('Thing')
  let property: Property
  beforeEach(() => {  
    property = new Property(schema, defaultModel.schemata.Thing.properties.address)
  })
  const requiredProperties = ['name', 'label', 'type']

  requiredProperties.forEach(propertyName => {
    it(`should have property ${propertyName}`, () => {
      expect(property).toHaveProperty(propertyName)
      expect(Reflect.get(property, propertyName)).not.toBeUndefined()
    })
  })

  it('check sameAs', function() {
    const sameAs = schema.getProperty('sameAs');
    expect(sameAs).toBeInstanceOf(Property)
    expect(sameAs.hasReverse).toBeTruthy()
    expect(sameAs.getRange()).toBe(schema)
    expect(sameAs.getReverse()).toBe(sameAs)
  })

  it('check name reverse', function() {
    const nameProp = schema.getProperty('name');
    expect(nameProp).toBeInstanceOf(Property)
    expect(nameProp.hasReverse).toBeFalsy()
    expect(() => {
      nameProp.getRange()
    }).toThrow(Error)
    expect(() => {
      nameProp.getReverse()
    }).toThrow(Error)
  })
})
