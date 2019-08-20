import io
from unittest import TestCase

from followthemoney import model
from followthemoney.types import registry
from followthemoney.export.graph import NXGraphExporter
from followthemoney.export.graph import CypherGraphExporter
from followthemoney.export.graph import edge_types

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
        sio = io.StringIO()
        exporter = NXGraphExporter(sio)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        self.assertEqual(len(exporter.graph.nodes), 3)
        self.assertEqual(len(exporter.graph.edges), 2)

        exporter.finalize()
        value = sio.getvalue()
        assert len(value), len(value)

    def test_nxgraph_full(self):
        sio = io.StringIO()
        edge_types = (registry.entity.name,
                      registry.email.name,
                      registry.phone.name,)
        exporter = NXGraphExporter(sio, edge_types=edge_types)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        self.assertEqual(len(exporter.graph.nodes), 5)
        self.assertEqual(len(exporter.graph.edges), 4)

    def test_cypher_simple(self):
        sio = io.StringIO()
        exporter = CypherGraphExporter(sio)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        value = sio.getvalue()
        assert 'entity:company' in value, value
        assert 'startDate: "2003-04-01"' in value, value
        assert 'tel:+12025557612' not in value, value

    def test_cypher_full(self):
        sio = io.StringIO()
        exporter = CypherGraphExporter(sio, edge_types=edge_types())
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        value = sio.getvalue()
        assert 'entity:company' in value, value
        assert 'tel:+12025557612' in value, value
