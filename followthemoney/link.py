from followthemoney.types import registry
from followthemoney.util import get_entity_id


class Link(object):
    """A wrapper object for an RDF-like statement, similar to a triple
    but with weighting and some other metadata. This has built-in
    support for packing, i.e. transforming the link to a form suitable
    for storage in a key/value store.
    """
    __slots__ = ['subject', 'subject_type', 'prop', 'value', 'weight',
                 'inverted', 'inferred']

    def __init__(self, subject, subject_type, prop, value, weight=1.0,
                 inverted=False, inferred=False):
        self.subject = get_entity_id(subject)
        self.subject_type = subject_type
        self.prop = prop
        self.value = get_entity_id(value)
        self.weight = weight
        self.inverted = inverted
        self.inferred = inferred

    @property
    def value_type(self):
        return self.prop.type

    def rdf(self):
        """Convert to an RDF triple. This looses weighting and inferrence
        metadata."""
        if self.inverted:
            return
        subject_uri = self.subject_type.rdf(self.subject)
        value_obj = self.prop.type.rdf(self.value)
        return (subject_uri, self.prop.uri, value_obj)

    def to_tuple(self):
        return (self.subject, self.subject_type.name, self.prop.qname,
                self.value, self.weight, self.inverted, self.inferred)

    @classmethod
    def from_tuple(cls, model, data):
        subject, subject_type_name, qname, \
            value, weight, inverted, inferred = data
        prop = model.get_qname(qname)
        subject_type = registry.get(subject_type_name)
        if prop is not None:
            return cls(subject, subject_type, prop, value,
                       weight=weight,
                       inverted=inverted,
                       inferred=inferred)

    def invert(self):
        if not self.inverted and self.prop.reverse is not None:
            return Link(self.value,
                        self.value_type,
                        self.prop.reverse,
                        self.subject,
                        weight=self.weight)
        return Link(self.value,
                    self.value_type,
                    self.prop,
                    self.subject,
                    weight=self.weight,
                    inverted=not self.inverted)

    # def to_nxgraph(self, graph):
    #     if self.inverted:
    #         return self.invert().to_nxgraph(graph)
    #     subject_id = ':'.join((self.subject_type.name, self.subject))
    #     value_id = ':'.join((self.value_type.name, self.value))
    #     graph.add_node(subject_id, label=self.subject)
    #     if self.prop.caption:
    #         graph.nodes[subject_id]['label'] = self.value
    #     if self.prop.type.group is None:
    #         graph.nodes[subject_id][self.prop.name] = self.value
    #         return
    #     graph.add_node(value_id)
    #     if 'label' not in graph.nodes[subject_id]:
    #         graph.nodes[subject_id]['label'] = self.value
    #     edge = {
    #         'weight': self.weight,
    #         'label': self.prop.label,
    #         'prop': self.prop.qname,
    #         'inferred': self.inferred
    #     }
    #     graph.add_edge(subject_id, value_id, **edge)

    def __repr__(self):
        return '<Link(%r, %r, %r)>' % (self.value, self.prop, self.value)

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.subject == other.subject \
            and self.subject_type == other.subject_type \
            and self.prop == other.prop \
            and self.value == other.value \
            and self.weight == other.weight \
            and self.inverted == other.inverted
