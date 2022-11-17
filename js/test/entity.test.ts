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

const passportEntity = {
  id: 'fa02de2d07a1062c7da8187e831010086de8c37',
  schema: 'Passport',
  properties: {
  }
}

describe('ftm/Entity class', () => {
  const model = new Model(defaultModel)
  const entity = model.getEntity(entityDatum)
  const person = model.getEntity(otherEntity)
  const passport = model.getEntity(passportEntity)
  describe('entity', () => {
    it('should return a an array', function() {
      expect(entity.getProperty('owner')).toBeInstanceOf(Array)
      expect(entity.getProperty('owner')).toHaveLength(1)
      expect(entity.getProperty('startDate')).toHaveLength(0)
      expect(entity.getProperty('banana')).toHaveLength(0)
    })
    it('can check a property', function() {
      expect(entity.hasProperty('owner')).toBeTruthy()
      expect(entity.hasProperty('startDate')).toBeFalsy()
      expect(entity.hasProperty('banana')).toBeFalsy()
    })
    it('lets you get set a property', function() {
      expect(entity.setProperty('summary', 'The Owner')).toBeInstanceOf(Array)
      expect(entity.setProperty('startDate', '')).toHaveLength(0)
      expect(entity.setProperty('startDate', '  ')).toHaveLength(0)
      expect(entity.setProperty('startDate', null)).toHaveLength(0)
      expect(entity.setProperty('startDate', undefined)).toHaveLength(0)
      expect(entity.setProperty('owner', otherEntity)).toHaveLength(2)
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
      expect(entity.getCaption()).toBe(entity.schema.label)
    })
    it('can get a text caption', function() {
      expect(person.getCaption()).toBe("Karl Marx")
    })
    it('can get a single property value', function() {
      expect(person.getFirst('name')).toBe("Karl Marx")
      expect(person.getFirst('previousName')).toBe(null)
    })
    it('can get all typed values', function() {
      expect(person.getTypeValues('name')).toHaveLength(1)
      expect(person.getTypeValues('name', true)).toHaveLength(1)
      expect(person.getTypeValues('date')).toHaveLength(0)
    })
    it('can get all typed values', function() {
      const type = model.getType('name')
      expect(person.getTypeValues(type)).toHaveLength(1)
    })
    it('can set a text caption', function() {
      const testNumber = '25289010'
      passport.setCaption(testNumber)
      expect(passport.getCaption()).toBe(testNumber)
    })
    it('can get temporal start', function() {
      let entity;

      entity = model.getEntity({ id: '1', schema: 'Event' })
      expect(entity.getTemporalStart()).toBeNull()

      entity = model.getEntity({
        id: '1',
        schema: 'Event',
        properties: {
          startDate: ['2022-01-01'],
        },
      })
      expect(entity.getTemporalStart()).toEqual('2022-01-01')

      entity = model.getEntity({
        id: '1',
        schema: 'Event',
        properties: {
          startDate: ['2022-01-01', '2022-02-01'],
        },
      })
      expect(entity.getTemporalStart()).toEqual('2022-01-01')
    })
    it('can get temporal end', function () {
      let entity;

      entity = model.getEntity({ id: '1', schema: 'Event' })
      expect(entity.getTemporalEnd()).toBeNull()

      entity = model.getEntity({
        id: '1',
        schema: 'Event',
        properties: {
          endDate: ['2022-02-01'],
        },
      })
      expect(entity.getTemporalEnd()).toEqual('2022-02-01')

      entity = model.getEntity({
        id: '1',
        schema: 'Event',
        properties: {
          endDate: ['2022-01-01', '2022-02-01'],
        },
      })
      expect(entity.getTemporalEnd()).toEqual('2022-02-01')
    })
  })
})
