import logging
from typing import Optional, Dict, List, Union, Sequence, Iterable, Iterator

from followthemoney.schema import Schema
from followthemoney.proxy import EntityProxy
from followthemoney.property import Property
from followthemoney.types import registry
from followthemoney.types.common import PropertyType

log = logging.getLogger(__name__)


class Node(object):
    """A node represents either an entity that can be rendered as a
    node in a graph, or as a re-ified value, like a name, email
    address or phone number."""
    __slots__ = ['type', 'value', 'id', 'proxy', 'schema']

    def __init__(self, type_: PropertyType, value: str,
                 proxy: Optional[EntityProxy]=None,
                 schema: Optional[Schema]=None):
        self.type: PropertyType = type_
        self.value: str = value
        node_id = type_.node_id_safe(value)
        if node_id is None:
            raise Exception('<FIXME>')
        self.id: str = node_id
        self.proxy: Optional[EntityProxy] = proxy
        _schema = schema if proxy is None else proxy.schema
        if _schema is None:
            raise Exception('<FIXME>')
        self.schema: Schema = _schema

    @property
    def is_entity(self) -> bool:
        return self.type == registry.entity

    @property
    def caption(self) -> str:
        if self.type != registry.entity:
            return self.type.caption(self.value)
        if self.proxy is not None:
            return self.proxy.caption
        return self.value

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            'id': self.id,
            'type': self.type.name,
            'value': self.value,
            'caption': self.caption
        }

    @classmethod
    def from_proxy(cls, proxy: EntityProxy) -> 'Node':
        if proxy.id is None:
            raise Exception('<FIXME>')
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

    def __init__(self, graph: 'Graph', source: Node, target: Node,
                 proxy: Optional[EntityProxy]=None, prop: Optional[Property]=None,
                 value: Optional[str]=None):  # noqa
        self.graph = graph
        self.id = f"{source.id}<>{target.id}"
        self.source_id = source.id
        self.target_id = target.id
        self.weight = 1.0
        self.prop: Optional[Property] = prop
        self.proxy: Optional[EntityProxy] = proxy
        self.schema: Optional[Schema] = None
        if prop is not None:
            self.weight = prop.specificity(value)
        if proxy is not None:
            self.id = f"{source.id}<{proxy.id}>{target.id}"
            self.schema = proxy.schema

    @property
    def source(self) -> Node:
        return self.graph.nodes[self.source_id]

    @property
    def source_prop(self) -> Property:
        """Get the entity property originating this edge."""
        if (self.schema is not None
                and self.schema.source_prop is not None
                and self.schema.source_prop.reverse is not None):
            return self.schema.source_prop.reverse
        if self.prop is None:
            raise Exception('<FIXME>')
        return self.prop

    @property
    def target(self) -> Optional[Node]:
        return self.graph.nodes.get(self.target_id)

    @property
    def target_prop(self) -> Optional[Property]:
        """Get the entity property originating this edge."""
        if self.schema is not None and self.schema.target_prop is not None:
            return self.schema.target_prop.reverse
        if self.prop is not None:
            return self.prop.reverse
        return None
        # NOTE: this edge points at a value node.

    @property
    def type_name(self) -> Optional[str]:
        if self.schema is None:
            if self.prop is not None:
                return self.prop.name
            else:
                return None
        else:
            return self.schema.name

    def to_dict(self) -> Dict[str, Optional[str]]:
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

    def __init__(self, edge_types: Sequence[Union[str, PropertyType]]=registry.pivots):
        _edge_types = registry.get_types(edge_types)
        self.edge_types: List[PropertyType] = [t for t in _edge_types if t.matchable]
        self.flush()

    def flush(self):
        self.edges: Dict[str, Edge] = {}
        self.nodes: Dict[str, Node] = {}
        self.proxies: Dict[str, Optional[EntityProxy]] = {}

    def queue(self, id_: str, proxy: Optional[EntityProxy]=None):
        if id_ not in self.proxies or proxy is not None:
            self.proxies[id_] = proxy

    @property
    def queued(self) -> List[str]:
        return [i for (i, p) in self.proxies.items() if p is None]

    def _get_node_stub(self, prop: Property, value: str) -> Node:
        if prop.type == registry.entity:
            self.queue(value)
        node = Node(prop.type, value, schema=prop.range)
        if node.id not in self.nodes:
            self.nodes[node.id] = node
        return self.nodes[node.id]

    def _add_edge(self, proxy: EntityProxy, source: str, target: str):
        if proxy.schema.source_prop is None or proxy.schema.target_prop is None:
            raise Exception('<FIXME>')
        _source = self._get_node_stub(proxy.schema.source_prop, source)
        _target = self._get_node_stub(proxy.schema.target_prop, target)
        edge = Edge(self, _source, _target, proxy=proxy)
        self.edges[edge.id] = edge

    def _add_node(self, proxy: EntityProxy):
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

    def add(self, proxy: Optional[EntityProxy]):
        if proxy is None or proxy.id is None:
            return
        self.queue(proxy.id, proxy)
        if proxy.schema.edge:
            for (source, target) in proxy.edgepairs():
                self._add_edge(proxy, source, target)
        else:
            self._add_node(proxy)

    def iternodes(self) -> Iterable[Node]:
        return self.nodes.values()

    def iteredges(self) -> Iterable[Edge]:
        return self.edges.values()

    def get_outbound(self, node: Node, prop: Optional[Property]=None) -> Iterable[Edge]:
        "Get all edges pointed out from the given node."
        for edge in self.iteredges():
            if edge.source == node:
                if prop and edge.source_prop != prop:
                    continue
                yield edge

    def get_inbound(self, node: Node, prop: Optional[Property]=None) -> Iterable[Edge]:
        "Get all edges pointed at the given node."
        for edge in self.iteredges():
            if edge.target == node:
                if prop and edge.target_prop != prop:
                    continue
                yield edge

    def get_adjacent(self, node: Node, prop: Optional[Property]=None) -> Iterator[Edge]:
        "Get all edges of the given node."
        yield from self.get_outbound(node, prop=prop)
        yield from self.get_inbound(node, prop=prop)

    def to_dict(self) -> Dict[str, List[Dict]]:
        return {
            'nodes': [n.to_dict() for n in self.iternodes()],
            'edges': [e.to_dict() for e in self.iteredges()]
        }
