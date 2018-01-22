from hashlib import sha1
from banal import ensure_list

from followthemoney.mapping.property import PropertyMapping
from followthemoney.util import key_bytes
from followthemoney.exc import InvalidMapping


class EntityMapping(object):

    def __init__(self, model, query, name, data, key_prefix=None):
        self.model = model
        self.name = name
        self.data = data

        self.seed = sha1(key_bytes(key_prefix) +
                         key_bytes(data.get('key_literal', '')))
        self.keys = ensure_list(data.get('key'))
        self.keys.extend(ensure_list(data.get('keys')))
        self.keys = set(self.keys)
        # if not len(self.keys):
        #     raise InvalidMapping("No keys defined for %r" % name)

        self.schema = model.get(data.get('schema'))
        if self.schema is None:
            raise InvalidMapping("Invalid schema: %s" % data.get('schema'))

        self.refs = set(self.keys)
        self.dependencies = set()
        self.properties = []
        for name, prop in data.get('properties', {}).items():
            prop_schema = self.schema.get(name)
            if prop_schema is None:
                raise InvalidMapping("Invalid property: %s" % name)
            prop = PropertyMapping(query, prop, prop_schema)
            self.properties.append(prop)
            self.refs.update(prop.refs)
            if prop.entity:
                self.dependencies.add(prop.entity)

    def bind(self):
        for prop in self.properties:
            prop.bind()

    def compute_key(self, record, related):
        """Generate a key for this entity, based on the given fields, and the
        ID of other entities referenced by this entity."""
        digest = self.seed.copy()
        for entity in sorted(related):
            digest.update(key_bytes(entity))
        for key in self.keys:
            value = record.get(key)
            digest.update(key_bytes(value))
        if digest.digest() != self.seed.digest():
            return digest.hexdigest()

    def map(self, record, entities):
        properties = {}

        # THIS IS HACKY
        # Some of the converters, e.g. for phone numbers, work better if they
        # know the country which the number is from. In order to provide that
        # detail, we are first running country fields, then making the data
        # from that accessible to phone and address parsers.
        countries = set()
        for prop in self.properties:
            if prop.schema.is_country:
                values = prop.map(record, entities)
                countries.update(values)
                properties[prop.name] = values

        related = set()
        for prop in self.properties:
            values = properties.pop(prop.name, None)
            if values is None:
                values = prop.map(record, entities, countries=countries)
            if len(values):
                properties[prop.name] = values
            if prop.entity is not None:
                related.update(values)

        key = self.compute_key(record, related)
        if key is None:
            return

        return {
            'id': key,
            'schema': self.schema.name,
            'properties': properties
        }

    def __repr__(self):
        return '<EntityMapping(%r)>' % self.name
