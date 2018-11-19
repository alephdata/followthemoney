from hashlib import sha1
from banal import ensure_list, is_mapping
from normality import stringify

from followthemoney.exc import InvalidData
from followthemoney.types import registry
from followthemoney.property import Property
from followthemoney.graph import Link, Node
from followthemoney.util import key_bytes, gettext


class EntityProxy(object):
    """A wrapper object for an entity, with utility functions for the
    introspection and manipulation of its properties."""
    __slots__ = ['schema', 'id', 'key_prefix', '_properties',
                 'countries', 'names']

    def __init__(self, schema, id, properties, key_prefix=None):
        self.schema = schema
        self.id = stringify(id)
        self.key_prefix = stringify(key_prefix)
        self.countries = set()
        self.names = set()
        self._properties = {}

        if is_mapping(properties):
            for key, value in properties.items():
                self.add(key, value, cleaned=True, quiet=True)

    def make_id(self, *parts):
        digest = sha1()
        if self.key_prefix:
            digest.update(key_bytes(self.key_prefix))
        base = digest.digest()
        for part in parts:
            digest.update(key_bytes(part))
        if digest.digest() == base:
            self.id = None
            return
        self.id = digest.hexdigest()
        return self.id

    def _get_prop(self, prop, quiet=False):
        if isinstance(prop, Property):
            return prop
        if prop not in self.schema.properties:
            if quiet:
                return
            msg = gettext("Unknown property (%s): %s")
            raise InvalidData(msg % (self.schema, prop))
        return self.schema.get(prop)

    def get(self, prop, quiet=False):
        prop = self._get_prop(prop, quiet=quiet)
        if prop is None or prop not in self._properties:
            return []
        return list(self._properties.get(prop))

    def add(self, prop, values, cleaned=False, quiet=False):
        prop = self._get_prop(prop, quiet=quiet)
        if prop is None:
            return
        for value in ensure_list(values):
            if not cleaned:
                value = prop.type.clean(value, countries=self.countries)
            if value is None:
                continue
            if prop not in self._properties:
                self._properties[prop] = set()
            self._properties[prop].add(value)
            if prop.type == registry.name:
                norm = prop.type.normalize(value, cleaned=True)
                self.names.update(norm)
            if prop.type == registry.country:
                norm = prop.type.normalize(value, cleaned=True)
                self.countries.update(norm)

    def pop(self, prop, quiet=False):
        prop = self._get_prop(prop, quiet=quiet)
        if prop is None:
            return []
        return ensure_list(self._properties.pop(prop, []))

    def iterprops(self):
        for prop in self.schema.properties.values():
            yield prop

    def itervalues(self):
        for prop, values in self._properties.items():
            for value in values:
                yield (prop, value)

    def get_type_values(self, type_, cleaned=True):
        if type_ == registry.name:
            return list(self.names)
        if type_ == registry.country:
            return list(self.countries)
        combined = set()
        for prop, values in self._properties.items():
            if prop.type == type_:
                combined.update(values)
        return type_.normalize_set(combined,
                                   cleaned=cleaned,
                                   countries=self.countries)

    def get_type_inverted(self, cleaned=True):
        """Invert the properties of an entity into their normalised form."""
        data = {}
        for group, type_ in registry.groups.items():
            values = self.get_type_values(type_, cleaned=cleaned)
            if len(values):
                data[group] = values
        return data

    @property
    def node(self):
        if self.id is None:
            return
        return Node(registry.entity, self.id)

    @property
    def links(self):
        node = self.node
        if node is None:
            return
        for prop, value in self.itervalues():
            yield Link(node, prop, value)

    @property
    def caption(self):
        for prop in self.iterprops():
            if prop.caption:
                for value in self.get(prop):
                    return value

    @property
    def country_hints(self):
        """Some property types, such as phone numbers, and IBAN codes,
        imply a country that may be associated with the entity.
        """
        countries = set(self.countries)
        for (prop, value) in self.itervalues():
            hint = prop.type.country_hint(value)
            if hint is not None:
                countries.add(hint)
        return countries

    @property
    def properties(self):
        return {p.name: self.get(p) for p in self._properties.keys()}

    def to_dict(self, inverted_index=False):
        return {
            'id': self.id,
            'schema': self.schema.name,
            'properties': self.properties
        }

    def to_full_dict(self):
        data = self.to_dict()
        data['schemata'] = list(self.schema.names)
        data.update(self.get_type_inverted())
        return data

    def clone(self):
        return EntityProxy(self.schema, self.id, self._properties)

    def merge(self, other):
        if id(self) == id(other):
            return
        model = self.schema.model
        other = self.from_dict(model, other)
        self.id = self.id or other.id
        self.schema = model.common_schema(self.schema, other.schema)
        for prop, value in set(other.itervalues()):
            self.add(prop, value)

    def __repr__(self):
        return '<EntityProxy(%r,%r,%r)>' % (self.id, self.schema, self.caption)

    def __str__(self):
        return self.caption or self.schema.name

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def from_dict(cls, model, data):
        if isinstance(data, cls):
            return data
        schema = model.get(data.get('schema'))
        if schema is None:
            raise InvalidData(gettext('No schema for entity.'))
        return cls(schema, data.get('id'), data.get('properties'))
