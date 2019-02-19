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
        self.assertEquals(linker.resolve('a'), linker.resolve('b'))
        self.assertEquals(linker.resolve('b'), linker.resolve('a'))
        linker.add('b', 'c')
        self.assertEquals(linker.resolve('a'), linker.resolve('c'))
        self.assertEquals(linker.resolve('b'), linker.resolve('c'))
        linker.add('b', 'a')
        self.assertEquals(linker.resolve('a'), linker.resolve('c'))
        self.assertEquals(linker.resolve('b'), linker.resolve('c'))
        linker.add('c', 'a')
        self.assertEquals(linker.resolve('a'), linker.resolve('c'))
        self.assertEquals(linker.resolve('b'), linker.resolve('c'))
        linker.add('c', 'd')
        self.assertEquals(linker.resolve('a'), linker.resolve('d'))
        self.assertEquals(linker.resolve('b'), linker.resolve('d'))

        self.assertTrue(linker.has('a'))
        self.assertTrue(linker.has('d'))
        self.assertFalse(linker.has('x'))
        self.assertFalse(linker.has(None))

    def test_remove_ns(self):
        linker = EntityLinker()
        linker.add('a.xxx', 'b.xxx')
        self.assertEquals(linker.resolve('b'), linker.resolve('a'))
        self.assertEquals(linker.resolve('b'), 'a')

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
        self.assertNotIn('bar', linked.get('sameAs'))
        self.assertIn('banana', linked.get('sameAs'))
        self.assertIn('qux', linked.get('sameAs'))
