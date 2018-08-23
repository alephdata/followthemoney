import unittest

from followthemoney.types import ips


class IPsTest(unittest.TestCase):

    def test_ip(self):
        self.assertTrue(ips.validate('172.16.254.1'))
        self.assertFalse(ips.validate('355.16.254.1'))
        self.assertFalse(ips.validate('16.254.1'))
        self.assertFalse(ips.validate('172.162541'))
        self.assertFalse(ips.validate(None))

        self.assertTrue(ips.validate('2001:db8:0:1234:0:567:8:1'))
        self.assertFalse(ips.validate('2001:zz8:0:1234:0:567:8:1'))
        self.assertFalse(ips.validate('20001:db8:0:1234:0:567:8:1'))
        self.assertFalse(ips.validate(None))
