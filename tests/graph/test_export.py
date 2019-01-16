# from nose.tools import assert_raises
from unittest import TestCase
from networkx import DiGraph

from followthemoney import model
from followthemoney.types import registry
from followthemoney.graph.export import to_nxgraph

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
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            to_nxgraph(g, proxy)

        self.assertEquals(len(g.nodes), 2)
        self.assertEquals(len(g.edges), 1)

    def test_nxgraph_full(self):
        g = DiGraph()
        edge_types = (registry.entity, registry.email, registry.phone,)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            to_nxgraph(g, proxy, edge_types=edge_types)

        self.assertEquals(len(g.nodes), 4)
        self.assertEquals(len(g.edges), 3)
