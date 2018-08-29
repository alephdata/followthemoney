import unittest

from followthemoney.types import entities


class EntityTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(entities.clean('88'), '88')
        self.assertEqual(entities.clean(88), '88')
        self.assertEqual(entities.clean({'id': 88}), '88')
        self.assertEqual(entities.clean(None), None)

    def test_normalize(self):
        self.assertEqual(entities.normalize('FOO'), ['FOO'])
        self.assertEqual(entities.normalize(None), [])
