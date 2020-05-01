import logging
from hashlib import sha1
from itertools import product
from typing import Mapping, Dict, Optional, Union, Any, Set, List, Iterable, Iterator, Tuple

from rdflib import Literal, URIRef  # type: ignore
from collections.abc import Hashable
from rdflib.namespace import RDF, SKOS  # type: ignore
from banal import ensure_list, is_mapping, ensure_dict
from ordered_set import OrderedSet  # type: ignore

from followthemoney.model import Model
from followthemoney.exc import InvalidData
from followthemoney.types import registry
from followthemoney.property import Property
from followthemoney.types.common import PropertyType
from followthemoney.schema import Schema
from followthemoney.util import sanitize_text, key_bytes, gettext

log = logging.getLogger(__name__)


class EntityProxy(object):
    """A wrapper object for an entity, with utility functions for the
    introspection and manipulation of its properties."""
    __slots__ = ['schema', 'id', 'key_prefix', 'context',
                 '_properties', '_size']

    def __init__(self, model: Model, data: Mapping, key_prefix: Any=None,
                 cleaned: bool=True):
        _data = dict(data)
        properties = ensure_dict(_data.pop('properties', {}))
        schema = model.get(_data.pop('schema', None))
        if schema is None:
            raise InvalidData(gettext('No schema for entity.'))
        self.schema: Schema = schema
        self.id = sanitize_text(_data.pop('id', None))
        self.key_prefix = sanitize_text(key_prefix)
        self.context = _data
        self._properties: Dict[Property, Set[str]] = {}
        self._size = 0

        if is_mapping(properties):
            for key, value in properties.items():
                self.add(key, value, cleaned=cleaned, quiet=True)

    def make_id(self, *parts: Iterable[Any]) -> Optional[str]:
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
            return None
        self.id = digest.hexdigest()
        return self.id

    def _get_prop(self, prop: Union[Property, str], quiet: bool=False) -> Optional[Property]:
        if isinstance(prop, Property):
            return prop
        if prop not in self.schema.properties:
            if quiet:
                return None
            msg = gettext("Unknown property (%s): %s")
            raise InvalidData(msg % (self.schema, prop))
        return self.schema.get(prop)

    def get(self, prop: Union[Property, str], quiet: bool=False) -> List[str]:
        """Get all values of a property."""
        _prop = self._get_prop(prop, quiet=quiet)
        if _prop is None or _prop not in self._properties:
            return []
        return list(self._properties[_prop])

    def first(self, prop: Union[Property, str], quiet: bool=False) -> Optional[str]:
        """Get only the first (random) value, or None."""
        for value in self.get(prop, quiet=quiet):
            return value
        return None

    def has(self, prop: str, quiet: bool=False) -> bool:
        """Check to see that the property has at least one value set."""
        _prop = self._get_prop(prop, quiet=quiet)
        if _prop is None:
            return False
        return _prop in self._properties

    def add(self, prop: Union[Property, str], values: Optional[Iterable], cleaned: bool=False,
            quiet: bool=False) -> None:
        """Add the given value(s) to the property if they are not empty."""
        _property = self._get_prop(prop, quiet=quiet)
        if _property is None:
            return

        # Don't allow setting the reverse properties:
        if _property.stub:
            if quiet:
                return
            msg = gettext("Stub property (%s): %s")
            raise InvalidData(msg % (self.schema, _property))

        for _value in ensure_list(values):
            if not cleaned:
                cleaned_value = _property.type.clean(_value, countries=self.countries)
            else:
                cleaned_value = _value
            if cleaned_value is None or not isinstance(cleaned_value, Hashable):
                continue
            if _property.type == registry.entity and cleaned_value == self.id:
                msg = gettext("Self-relationship (%s): %s")
                raise InvalidData(msg % (self.schema, _property))

            # Somewhat hacky: limit the maximum size of any particular
            # field to avoid overloading upstream aleph/elasticsearch.
            value_size = _property.type.values_size(cleaned_value)
            if _property.type.max_size is not None:
                if self._size + value_size > _property.type.max_size:
                    msg = "[%s] too large. Rejecting additional values."
                    log.warning(msg, _property.name)
                    continue
            self._size += value_size

            if prop not in self._properties:
                self._properties[_property] = OrderedSet()
            self._properties[_property].add(cleaned_value)

    def set(self, prop: Union[Property, str], values: Iterable,
            cleaned: bool=False, quiet: bool=False) -> None:
        """Replace the values of the property with the given value(s)."""
        _prop = self._get_prop(prop, quiet=quiet)
        if _prop is None:
            return
        self._properties.pop(_prop, None)
        return self.add(_prop, values, cleaned=cleaned, quiet=quiet)

    def pop(self, prop: Union[Property, str], quiet: bool=True) -> Iterable[Property]:
        """Remove all the values from the given property and return them."""
        _prop = self._get_prop(prop, quiet=quiet)
        if _prop is None:
            return []
        return ensure_list(self._properties.pop(_prop, []))

    def remove(self, prop: Union[Property, str], value: Any, quiet: bool=True) -> None:
        """Remove a single element from the given property if it
        exists. If it is not there, no action."""
        _prop = self._get_prop(prop, quiet=quiet)
        if _prop is None:
            return
        try:
            self._properties[_prop].remove(value)
        except KeyError:
            pass

    def iterprops(self) -> List[Property]:
        return list(self._properties.keys())

    def itervalues(self) -> Iterator[Tuple[Property, Any]]:
        for prop, values in self._properties.items():
            for value in values:
                yield (prop, value)

    def edgepairs(self) -> Iterator[Tuple[str, str]]:
        """If the given schema allows for an edge representation of
        the given entity."""
        if self.schema.edge:
            if (isinstance(self.schema.source_prop, Property)
                    and isinstance(self.schema.target_prop, Property)):
                sources = self.get(self.schema.source_prop)
                targets = self.get(self.schema.target_prop)
                for (source, target) in product(sources, targets):
                    yield (source, target)

    def get_type_values(self, type_: PropertyType, cleaned: bool=True) -> List:
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

    def get_type_inverted(self, cleaned: bool=True) -> Dict[str, List]:
        """Invert the properties of an entity into their normalised form."""
        data: Dict[str, List] = {}
        for group, type_ in registry.groups.items():
            values = self.get_type_values(type_, cleaned=cleaned)
            if len(values):
                data[group] = values
        return data

    def triples(self, qualified: bool=True) -> Iterable[Tuple[Literal, URIRef, URIRef]]:
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
    def caption(self) -> str:
        for prop in self.schema.caption:
            for value in self.get(prop):
                return value
        return self.schema.label

    @property
    def names(self) -> List:
        return self.get_type_values(registry.name)

    @property
    def countries(self) -> List:
        return self.get_type_values(registry.country)

    @property
    def country_hints(self) -> Set[str]:
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
    def properties(self) -> Dict[str, List[str]]:
        return {p.name: self.get(p) for p in self._properties.keys()}

    def to_dict(self) -> Dict[str, Any]:
        data = dict(self.context)
        data.update({
            'id': self.id,
            'schema': self.schema.name,
            'properties': self.properties
        })
        return data

    def to_full_dict(self) -> Dict:
        data = self.to_dict()
        data['schemata'] = list(self.schema.names)
        data['name'] = self.caption
        data.update(self.get_type_inverted())
        return data

    def clone(self) -> 'EntityProxy':
        return EntityProxy(self.schema.model, self.to_dict())

    def merge(self, other: 'EntityProxy'):
        model = self.schema.model
        other = self.from_dict(model, other)
        self.id = self.id or other.id
        try:
            self.schema = model.common_schema(self.schema, other.schema)
        except InvalidData as e:
            msg = "Cannot merge entities with id %s: %s"
            raise InvalidData(msg % (self.id, e))

        self.context.update(other.context)
        for prop, value in set(other.itervalues()):
            self.add(prop, value, cleaned=True, quiet=True)

    def __str__(self):
        return self.caption

    def __repr__(self):
        return '<E(%r,%r)>' % (self.id, str(self))

    def __len__(self):
        return self._size

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    @classmethod
    def from_dict(cls, model: Model, data, cleaned: bool=True):
        if isinstance(data, cls):
            return data
        return cls(model, data, cleaned=cleaned)
