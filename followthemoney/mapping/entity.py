from hashlib import sha1
from banal import keys_values

from followthemoney.mapping.property import PropertyMapping
from followthemoney.types import registry
from followthemoney.util import key_bytes
from followthemoney.exc import InvalidMapping


class EntityMapping(object):

    def __init__(self, model, query, name, data, key_prefix=None):
        self.model = model
        self.name = name
        self.data = data

        self.seed = sha1(key_bytes(key_prefix))
        self.seed.update(key_bytes(data.get('key_literal')))

        self.keys = keys_values(data, 'key', 'keys')
        self.id_column = data.get('id_column')
        if not len(self.keys) and self.id_column is None:
            raise InvalidMapping("No keys or ID: %r" % name)
        if len(self.keys) and self.id_column is not None:
            msg = "Please use only keys or id_column, not both: %r" % name
            raise InvalidMapping(msg)

        self.schema = model.get(data.get('schema'))
        if self.schema is None:
            raise InvalidMapping("Invalid schema: %s" % data.get('schema'))

        self.refs = set(self.keys)
        if self.id_column:
            self.refs.add(self.id_column)
        self.dependencies = set()
        self.properties = []
        for name, mapping in data.get('properties', {}).items():
            prop = self.schema.get(name)
            if prop is None:
                raise InvalidMapping("Invalid property: %s" % name)
            mapping = PropertyMapping(query, mapping, prop)
            self.properties.append(mapping)
            self.refs.update(mapping.refs)
            if mapping.entity:
                self.dependencies.add(mapping.entity)

    def bind(self):
        for prop in self.properties:
            prop.bind()

    def compute_key(self, record):
        """Generate a key for this entity, based on the given fields."""
        if self.id_column is not None:
            return record.get(self.id_column)
        values = [key_bytes(record.get(k)) for k in self.keys]
        digest = self.seed.copy()
        for value in sorted(values):
            digest.update(value)
        if digest.digest() != self.seed.digest():
            return digest.hexdigest()

    def map(self, record, entities):
        proxy = self.model.make_entity(self.schema)
        proxy.id = self.compute_key(record)
        if proxy.id is None:
            return

        # THIS IS HACKY
        # Some of the converters, e.g. for phone numbers, work better if they
        # know the country which the number is from. In order to provide that
        # detail, we are first running country fields, then making the data
        # from that accessible to phone and address parsers.
        for prop in self.properties:
            if prop.prop.type == registry.country:
                prop.map(proxy, record, entities)

        for prop in self.properties:
            if prop.prop.type != registry.country:
                prop.map(proxy, record, entities, countries=proxy.countries)

        for prop in self.properties:
            if prop.required and not proxy.has(prop.prop):
                # This is a bit weird, it flags fields to be required in
                # the mapping, not in the model. Basically it means: if
                # this row of source data doesn't have that field, then do
                # not map it again.
                return
        return proxy

    def __repr__(self):
        return '<EntityMapping(%r)>' % self.name
