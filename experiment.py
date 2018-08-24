import sys
import yaml

from followthemoney import model
from followthemoney.types import registry


class Statement(object):

    def __init__(self, ref, prop, value, weight=1.0, inverted=False):
        self.ref = ref
        self.prop = prop
        self.value = value
        self.weight = weight
        self.inverted = inverted

    def pack(self):
        qualifier = '*' if self.inverted else ''
        if self.weight < 1.0:
            qualifier += self.weight
        return '>'.join((self.prop.qname, qualifier, self.value))

    @classmethod
    def unpack(cls, ref, packed):
        qname, qualifier, value = packed.split('>', 2)
        prop = model.get_qname(qname)
        # TODO: parse qualifier
        return cls(ref, prop, value)

    def invert(self):
        ref = self.prop.type.ref(self.value)
        _, value = registry.deref(self.ref)
        cls = type(self)
        return cls(ref, self.prop, value,
                   weight=self.weight,
                   inverted=not self.inverted)

    def __str__(self):
        return '->'.join((self.ref, self.pack()))

    def __repr__(self):
        return '<Statement(%r,%r,%r,%r,%r)>' % (self.ref, self.prop,
                                                self.value, self.weight,
                                                self.inverted)


def execute_mapping(query):
    for entity in model.map_entities(query):
        schema = model.get(entity['schema'])
        properties = entity.pop('properties')
        entity_ref = registry.entity.ref(entity)
        for name, values in properties.items():
            prop = schema.get(name)
            for value in values:
                if prop.type.prefix:
                    stmt = Statement(entity_ref, prop, value)
                    print(stmt)
                    print(stmt.invert())


if __name__ == '__main__':
    mapping_file = sys.argv[1]
    with open(mapping_file, 'r') as fh:
        data = yaml.load(fh)
        for dataset, mapping in data.items():
            for query in mapping.get('queries'):
                execute_mapping(query)
