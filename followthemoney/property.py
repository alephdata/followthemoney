from banal import is_mapping, as_bool
from typing import TYPE_CHECKING, cast, Any, List, Optional, TypedDict

from followthemoney.exc import InvalidModel
from followthemoney.types import registry
from followthemoney.rdf import NS, URIRef
from followthemoney.util import gettext, get_entity_id

if TYPE_CHECKING:
    from followthemoney.schema import Schema


class ReverseSpec(TypedDict, total=False):
    name: str
    label: Optional[str]
    hidden: Optional[bool]


class PropertyDict(TypedDict, total=False):
    label: Optional[str]
    description: Optional[str]
    type: Optional[str]
    hidden: Optional[bool]
    matchable: Optional[bool]
    # stub: Optional[bool]
    rdf: Optional[str]
    range: Optional[str]


class PropertySpec(PropertyDict):
    reverse: ReverseSpec


class PropertyToDict(PropertyDict, total=False):
    name: str
    qname: str
    reverse: Optional[str]
    stub: Optional[bool]


class Property:
    """A definition of a value-holding field on a schema. Properties define
    the field type and other possible constraints. They also serve as entity
    to entity references."""

    __slots__ = (
        "model",
        "schema",
        "name",
        "qname",
        "_label",
        "_hash",
        "_description",
        "hidden",
        "type",
        "matchable",
        "_range",
        "range",
        "stub",
        "_reverse",
        "reverse",
        "uri",
    )

    #: Invalid property names.
    RESERVED = ["id", "caption", "schema", "schemata"]

    def __init__(self, schema: "Schema", name: str, data: PropertySpec) -> None:
        self.model = schema.model

        #: The schema which the property is defined for. This is always the
        #: most abstract schema that has this property, not the possible
        #: child schemata that inherit it.
        self.schema = schema

        #: Machine-readable name for this property.
        self.name = name

        #: Qualified property name, which also includes the schema name.
        self.qname = "%s:%s" % (schema.name, self.name)
        if self.name in self.RESERVED:
            raise InvalidModel("Reserved name: %s" % self.name)

        self._hash = hash("<Property(%r)>" % self.qname)

        self._label = data.get("label", name)
        self._description = data.get("description")

        #: This property should not be shown or mentioned in the user interface.
        self.hidden = as_bool(data.get("hidden", False))

        type_ = data.get("type", "string")
        if type_ is None or type_ not in registry.named:
            raise InvalidModel("Invalid type: %s" % type_)

        #: The data type for this property.
        self.type = registry[type_]

        #: Whether this property should be used for matching and cross-referencing.
        _matchable = data.get("matchable")
        if _matchable is not None:
            self.matchable = as_bool(data.get("matchable"))
        else:
            self.matchable = self.type.matchable

        #: If the property is of type ``entity``, the set of valid schema to be added
        #: in this property can be constrained. For example, an asset can be owned,
        #: but a person cannot be owned.
        self._range = data.get("range")
        self.range: Optional["Schema"] = None

        #: When a property points to another schema, a reverse property is added for
        #: various administrative reasons. These properties are, however, not real
        #: and cannot be written to. That's why they are marked as stubs and adding
        #: values to them will raise an exception.
        self.stub: Optional[bool] = False

        #: When a property points to another schema, a stub reverse property is
        #: added as a place to store metadata to help display the link in inverted
        #: views.
        self._reverse = data.get("reverse")
        self.reverse: Optional["Property"] = None

        #: RDF term for this property (i.e. the predicate URI).
        self.uri = URIRef(cast(str, data.get("rdf", NS[self.qname])))

    def generate(self) -> None:
        """Setup method used when loading the model in order to build out the reverse
        links of the property."""
        self.model.properties.add(self)

        if self.type == registry.entity:
            if self.range is None and self._range is not None:
                self.range = self.model.get(self._range)

            if self.reverse is None and self.range and self._reverse:
                if not is_mapping(self._reverse):
                    raise InvalidModel("Invalid reverse: %s" % self)
                self.reverse = self.range._add_reverse(self._reverse, self)

    @property
    def label(self) -> str:
        """User-facing title for this property."""
        return gettext(self._label)

    @property
    def description(self) -> str:
        """A longer description of the semantics of this property."""
        return gettext(self._description)

    def specificity(self, value: str) -> float:
        """Return a measure of how precise the given value is."""
        if not self.matchable:
            return 0.0
        return self.type.specificity(value)

    def validate(self, data: List[Any]) -> Optional[str]:
        """Validate that the data should be stored.

        Since the types system doesn't really have validation, this currently
        tries to normalize the value to see if it passes strict parsing.
        """
        values = []
        for val in data:
            if self.stub:
                return gettext("Property cannot be written")
            val = get_entity_id(val)
            if not self.type.validate(val):
                return gettext("Invalid value")
            if val is not None:
                values.append(val)
        return None

    def __eq__(self, other: Any) -> bool:
        return self._hash == hash(other)

    def __hash__(self) -> int:
        return self._hash

    def to_dict(self) -> PropertyToDict:
        """Return property metadata in a serializable form."""
        data: PropertyToDict = {
            "name": self.name,
            "qname": self.qname,
            "label": self.label,
            "type": self.type.name,
        }
        if self.description:
            data["description"] = self.description
        if self.stub:
            data["stub"] = True
        if self.matchable:
            data["matchable"] = True
        if self.hidden:
            data["hidden"] = True
        if self.range is not None:
            data["range"] = self.range.name
        if self.reverse is not None:
            data["reverse"] = self.reverse.name
        return data

    def __repr__(self) -> str:
        return "<Property(%r)>" % self.qname

    def __str__(self) -> str:
        return self.qname
