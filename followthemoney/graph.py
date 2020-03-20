import logging

from followthemoney.types import registry

log = logging.getLogger(__name__)


class Node(object):
    """A node represents either an entity that can be rendered as a
    node in a graph, or as a re-ified value, like a name, email
    address or phone number."""
    __slots__ = ['type', 'value', 'id', 'proxy', 'schema']

    def __init__(self, type_, value, proxy=None, schema=None):
        self.type = type_
        self.value = value
        self.id = type_.node_id_safe(value)
        self.proxy = proxy
        self.schema = schema if proxy is None else proxy.schema

    @property
    def is_entity(self):
        return self.type == registry.entity

    @property
    def caption(self):
        if self.type != registry.entity:
            return self.type.caption(self.value)
        if self.proxy is not None:
            return self.proxy.caption
        return self.value

    def __str__(self):
        return self.caption

    def __repr__(self):
        return '<Node(%r, %r, %r)>' % (self.id, self.type, self.caption)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Edge(object):
    """A link between two nodes."""
    __slots__ = ['id', 'weight', 'source_id', 'target_id',
                 'prop', 'proxy', 'graph']

    def __init__(self, graph, source, target, proxy=None, prop=None, value=None):  # noqa
        self.graph = graph
        self.id = None
        self.source_id = source.id
        self.target_id = target.id
        self.weight = 1.0
        self.prop = prop
        self.proxy = proxy
        if prop is not None:
            self.weight = prop.specificity(value)
            self.id = f"{source.id}:{target.id}"
        elif proxy is not None:
            self.id = f"{proxy.id}:{source.id}:{target.id}"
        else:
            raise RuntimeError()

    @property
    def source(self):
        return self.graph.nodes.get(self.source_id)

    @property
    def target(self):
        return self.graph.nodes.get(self.target_id)

    @property
    def type_name(self):
        return self.prop.name if self.proxy is None else self.proxy.schema.name

    def __repr__(self):
        return '<Edge(%r)>' % self.id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Graph(object):
    """A manager for a set of nodes and edges, all derived from FtM
    entities and their properties.

    This class is meant to be extensible in order to support additional
    backends, like Aleph.
    """

    def __init__(self, edge_types=None):
        edge_types = registry.get_types(edge_types)
        self.edge_types = [t for t in edge_types if t.matchable]
        self.flush()

    def flush(self):
        self.edges = {}
        self.nodes = {}
        self.proxies = {}

    def queue(self, id_, proxy=None):
        if id_ not in self.proxies or proxy is not None:
            self.proxies[id_] = proxy

    @property
    def queued(self):
        return [i for (i, p) in self.proxies.items() if p is None]

    def _get_node_stub(self, value, prop):
        if prop.type == registry.entity:
            self.queue(value)
        node = Node(prop.type, value, schema=prop.range)
        if node.id not in self.nodes:
            self.nodes[node.id] = node
        return self.nodes[node.id]

    def _add_edge(self, proxy, source, target):
        schema = proxy.schema
        source = self._get_node_stub(source, schema.get(schema.edge_source))
        target = self._get_node_stub(target, schema.get(schema.edge_target))
        edge = Edge(self, source, target, proxy=proxy)
        if edge.weight > 0:
            self.edges[edge.id] = edge

    def _add_node(self, proxy, expand_properties=True):
        """Derive a node and its value edges from the given proxy."""
        entity = Node(registry.entity, proxy.id, proxy=proxy)
        self.nodes[entity.id] = entity
        for prop, value in proxy.itervalues():
            if prop.type not in self.edge_types:
                continue
            if expand_properties:
                node = self._get_node_stub(value, prop)
                edge = Edge(self, entity, node, prop=prop, value=value)
                if edge.weight > 0:
                    self.edges[edge.id] = edge

    def add(self, proxy, expand_properties=True):
        self.queue(proxy.id, proxy)
        if proxy.schema.edge:
            for (source, target) in proxy.edgepairs():
                self._add_edge(proxy, source, target)
        else:
            self._add_node(proxy, expand_properties=expand_properties)

    def iternodes(self):
        return self.nodes.values()

    def iteredges(self):
        return self.edges.values()
