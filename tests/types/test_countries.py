import unittest

from followthemoney.types import registry


class CountriesTest(unittest.TestCase):

    def test_country_codes(self):
        countries = registry.country
        self.assertEqual(countries.clean('DE'), 'de')
        self.assertTrue(countries.validate('DE'))
        self.assertFalse(countries.validate('DEU'))
        self.assertFalse(countries.validate(''))
        self.assertFalse(countries.validate(None))
        self.assertFalse(countries.validate(4))
        self.assertFalse(countries.validate('SU'))
        self.assertTrue(countries.validate('XK'))
        self.assertTrue(countries.validate('EU'))

        self.assertEqual(countries.country_hint('eu'), 'eu')
        assert 'iso-3166-1:eu' in countries.rdf('eu')

    def test_country_names(self):
        countries = registry.country
        self.assertEqual(countries.clean(None), None)
        self.assertEqual(countries.clean('Takatukaland', guess=False), None)
        self.assertEqual(countries.clean('Germany'), 'de')
        # self.assertEqual(countries.clean('Germani'), 'de')
        self.assertEqual(countries.clean('Soviet Union'), 'suhh')
