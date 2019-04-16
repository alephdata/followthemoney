from unittest import TestCase

from followthemoney import model
from followthemoney.pragma import cleanup


class PragmaTestCase(TestCase):

    def test_cleanup(self):
        proxy = model.get_proxy({
            'id': 'banana',
            'schema': 'Document',
            'properties': {
                'contentHash': ['banana'],
                'publishedAt': ['2016-01-01', '2018-02-03'],
                'modifiedAt': ['2016-01-01'],
            }
        })
        proxy = cleanup(proxy)
        assert 1 == len(proxy.get('publishedAt')), proxy.get('publishedAt')
        assert '2016-01-01' in proxy.get('publishedAt')
        assert not proxy.has('contentHash')
