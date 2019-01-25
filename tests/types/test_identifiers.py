import unittest

from followthemoney.types import registry

identifiers = registry.identifier


class IdentifiersTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(identifiers.clean('88/9'), '88/9')

    def test_normalize(self):
        self.assertEqual(identifiers.normalize('FOO'), ['foo'])
        self.assertEqual(identifiers.normalize('xx '), ['xx'])
        self.assertEqual(identifiers.normalize(' '), [])

    def test_domain_validity(self):
        self.assertTrue(identifiers.validate('foo@pudo.org'))

    def test_compare(self):
        comp = identifiers.compare('AS98187', '98187')
        assert comp > 0, comp
        comp = identifiers.compare_safe(None, '98187')
        assert comp == 0, comp
        comp = identifiers.compare_sets(['AS98187'], ['98187'])
        assert comp > 0, comp
        comp = identifiers.compare_sets(['98187'], ['AS98187'])
        assert comp > 0, comp
