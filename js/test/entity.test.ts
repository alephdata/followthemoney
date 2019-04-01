import { Model, Entity } from '../src/followthemoney'
import { modelData } from './_model'

const entityDatum = {
  id: 'ade69374e3f57d2dfed29ca456e4f4105e9537fe',
  schema: 'Ownership',
  properties: {
    owner: ['fa02de2d07a1062c7da8187e831010086de8c377'],
    asset: ['251e80661ad58a75f0048c629e101d1fca99e7ed'],
    role: ['Indirect Ownership']
  }
}
describe('ftm/Entity class', () => {
  const model = new Model(modelData)
  const entity = model.getEntity(entityDatum)
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
    it('should serialise to a string', function() {
      expect(entity.toString()).toContain('ade69374e3f57d2')
    })
    
  })
})
