import networkx as nx
from pprint import pprint  # noqa
from banal import ensure_list
from networkx.readwrite.gexf import generate_gexf

from followthemoney.types import registry
from followthemoney.export.common import Exporter

DEFAULT_EDGE_TYPES = (registry.entity.name,)


def edge_types():
    return [t.name for t in registry.types if t.matchable]


class GraphExporter(Exporter):
    """Base functions for exporting a property graph from a stream
    of entities."""

    def __init__(self, edge_types=DEFAULT_EDGE_TYPES):
        self.edge_types = edge_types

    def get_attributes(self, proxy):
        attributes = {}
        for prop, values in proxy._properties.items():
            if prop.hidden or prop.stub:
                continue
            if prop.type.name not in self.edge_types:
                attributes[prop.name] = prop.type.join(values)
        return attributes

    def get_id(self, type_, value):
        if value is None:
            return None
        return type_.node_id(value)

    def write_edges(self, proxy):
        attributes = self.get_attributes(proxy)
        attributes['weight'] = 1
        for (source, target) in proxy.edgepairs():
            self.write_edge(proxy, source, target, attributes)

    def write(self, proxy):
        if proxy.schema.edge:
            self.write_edges(proxy)
        else:
            self.write_node(proxy)
            for prop, values in proxy._properties.items():
                if prop.type.name not in self.edge_types:
                    continue
                for value in ensure_list(values):
                    weight = prop.specificity(value)
                    if weight == 0:
                        continue
                    self.write_link(proxy, prop, value, weight)


class NXGraphExporter(GraphExporter):
    """Write to NetworkX data structure, which in turn can be exported
    to the file formats for Gephi (GEXF) and D3."""

    def __init__(self, fh, edge_types=DEFAULT_EDGE_TYPES):
        super(NXGraphExporter, self).__init__(edge_types=edge_types)
        self.graph = nx.MultiDiGraph()
        self.fh = fh

    def _make_node(self, id, attributes):
        if not self.graph.has_node(id):
            self.graph.add_node(id, **attributes)
        else:
            self.graph.nodes[id].update(attributes)

    def write_edge(self, proxy, source, target, attributes):
        source = self.get_id(registry.entity, source)
        self._make_node(source, {})

        target = self.get_id(registry.entity, target)
        self._make_node(target, {})

        attributes['schema'] = proxy.schema.name
        self.graph.add_edge(source, target, **attributes)

    def write_node(self, proxy):
        node_id = self.get_id(registry.entity, proxy.id)
        attributes = self.get_attributes(proxy)
        attributes['label'] = proxy.caption
        attributes['schema'] = proxy.schema.name
        self._make_node(node_id, attributes)

    def write_link(self, proxy, prop, value, weight):
        node_id = self.get_id(registry.entity, proxy.id)
        other_id = self.get_id(prop.type, value)
        if prop.type != registry.entity:
            self._make_node(node_id, {
                'label': prop.type.caption(value),
                'schema': prop.type.name
            })
        self.graph.add_edge(node_id, other_id,
                            weight=weight,
                            schema=prop.qname)

    def finalize(self):
        for line in generate_gexf(self.graph, prettyprint=False):
            self.fh.write(line)
