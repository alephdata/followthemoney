import { Model, Schema, defaultModel } from '../src'


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
  describe('method getEditableProperties', () => {
    let document: Schema
    beforeEach(() => {
      document = new Schema(schema.model, 'Audio', defaultModel.schemata.Audio)
    })
    it('should exist', () => {
      expect(document.getEditableProperties).toBeDefined()
    })
    it('should be a function', () => {
      expect(document.getEditableProperties).toBeInstanceOf(Function)
    })
    it('should return an array', () => {
      expect(document.getEditableProperties()).toBeInstanceOf(Array)
    })
    it('should not return non-editable properties', () => {
      const shouldBeHidden = document.getEditableProperties()
        .filter(prop => prop.hidden || prop.stub)
      expect(shouldBeHidden).toHaveLength(0)
    })
  })
  describe('method getParents', () => {
    let vessel: Schema
    beforeEach(() => {
      vessel = new Schema(schema.model, 'Vessel', defaultModel.schemata.Vessel)
    })
    it('should exist', () => {
      expect(vessel.getParents).toBeDefined()
    })
    it('should be a function', () => {
      expect(vessel.getParents).toBeInstanceOf(Function)
    })
    it('should return an array', () => {
      expect(vessel.getParents()).toBeInstanceOf(Array)
    })
    it('should not return Person', () => {
      const parents = vessel.getParents().map((s) => s.name)
      expect(parents).not.toContain('Person')
      expect(parents).toContain('Thing')
    })
  })
  describe('method getChildren', () => {
    let legal: Schema
    beforeEach(() => {
      legal = new Schema(schema.model, 'LegalEntity', defaultModel.schemata.LegalEntity)
    })
    it('should exist', () => {
      expect(legal.getChildren).toBeDefined()
    })
    it('should be a function', () => {
      expect(legal.getChildren).toBeInstanceOf(Function)
    })
    it('should return an array', () => {
      expect(legal.getChildren()).toBeInstanceOf(Array)
    })
    it('should return Person', () => {
      const children = legal.getChildren().map((s) => s.name)
      expect(children).not.toContain('Vessel')
      expect(children).toContain('Person')
      expect(children).toContain('Company')
    })
  })
  describe('method getTemporalStartProperties', () => {
    it('returns empty array if not specified', () => {
      const thing = model.getSchema('Thing')
      expect(thing.getTemporalStartProperties()).toEqual([])
    })

    it('returns array of properties', () => {
      const interval = model.getSchema('Interval')
      const props = interval.getTemporalStartProperties()
      expect(props.map(prop => prop.name)).toEqual(['startDate', 'date'])
    })

    it('inherits properties', () => {
      const event = model.getSchema('Event')
      const props = event.getTemporalStartProperties()
      expect(props.map(prop => prop.name)).toEqual(['startDate', 'date'])
    })
  })
  describe('method getTemporalEndProperties', () => {
    it('returns empty array if not specified', () => {
      const thing = model.getSchema('Thing')
      expect(thing.getTemporalEndProperties()).toEqual([])
    })

    it('returns array of properties', () => {
      const interval = model.getSchema('Interval')
      const props = interval.getTemporalEndProperties()
      expect(props.map(prop => prop.name)).toEqual(['endDate'])
    })

    it('inherits properties', () => {
      const event = model.getSchema('Event')
      const props = event.getTemporalEndProperties()
      expect(props.map(prop => prop.name)).toEqual(['endDate'])
    })
  })
})
