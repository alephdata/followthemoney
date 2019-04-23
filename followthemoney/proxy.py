import logging
from hashlib import sha1
from itertools import product
from normality import stringify
from rdflib import Literal
from collections.abc import Hashable
from rdflib.namespace import RDF, SKOS
from banal import ensure_list, is_mapping, ensure_dict

from followthemoney.exc import InvalidData
from followthemoney.types import registry
from followthemoney.property import Property
from followthemoney.graph import Statement, Node
from followthemoney.util import key_bytes, gettext

log = logging.getLogger(__name__)


class EntityProxy(object):
    """A wrapper object for an entity, with utility functions for the
    introspection and manipulation of its properties."""
    __slots__ = ['schema', 'id', 'key_prefix', '_properties', 'context']

    def __init__(self, model, data, key_prefix=None):
        data = dict(data)
        properties = ensure_dict(data.pop('properties', {}))
        self.schema = model.get(data.pop('schema', None))
        if self.schema is None:
            raise InvalidData(gettext('No schema for entity.'))
        self.id = stringify(data.pop('id', None))
        self.key_prefix = stringify(key_prefix)
        self.context = data
        self._properties = {}

        if is_mapping(properties):
            for key, value in properties.items():
                self.add(key, value, cleaned=True, quiet=True)

    def make_id(self, *parts):
        """Generate a (hopefully unique) ID for the given entity, composed
        of the given components, and the key_prefix defined in the proxy.
        """
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
        """Get all values of a property."""
        prop = self._get_prop(prop, quiet=quiet)
        if prop is None or prop not in self._properties:
            return []
        return list(self._properties.get(prop))

    def first(self, prop, quiet=False):
        """Get only the first (random) value, or None."""
        for value in self.get(prop, quiet=quiet):
            return value

    def has(self, prop, quiet=False):
        """Check to see that the property has at least one value set."""
        prop = self._get_prop(prop, quiet=quiet)
        if prop is None:
            return False
        return prop in self._properties

    def add(self, prop, values, cleaned=False, quiet=False):
        """Add the given value(s) to the property if they are not empty."""
        prop = self._get_prop(prop, quiet=quiet)
        if prop is None:
            return
        for value in ensure_list(values):
            if not cleaned:
                value = prop.type.clean(value, countries=self.countries)
            if value is None or not isinstance(value, Hashable):
                continue
            if prop not in self._properties:
                self._properties[prop] = set()

            # Somewhat hacky: limit the maximum size of any particular
            # field to avoid overloading upstream aleph/elasticsearch.
            if prop.type.max_size is not None:
                existing_size = prop.type.values_size(self._properties[prop])
                new_size = existing_size + prop.type.values_size(value)
                if new_size > prop.type.max_size:
                    msg = "[%s] too large. Rejecting additional values."
                    log.warning(msg, prop.name)
                    continue

            self._properties[prop].add(value)

    def set(self, prop, values, cleaned=False, quiet=False):
        """Replace the values of the property with the given value(s)."""
        prop = self._get_prop(prop, quiet=quiet)
        if prop is None:
            return
        self._properties.pop(prop, None)
        return self.add(prop, values, cleaned=cleaned, quiet=quiet)

    def pop(self, prop, quiet=True):
        """Remove all the values from the given property and return them."""
        prop = self._get_prop(prop, quiet=quiet)
        if prop is None:
            return []
        return ensure_list(self._properties.pop(prop, []))

    def remove(self, prop, value, quiet=True):
        """Remove a single element from the given property if it
        exists. If it is not there, no action."""
        prop = self._get_prop(prop, quiet=quiet)
        try:
            self._properties[prop].remove(value)
        except KeyError:
            pass

    def iterprops(self):
        for prop in self.schema.properties.values():
            yield prop

    def itervalues(self):
        for prop, values in self._properties.items():
            for value in values:
                yield (prop, value)

    def edgepairs(self):
        """If the given schema allows for an edge representation of
        the given entity."""
        if self.schema.edge:
            sources = self.get(self.schema.edge_source)
            targets = self.get(self.schema.edge_target)
            for (source, target) in product(sources, targets):
                yield (source, target)

    def get_type_values(self, type_, cleaned=True):
        """All values of a particular type associated with a the entity."""
        combined = set()
        for prop, values in self._properties.items():
            if prop.type == type_:
                combined.update(values)
        countries = []
        if type_ != registry.country:
            countries = self.get_type_values(registry.country)
        return type_.normalize_set(combined, cleaned=cleaned,
                                   countries=countries)

    def get_type_inverted(self, cleaned=True):
        """Invert the properties of an entity into their normalised form."""
        data = {}
        for group, type_ in registry.groups.items():
            if group is None:
                continue
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
    def statements(self):
        if self.id is None:
            return
        node = self.node
        for prop, value in self.itervalues():
            yield Statement(node, prop, value)

    @property
    def triples(self):
        if self.id is None or self.schema is None:
            return
        yield (self.node.uri, RDF.type, self.schema.uri)
        caption = self.caption
        if caption is not None:
            yield (self.node.uri, SKOS.prefLabel, Literal(caption))
        for statement in self.statements:
            yield statement.rdf()

    @property
    def caption(self):
        for prop in self.iterprops():
            if prop.caption:
                for value in self.get(prop):
                    return value

    @property
    def names(self):
        return self.get_type_values(registry.name)

    @property
    def countries(self):
        return self.get_type_values(registry.country)

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

    def to_dict(self):
        data = dict(self.context)
        data.update({
            'id': self.id,
            'schema': self.schema.name,
            'properties': self.properties
        })
        return data

    def to_full_dict(self):
        data = self.to_dict()
        data['schemata'] = list(self.schema.names)
        data['name'] = self.caption
        if not data['name']:
            data.pop('name')
        data.update(self.get_type_inverted())
        return data

    def clone(self):
        return EntityProxy(self.schema.model, self.to_dict())

    def merge(self, other):
        model = self.schema.model
        other = self.from_dict(model, other)
        self.id = self.id or other.id
        self.schema = model.common_schema(self.schema, other.schema)
        self.context.update(other.context)
        for prop, value in set(other.itervalues()):
            self.add(prop, value, cleaned=True, quiet=True)

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
        return cls(model, data)
