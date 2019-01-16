from pprint import pprint  # noqa
from banal import ensure_list

from followthemoney.types import registry


def _proxy_attributes(proxy, edge_types):
    attributes = {
        'id': proxy.id,
        'schema': proxy.schema.name
    }
    for prop, values in proxy._properties.items():
        if prop.type not in edge_types:
            attributes[prop.name] = prop.type.join(values)
    return attributes


def _to_nxgraph_node(graph, proxy, edge_types):
    node_id = registry.entity.rdf(proxy.id).n3()
    attributes = _proxy_attributes(proxy, edge_types)
    if not graph.has_node(node_id):
        graph.add_node(node_id)
    attributes['label'] = proxy.caption
    graph.node[node_id].update(attributes)

    for prop, values in proxy._properties.items():
        if prop.type not in edge_types:
            continue
        for value in ensure_list(values):
            weight = prop.type.specificity(value)
            if weight == 0:
                continue
            other = prop.type.rdf(value).n3()
            if not graph.has_node(other):
                graph.add_node(other, label=value)
            graph.add_edge(node_id, other,
                           weight=weight,
                           schema=prop.qname)


def _to_nxgraph_edge(graph, proxy, edge_types):
    attributes = _proxy_attributes(proxy, edge_types)
    attributes['weight'] = 1
    for (source, target) in proxy.edgepairs():
        source = registry.entity.rdf(source).n3()
        if not graph.has_node(source):
            graph.add_node(source)

        target = registry.entity.rdf(target).n3()
        if not graph.has_node(target):
            graph.add_node(target)

        graph.add_edge(source, target, **attributes)


def to_nxgraph(graph, proxy, edge_types=(registry.entity,)):
    if proxy.schema.edge:
        _to_nxgraph_edge(graph, proxy, edge_types)
    else:
        _to_nxgraph_node(graph, proxy, edge_types)
