# from nose.tools import assert_raises
from unittest import TestCase

from followthemoney import model
from followthemoney.types import registry
from followthemoney.link import Link

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


class LinkTestCase(TestCase):

    def test_link(self):
        ref = registry.entity.ref('banana')
        prop = model.get_qname('Thing:name')
        link = Link(ref, prop, "Theodore")
        assert link.subject == 'banana'
        assert link.value_ref == 'n:Theodore'

        key, value = link.pack()
        other = link.unpack(model, key, value)
        assert other == link, (link, other)

        assert not link.inverted
        inv = link.invert()
        assert inv.inverted
        assert inv.rdf() is None

    def test_make_links(self):
        links = list(model.entity_links(ENTITY))
        assert len(links) == 8, len(links)

    def test_rdf(self):
        triples = list(model.entity_rdf(ENTITY))
        assert len(triples) == 8, len(triples)
        for (s, p, o) in triples:
            assert 'test' in s, s
            if str(o) == 'Ralph Tester':
                assert str(p) == 'http://www.w3.org/2004/02/skos/core#prefLabel'  # noqa
            if p == registry.phone:
                assert str(o) == 'tel:+12025557612', o
        # assert False, triples

    def test_rdf_noschema(self):
        entity = ENTITY.copy()
        entity.pop('schema')
        triples = list(model.entity_rdf(entity))
        assert len(triples) == 0, triples
