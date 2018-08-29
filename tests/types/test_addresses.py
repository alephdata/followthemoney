import unittest

from followthemoney.types import addresses

UK = """43 Duke Street
Edinburgh
EH6 8HH"""


class AddressesTest(unittest.TestCase):

    def test_clean(self):
        self.assertEqual(addresses.clean(UK),
                         '43 Duke Street, Edinburgh, EH6 8HH')
        self.assertEqual(addresses.clean('huhu\n   haha'), 'huhu, haha')
        self.assertEqual(addresses.clean('huhu,\n haha'), 'huhu, haha')

    def test_normalize(self):
        self.assertEqual(addresses.normalize(UK), ['43 Duke Street, Edinburgh, EH6 8HH'])  # noqa
        self.assertEqual(addresses.normalize('\n  '), [])

    def test_specificity(self):
        self.assertGreater(addresses.specificity(UK), 0.2)
        self.assertLess(addresses.specificity('London'), 0.2)
