import unittest

from followthemoney.types import registry


class LanguagesTest(unittest.TestCase):

    def test_validate(self):
        languages = registry.language
        self.assertTrue(languages.validate('deu'))
        self.assertTrue(languages.validate('eng'))
        self.assertFalse(languages.validate('us'))
        self.assertFalse(languages.validate(''))
        self.assertFalse(languages.validate(None))

    def test_clean(self):
        languages = registry.language
        self.assertEqual(languages.clean('deu'), 'deu')
        self.assertEqual(languages.clean('de'), 'deu')
        self.assertEqual(languages.clean('xx'), None)
        self.assertEqual(languages.clean(None), None)

    def test_funcs(self):
        languages = registry.language
        self.assertGreater(len(languages.names), 1)
        self.assertEqual(str(languages.rdf('deu')), 'iso-639:deu')
        self.assertEqual(languages.specificity('deu'), 0)
