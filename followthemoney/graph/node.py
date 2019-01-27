from followthemoney.util import get_entity_id


class Node(object):
    """A node in a graph, either specifying an entity or a property value."""
    __slots__ = ['type', 'value', 'uri']

    def __init__(self, type_, value):
        self.type = type_
        self.value = get_entity_id(value)
        self.uri = self.type.rdf(self.value)

    def __hash__(self):
        return hash(self.uri)

    def __eq__(self, other):
        return self.uri == other.uri

    def __repr__(self):
        return '<Node(%r, %r)>' % (self.type, self.value)

    def __str__(self):
        return self.uri
