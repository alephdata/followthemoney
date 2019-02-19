import io
from unittest import TestCase
from networkx import DiGraph

from followthemoney import model
from followthemoney.types import registry
from followthemoney.graph.export import NXGraphExport, CypherGraphExport

ENTITIES = [
    {
        'id': 'person',
        'schema': 'Person',
        'properties': {
            'name': 'Ralph Tester',
            'birthDate': '1972-05-01',
            'idNumber': ['9177171', '8e839023'],
            'website': 'https://ralphtester.me',
            'phone': '+12025557612',
            'email': 'info@ralphtester.me'
        }
    },
    {
        'id': 'sanction',
        'schema': 'Sanction',
        'properties': {
            'entity': 'person',
            'program': 'Hateys'
        }
    },
    {
        'id': 'company',
        'schema': 'Company',
        'properties': {
            'name': 'Ralph Industries, Inc.',
        }
    },
    {
        'id': 'owner',
        'schema': 'Ownership',
        'properties': {
            'startDate': '2003-04-01',
            'owner': 'person',
            'asset': 'company'
        }
    }
]


class ExportTestCase(TestCase):

    def test_nxgraph_simple(self):
        g = DiGraph()
        exporter = NXGraphExport(g)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        self.assertEqual(len(g.nodes), 3)
        self.assertEqual(len(g.edges), 2)

    def test_nxgraph_full(self):
        g = DiGraph()
        edge_types = (registry.entity, registry.email, registry.phone,)
        exporter = NXGraphExport(g, edge_types=edge_types)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        self.assertEqual(len(g.nodes), 5)
        self.assertEqual(len(g.edges), 4)

    def test_cypher_simple(self):
        sio = io.StringIO()
        exporter = CypherGraphExport(sio)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        value = sio.getvalue()
        assert '<urn:entity:company>' in value, value
        assert 'startDate: "2003-04-01"' in value, value
        assert '<tel:+12025557612>' not in value, value

    def test_cypher_full(self):
        sio = io.StringIO()
        edge_types = list(registry.types)
        exporter = CypherGraphExport(sio, edge_types=edge_types)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        value = sio.getvalue()
        assert '<urn:entity:company>' in value, value
        assert '<tel:+12025557612>' in value, value
