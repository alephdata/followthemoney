from unittest import TestCase

from followthemoney import model
from followthemoney.types import registry
from followthemoney.graph import Graph, Node


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
        'passport': 'passportEntityId',
        'topics': 'role.spy'
    }
}


class GraphTestCase(TestCase):

    def test_basic_graph(self):
        proxy = model.get_proxy(ENTITY)
        graph = Graph(edge_types=registry.pivots)
        graph.add(proxy)
        assert len(graph.iternodes()) > 1, graph.to_dict()
        assert len(graph.proxies) == 1, graph.proxies
        assert len(graph.queued) == 0, graph.proxies
        graph.add(None)
        assert len(graph.proxies) == 1, graph.proxies
        assert len(graph.queued) == 0, graph.proxies

    def test_to_dict(self):
        proxy = model.get_proxy(ENTITY)
        graph = Graph(edge_types=registry.pivots)
        graph.add(proxy)
        data = graph.to_dict()
        assert 'nodes' in data, data
        assert 'edges' in data, data

    def test_nodes(self):
        node = Node(registry.phone, '+4917778271717')
        assert '+49177' in repr(node), repr(node)
        assert node == node, repr(node)
        assert node.caption == str(node), str(node)
        assert hash(node) == hash(node.id), repr(node)
