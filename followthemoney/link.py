from followthemoney.types import registry


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
        self.subject = subject
        self.subject_type = subject_type
        self.prop = prop
        self.value = value
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
