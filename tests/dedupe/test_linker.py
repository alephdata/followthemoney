from unittest import TestCase

from followthemoney import model
from followthemoney.dedupe import EntityLinker


class LinkerTestCase(TestCase):

    def test_linker(self):
        linker = EntityLinker()
        self.assertEqual(linker.resolve('abc'), 'abc')
        self.assertEqual(linker.resolve({'id': 'abc'}), 'abc')
        linker.add('abc', 'bbc')
        linker.add('abc', None)
        linker.add('abc', 'abc')
        self.assertEqual(linker.resolve('abc'), linker.resolve('bbc'))
        self.assertEqual(linker.resolve('bbc'), linker.resolve('abc'))
        linker.add('bbc', 'ccc')
        self.assertEqual(linker.resolve('abc'), linker.resolve('ccc'))
        self.assertEqual(linker.resolve('bbc'), linker.resolve('ccc'))
        linker.add('bbc', 'abc')
        self.assertEqual(linker.resolve('abc'), linker.resolve('ccc'))
        self.assertEqual(linker.resolve('bbc'), linker.resolve('ccc'))
        linker.add('ccc', 'abc')
        self.assertEqual(linker.resolve('abc'), linker.resolve('ccc'))
        self.assertEqual(linker.resolve('bbc'), linker.resolve('ccc'))
        linker.add('ccc', 'cdc')
        self.assertEqual(linker.resolve('abc'), linker.resolve('cdc'))
        self.assertEqual(linker.resolve('bbc'), linker.resolve('cdc'))

        self.assertTrue(linker.has('abc'))
        self.assertTrue(linker.has('cdc'))
        self.assertFalse(linker.has('x'))
        self.assertFalse(linker.has(None))

    def test_remove_ns(self):
        linker = EntityLinker()
        linker.add('abc.xxx', 'bbc.xxx')
        self.assertEqual(linker.resolve('bbc'), linker.resolve('abc'))
        self.assertEqual(linker.resolve('bbc'), 'abc')

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
        self.assertEqual(linked.id, 'bar')
        self.assertNotIn('bar', linked.get('sameAs'))
        self.assertIn('banana', linked.get('sameAs'))
        self.assertIn('qux', linked.get('sameAs'))
