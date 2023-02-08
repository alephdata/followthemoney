import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    Type,
    TypeVar,
    cast,
)
import warnings
from itertools import product
from banal import ensure_dict

from followthemoney.exc import InvalidData
from followthemoney.types import registry
from followthemoney.types.common import PropertyType
from followthemoney.property import Property
from followthemoney.rdf import SKOS, RDF, Literal, URIRef, Identifier
from followthemoney.util import sanitize_text, gettext
from followthemoney.util import merge_context, value_list, make_entity_id

if TYPE_CHECKING:
    from followthemoney.model import Model

log = logging.getLogger(__name__)
P = Union[Property, str]
Triple = Tuple[Identifier, Identifier, Identifier]
E = TypeVar("E", bound="EntityProxy")


class EntityProxy(object):
    """A wrapper object for an entity, with utility functions for the
    introspection and manipulation of its properties.

    This is the main working object in the library, used to generate, validate
    and emit data."""

    __slots__ = ["schema", "id", "key_prefix", "context", "_properties", "_size"]

    def __init__(
        self,
        model: "Model",
        data: Dict[str, Any],
        key_prefix: Optional[str] = None,
        cleaned: bool = True,
    ):
        data = dict(data or {})
        properties = data.pop("properties", {})
        if not cleaned:
            properties = ensure_dict(properties)

        #: The schema definition for this entity, which implies the properties
        #: That can be set on it.
        schema = model.get(data.pop("schema", None))
        if schema is None:
            raise InvalidData(gettext("No schema for entity."))
        self.schema = schema

        #: When using :meth:`~make_id` to generate a natural key for this entity,
        #: the prefix will be added to the ID as a salt to make it easier to keep
        #: IDs unique across datasets. This is somewhat redundant following the
        #: introduction of :class:`~followthemoney.namespace.Namespace`.
        self.key_prefix = key_prefix

        #: A unique identifier for this entity, usually a hashed natural key,
        #: a UUID, or a very simple slug. Can be signed using a
        #: :class:`~followthemoney.namespace.Namespace`.
        self.id = data.pop("id", None)
        if not cleaned:
            self.id = sanitize_text(self.id)

        #: If the input dictionary for the entity proxy contains fields other
        #: than ``id``, ``schema`` or ``properties``, they will be kept in here
        #: and re-added upon serialization.
        self.context = data
        self._properties: Dict[str, Set[str]] = {}
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

    def make_id(self, *parts: Any) -> Optional[str]:
        """Generate a (hopefully unique) ID for the given entity, composed
        of the given components, and the :attr:`~key_prefix` defined in
        the proxy.
        """
        self.id = make_entity_id(*parts, key_prefix=self.key_prefix)
        return self.id

    def _prop_name(self, prop: P, quiet: bool = False) -> Optional[str]:
        # This is pretty unwound because it gets called a *lot*.
        if prop in self.schema.properties:
            return cast(str, prop)
        try:
            obj = cast(Property, prop)
            if obj.name in self.schema.properties:
                return obj.name
        except AttributeError:
            pass
        if quiet:
            return None
        msg = gettext("Unknown property (%s): %s")
        raise InvalidData(msg % (self.schema, prop))

    def get(self, prop: P, quiet: bool = False) -> List[str]:
        """Get all values of a property.

        :param prop: can be given as a name or an instance of
            :class:`~followthemoney.property.Property`.
        :param quiet: a reference to an non-existent property will return
            an empty list instead of raising an error.
        :return: A list of values.
        """
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None:
            return []
        return list(self._properties.get(prop_name, []))

    def first(self, prop: P, quiet: bool = False) -> Optional[str]:
        """Get only the first value set for the property, in no particular
        order.

        :param prop: can be given as a name or an instance of
            :class:`~followthemoney.property.Property`.
        :param quiet: a reference to an non-existent property will return
            an empty list instead of raising an error.
        :return: A value, or ``None``.
        """
        for value in self.get(prop, quiet=quiet):
            return value
        return None

    def has(self, prop: P, quiet: bool = False) -> bool:
        """Check to see if the given property has at least one value set.

        :param prop: can be given as a name or an instance of
            :class:`~followthemoney.property.Property`.
        :param quiet: a reference to an non-existent property will return
            an empty list instead of raising an error.
        :return: a boolean.
        """
        prop_name = self._prop_name(prop, quiet=quiet)
        return prop_name in self._properties

    def add(
        self,
        prop: P,
        values: Any,
        cleaned: bool = False,
        quiet: bool = False,
        fuzzy: bool = False,
        format: Optional[str] = None,
    ) -> None:
        """Add the given value(s) to the property if they are valid for
        the type of the property.

        :param prop: can be given as a name or an instance of
            :class:`~followthemoney.property.Property`.
        :param values: either a single value, or a list of values to be added.
        :param cleaned: should the data be normalised before adding it.
        :param quiet: a reference to an non-existent property will return
            an empty list instead of raising an error.
        :param fuzzy: when normalising the data, should fuzzy matching be allowed.
        :param format: when normalising the data, formatting for a date.
        """
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None:
            return None
        prop = self.schema.properties[prop_name]

        # Don't allow setting the reverse properties:
        if prop.stub:
            if quiet:
                return None
            msg = gettext("Stub property (%s): %s")
            raise InvalidData(msg % (self.schema, prop))

        for value in value_list(values):
            if not cleaned:
                value = prop.type.clean(value, proxy=self, fuzzy=fuzzy, format=format)
            self.unsafe_add(prop, value, cleaned=True)
        return None

    def unsafe_add(
        self,
        prop: Property,
        value: Optional[str],
        cleaned: bool = False,
        fuzzy: bool = False,
        format: Optional[str] = None,
    ) -> None:
        """A version of `add()` to be used only in type-checking code. This accepts
        only a single value, and performs input cleaning on the premise that the
        value is already valid unicode."""
        if not cleaned and value is not None:
            value = prop.type.clean_text(value, fuzzy=fuzzy, format=format, proxy=self)
        if value is not None:
            # Somewhat hacky: limit the maximum size of any particular
            # field to avoid overloading upstream aleph/elasticsearch.
            value_size = len(value)
            if prop.type.max_size is not None:
                if self._size + value_size > prop.type.max_size:
                    # msg = "[%s] too large. Rejecting additional values."
                    # log.warning(msg, prop.name)
                    return None
            self._size += value_size
            self._properties.setdefault(prop.name, set())
            self._properties[prop.name].add(value)
        return None

    def set(
        self,
        prop: P,
        values: Any,
        cleaned: bool = False,
        quiet: bool = False,
        fuzzy: bool = False,
        format: Optional[str] = None,
    ) -> None:
        """Replace the values of the property with the given value(s).

        :param prop: can be given as a name or an instance of
            :class:`~followthemoney.property.Property`.
        :param values: either a single value, or a list of values to be added.
        :param cleaned: should the data be normalised before adding it.
        :param quiet: a reference to an non-existent property will return
            an empty list instead of raising an error.
        """
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None:
            return
        self._properties.pop(prop_name, None)
        return self.add(
            prop, values, cleaned=cleaned, quiet=quiet, fuzzy=fuzzy, format=format
        )

    def pop(self, prop: P, quiet: bool = True) -> List[str]:
        """Remove all the values from the given property and return them.

        :param prop: can be given as a name or an instance of
            :class:`~followthemoney.property.Property`.
        :param quiet: a reference to an non-existent property will return
            an empty list instead of raising an error.
        :return: a list of values, possibly empty.
        """
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None or prop_name not in self._properties:
            return []
        return list(self._properties.pop(prop_name))

    def remove(self, prop: P, value: str, quiet: bool = True) -> None:
        """Remove a single value from the given property. If it is not there,
        no action takes place.

        :param prop: can be given as a name or an instance of
            :class:`~followthemoney.property.Property`.
        :param value: will not be cleaned before checking.
        :param quiet: a reference to an non-existent property will return
            an empty list instead of raising an error.
        """
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is not None and prop_name in self._properties:
            try:
                self._properties[prop_name].remove(value)
            except KeyError:
                pass

    def iterprops(self) -> List[Property]:
        """Iterate across all the properties for which a value is set in
        the proxy (but do not return their values)."""
        return [self.schema.properties[p] for p in self._properties.keys()]

    def itervalues(self) -> Generator[Tuple[Property, str], None, None]:
        """Iterate across all values in the proxy one by one, each given as a
        tuple of the property and the value."""
        for name, values in self._properties.items():
            prop = self.schema.properties[name]
            for value in values:
                yield (prop, value)

    def edgepairs(self) -> Generator[Tuple[str, str], None, None]:
        """Return all the possible pairs of values for the edge source and target if
        the schema allows for an edge representation of the entity."""
        if self.schema.source_prop is not None and self.schema.target_prop is not None:
            sources = self.get(self.schema.source_prop)
            targets = self.get(self.schema.target_prop)
            for (source, target) in product(sources, targets):
                yield (source, target)

    def get_type_values(
        self, type_: PropertyType, matchable: bool = False
    ) -> List[str]:
        """All values of a particular type associated with a the entity. For
        example, this lets you return all countries linked to an entity, rather
        than manually checking each property to see if it contains countries.

        :param type_: The type object to be searched.
        :param matchable: Whether to return only property values marked as matchable.
        """
        combined = set()
        for prop_name, values in self._properties.items():
            prop = self.schema.properties[prop_name]
            if matchable and not prop.matchable:
                continue
            if prop.type == type_:
                combined.update(values)
        return list(combined)

    @property
    def names(self) -> List[str]:
        """Get the set of all name-type values set of the entity."""
        return self.get_type_values(registry.name)

    @property
    def countries(self) -> List[str]:
        """Get the set of all country-type values set of the entity."""
        return self.get_type_values(registry.country)

    @property
    def temporal_start(self) -> Optional[Tuple[Property, str]]:
        """Get a date that can be used to represent the start of the entity in a timeline.
        If there are multiple possible dates, the earliest date is returned."""
        values = []

        for prop in self.schema.temporal_start_props:
            values += [(prop, value) for value in self.get(prop.name)]

        values.sort(key=lambda tuple: tuple[1])
        return next(iter(values), None)

    @property
    def temporal_end(self) -> Optional[Tuple[Property, str]]:
        """Get a date that can be used to represent the end of the entity in a timeline.
        If therer are multiple possible dates, the latest date is returned."""
        values = []

        for prop in self.schema.temporal_end_props:
            values += [(prop, value) for value in self.get(prop.name)]

        values.sort(reverse=True, key=lambda tuple: tuple[1])
        return next(iter(values), None)

    def get_type_inverted(self, matchable: bool = False) -> Dict[str, List[str]]:
        """Return all the values of the entity arranged into a mapping with the
        group name of their property type. These groups include ``countries``,
        ``addresses``, ``emails``, etc."""
        data: Dict[str, List[str]] = {}
        for group, type_ in registry.groups.items():
            values = self.get_type_values(type_, matchable=matchable)
            if len(values):
                data[group] = values
        return data

    def triples(self, qualified: bool = True) -> Generator[Triple, None, None]:
        """Serialise the entity into a set of RDF triple statements. The
        statements include the property values, an ``RDF#type`` definition
        that refers to the entity schema, and a ``SKOS#prefLabel`` with the
        entity caption."""
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
        """The user-facing label to be used for this entity. This checks a list
        of properties defined by the schema (caption) and returns the first
        available value. If no caption is available, return the schema label."""
        for prop in self.schema.caption:
            for value in self.get(prop):
                return value
        return self.schema.label

    @property
    def country_hints(self) -> Set[str]:
        """Some property types, such as phone numbers and IBAN codes imply a
        country that may be associated with the entity. This list can be used
        for a more generous matching approach than the actual country values."""
        countries = set(self.countries)
        if not len(countries):
            for (prop, value) in self.itervalues():
                hint = prop.type.country_hint(value)
                if hint is not None:
                    countries.add(hint)
        return countries

    @property
    def properties(self) -> Dict[str, List[str]]:
        """Return a mapping of the properties and set values of the entity."""
        return {p: list(vs) for p, vs in self._properties.items()}

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the proxy into a dictionary with the defined properties, ID,
        schema and any contextual values that were handed in initially. The resulting
        dictionary can be used to make a new proxy, and it is commonly written to disk
        or a database."""
        data = dict(self.context)
        data.update(
            {"id": self.id, "schema": self.schema.name, "properties": self.properties}
        )
        return data

    def to_full_dict(self, matchable: bool = False) -> Dict[str, Any]:
        """Return a serialised version of the entity with inverted type groups mixed
        in. See :meth:`~get_type_inverted`."""
        data = self.to_dict()
        data.update(self.get_type_inverted(matchable=matchable))
        return data

    def clone(self: E) -> E:
        """Make a deep copy of the current entity proxy."""
        return self.__class__.from_dict(self.schema.model, self.to_dict())

    def merge(self: E, other: E) -> E:
        """Merge another entity proxy into this one. This will try and find
        the common schema between both entities and then add all property
        values from the other entity into this one."""
        model = self.schema.model
        self.id = self.id or other.id
        try:
            self.schema = model.common_schema(self.schema, other.schema)
        except InvalidData as e:
            msg = "Cannot merge entities with id %s: %s"
            raise InvalidData(msg % (self.id, e))

        self.context = merge_context(self.context, other.context)
        for prop, values in other._properties.items():
            self.add(prop, values, cleaned=True, quiet=True)
        return self

    def __str__(self) -> str:
        return self.caption

    def __repr__(self) -> str:
        return "<E(%r,%r)>" % (self.id, str(self))

    def __len__(self) -> int:
        return self._size

    def __hash__(self) -> int:
        if not self.id:
            warnings.warn(
                "Taking the hash of an EntityProxy without an ID set results in undefined behaviour",
                RuntimeWarning,
            )
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        try:
            if self.id is None or other.id is None:
                warnings.warn(
                    "Comparing EntityProxys without an ID set results in undefined behaviour",
                    RuntimeWarning,
                )
            return bool(self.id == other.id)
        except AttributeError:
            return False

    @classmethod
    def from_dict(
        cls: Type[E],
        model: "Model",
        data: Dict[str, Any],
        cleaned: bool = True,
    ) -> E:
        """Instantiate a proxy based on the given model and serialised dictionary.

        Use :meth:`followthemoney.model.Model.get_proxy` instead."""
        return cls(model, data, cleaned=cleaned)
