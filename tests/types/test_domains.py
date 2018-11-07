import unittest

from followthemoney.types import registry

domains = registry.domain


class DomainsTest(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(domains.clean('pudo.org'), 'pudo.org')
        self.assertEqual(domains.clean('pudoorg'), None)
        self.assertEqual(domains.clean(None), None)
        self.assertEqual(domains.clean('x.a'), None)

    def test_normalize(self):
        self.assertEqual(domains.normalize('PUDO'), [])
        self.assertEqual(domains.normalize('PUDO.org'), ['pudo.org'])

    def test_domain_validity(self):
        self.assertTrue(domains.validate('pudo.org'))
        self.assertFalse(domains.validate('pudo'))
        self.assertFalse(domains.validate('x.a'))
        self.assertFalse(domains.validate(''))
        self.assertFalse(domains.validate('@pudo.org'))
