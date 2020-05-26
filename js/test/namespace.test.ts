import { Namespace } from '../src/namespace'


describe('ftm/Namespace class', () => {
  const namespaceInstance = new Namespace('test_namespace');
  const testId = '3f4e94b5e30aa66090df8f4bf9e701e4f4061fdf';
  const testId2 = 'e701e4f4061f45345354df';
  const testSignedId = namespaceInstance.sign(testId);
  const testSignedId2 = namespaceInstance.sign(testId2);

  it('should be instantiable', () => {
    expect(namespaceInstance).toBeInstanceOf(Namespace)
  })

  describe('method parse', () => {
    it('should exist', () => {
      expect(namespaceInstance).toHaveProperty('parse')
    })
    it('should return a separated namespace and entity', function() {
      expect(namespaceInstance.parse(testSignedId)).toHaveLength(2);
      expect(namespaceInstance.parse(testSignedId)[0]).toStrictEqual(testId);
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
      const [signedId1a, digest1a] = namespaceInstance.sign(testSignedId).split('.');
      const [signedId2, digest2] = namespaceInstance.sign(testSignedId2).split('.');

      expect(signedId1).toMatch(testId);
      expect(digest1).toMatch(digest1a);
      expect(signedId2).toMatch(testId2);
    })
  })
})
