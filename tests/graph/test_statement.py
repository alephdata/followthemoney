# from nose.tools import assert_raises
from unittest import TestCase
from networkx import DiGraph

from followthemoney import model
from followthemoney.types import registry
from followthemoney.graph import Statement, Node

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
        stmt = Statement(node, prop, "Theodore Böln")
        assert stmt.subject == node

        value = stmt.to_tuple()
        other = stmt.from_tuple(model, value)
        assert other == stmt, (stmt, other)
        assert hash(other) == hash(stmt)
        assert repr(other) == repr(stmt)

    def test_invert(self):
        prop = model.get_qname('Thing:name')
        node = Node(registry.entity, 'banana')
        stmt = Statement(node, prop, "Theodore")
        assert not stmt.inverted
        inv = stmt.invert()
        assert inv.inverted
        assert inv.rdf() is None

        banana = Node(registry.entity, 'banana')
        peach = Node(registry.entity, 'peach')
        prop = model.get_qname('Thing:sameAs')
        stmt = Statement(banana, prop, peach.value)
        inv = stmt.invert()
        assert inv.subject == peach
        assert inv.value_node == banana
        assert inv.prop == stmt.prop

    def test_make_statements(self):
        statements = list(model.get_proxy(ENTITY).statements)
        assert len(statements) == 8, len(statements)

    def test_rdf(self):
        statements = list(model.get_proxy(ENTITY).statements)
        triples = [l.rdf() for l in statements]
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
        for stmt in proxy.statements:
            stmt.to_digraph(g)
        self.assertEqual(g.number_of_edges(), 8)
        self.assertEqual(g.number_of_nodes(), 9)
        self.assertIn(node.id, g.nodes)

        prop = model.get_qname('Thing:name')
        stmt = Statement(Node(registry.name, 'Bob'), prop, proxy.id,
                         inverted=True)
        stmt.to_digraph(g)
        self.assertEqual(g.number_of_edges(), 9)

        stmt = Statement(node, prop, 'Blub', weight=0)
        stmt.to_digraph(g)
        self.assertEqual(g.number_of_edges(), 9)

        prop = model.get_qname('Thing:summary')
        stmt = Statement(node, prop, 'This is a text')
        stmt.to_digraph(g)
        self.assertEqual(g.number_of_edges(), 9)
