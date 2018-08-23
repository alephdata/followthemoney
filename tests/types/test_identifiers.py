import unittest

from followthemoney.types import identifiers


class IdentifiersTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(identifiers.clean('88/9'), '88/9')

    def test_normalize(self):
        self.assertEqual(identifiers.normalize('FOO'), ['foo'])
        self.assertEqual(identifiers.normalize('xx '), ['xx'])
        self.assertEqual(identifiers.normalize(' '), [])

    def test_domain_validity(self):
        self.assertTrue(identifiers.validate('foo@pudo.org'))