import { Namespace } from '../src/namespace'


describe('ftm/Namespace class', () => {
  const namespaceInstance = new Namespace('test_namespace');
  const testSignature = '49673416';
  const testId = '3f4e94b5e30aa66090df8f4bf9e701e4f4061fdf';
  const testId2 = 'e701e4f4061f45345354df';
  const testSignedId = [testSignature, testId].join('.');
  const testSignedId2 = [testSignature, testId2].join('.');

  it('should be instantiable', () => {
    expect(namespaceInstance).toBeInstanceOf(Namespace)
  })

  describe('method parse', () => {
    it('should exist', () => {
      expect(namespaceInstance).toHaveProperty('parse')
    })
    it('should return a separated namespace and entity', function() {
      expect(namespaceInstance.parse(testSignedId)).toHaveLength(2);
      expect(namespaceInstance.parse(testSignedId)).toStrictEqual([testSignature, testId]);
    })
    it('should handle non-namespaced ids', function() {
      expect(namespaceInstance.parse(testId)).toHaveLength(2);
      expect(namespaceInstance.parse(testId)).toStrictEqual([null, testId]);
    })
  })

  describe('method sign', () => {
    it('should exist', () => {
      expect(namespaceInstance).toHaveProperty('sign')
    })
    it('should return null if input id is null', function() {
      expect(namespaceInstance.sign('')).toBe(null);
    })
    it('should return the input id if no namespace given', function() {
      const emptyNamespace = new Namespace('');
      expect(emptyNamespace.sign(testSignedId)).toBe(testId);
    })
    it('should return a signed entityId', function() {
      const re = new RegExp(`.*\.${testId}`)
      expect(namespaceInstance.sign(testSignedId)).toMatch(re);
    })
    it('should be able to sign multiple ids', function() {
      const re = new RegExp(`.*\.${testId}`)
      expect(namespaceInstance.sign(testSignedId)).toMatch(re);
      const re2 = new RegExp(`.*\.${testId2}`)
      expect(namespaceInstance.sign(testSignedId2)).toMatch(re2);

    })
  })
})
