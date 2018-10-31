from followthemoney.util import get_entity_id


class Node(object):
    """A node in a graph, either specifying an entity or a property value."""
    __slots__ = ['type', 'value']

    def __init__(self, type_, value):
        self.type = type_
        self.value = get_entity_id(value)

    @property
    def id(self):
        if self.value is not None:
            return f'{self.type.name}:{self.value}'

    @property
    def uri(self):
        return self.type.rdf(self.value)

    def __hash__(self):
        return hash((self.type, self.value))

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value

    def __repr__(self):
        return '<Node(%r, %r)>' % (self.type, self.value)

    def __str__(self):
        return self.id
