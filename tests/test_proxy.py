from unittest import TestCase
from nose.tools import assert_raises
from followthemoney.exc import InvalidData


from followthemoney import model
from followthemoney.types import registry
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
        assert hash(proxy) == hash(proxy.id)
        assert proxy.get('name') == ['Ralph Tester']
        assert proxy.first('name') == 'Ralph Tester'
        prop = model.get_qname('Thing:name')
        assert proxy.get(prop) == ['Ralph Tester']
        assert proxy.caption == 'Ralph Tester'
        assert str(proxy) == 'Ralph Tester'

        name = 'Ralph the Great'
        proxy.add('name', name)
        assert len(proxy.get('name')) == 2
        proxy.add('name', None)
        assert len(proxy.get('name')) == 2
        proxy.add('name', '')
        assert len(proxy.get('name')) == 2
        proxy.add('name', [''])
        assert len(proxy.get('name')) == 2
        proxy.add('name', {'name': 'banana'}, cleaned=True)
        assert len(proxy.get('name')) == 2
        assert name in proxy.get('name')
        assert name in proxy.names, proxy.names

        with assert_raises(InvalidData):
            proxy.add('banana', 'yellow')
        proxy.add('banana', 'yellow', quiet=True)

        mem = model.make_entity('Membership')
        mem.id = 'foo'
        with assert_raises(InvalidData):
            proxy.add('directorshipDirector', mem)

        with assert_raises(InvalidData):
            proxy.add('sameAs', proxy)

        with assert_raises(InvalidData):
            proxy.get('banana')
        assert [] == proxy.get('banana', quiet=True)

        with assert_raises(InvalidData):
            proxy.first('banana')
        assert proxy.first('banana', quiet=True) is None

        assert len(proxy.get('nationality')) == 0

        double = EntityProxy.from_dict(model, proxy)
        assert double == proxy

        proxy.add('banana', name, quiet=True)
        with assert_raises(InvalidData):
            proxy.add('banana', name)

        with assert_raises(InvalidData):
            EntityProxy.from_dict(model, {})

    def test_pop(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        get_ids = proxy.get('idNumber')
        assert get_ids, get_ids
        ids = proxy.pop('idNumber')
        assert get_ids == ids, ids
        assert not proxy.get('idNumber')
        assert not proxy.pop('idNumber')

        # new in 1.6.1: pop is quiet by default
        assert not proxy.pop('banana')
        with assert_raises(InvalidData):
            proxy.pop('banana', quiet=False)

    def test_remove(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        assert '9177171' in proxy.get('idNumber')
        proxy.remove('idNumber', '9177171')
        assert '9177171' not in proxy.get('idNumber')
        assert proxy.has('idNumber')

        proxy.remove('idNumber', 'banana')
        assert proxy.has('idNumber')
        proxy.remove('idNumber', 'banana', quiet=False)
        proxy.remove('fruit', 'banana')

        with assert_raises(InvalidData):
            proxy.remove('fruit', 'banana', quiet=False)

    def test_has(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        assert not proxy.has('birthPlace')
        proxy.add('birthPlace', 'Inferno')
        assert proxy.has('birthPlace')
        assert 1 == len(proxy.get('birthPlace'))
        proxy.add('birthPlace', 'Hell')
        assert 2 == len(proxy.get('birthPlace'))
        proxy.set('birthPlace', 'Inferno')
        assert 1 == len(proxy.get('birthPlace'))

        with assert_raises(InvalidData):
            proxy.set('banana', 'fruit')
        assert not proxy.set('banana', 'fruit', quiet=True)

        with assert_raises(InvalidData):
            proxy.has('banana')
        assert not proxy.has('banana', quiet=True)

    def test_max_size(self):
        t = registry.name
        proxy = EntityProxy.from_dict(model, ENTITY)
        prev_size = t.max_size
        t.max_size = len(proxy) + 10
        assert len(proxy.get('name')) == 1
        proxy.add('name', 'Louis George Maurice Adolphe Roche Albert Abel')
        assert len(proxy.get('name')) == 1

        proxy.set('name', 'Louis')
        assert len(proxy.get('name')) == 1, proxy.get('name')
        proxy.add('name', 'A')
        assert len(proxy.get('name')) == 2, proxy.get('name')
        proxy.add('name', 'George')
        assert len(proxy.get('name')) == 2, proxy.get('name')
        t.max_size = prev_size

    def test_len(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        proxy_len = len(proxy)
        assert proxy_len > 0, proxy_len
        proxy.add('name', "Some text")
        assert len(proxy) > proxy_len, (len(proxy), proxy_len)

    def test_dict_passthrough(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        data = proxy.to_dict()
        assert data['id'] == ENTITY['id']
        assert data['schema'] == ENTITY['schema']
        assert 'idNumber' in data['properties']

        data = proxy.to_full_dict()
        assert ENTITY['schema'] in data['schemata']
        assert 'Ralph Tester' in data['names']

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
        assert 'vg' in proxy.country_hints, proxy.country_hints
        assert 'us' in proxy.country_hints, proxy.country_hints

    def test_make_id(self):
        proxy = model.make_entity('Thing')
        assert not proxy.make_id(None)
        assert proxy.make_id('banana')
        assert proxy.make_id('banana') == proxy.make_id('banana')
        ff = proxy.make_id(44)
        assert ff is not None
        proxy = model.make_entity('Thing', key_prefix='foo')
        assert proxy.make_id(44)
        assert proxy.make_id(44) != ff, proxy.make_id(44)

    def test_clone(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        other = proxy.clone()
        assert other == proxy
        other.id = 'banana'
        assert proxy.id == 'test'
        assert other != proxy

    def test_merge(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        proxy.merge(proxy)
        other = {
            'schema': 'LegalEntity',
            'properties': {
                'country': 'gb'
            }
        }
        other = EntityProxy.from_dict(model, other)
        proxy.merge(other)
        assert 'Ralph Tester' in proxy.names, proxy.names
        assert 'gb' in proxy.countries, proxy.countries

    def test_context(self):
        data = {'fruit': 'banana', 'schema': 'Person'}
        proxy = EntityProxy.from_dict(model, data)
        res = proxy.clone().to_dict()
        assert res['fruit'] == data['fruit'], res

    def test_rdf(self):
        proxy = EntityProxy.from_dict(model, ENTITY)
        triples = list(proxy.triples())
        assert 10 == len(triples), len(triples)

        proxy = model.make_entity('Person')
        assert 0 == len(list(proxy.triples()))
