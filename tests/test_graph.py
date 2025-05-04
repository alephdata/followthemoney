from followthemoney import model
from followthemoney.types import registry
from followthemoney.graph import Graph, Node


ENTITY = {
    "id": "ralph",
    "schema": "Person",
    "properties": {
        "name": ["Ralph Tester"],
        "birthDate": ["1972-05-01"],
        "idNumber": ["9177171", "8e839023"],
        "website": ["https://ralphtester.me"],
        "phone": ["+12025557612"],
        "email": ["info@ralphtester.me"],
        "topics": ["role.spy"],
    },
}

ENTITY2 = {
    "id": "jodie",
    "schema": "Person",
    "properties": {"name": ["Jodie Tester"], "birthDate": ["1972-05-01"]},
}

REL = {
    "id": "jodie2ralph",
    "schema": "Family",
    "properties": {"person": ["jodie"], "relative": ["ralph"]},
}

PASS = {
    "id": "passpoat",
    "schema": "Passport",
    "properties": {"holder": ["jodie"], "passportNumber": ["HJSJHAS"]},
}


def test_basic_graph():
    proxy = model.get_proxy(ENTITY, cleaned=False)
    graph = Graph(edge_types=registry.pivots)
    graph.add(proxy)
    assert len(graph.iternodes()) > 1, graph.to_dict()
    assert len(graph.proxies) == 1, graph.proxies
    assert len(graph.queued) == 0, graph.proxies
    graph.add(None)
    assert len(graph.proxies) == 1, graph.proxies
    assert len(graph.queued) == 0, graph.proxies


def test_adjacent():
    graph = Graph(edge_types=registry.pivots)
    graph.add(model.get_proxy(ENTITY, cleaned=False))
    graph.add(model.get_proxy(ENTITY2, cleaned=False))
    graph.add(model.get_proxy(REL, cleaned=False))
    graph.add(model.get_proxy(PASS, cleaned=False))
    node = Node(registry.entity, "jodie")
    adj = list(graph.get_adjacent(node))
    assert len(adj) == 3, adj
    node = Node(registry.entity, "ralph")
    adj = list(graph.get_adjacent(node))
    assert len(adj) == 7, adj
    node = Node(registry.entity, "passpoat")
    adj = list(graph.get_adjacent(node))
    assert len(adj) == 2, adj

    node = Node(registry.entity, "passpoat")
    prop = model.get_qname("Identification:holder")
    adj = list(graph.get_adjacent(node, prop))
    assert len(adj) == 1, adj
    assert adj[0].source_prop == prop, adj[0].source_prop
    assert adj[0].target_prop == prop.reverse, adj[0].target_prop

    node = Node(registry.entity, "jodie")
    prop = model.get_qname("Person:familyPerson")
    adj = list(graph.get_adjacent(node, prop))
    assert len(adj) == 1, adj
    assert adj[0].source_prop == prop, adj[0].source_prop

    node = Node(registry.entity, "ralph")
    prop = model.get_qname("Person:familyRelative")
    adj2 = list(graph.get_adjacent(node, prop))
    assert len(adj2) == 1, adj2
    assert adj2[0].target_prop == prop, adj2[0].target_prop

    assert adj[0] == adj2[0], (adj[0], adj2[0])
    assert adj[0].id in repr(adj[0]), repr(adj[0])


def test_to_dict():
    proxy = model.get_proxy(ENTITY, cleaned=False)
    graph = Graph(edge_types=registry.pivots)
    graph.add(proxy)
    data = graph.to_dict()
    assert "nodes" in data, data
    assert "edges" in data, data


def test_nodes():
    node = Node(registry.phone, "+4917778271717")
    assert "+49177" in repr(node), repr(node)
    assert node == node, repr(node)
    assert node.caption == str(node), str(node)
    assert hash(node) == hash(node.id), repr(node)
