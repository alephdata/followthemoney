from hashlib import sha1
from copy import deepcopy
from banal import ensure_list

from followthemoney.exc import InvalidData
from followthemoney.types import registry
from followthemoney.property import Property
from followthemoney.util import merge_data, key_bytes


class EntityProxy(object):
    """A wrapper object for an entity, with utility functions for the
    introspection and manipulation of its properties."""

    def __init__(self, schema, data, key_prefix=None):
        self.schema = schema
        self.id = data.pop('id')
        self._key_prefix = key_prefix
        self._properties = data.pop('properties', {})
        self._data = data

    def make_id(self, *parts):
        digest = sha1()
        if self._key_prefix:
            digest.update(key_bytes(self._key_prefix))
        for part in parts:
            digest.update(key_bytes(part))
        self.id = digest.hexdigest()

    def get(self, prop):
        if not isinstance(prop, Property):
            prop = self.schema.get(prop)
            if prop is None:
                raise InvalidData("Unknown property.")
        return ensure_list(self._properties.get(prop.name))

    def add(self, prop, value, cleaned=False):
        values = self.get(prop)
        if not isinstance(prop, Property):
            prop = self.schema.get(prop)
        for val in ensure_list(value):
            if not cleaned:
                val = prop.type.clean(val)
            if val is not None and val not in values:
                values.append(val)
        self._properties[prop.name] = values

    def iterprops(self):
        for prop in self.schema.properties.values():
            yield prop

    def get_type_values(self, type_, cleaned=True):
        values = []
        for prop in self.iterprops():
            if prop.type == type_:
                values.extend(self.get(prop))
        return type_.normalize_set(values, cleaned=cleaned)

    @property
    def countries(self):
        return self.get_type_values(registry.country)

    @property
    def names(self):
        return self.get_type_values(registry.name)

    def get_type_inverted(self, cleaned=True):
        """Invert the properties of an entity into their normalised form."""
        data = {}
        for group, type_ in registry.groups.items():
            values = self.get_type_values(type_, cleaned=cleaned)
            if len(values):
                data[group] = values
        return data

    def to_dict(self):
        data = deepcopy(self._data)
        data['id'] = self.id
        data['schema'] = self.schema.name
        data['properties'] = self._properties
        return data

    def merge(self, other):
        model = self.schema.model
        schema = model.precise_schema(self.schema, other.schema)
        data = {
            'properties': merge_data(self._properties, other._properties)
        }
        return EntityProxy(schema, data)

    def __repr__(self):
        return '<EntityProxy(%r,%r)>' % (self.id, self.schema)

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def from_dict(cls, model, data):
        if isinstance(data, cls):
            return data
        schema = model.get(data.get('schema'))
        return cls(schema, data)
