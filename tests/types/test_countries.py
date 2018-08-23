import unittest

from followthemoney.types import countries


class CountriesTest(unittest.TestCase):

    def test_country_codes(self):
        self.assertEqual(countries.clean('DE'), 'de')
        self.assertTrue(countries.validate('DE'))
        self.assertFalse(countries.validate('DEU'))
        self.assertFalse(countries.validate('SU'))
        self.assertTrue(countries.validate('XK'))
        self.assertTrue(countries.validate('EU'))

    def test_country_names(self):
        self.assertEqual(countries.clean(None), None)
        self.assertEqual(countries.clean('Takatukaland', guess=False), None)
        self.assertEqual(countries.clean('Germany'), 'de')
        # self.assertEqual(countries.clean('Germani'), 'de')
        self.assertEqual(countries.clean('Soviet Union'), 'suhh')
