from banal import ensure_list

from followthemoney.types import registry
# from followthemoney.exc import InvalidData


class Link(object):
    """A wrapper object for an RDF-like statement, similar to a triple
    but with weighting and some other metadata. This has built-in
    support for packing, i.e. transforming the link to a form suitable
    for storage in a key/value store.
    """

    def __init__(self, ref, prop, value, weight=1.0, inverted=False):
        self.ref = ref
        self.prop = prop
        self.value = value
        self.weight = weight
        self.inverted = inverted

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

    def pack(self):
        qualifier = '*' if self.inverted else ''
        if self.weight < 1.0:
            qualifier += self.weight
        return self.ref, f'{self.prop.qname}>{qualifier}>{self.value}'

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

    @classmethod
    def unpack(cls, model, ref, packed):
        qname, qualifier, value = packed.split('>', 2)
        prop = model.get_qname(qname)
        # TODO: parse qualifier
        return cls(ref, prop, value)

    @classmethod
    def from_entity(cls, model, entity):
        ref = registry.entity.ref(entity.get('id'))
        schema = model.get(entity.get('schema'))
        if schema is None:
            return

        properties = entity.get('properties', {})
        for prop in schema.properties.values():
            for value in ensure_list(properties.get(prop.name)):
                yield cls(ref, prop, value)

    def __eq__(self, other):
        return self.ref == other.ref \
            and self.prop == other.prop \
            and self.value == other.value \
            and self.weight == other.weight \
            and self.inverted == other.inverted
