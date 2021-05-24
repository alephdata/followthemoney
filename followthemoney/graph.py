"""
Converting FtM data to a property graph data model.

This module provides an abstract data object that represents a property
graph. This is used by the exporter modules to convert data
to a specific output format, like Cypher or NetworkX.
"""
import logging

from followthemoney.types import registry

log = logging.getLogger(__name__)


class Node(object):
    """A node represents either an entity that can be rendered as a
    node in a graph, or as a re-ified value, like a name, email
    address or phone number."""

    __slots__ = ["type", "value", "id", "proxy", "schema"]

    def __init__(self, type_, value, proxy=None, schema=None):
        self.type = type_
        self.value = value
        self.id = type_.node_id_safe(value)
        self.proxy = proxy
        self.schema = schema if proxy is None else proxy.schema

    @property
    def is_entity(self):
        """Check to see if the node represents an entity. If this is false, the
        node represents a non-entity property value that has been reified, like
        a phone number or a name."""
        return self.type == registry.entity

    @property
    def caption(self):
        """A user-facing label for the current node."""
        if self.type != registry.entity:
            return self.type.caption(self.value)
        if self.proxy is not None:
            return self.proxy.caption
        return self.value

    def to_dict(self):
        """Return a simple dictionary to reflect this graph node."""
        return {
            "id": self.id,
            "type": self.type.name,
            "value": self.value,
            "caption": self.caption,
        }

    @classmethod
    def from_proxy(cls, proxy):
        """For a given :class:`~followthemoney.proxy.EntityProxy`, return a node
        based on the entity."""
        return cls(registry.entity, proxy.id, proxy=proxy)

    def __str__(self):
        return self.caption

    def __repr__(self):
        return "<Node(%r, %r, %r)>" % (self.id, self.type, self.caption)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Edge(object):
    """A link between two nodes."""

    __slots__ = [
        "id",
        "weight",
        "source_id",
        "target_id",
        "prop",
        "proxy",
        "schema",
        "graph",
    ]

    def __init__(self, graph, source, target, proxy=None, prop=None, value=None):
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
        """The graph node from which the edge originates."""
        return self.graph.nodes.get(self.source_id)

    @property
    def source_prop(self):
        """Get the entity property originating this edge."""
        if self.schema is not None:
            return self.schema.source_prop.reverse
        return self.prop

    @property
    def target(self):
        """The graph node to which the edge points."""
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
        """Return a machine-readable descripton of the type of the edge.
        This is either a property name or a schema name."""
        return self.prop.name if self.schema is None else self.schema.name

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type_name": self.type_name,
        }

    def __repr__(self):
        return "<Edge(%r)>" % self.id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Graph(object):
    """A set of nodes and edges, derived from entities and their properties.
    This represents an alternative interpretation of FtM data as a property
    graph.

    This class is meant to be extensible in order to support additional
    backends, like Aleph.
    """

    def __init__(self, edge_types=registry.pivots):
        edge_types = registry.get_types(edge_types)
        self.edge_types = [t for t in edge_types if t.matchable]
        self.flush()

    def flush(self):
        """Remove all nodes, edges and proxies from the graph."""
        self.edges = {}
        self.nodes = {}
        self.proxies = {}

    def queue(self, id_, proxy=None):
        """Register a reference to an entity in the graph."""
        if id_ not in self.proxies or proxy is not None:
            self.proxies[id_] = proxy

    @property
    def queued(self):
        """Return a list of all the entities which are referenced from the graph
        but that haven't been loaded yet. This can be used to get a list of
        entities that should be included to expand the whole graph by one degree.
        """
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
        """Add an :class:`~followthemoney.proxy.EntityProxy` to the graph and make
        it either a :class:`~followthemoney.graph.Node` or an
        :class:`~followthemoney.graph.Edge`."""
        if proxy is None:
            return
        self.queue(proxy.id, proxy)
        if proxy.schema.edge:
            for (source, target) in proxy.edgepairs():
                self._add_edge(proxy, source, target)
        else:
            self._add_node(proxy)

    def iternodes(self):
        """Iterate all :class:`nodes <followthemoney.graph.Node>` in the graph."""
        return self.nodes.values()

    def iteredges(self):
        """Iterate all :class:`edges <followthemoney.graph.Edge>` in the graph."""
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
        "Get all adjacent edges of the given node."
        yield from self.get_outbound(node, prop=prop)
        yield from self.get_inbound(node, prop=prop)

    def to_dict(self):
        """Return a dictionary with the graph nodes and edges."""
        return {
            "nodes": [n.to_dict() for n in self.iternodes()],
            "edges": [e.to_dict() for e in self.iteredges()],
        }
