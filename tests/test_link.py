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

    def test_link_pack(self):
        ref = registry.entity.ref('banana')
        prop = model.get_qname('Thing:name')
        link = Link(ref, prop, "Theodore Böln")
        assert link.subject == 'banana'
        assert link.value_ref == 'n:Theodore Böln'

        value = link.to_tuple()
        other = link.from_tuple(model, link.ref, value)
        assert other == link, (link, other)
        assert hash(other) == hash(link)
        assert repr(other) == repr(link)

    def test_invert(self):
        ref = registry.entity.ref('banana')
        prop = model.get_qname('Thing:name')
        link = Link(ref, prop, "Theodore")
        assert not link.inverted
        inv = link.invert()
        assert inv.inverted
        assert inv.rdf() is None

        banana = registry.entity.ref('banana')
        peach = 'peach'
        peach_ref = registry.entity.ref(peach)
        prop = model.get_qname('Thing:sameAs')
        link = Link(banana, prop, peach)
        inv = link.invert()
        assert inv.ref == peach_ref
        assert inv.value_ref == banana
        assert inv.prop == link.prop

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
