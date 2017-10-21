from hashlib import sha1
from normality import stringify
from banal import unique_list, ensure_list

from followthemoney.mapping.formatter import Formatter
from followthemoney.util import key_bytes
from followthemoney.exc import InvalidMapping


class QueryMapping(object):

    def __init__(self, model, data, key_prefix=None):
        self.model = model
        self.data = data

        self.mappings = {}
        self.refs = set()
        for name, data in data.get('entities').items():
            mapping = EntityMapping(model, name, data, key_prefix=key_prefix)
            self.mappings[name] = mapping
            self.refs.update(mapping.refs)

    def map(self, record):
        entities = {}
        for name, mapping in self.mappings.items():
            entity = mapping.map(record)
            entities[name] = entity

        for name, entity in entities.items():
            mapping = self.mappings.get(name)
            mapping.resolve(entity, entities)

        return entities


class EntityMapping(object):

    def __init__(self, model, name, data, key_prefix=None):
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
        for prop in self.properties:
            properties[prop.name] = prop.map(record)
        return {
            'id': self.compute_key(record),
            'properties': properties
        }

    def resolve(self, entity, entities):
        for prop in self.properties:
            value = prop.resolve(entities)
            if value is not None:
                entity['properties'][prop.name] = ensure_list(value)
        return entity


class PropertyMapping(object):
    """Map values from a given record (e.g. a CSV row or SQL result) to the
    schema form."""

    def __init__(self, mapper, data, schema):
        self.mapper = mapper
        self.data = data
        self.schema = schema
        self.type = schema.type

        self.refs = ensure_list(data.get('column'))
        self.refs.extend(ensure_list(data.get('columns')))

        self.literals = ensure_list(data.get('literal'))
        self.literals.extend(ensure_list(data.get('literals')))

        self.join = stringify(data.get('join'))
        self.entity = data.get('entity')
        # TODO: check entity type against model constraints

        # this is hacky, trying to generate refs from template
        self.template = data.get('template')
        if self.template is not None:
            self.formatter = Formatter(self.template)
            self.refs.extend(self.formatter.refs)

    def map(self, record):
        values = list(self.literals)

        if self.template is not None:
            values.append(self.formatter.apply(record))
        else:
            for ref in self.refs:
                values.append(record.get(ref))

        values = [self.type.clean(v, record, self.data) for v in values]
        values = [v for v in values if v is not None]

        if self.join is not None:
            values = [self.join.join(values)]

        return unique_list(values)

    def resolve(self, entities):
        if self.entity is None:
            return
        entity = entities.get(self.entity)
        if entity is not None:
            return entity.get('id')
