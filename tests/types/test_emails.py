import unittest

from followthemoney.types import registry

emails = registry.email


class EmailsTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(emails.clean('foo@pudo.org'), 'foo@pudo.org')
        self.assertEqual(emails.clean('"foo@pudo.org"'), 'foo@pudo.org')
        self.assertEqual(emails.clean('pudo.org'), None)
        self.assertEqual(emails.clean('@pudo.org'), None)
        self.assertEqual(emails.clean('foo@'), None)
        self.assertEqual(emails.clean(None), None)
        self.assertEqual(emails.clean(5), None)
        self.assertEqual(emails.clean('foo@PUDO.org'), 'foo@pudo.org')
        self.assertEqual(emails.clean('FOO@PUDO.org'), 'FOO@pudo.org')

    def test_normalize(self):
        self.assertEqual(emails.normalize(None), [])
        self.assertEqual(emails.normalize('FOO@PUDO'), [])
        self.assertEqual(emails.normalize('FOO@PUDO.org'), ['foo@pudo.org'])

    def test_domain_validity(self):
        self.assertTrue(emails.validate('foo@pudo.org'))
        self.assertFalse(emails.validate('foo@pudo'))
        self.assertFalse(emails.validate(None))
        self.assertFalse(emails.validate(''))
        self.assertFalse(emails.validate('@pudo.org'))
        self.assertFalse(emails.validate('foo@'))

    def test_specificity(self):
        self.assertEqual(emails.specificity('foo@pudo.org'), 1)
