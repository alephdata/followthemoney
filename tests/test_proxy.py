from unittest import TestCase

from followthemoney import model
from followthemoney.proxy import EntityProxy


ENTITY = {
    'id': 'test',
    'schema': 'Person',
    'properties': {
        'name': 'Ralph Tester',
        'birthDate': '1972-05-01',
        'idNumber': ['9177171', '8e839023'],
        'website': 'https://ralphtester.me',
        'phone': '+12025557612',
        'email': 'info@ralphtester.me',
        'passport': 'passportEntityId'
    }
}


class ProxyTestCase(TestCase):

    def test_base_functions(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        assert 'test' in repr(proxy), repr(proxy)
        data = proxy.to_dict()
        assert data['id'] == ENTITY['id']
        assert data['schema'] == ENTITY['schema']
