import unittest

from followthemoney.types import registry

emails = registry.email


class EmailsTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(emails.clean("foo@pudo.org"), "foo@pudo.org")
        self.assertEqual(emails.clean('"foo@pudo.org"'), "foo@pudo.org")
        self.assertEqual(emails.clean("pudo.org"), None)
        self.assertEqual(emails.clean("@pudo.org"), None)
        self.assertEqual(emails.clean("foo@"), None)
        self.assertEqual(emails.clean(None), None)
        self.assertEqual(emails.clean(5), None)
        self.assertEqual(emails.clean("foo@PUDO.org"), "foo@pudo.org")
        self.assertEqual(emails.clean("FOO@PUDO.org"), "FOO@pudo.org")
        self.assertEqual(
            emails.clean(
                "foo@0123456789012345678901234567890123456789012345678901234567890.example.com"
            ),
            "foo@0123456789012345678901234567890123456789012345678901234567890.example.com",
        )
        self.assertEqual(
            emails.clean(
                "foo@0123456789012345678901234567890123456789012345678901234567890123.example.com"
            ),
            None,
        )

    def test_domain_validity(self):
        self.assertTrue(emails.validate("foo@pudo.org"))
        self.assertFalse(emails.validate("foo@pudo"))
        self.assertFalse(emails.validate(None))
        self.assertFalse(emails.validate(""))
        self.assertFalse(emails.validate("@pudo.org"))
        self.assertFalse(emails.validate("foo@"))

    def test_specificity(self):
        self.assertEqual(emails.specificity("foo@pudo.org"), 1)
