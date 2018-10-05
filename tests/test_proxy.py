from unittest import TestCase
from nose.tools import assert_raises
from followthemoney.exc import InvalidData


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
        assert proxy.get('name') == ['Ralph Tester']
        prop = model.get_qname('Thing:name')
        assert proxy.get(prop) == ['Ralph Tester']

        name = 'Ralph the Great'
        proxy.add('name', name)
        assert len(proxy.get('name')) == 2
        assert name in proxy.get('name')
        assert name in proxy.names, proxy.names

        double = EntityProxy.from_dict(model, proxy)
        assert double == proxy

        with assert_raises(InvalidData):
            proxy.add('banana', name)

        with assert_raises(InvalidData):
            EntityProxy.from_dict(model, {})

    def test_dict_passthrough(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        data = proxy.to_dict()
        assert data['id'] == ENTITY['id']
        assert data['schema'] == ENTITY['schema']
        assert 'idNumber' in data['properties']

    def test_inverted_props(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        data = proxy.get_type_inverted()
        assert 'names' in data
        assert '1972-05-01' in data['dates']
        assert 'countries' not in data
        proxy.add('nationality', ['vg'])
        assert 'vg' in proxy.countries
        data = proxy.get_type_inverted()
        assert 'countries'in data

    def test_make_id(self):
        thing = model.get('Thing')
        proxy = EntityProxy(thing, {}, key_prefix=None)
        assert not proxy.make_id(None)
        assert proxy.make_id('banana')
        assert proxy.make_id('banana') == proxy.make_id('banana')
        ff = proxy.make_id(44)
        assert ff is not None
        proxy = EntityProxy(thing, {}, key_prefix='foo')
        assert proxy.make_id(44)
        assert proxy.make_id(44) != ff, proxy.make_id(44)

    def test_merge(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        other = {
            'schema': 'LegalEntity',
            'properties': {
                'country': 'gb'
            }
        }
        other = EntityProxy.from_dict(model, other)
        merged = proxy.merge(other)
        assert 'Ralph Tester' in merged.names, merged.names
        assert 'gb' in merged.countries, merged.countries
