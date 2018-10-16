import unittest

from followthemoney.types import languages


class LanguagesTest(unittest.TestCase):

    def test_validate(self):
        self.assertTrue(languages.validate('de'))
        self.assertTrue(languages.validate('en'))
        self.assertFalse(languages.validate('us'))
        self.assertFalse(languages.validate(None))

    def test_cleam(self):
        self.assertEquals(languages.clean('de'), 'de')
        self.assertEquals(languages.clean('xx'), None)
        self.assertEquals(languages.clean(None), None)

    def test_funcs(self):
        self.assertEqual(str(languages.rdf('de')), 'iso-639:de')

    def test_specificity(self):
        self.assertEqual(languages.specificity('de'), 0)
