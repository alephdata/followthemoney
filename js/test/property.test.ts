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

  it('check entity property', function () {
    const notes = schema.getProperty('noteEntities');
    expect(notes).toBeInstanceOf(Property)
    expect(notes.hasReverse).toBeTruthy()
    expect(notes.hasRange).toBeTruthy()
    expect(notes.getReverse().getRange()).toBe(schema)
  })

  it('check name reverse', function () {
    const nameProp = schema.getProperty('name');
    expect(nameProp).toBeInstanceOf(Property)
    expect(nameProp.hasReverse).toBeFalsy()
    expect(nameProp.hasRange).toBeFalsy()
    expect(() => {
      nameProp.getRange()
    }).toThrow(Error)
    expect(() => {
      nameProp.getReverse()
    }).toThrow(Error)
  })
})
