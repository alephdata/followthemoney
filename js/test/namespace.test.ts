import { Namespace } from '../src/namespace'


describe('ftm/Namespace class', () => {
  const namespaceInstance = new Namespace('test_namespace');
  const testSignature = '49673416';
  const testId = '3f4e94b5e30aa66090df8f4bf9e701e4f4061fdf';
  const testId2 = 'e701e4f4061f45345354df';
  const testSignedId = [testId, testSignature].join('.');
  const testSignedId2 = [testId2, testSignature].join('.');

  it('should be instantiable', () => {
    expect(namespaceInstance).toBeInstanceOf(Namespace)
  })

  describe('method parse', () => {
    it('should exist', () => {
      expect(namespaceInstance).toHaveProperty('parse')
    })
    it('should return a separated namespace and entity', function() {
      expect(namespaceInstance.parse(testSignedId)).toHaveLength(2);
      expect(namespaceInstance.parse(testSignedId)).toStrictEqual([testId, testSignature]);
    })
    it('should handle non-namespaced ids', function() {
      expect(namespaceInstance.parse(testId)).toStrictEqual([testId]);
    })
  })

  describe('method sign', () => {
    it('should exist', () => {
      expect(namespaceInstance).toHaveProperty('sign')
    })
    it('should return the input if input id is empty', function() {
      expect(namespaceInstance.sign('')).toBe('');
    })
    it('should return the input id if no namespace given', function() {
      const emptyNamespace = new Namespace('');
      expect(emptyNamespace.sign(testSignedId)).toBe(testId);
    })
    it('should return a signed entityId', function() {
      const re = new RegExp(`${testId}\..*`)
      expect(namespaceInstance.sign(testSignedId)).toMatch(re);
    })
    it('should be able to sign multiple ids', function() {
      const [signedId1, digest1] = namespaceInstance.sign(testSignedId).split('.');
      const [signedId2, digest2] = namespaceInstance.sign(testSignedId2).split('.');

      expect(signedId1).toMatch(testId);
      expect(signedId2).toMatch(testId2);
      expect(digest1).toEqual(digest2);
    })
  })
})
