from itertools import product
from rdflib import Literal  # type: ignore
from rdflib.term import Identifier  # type: ignore
from banal import ensure_list
from normality import stringify
from typing import Any, Dict, Optional, Sequence, Callable

from followthemoney.util import get_locale
from followthemoney.util import gettext, sanitize_text


class PropertyType(object):
    """Base class for all property types."""

    name: str = "any"
    """A machine-facing, variable safe name for the given type."""

    group: Optional[str] = None
    """Groups are used to invert all the properties of an entity that have a
    given  type into a single list before indexing them. This way, in Aleph,
    you can query for ``countries:gb`` instead of having to make a set of filters
    like ``properties.jurisdiction:gb OR properties.country:gb OR ...``."""

    label: Optional[str] = None
    """A name for this type to be shown to users."""

    plural: Optional[str] = None
    """A plural name for this type which can be used in appropriate places in
    a user interface."""

    matchable: bool = True
    """Matchable types allow properties to be compared with each other in order to
    assess entity similarity. While it makes sense to compare names, countries or
    phone numbers, the same isn't true for raw JSON blobs or long text snippets."""

    pivot: bool = False
    """Pivot property types are like a stronger form of matchable types: they will
    be used by default when value-based lookups are used to find commonalities
    between entities. This includes generating graph pseudo-nodes, and the
    `Mentions` functionality in the Aleph user interface."""

    max_size: Optional[int] = None
    """Some types have overall size limitations in place in order to avoid generating
    entities that are very large (upstream ElasticSearch has a 100MB document limit).
    Once the total size of all properties of this type has exceed the given limit,
    an entity will refuse to add further values."""

    @property
    def docs(self) -> Optional[str]:
        return self.__doc__

    def validate(self, text: Any, **kwargs) -> bool:
        """Returns a boolean to indicate if the given value is a valid instance of
        the type."""
        cleaned = self.clean(text, **kwargs)
        return cleaned is not None

    def clean(self, text: Any, **kwargs) -> Optional[str]:
        """Create a clean version of a value of the type, suitable for storage
        in an entity proxy."""
        text = sanitize_text(text)
        if text is None:
            return None
        return self.clean_text(text, **kwargs)

    def clean_text(self, text: str, **kwargs) -> Optional[str]:
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
        l: str = ""
        r: str = ""
        for (l, r) in product(ensure_list(left), ensure_list(right)):
            results.append(self.compare_safe(l, r))
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

    def node_id(self, value: str) -> str:
        """Return an ID suitable to identify this entity as a typed node in a
        graph representation of some FtM data. It's usually the same as the the
        RDF form."""
        return str(self.rdf(value))

    def node_id_safe(self, value: Optional[str]) -> Optional[str]:
        """Wrapper for node_id to handle None values."""
        if value is None:
            return None
        return self.node_id(value)

    def caption(self, value: str) -> str:
        """Return a label for the given property value. This is often the same as the
        value, but for types like countries or languages, it would return the label,
        while other values like phone numbers can be formatted to be nicer to read."""
        return value

    def to_dict(self) -> Dict[str, Any]:
        """Return a serialisable description of this data type."""
        data = {"label": gettext(self.label), "plural": gettext(self.plural)}
        if self.group:
            data["group"] = self.group
        if self.matchable:
            data["matchable"] = True
        if self.pivot:
            data["pivot"] = True
        return data

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s()>" % type(self).__name__


class EnumType(PropertyType):
    """Enumerated type properties are used for types which have a defined set
    of possible values, like languages and countries."""

    def __init__(self, *args):
        self._names = {}
        self.codes = set(self.names.keys())

    def _locale_names(self, locale):
        return {}

    @property
    def names(self):
        """Return a mapping from property values to their labels in the current
        locale."""
        locale = get_locale()
        if locale not in self._names:
            self._names[locale] = self._locale_names(locale)
        return self._names[locale]

    def validate(self, code, **kwargs):
        """Make sure that the given code value is one of the supported set."""
        code = sanitize_text(code)
        if code is None:
            return False
        return code.lower() in self.codes

    def clean_text(self, code, guess=False, **kwargs):
        """All code values are cleaned to be lowercase and trailing whitespace is
        removed."""
        code = code.lower().strip()
        if code in self.codes:
            return code

    def caption(self, value):
        """Given a code value, return the label that should be shown to a user."""
        return self.names.get(value, value)

    def to_dict(self):
        """When serialising the model to JSON, include all values."""
        data = super(EnumType, self).to_dict()
        data["values"] = self.names
        return data
