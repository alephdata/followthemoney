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

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.name,
            'value': self.value,
            'caption': self.caption
        }

    @classmethod
    def from_proxy(cls, proxy):
        return cls(registry.entity, proxy.id, proxy=proxy)

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
                 'prop', 'proxy', 'schema', 'graph']

    def __init__(self, graph, source, target, proxy=None, prop=None, value=None):  # noqa
        self.graph = graph
        self.id = f"{source.id}<>{target.id}"
        self.source_id = source.id
        self.target_id = target.id
        self.weight = 1.0
        self.prop = prop
        self.proxy = proxy
        self.schema = None
        if prop is not None:
            self.weight = prop.specificity(value)
        if proxy is not None:
            self.id = f"{source.id}<{proxy.id}>{target.id}"
            self.schema = proxy.schema

    @property
    def source(self):
        return self.graph.nodes.get(self.source_id)

    @property
    def source_prop(self):
        """Get the entity property originating this edge."""
        if self.schema is not None:
            return self.schema.source_prop.reverse
        return self.prop

    @property
    def target(self):
        return self.graph.nodes.get(self.target_id)

    @property
    def target_prop(self):
        """Get the entity property originating this edge."""
        if self.schema is not None:
            return self.schema.target_prop.reverse
        if self.prop is not None:
            return self.prop.reverse
        # NOTE: this edge points at a value node.

    @property
    def type_name(self):
        return self.prop.name if self.schema is None else self.schema.name

    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type_name': self.type_name
        }

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

    def __init__(self, edge_types=registry.pivots):
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

    def _get_node_stub(self, prop, value):
        if prop.type == registry.entity:
            self.queue(value)
        node = Node(prop.type, value, schema=prop.range)
        if node.id not in self.nodes:
            self.nodes[node.id] = node
        return self.nodes[node.id]

    def _add_edge(self, proxy, source, target):
        source = self._get_node_stub(proxy.schema.source_prop, source)
        target = self._get_node_stub(proxy.schema.target_prop, target)
        edge = Edge(self, source, target, proxy=proxy)
        self.edges[edge.id] = edge

    def _add_node(self, proxy):
        """Derive a node and its value edges from the given proxy."""
        entity = Node.from_proxy(proxy)
        self.nodes[entity.id] = entity
        for prop, value in proxy.itervalues():
            if prop.type not in self.edge_types:
                continue
            node = self._get_node_stub(prop, value)
            edge = Edge(self, entity, node, prop=prop, value=value)
            if edge.weight > 0:
                self.edges[edge.id] = edge

    def add(self, proxy):
        if proxy is None:
            return
        self.queue(proxy.id, proxy)
        if proxy.schema.edge:
            for (source, target) in proxy.edgepairs():
                self._add_edge(proxy, source, target)
        else:
            self._add_node(proxy)

    def iternodes(self):
        return self.nodes.values()

    def iteredges(self):
        return self.edges.values()

    def get_outbound(self, node, prop=None):
        "Get all edges pointed out from the given node."
        for edge in self.iteredges():
            if edge.source == node:
                if prop and edge.source_prop != prop:
                    continue
                yield edge

    def get_inbound(self, node, prop=None):
        "Get all edges pointed at the given node."
        for edge in self.iteredges():
            if edge.target == node:
                if prop and edge.target_prop != prop:
                    continue
                yield edge

    def get_adjacent(self, node, prop=None):
        "Get all edges of the given node."
        yield from self.get_outbound(node, prop=prop)
        yield from self.get_inbound(node, prop=prop)

    def to_dict(self):
        return {
            'nodes': [n.to_dict() for n in self.iternodes()],
            'edges': [e.to_dict() for e in self.iteredges()]
        }
