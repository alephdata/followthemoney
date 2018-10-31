# from nose.tools import assert_raises
from unittest import TestCase
from networkx import DiGraph

from followthemoney import model
from followthemoney.types import registry
from followthemoney.graph import Link, Node

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

    def test_base(self):
        prop = model.get_qname('Thing:name')
        node = Node(registry.entity, 'banana')
        link = Link(node, prop, "Theodore Böln")
        assert link.subject == node

        value = link.to_tuple()
        other = link.from_tuple(model, value)
        assert other == link, (link, other)
        assert hash(other) == hash(link)
        assert repr(other) == repr(link)

    def test_invert(self):
        prop = model.get_qname('Thing:name')
        node = Node(registry.entity, 'banana')
        link = Link(node, prop, "Theodore")
        assert not link.inverted
        inv = link.invert()
        assert inv.inverted
        assert inv.rdf() is None

        banana = Node(registry.entity, 'banana')
        peach = Node(registry.entity, 'peach')
        prop = model.get_qname('Thing:sameAs')
        link = Link(banana, prop, peach.value)
        inv = link.invert()
        assert inv.subject == peach
        assert inv.value_node == banana
        assert inv.prop == link.prop

    def test_make_links(self):
        links = list(model.get_proxy(ENTITY).links)
        assert len(links) == 8, len(links)

    def test_rdf(self):
        links = list(model.get_proxy(ENTITY).links)
        triples = [l.rdf() for l in links]
        assert len(triples) == 8, len(triples)
        for (s, p, o) in triples:
            assert 'test' in s, s
            if str(o) == 'Ralph Tester':
                assert str(p) == 'http://www.w3.org/2004/02/skos/core#prefLabel'  # noqa
            if p == registry.phone:
                assert str(o) == 'tel:+12025557612', o
        # assert False, triples

    def test_graph(self):
        g = DiGraph()
        proxy = model.get_proxy(ENTITY)
        node = proxy.node
        self.assertEqual(str(node), node.id)
        for link in proxy.links:
            link.to_digraph(g)
        self.assertEqual(g.number_of_edges(), 8)
        self.assertEqual(g.number_of_nodes(), 9)
        self.assertIn(node.id, g.nodes)

        prop = model.get_qname('Thing:name')
        link = Link(Node(registry.name, 'Bob'), prop, proxy.id, inverted=True)
        link.to_digraph(g)
        self.assertEqual(g.number_of_edges(), 9)

        link = Link(node, prop, 'Blub', weight=0)
        link.to_digraph(g)
        self.assertEqual(g.number_of_edges(), 9)

        prop = model.get_qname('Thing:summary')
        link = Link(node, prop, 'This is a text')
        link.to_digraph(g)
        self.assertEqual(g.number_of_edges(), 9)
