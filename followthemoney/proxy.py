import logging
from itertools import product
from rdflib import Literal, URIRef  # type: ignore
from rdflib.namespace import RDF, SKOS  # type: ignore
from banal import ensure_dict

from followthemoney.exc import InvalidData
from followthemoney.types import registry
from followthemoney.util import sanitize_text, gettext
from followthemoney.util import merge_context, value_list, make_entity_id

log = logging.getLogger(__name__)


class EntityProxy(object):
    """A wrapper object for an entity, with utility functions for the
    introspection and manipulation of its properties."""

    __slots__ = ["schema", "id", "key_prefix", "context", "_properties", "_size"]

    def __init__(self, model, data, key_prefix=None, cleaned=True):
        data = dict(data)
        properties = data.pop("properties", {})
        if not cleaned:
            properties = ensure_dict(properties)
        self.schema = model.get(data.pop("schema", None))
        if self.schema is None:
            raise InvalidData(gettext("No schema for entity."))
        self.key_prefix = key_prefix
        self.id = data.pop("id", None)
        if not cleaned:
            self.id = sanitize_text(self.id)
        self.context = data
        self._properties = {}
        self._size = 0

        for key, value in properties.items():
            if key not in self.schema.properties:
                continue
            if not cleaned:
                self.add(key, value, cleaned=cleaned, quiet=True)
            else:
                values = set(value)
                self._properties[key] = values
                self._size += sum([len(v) for v in values])

    def make_id(self, *parts):
        """Generate a (hopefully unique) ID for the given entity, composed
        of the given components, and the key_prefix defined in the proxy.
        """
        self.id = make_entity_id(*parts, key_prefix=self.key_prefix)
        return self.id

    def _prop_name(self, prop, quiet=False):
        # This is pretty unwound because it gets called a *lot*.
        if prop in self.schema.properties:
            return prop
        try:
            if prop.name in self.schema.properties:
                return prop.name
        except AttributeError:
            pass
        if quiet:
            return
        msg = gettext("Unknown property (%s): %s")
        raise InvalidData(msg % (self.schema, prop))

    def get(self, prop, quiet=False):
        """Get all values of a property."""
        prop = self._prop_name(prop, quiet=quiet)
        if prop not in self._properties:
            return []
        return list(self._properties.get(prop))

    def first(self, prop, quiet=False):
        """Get only the first (random) value, or None."""
        for value in self.get(prop, quiet=quiet):
            return value

    def has(self, prop, quiet=False):
        """Check to see that the property has at least one value set."""
        prop = self._prop_name(prop, quiet=quiet)
        return prop in self._properties

    def add(self, prop, values, cleaned=False, quiet=False, fuzzy=False):
        """Add the given value(s) to the property if they are not empty."""
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None:
            return
        prop = self.schema.properties[prop_name]

        # Don't allow setting the reverse properties:
        if prop.stub:
            if quiet:
                return
            msg = gettext("Stub property (%s): %s")
            raise InvalidData(msg % (self.schema, prop))

        for value in value_list(values):
            if not cleaned:
                value = prop.type.clean(value, proxy=self, fuzzy=fuzzy)
            if value is None:
                continue
            if prop.type == registry.entity and value == self.id:
                msg = gettext("Self-relationship (%s): %s")
                raise InvalidData(msg % (self.schema, prop))

            # Somewhat hacky: limit the maximum size of any particular
            # field to avoid overloading upstream aleph/elasticsearch.
            value_size = len(value)
            if prop.type.max_size is not None:
                if self._size + value_size > prop.type.max_size:
                    # msg = "[%s] too large. Rejecting additional values."
                    # log.warning(msg, prop.name)
                    continue
            self._size += value_size

            if prop_name not in self._properties:
                self._properties[prop_name] = set()
            self._properties[prop_name].add(value)

    def set(self, prop, values, cleaned=False, quiet=False):
        """Replace the values of the property with the given value(s)."""
        prop = self._prop_name(prop, quiet=quiet)
        if prop is None:
            return
        self._properties.pop(prop, None)
        return self.add(prop, values, cleaned=cleaned, quiet=quiet)

    def pop(self, prop, quiet=True):
        """Remove all the values from the given property and return them."""
        prop = self._prop_name(prop, quiet=quiet)
        if prop is None or prop not in self._properties:
            return []
        return list(self._properties.pop(prop))

    def remove(self, prop, value, quiet=True):
        """Remove a single element from the given property if it
        exists. If it is not there, no action."""
        prop = self._prop_name(prop, quiet=quiet)
        if prop is not None and prop in self._properties:
            try:
                self._properties[prop].remove(value)
            except KeyError:
                pass

    def iterprops(self):
        return [self.schema.properties[p] for p in self._properties.keys()]

    def itervalues(self):
        for name, values in self._properties.items():
            prop = self.schema.properties[name]
            for value in values:
                yield (prop, value)

    def edgepairs(self):
        """If the given schema allows for an edge representation of
        the given entity."""
        if self.schema.edge:
            sources = self.get(self.schema.source_prop)
            targets = self.get(self.schema.target_prop)
            for (source, target) in product(sources, targets):
                yield (source, target)

    def get_type_values(self, type_, cleaned=True):
        """All values of a particular type associated with a the entity."""
        combined = set()
        for prop, values in self._properties.items():
            if self.schema.properties[prop].type == type_:
                combined.update(values)
        return list(combined)

    def get_type_inverted(self, cleaned=True):
        """Invert the properties of an entity into their normalised form."""
        data = {}
        for group, type_ in registry.groups.items():
            values = self.get_type_values(type_, cleaned=cleaned)
            if len(values):
                data[group] = values
        return data

    def triples(self, qualified=True):
        if self.id is None or self.schema is None:
            return
        uri = registry.entity.rdf(self.id)
        yield (uri, RDF.type, self.schema.uri)
        if qualified:
            caption = self.caption
            if caption != self.schema.label:
                yield (uri, SKOS.prefLabel, Literal(caption))
        for prop, value in self.itervalues():
            value = prop.type.rdf(value)
            if qualified:
                yield (uri, prop.uri, value)
            else:
                yield (uri, URIRef(prop.name), value)

    @property
    def caption(self):
        for prop in self.schema.caption:
            for value in self.get(prop):
                return value
        return self.schema.label

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
        return {p: list(vs) for p, vs in self._properties.items()}

    def to_dict(self):
        data = dict(self.context)
        data.update(
            {"id": self.id, "schema": self.schema.name, "properties": self.properties}
        )
        return data

    def to_full_dict(self):
        data = self.to_dict()
        data.update(self.get_type_inverted())
        return data

    def clone(self):
        return EntityProxy(self.schema.model, self.to_dict())

    def merge(self, other):
        model = self.schema.model
        other = self.from_dict(model, other)
        self.id = self.id or other.id
        try:
            self.schema = model.common_schema(self.schema, other.schema)
        except InvalidData as e:
            msg = "Cannot merge entities with id %s: %s"
            raise InvalidData(msg % (self.id, e))

        self.context = merge_context(self.context, other.context)
        self._size = 0
        for prop, values in other._properties.items():
            self._properties.setdefault(prop, set())
            self._properties[prop].update(values)
            self._size += sum([len(v) for v in self._properties[prop]])
        return self

    def __str__(self):
        return self.caption

    def __repr__(self):
        return "<E(%r,%r)>" % (self.id, str(self))

    def __len__(self):
        return self._size

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def from_dict(cls, model, data, cleaned=True):
        if isinstance(data, cls):
            return data
        return cls(model, data, cleaned=cleaned)
