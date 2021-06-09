import unittest

from followthemoney.types import registry

names = registry.name


class NamesTest(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(repr(names), "<name>")

    def test_parse(self):
        self.assertEqual(names.clean("Hans Well"), "Hans Well")
        self.assertEqual(names.clean("Hans   Well "), "Hans Well")
        self.assertEqual(names.clean('"Hans Well"'), "Hans Well")

    def test_pick(self):
        values = ["Banana", "banana", "nanana", "Batman"]
        self.assertEqual(names.pick(values), "Banana")
        self.assertEqual(names.pick("Banana"), "Banana")
        self.assertEqual(names.pick([]), None)
        values = ["Robert Smith", "Rob Smith", "Robert SMITH"]
        self.assertEqual(names.pick(values), "Robert SMITH")

    def test_domain_validity(self):
        self.assertTrue(names.validate("huhu"))
        self.assertFalse(names.validate(""))

    def test_specificity(self):
        self.assertEqual(names.specificity("bo"), 0)
        self.assertGreater(names.specificity("boban"), 0)
