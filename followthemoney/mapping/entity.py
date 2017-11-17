from hashlib import sha1
from banal import ensure_list

from followthemoney.mapping.property import PropertyMapping
from followthemoney.util import key_bytes
from followthemoney.exc import InvalidMapping


class EntityMapping(object):

    def __init__(self, mapping, model, name, data, key_prefix=None):
        self.mappings = mapping.mappings
        self.model = model
        self.data = data

        self.seed = sha1(key_bytes(key_prefix))
        self.keys = ensure_list(data.get('key'))
        self.keys.extend(ensure_list(data.get('keys')))
        if not len(self.keys):
            raise InvalidMapping("No keys defined for %r" % name)

        self.schema = model.get(data.get('schema'))
        if self.schema is None:
            raise InvalidMapping("Invalid schema: %s" % data.get('schema'))

        self.refs = set(self.keys)
        self.properties = []
        for name, prop in data.get('properties', {}).items():
            prop_schema = self.schema.get(name)
            if prop_schema is None:
                raise InvalidMapping("Invalid property: %s" % name)
            prop = PropertyMapping(self, prop, prop_schema)
            self.properties.append(prop)
            self.refs.update(prop.refs)

    def compute_key(self, record):
        digest = self.seed.copy()
        for key in self.keys:
            digest.update(key_bytes(record.get(key)))
        if digest.digest() != self.seed.digest():
            return digest.hexdigest()

    def map(self, record):
        properties = {}

        # THIS IS HACKY
        # Some of the converters, e.g. for phone numbers, work better if they
        # know the country which the number is from. In order to provide that
        # detail, we are first running country fields, then making the data
        # from that accessible to phone and address parsers.
        countries = set()
        for prop in self.properties:
            if prop.schema.is_country:
                values = prop.map(record)
                countries.update(values)
                properties[prop.name] = values

        for prop in self.properties:
            if not prop.schema.is_country:
                properties[prop.name] = prop.map(record, countries=countries)

        return {
            'id': self.compute_key(record),
            'schema': self.schema.name,
            'properties': properties
        }

    def resolve(self, entity, entities):
        for prop in self.properties:
            value = prop.resolve(entities)
            if value is not None:
                entity['properties'][prop.name] = ensure_list(value)
        return entity
