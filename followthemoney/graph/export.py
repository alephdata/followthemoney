import json
import stringcase
from pprint import pprint  # noqa
from banal import ensure_list

from followthemoney.types import registry


class GraphExport(object):
    """Base functions for exporting a property graph from a stream
    of entities."""

    DEFAULT_TYPES = (registry.entity,)
    COMPLETE = list(registry.types)

    def __init__(self, edge_types=DEFAULT_TYPES):
        self.edge_types = edge_types

    def get_attributes(self, proxy):
        attributes = {}
        for prop, values in proxy._properties.items():
            if prop.type not in self.edge_types:
                attributes[prop.name] = prop.type.join(values)
        return attributes

    def get_id(self, type_, value):
        return type_.rdf(value).n3()

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
                if prop.type not in self.edge_types:
                    continue
                for value in ensure_list(values):
                    weight = prop.specificity(value)
                    if weight == 0:
                        continue
                    self.write_link(proxy, prop, value, weight)


class NXGraphExport(GraphExport):
    """Write to NetworkX data structure, which in turn can be exported
    to the file formats for Gephi (GEXF) and D3."""

    def __init__(self, graph, edge_types=GraphExport.DEFAULT_TYPES):
        super(NXGraphExport, self).__init__(edge_types=edge_types)
        self.graph = graph

    def _make_node(self, id, attributes):
        if not self.graph.has_node(id):
            self.graph.add_node(id, **attributes)
        else:
            self.graph.node[id].update(attributes)

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
        attributes = {}
        if prop.type != registry.entity:
            attributes['label'] = value
            attributes['schema'] = prop.type.name
        self._make_node(node_id, attributes)
        self.graph.add_edge(node_id, other_id,
                            weight=weight,
                            schema=prop.qname)


class CypherGraphExport(GraphExport):
    """Cypher query format, used for import to Neo4J. This is a bit like
    writing SQL with individual statements - so for large datasets it
    might be a better idea to do a CSV-based import."""
    # https://www.opencypher.org/
    # MATCH (n) DETACH DELETE n;

    def __init__(self, fh, edge_types=GraphExport.DEFAULT_TYPES):
        super(CypherGraphExport, self).__init__(edge_types=edge_types)
        self.fh = fh

    def _to_map(self, data):
        values = []
        for key, value in data.items():
            value = '%s: %s' % (key, json.dumps(value))
            values.append(value)
        return ', '.join(values)

    def _make_node(self, attributes, label):
        cypher = 'MERGE (p { %(id)s }) ' \
                 'SET p += { %(map)s } SET p :%(label)s;\n'
        self.fh.write(cypher % {
            'id': self._to_map({'id': attributes.get('id')}),
            'map': self._to_map(attributes),
            'label': ':'.join(ensure_list(label))
        })

    def _make_edge(self, source, target, attributes, label):
        cypher = 'MATCH (s { %(source)s }), (t { %(target)s }) ' \
                 'MERGE (s)-[:%(label)s { %(map)s }]->(t);\n'
        label = [stringcase.constcase(l) for l in ensure_list(label)]
        self.fh.write(cypher % {
            'source': self._to_map({'id': source}),
            'target': self._to_map({'id': target}),
            'label': ':'.join(label),
            'map': self._to_map(attributes),
        })

    def write_edge(self, proxy, source, target, attributes):
        source = self.get_id(registry.entity, source)
        source_prop = proxy.schema.get(proxy.schema.edge_source)
        self._make_node({'id': source}, source_prop.range.name)

        target = self.get_id(registry.entity, target)
        target_prop = proxy.schema.get(proxy.schema.edge_target)
        self._make_node({'id': target}, target_prop.range.name)
        self._make_edge(source, target, attributes, proxy.schema.name)

    def write_node(self, proxy):
        node_id = self.get_id(registry.entity, proxy.id)
        attributes = self.get_attributes(proxy)
        attributes['name'] = proxy.caption
        attributes['id'] = node_id
        self._make_node(attributes, proxy.schema.names)

    def write_link(self, proxy, prop, value, weight):
        node_id = self.get_id(registry.entity, proxy.id)
        other_id = self.get_id(prop.type, value)
        if prop.range:
            self._make_node({'id': other_id}, prop.range.name)
        else:
            attributes = {'id': other_id, 'name': value}
            self._make_node({'id': other_id}, prop.type.name)
        attributes = {'weight': weight}
        self._make_edge(node_id, other_id, attributes, prop.name)
