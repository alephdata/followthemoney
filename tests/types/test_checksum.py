import unittest

from followthemoney.types import registry


class ChecksumTest(unittest.TestCase):

    def test_rdf(self):
        csum = registry.checksum.rdf('00deadbeef')
        assert 'hash:00deadbeef' in csum
