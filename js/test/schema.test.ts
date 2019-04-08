import { Schema, Model, defaultModel } from '../src'


describe('ftm/Schema class', () => {
  const model = new Model(defaultModel)
  let schema: Schema
  beforeEach(() => {  
    schema = new Schema(model, 'Airplane', defaultModel.schemata.Airplane)
  })
  const requiredProperties = ['name', 'label', 'schemata', 'featured', 'properties']
  requiredProperties.forEach(propertyName => {
    it(`should have property ${propertyName}`, () => {
      expect(schema).toHaveProperty(propertyName)
    })
  })
  describe('method isA', () => {
    it('should work for a different inputs', () => {
      expect(schema.isA('Thing')).toBe(true)
      expect(schema.isA('Directorship')).toBe(false)
      expect(schema.isA(null)).toBe(false)
      expect(schema.isA(undefined)).toBe(false)
      const ex = model.getSchema('Thing')
      expect(schema.isA(ex)).toBe(true)
    })
  })
  describe('method isAny', () => {
    it('should work for a different inputs', () => {
      expect(schema.isAny(['Thing'])).toBe(true)
      expect(schema.isAny(['Directorship'])).toBe(false)
      expect(schema.isAny(['Banana'])).toBe(false)
    })
  })
  describe('method isThing', () => {
    it('should exist', () => {
      expect(schema.isThing).toBeDefined()
    })
    it('should be a function', () => {
      expect(schema.isThing).toBeInstanceOf(Function)
    })
    it('should return true for things', () => {
      expect(schema.isThing()).toBe(true)
    })
    it('should return false for Intervals', () => {
      const theSchema = new Schema(schema.model, 'Interval', defaultModel.schemata.Interval)
      expect(theSchema.isThing()).toBe(false)
    })
  })
  describe('method isDocument', () => {
    let document: Schema
    beforeEach(() => {
      document = new Schema(schema.model, 'Audio', defaultModel.schemata.Audio)
    })
    it('should exist', () => {
      expect(document.isDocument).toBeDefined()
    })
    it('should be a function', () => {
      expect(document.isDocument).toBeInstanceOf(Function)
    })
    it('should return true for documents', () => {
      expect(document.isDocument()).toBe(true)
    })
    it('should return false for non-documents', () => {
      const nonDocument = new Schema(schema.model, 'Interval', defaultModel.schemata.Interval)
      expect(nonDocument.isDocument()).toBe(false)
    })
  })
})
