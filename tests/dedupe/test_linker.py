from unittest import TestCase

from followthemoney import model
from followthemoney.dedupe import EntityLinker


class LinkerTestCase(TestCase):

    def test_linker(self):
        linker = EntityLinker()
        self.assertEquals(linker.resolve('a'), 'a')
        self.assertEquals(linker.resolve({'id': 'a'}), 'a')
        linker.add('a', 'b')
        linker.add('a', None)
        linker.add('a', 'a')
        self.assertEquals(linker.resolve('a'), 'b')
        self.assertEquals(linker.resolve('b'), 'b')
        linker.add('b', 'c')
        self.assertEquals(linker.resolve('a'), 'c')
        self.assertEquals(linker.resolve('b'), 'c')
        linker.add('b', 'a')
        self.assertEquals(linker.resolve('a'), 'c')
        self.assertEquals(linker.resolve('b'), 'c')
        linker.add('c', 'a')
        self.assertEquals(linker.resolve('a'), 'c')
        self.assertEquals(linker.resolve('b'), 'c')
        linker.add('c', 'd')
        self.assertEquals(linker.resolve('a'), 'd')
        self.assertEquals(linker.resolve('b'), 'd')

        self.assertTrue(linker.has('a'))
        self.assertFalse(linker.has('d'))
        self.assertFalse(linker.has('x'))
        self.assertFalse(linker.has(None))

    def test_linker_apply(self):
        linker = EntityLinker()
        linker.add('foo', 'fox')
        linker.add('fox', 'bar')
        linker.add('qux', 'quux')

        entity = model.get_proxy({
            'id': 'foo',
            'schema': 'Company',
            'properties': {
                'sameAs': ['qux', 'banana']
            }
        })
        linked = linker.apply(entity)
        self.assertEquals(linked.id, 'bar')
        self.assertIn('quux', linked.get('sameAs'))
        self.assertIn('banana', linked.get('sameAs'))
        self.assertNotIn('qux', linked.get('sameAs'))
