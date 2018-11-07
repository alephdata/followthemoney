import unittest

from followthemoney.types import registry


class LanguagesTest(unittest.TestCase):

    def test_validate(self):
        languages = registry.language
        self.assertTrue(languages.validate('de'))
        self.assertTrue(languages.validate('en'))
        self.assertFalse(languages.validate('us'))
        self.assertFalse(languages.validate(None))

    def test_cleam(self):
        languages = registry.language
        self.assertEquals(languages.clean('de'), 'de')
        self.assertEquals(languages.clean('xx'), None)
        self.assertEquals(languages.clean(None), None)

    def test_funcs(self):
        languages = registry.language
        self.assertEqual(str(languages.rdf('de')), 'iso-639:de')
        self.assertEqual(languages.specificity('de'), 0)
