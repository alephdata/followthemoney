from followthemoney.types import registry


class Node(object):

    def __init__(self, value, type_, caption=None):
        self.id = type_.node_id_safe(value)
        self.type = type_
        self.value = value
        self.caption = caption or type_.caption(value)

    def __str__(self):
        return self.caption

    def __repr__(self):
        return '<Node(%r, %r, %r)>' % (self.id, self.type, self.caption)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class EntityNode(Node):

    def __init__(self, proxy):
        super(EntityNode, self).__init__(proxy.id,
                                         registry.entity,
                                         proxy.caption)
        self.proxy = proxy


class ValueNode(Node):

    def __init__(self, type_, value):
        super(ValueNode, self).__init__(value, type_)


class EdgeType(object):

    def __init__(self, id_, caption):
        self.id = id_
        self.caption = caption


class Edge(object):

    def __init__(self, id_, source_id, target_id, type_, weight=1):
        self.id = f"{id_}:{source_id}:{target_id}"
        self.source_id = source_id
        self.target_id = target_id
        self.type = type_
        self.weight = weight

    def __repr__(self):
        return '<Edge(%r)>' % self.id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class EntityEdge(Edge):

    def __init__(self, source_id, target_id, proxy):
        super(EntityEdge, self).__init__(proxy.id, source_id, target_id)
        self.proxy = proxy


class PropertyEdge(Edge):

    def __init__(self, source_id, prop, value):
        super(EntityEdge, self).__init__(prop.qname, source_id,
                                         prop.type.node_id_safe(value),
                                         weight=prop.specificity(value))
        self.prop = prop
        self.value = value


class Graph(object):

    def __init__(self, edge_types=None):
        self.edge_types = edge_types
        self.flush()

    def flush(self):
        self.edges = {}
        self.nodes = {}
        self.proxies = {}

    def probe(self, node):
        pass

    def expand(self, node, edge_type=None):
        pass

    def queue(self, id_, proxy=None):
        if id_ not in self.proxies or proxy is not None:
            self.proxies[id_] = proxy

    @property
    def queued(self):
        return [i for (i, p) in self.proxies.items() if p is None]

    def add(self, proxy):
        self.queue(proxy.id, proxy)
        if proxy.schema.edge:
            for (source, target) in proxy.edgepairs():
                edge = EntityEdge(source, target, proxy)
                self.edges[edge.id] = edge
                self.queue(source)
                self.queue(target)
        else:
            node = EntityNode(proxy)
            self.nodes[node.id] = node
            for prop, values in proxy._properties.items():
                if prop.type.name not in self.edge_types:
                    continue
                for value in values:
                    node = ValueNode(prop.type, value)
                    edge = PropertyEdge(node.id, prop, value)
                    if edge.weight == 0:
                        continue
                    self.edges[edge.id] = edge
                    if prop.type == registry.entity:
                        self.queue(value)
                    else:
                        self.nodes[node.id] = node
