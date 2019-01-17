from followthemoney.util import get_entity_id
from followthemoney.graph.node import Node


class Statement(object):
    """A wrapper object for an RDF-like statement, similar to a triple
    but with weighting and some other metadata.
    """
    __slots__ = ['subject', 'prop', 'value', 'weight',
                 'inverted', 'inferred']

    def __init__(self, subject, prop, value, weight=1.0,
                 inverted=False, inferred=False):
        self.subject = subject
        self.prop = prop
        self.value = get_entity_id(value)
        self.weight = weight
        self.inverted = inverted
        self.inferred = inferred

    @property
    def value_node(self):
        return Node(self.prop.type, self.value)

    def rdf(self):
        """Convert to an RDF triple. This looses weighting and inferrence
        metadata."""
        if self.inverted:
            return
        return (self.subject.uri, self.prop.uri, self.value_node.uri)

    def to_tuple(self):
        return (self.subject, self.prop.qname, self.value,
                self.weight, self.inverted, self.inferred)

    @classmethod
    def from_tuple(cls, model, data):
        subject, qname, value, weight, inverted, inferred = data
        prop = model.get_qname(qname)
        if prop is not None:
            return cls(subject, prop, value,
                       weight=weight,
                       inverted=inverted,
                       inferred=inferred)

    def invert(self):
        if not self.inverted and self.prop.reverse is not None:
            return Statement(self.value_node,
                             self.prop.reverse,
                             self.subject.value,
                             weight=self.weight,
                             inferred=self.inferred)
        return Statement(self.value_node,
                         self.prop,
                         self.subject.value,
                         weight=self.weight,
                         inverted=not self.inverted,
                         inferred=self.inferred)

    def __repr__(self):
        return '<Statement(%r, %r, %r)>' % \
            (self.subject, self.prop, self.value)

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.subject == other.subject \
            and self.prop == other.prop \
            and self.value == other.value \
            and self.weight == other.weight \
            and self.inverted == other.inverted
