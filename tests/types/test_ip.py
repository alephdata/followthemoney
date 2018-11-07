import unittest

from followthemoney.types import registry

ips = registry.ip


class IPsTest(unittest.TestCase):

    def test_ip_validate(self):
        self.assertTrue(ips.validate('172.16.254.1'))
        self.assertFalse(ips.validate('355.16.254.1'))
        self.assertFalse(ips.validate('16.254.1'))
        self.assertFalse(ips.validate('172.162541'))
        self.assertFalse(ips.validate(None))

        self.assertTrue(ips.validate('2001:db8:0:1234:0:567:8:1'))
        self.assertFalse(ips.validate('2001:zz8:0:1234:0:567:8:1'))
        self.assertFalse(ips.validate('20001:db8:0:1234:0:567:8:1'))
        self.assertFalse(ips.validate(None))

    def test_ip_clean(self):
        self.assertEqual(ips.clean('172.16.254.1'), '172.16.254.1')
        self.assertEqual(ips.clean(None), None)
        self.assertEqual(ips.clean('-1'), None)

    def test_funcs(self):
        self.assertEqual(str(ips.rdf('172.16.254.1')), 'ip:172.16.254.1')

    def test_specificity(self):
        self.assertEqual(ips.specificity('172.16.254.1'), 1)
