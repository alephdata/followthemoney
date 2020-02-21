import unittest

from followthemoney.types import registry

entities = registry.entity


class EntityTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(entities.clean('888'), '888')
        self.assertEqual(entities.clean(888), '888')
        self.assertEqual(entities.clean({'id': 888}), '888')
        self.assertEqual(entities.clean(None), None)
        self.assertEqual(entities.clean('With spaces'), None)
        self.assertEqual(entities.clean('With-dash'), 'With-dash')
        self.assertEqual(entities.clean('With!special'), None)
        self.assertEqual(entities.clean('with.dot'), 'with.dot')
        self.assertEqual(entities.clean('14'), '14')
        self.assertEqual(entities.clean(14), '14')


    def test_normalize(self):
        self.assertEqual(entities.normalize('FOO'), ['FOO'])
        self.assertEqual(entities.normalize(None), [])

    def test_funcs(self):
        self.assertEqual(entities.specificity('bla'), 1)
