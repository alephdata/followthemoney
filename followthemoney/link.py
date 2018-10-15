from followthemoney.types import registry


class Link(object):
    """A wrapper object for an RDF-like statement, similar to a triple
    but with weighting and some other metadata. This has built-in
    support for packing, i.e. transforming the link to a form suitable
    for storage in a key/value store.
    """
    __slots__ = ['ref', 'prop', 'value', 'weight', 'inverted', 'inferred']

    def __init__(self, ref, prop, value, weight=1.0,
                 inverted=False, inferred=False):
        self.ref = ref
        self.prop = prop
        self.value = value
        self.weight = weight
        self.inverted = inverted
        self.inferred = inferred

    @property
    def subject(self):
        return registry.deref(self.ref)[1]

    @property
    def value_ref(self):
        return self.prop.type.ref(self.value)

    def rdf(self):
        """Convert to an RDF triple. This looses weighting and inferrence
        metadata."""
        if self.inverted:
            return
        subject_type, subject = registry.deref(self.ref)
        subject_uri = subject_type.rdf(subject)
        value_obj = self.prop.type.rdf(self.value)
        return (subject_uri, self.prop.uri, value_obj)

    def to_tuple(self):
        return (self.prop.qname, self.weight, self.inverted, self.inferred,
                self.value)

    @classmethod
    def from_tuple(cls, model, ref, data):
        qname, weight, inverted, inferred, value = data
        prop = model.get_qname(qname)
        return cls(ref, prop, value,
                   weight=weight,
                   inverted=inverted,
                   inferred=inferred)

    def invert(self):
        if not self.inverted and self.prop.reverse is not None:
            return Link(self.value_ref,
                        self.prop.reverse,
                        self.subject,
                        weight=self.weight)
        return Link(self.value_ref,
                    self.prop,
                    self.subject,
                    weight=self.weight,
                    inverted=not self.inverted)

    def __repr__(self):
        return '<Link(%r, %r, %r)>' % (self.ref, self.prop, self.value)

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.ref == other.ref \
            and self.prop == other.prop \
            and self.value == other.value \
            and self.weight == other.weight \
            and self.inverted == other.inverted
