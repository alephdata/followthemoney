import unittest

from followthemoney import model
from followthemoney.types import registry


class PhonesTest(unittest.TestCase):
    def test_us_number(self):
        phones = registry.phone
        self.assertEqual(phones.clean("+1-800-784-2433"), "+18007842433")
        self.assertEqual(phones.clean("+1 800 784 2433"), "+18007842433")
        self.assertEqual(phones.clean("+18007842433"), "+18007842433")
        self.assertEqual(phones.clean("+1 555 8379"), None)

        self.assertTrue(phones.validate("+18007842433"))
        self.assertFalse(phones.validate("banana"))

    def test_de_number(self):
        phones = registry.phone
        proxy = model.make_entity("Person")
        proxy.add("country", "DE")
        self.assertEqual(phones.clean("017623423980"), None)
        self.assertEqual(phones.clean("017623423980", proxy=proxy), "+4917623423980")

    def test_specificity(self):
        phones = registry.phone
        self.assertEqual(phones.specificity("+4917623423980"), 1)

    def test_country_hint(self):
        phones = registry.phone
        self.assertEqual(phones.country_hint("+4917623423980"), "de")
        self.assertEqual(phones.country_hint(None), None)
