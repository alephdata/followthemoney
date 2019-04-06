import { Model, defaultModel } from '../src/followthemoney'

const entityDatum = {
  id: 'ade69374e3f57d2dfed29ca456e4f4105e9537fe',
  schema: 'Ownership',
  properties: {
    owner: ['fa02de2d07a1062c7da8187e831010086de8c377'],
    asset: ['251e80661ad58a75f0048c629e101d1fca99e7ed'],
    role: ['Indirect Ownership']
  }
}

const otherEntity = {
  id: 'fa02de2d07a1062c7da8187e831010086de8c377',
  schema: 'Person',
  properties: {
    name: ['Karl Marx']
  }
}

describe('ftm/Entity class', () => {
  const model = new Model(defaultModel)
  const entity = model.getEntity(entityDatum)
  const person = model.getEntity(otherEntity)
  describe('entity', () => {
    it('should return a an array', function() {
      expect(entity.getProperty('owner')).toBeInstanceOf(Array)
      expect(entity.getProperty('owner')).toHaveLength(1)
      expect(() => {
        entity.hasProperty('banana')
      }).toThrow(Error)
    })
    it('can check a property', function() {
      expect(entity.hasProperty('owner')).toBeTruthy()
      expect(entity.hasProperty('startDate')).toBeFalsy()
      expect(() => {
        entity.hasProperty('banana')
      }).toThrow(Error)
    })
    it('lets you get set a property', function() {
      expect(entity.setProperty('summary', 'The Owner')).toBeInstanceOf(Array)
      expect(() => {
        entity.setProperty('fruit', 'banana')
      }).toThrow(Error)
    })
    it('can list properties', function() {
      const fresh = model.getEntity(entityDatum)
      expect(fresh.getProperties()).toBeInstanceOf(Array)
      expect(fresh.getProperties()).toHaveLength(3)
    })
    it('can get a null caption', function() {
      expect(entity.getCaption()).toBeFalsy()
    })
    it('can get a text caption', function() {
      expect(person.getCaption()).toBe("Karl Marx")
    })
    it('can get all typed values', function() {
      expect(person.getTypeValues('name')).toHaveLength(1)
      expect(person.getTypeValues('date')).toHaveLength(0)
    })
    it('can get all typed values', function() {
      const type = model.getType('name')
      expect(person.getTypeValues(type)).toHaveLength(1)
    })
    it('should serialise to a string', function() {
      expect(entity.toString()).toContain('ade69374e3f57d2')
    })
  })
})
