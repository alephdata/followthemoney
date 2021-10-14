from itertools import product
from babel.core import Locale  # type: ignore
from banal import ensure_list
from normality import stringify
from typing import Any, Dict, Optional, Sequence, Callable, TYPE_CHECKING, TypedDict

from followthemoney.rdf import Literal, Identifier
from followthemoney.util import get_locale
from followthemoney.util import gettext, sanitize_text

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy

EnumValues = Dict[str, str]


class PropertyTypeToDict(TypedDict, total=False):
    label: str
    plural: str
    group: Optional[str]
    matchable: Optional[bool]
    pivot: Optional[bool]
    values: Optional[EnumValues]


class PropertyType(object):
    """Base class for all property types."""

    name: str = "any"
    """A machine-facing, variable safe name for the given type."""

    group: Optional[str] = None
    """Groups are used to invert all the properties of an entity that have a
    given  type into a single list before indexing them. This way, in Aleph,
    you can query for ``countries:gb`` instead of having to make a set of filters
    like ``properties.jurisdiction:gb OR properties.country:gb OR ...``."""

    label: str = "Any"
    """A name for this type to be shown to users."""

    plural: str = "Any"
    """A plural name for this type which can be used in appropriate places in
    a user interface."""

    matchable: bool = True
    """Matchable types allow properties to be compared with each other in order to
    assess entity similarity. While it makes sense to compare names, countries or
    phone numbers, the same isn't true for raw JSON blobs or descriptive text
    snippets."""

    pivot: bool = False
    """Pivot property types are like a stronger form of :attr:`~matchable` types:
    they will be used when value-based lookups are used to find commonalities
    between entities. For example, pivot typed-properties are used to show all the
    other entities that mention the same phone number, email address or name as the
    one currently seen by the user."""

    max_size: Optional[int] = None
    """Some types have overall size limitations in place in order to avoid generating
    entities that are very large (upstream ElasticSearch has a 100MB document limit).
    Once the total size of all properties of this type has exceed the given limit,
    an entity will refuse to add further values."""

    @property
    def docs(self) -> Optional[str]:
        return self.__doc__

    def validate(self, value: str) -> bool:
        """Returns a boolean to indicate if the given value is a valid instance of
        the type."""
        cleaned = self.clean(value)
        return cleaned is not None

    def clean(
        self,
        raw: Any,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """Create a clean version of a value of the type, suitable for storage
        in an entity proxy."""
        text = sanitize_text(raw)
        if text is None:
            return None
        return self.clean_text(text, fuzzy=fuzzy, format=format, proxy=proxy)

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """Specific types can apply their own cleaning routines here (this is called
        by ``clean`` after the value has been converted to a string and null values
        have been filtered)."""
        return text

    def join(self, values: Sequence[str]) -> str:
        """Helper function for converting multi-valued FtM data into formats that
        allow only a single value per field (e.g. CSV). This is not fully reversible
        and should be used as a last option."""
        values = ensure_list(values)
        return "; ".join(values)

    def _specificity(self, value: str) -> float:
        return 1.0

    def specificity(self, value: Optional[str]) -> float:
        """Return a score for how specific the given value is. This can be used as a
        weighting factor in entity comparisons in order to rate matching property
        values by how specific they are. For example: a longer address is considered
        to be more specific than a short one, a full date more specific than just a
        year number, etc."""
        if not self.matchable or value is None:
            return 0.0
        return self._specificity(value)

    def compare_safe(self, left: Optional[str], right: Optional[str]) -> float:
        """Compare, but support None values on either side of the comparison."""
        left = stringify(left)
        right = stringify(right)
        if left is None or right is None:
            return 0.0
        return self.compare(left, right)

    def compare(self, left: str, right: str) -> float:
        """Comparisons are a float between 0 and 1. They can assume
        that the given data is cleaned, but not normalised."""
        if left.lower() == right.lower():
            return 1.0 * self.specificity(left)
        return 0.0

    def compare_sets(
        self,
        left: Sequence[str],
        right: Sequence[str],
        func: Callable[[Sequence[float]], float] = max,
    ) -> float:
        """Compare two sets of values and select the highest-scored result."""
        results = []
        for (l, r) in product(ensure_list(left), ensure_list(right)):
            results.append(self.compare(l, r))
        if not len(results):
            return 0.0
        return func(results)

    def country_hint(self, value: str) -> Optional[str]:
        """Determine if the given value allows us to infer a country that it may
        be related to (e.g. using a country prefix on a phone number or IBAN)."""
        return None

    def rdf(self, value: str) -> Identifier:
        """Return an RDF term to represent the given value - either a string
        literal, or a URI reference."""
        return Literal(value)

    def pick(self, values: Sequence[str]) -> Optional[str]:
        """Pick the best value to show to the user."""
        raise NotImplemented

    def node_id(self, value: str) -> Optional[str]:
        """Return an ID suitable to identify this entity as a typed node in a
        graph representation of some FtM data. It's usually the same as the the
        RDF form."""
        return str(self.rdf(value))

    def node_id_safe(self, value: Optional[str]) -> Optional[str]:
        """Wrapper for node_id to handle None values."""
        if value is None:
            return None
        return self.node_id(value)

    def caption(self, value: str) -> Optional[str]:
        """Return a label for the given property value. This is often the same as the
        value, but for types like countries or languages, it would return the label,
        while other values like phone numbers can be formatted to be nicer to read."""
        return value

    def to_dict(self) -> PropertyTypeToDict:
        """Return a serialisable description of this data type."""
        data: PropertyTypeToDict = {
            "label": gettext(self.label),
            "plural": gettext(self.plural),
        }
        if self.group:
            data["group"] = self.group
        if self.matchable:
            data["matchable"] = True
        if self.pivot:
            data["pivot"] = True
        return data

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PropertyType):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.name}>"


class EnumType(PropertyType):
    """Enumerated type properties are used for types which have a defined set
    of possible values, like languages and countries."""

    def __init__(self) -> None:
        self._names: Dict[Locale, EnumValues] = {}
        self.codes = set(self.names.keys())

    def _locale_names(self, locale: str) -> EnumValues:
        return {}

    @property
    def names(self) -> EnumValues:
        """Return a mapping from property values to their labels in the current
        locale."""
        locale = get_locale()
        if locale not in self._names:
            self._names[locale] = self._locale_names(locale)
        return self._names[locale]

    def validate(self, value: str) -> bool:
        """Make sure that the given code value is one of the supported set."""
        if value is None:
            return False
        return str(value).lower().strip() in self.codes

    def clean_text(
        self,
        code: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """All code values are cleaned to be lowercase and trailing whitespace is
        removed."""
        code = code.lower().strip()
        if code not in self.codes:
            return None
        return code

    def caption(self, value: str) -> str:
        """Given a code value, return the label that should be shown to a user."""
        return self.names.get(value, value)

    def to_dict(self) -> PropertyTypeToDict:
        """When serialising the model to JSON, include all values."""
        data = super(EnumType, self).to_dict()
        data["values"] = self.names
        return data
