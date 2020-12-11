import unittest

from followthemoney.types import registry

identifiers = registry.identifier


class IdentifiersTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(identifiers.clean("88/9"), "88/9")

    def test_domain_validity(self):
        self.assertTrue(identifiers.validate("foo@pudo.org"))

    def test_compare(self):
        comp = identifiers.compare("AS9818700", "9818700")
        assert comp > 0, comp
        comp = identifiers.compare_safe(None, "9818700")
        assert comp == 0, comp
        comp = identifiers.compare_sets(["AS9818700"], ["9818700"])
        assert comp > 0, comp
        comp = identifiers.compare_sets(["9818700"], ["AS9818700"])
        assert comp > 0, comp
