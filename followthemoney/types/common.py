from itertools import product
from rdflib import Literal  # type: ignore
from banal import ensure_list
from normality import stringify
from typing import Any, Optional

from followthemoney.util import get_locale
from followthemoney.util import gettext, sanitize_text


class PropertyType(object):
    """Base class for all types."""

    name: Optional[str] = None
    group: Optional[str] = None
    label: Optional[str] = None
    plural: Optional[str] = None
    matchable: bool = True
    pivot: bool = False
    max_size: Optional[int] = None

    def validate(self, text: Any, **kwargs):
        """Returns a boolean to indicate if this is a valid instance of
        the type."""
        cleaned = self.clean(text, **kwargs)
        return cleaned is not None

    def clean(self, text: Any, **kwargs):
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        text = sanitize_text(text)
        if text is not None:
            return self.clean_text(text, **kwargs)

    def clean_text(self, text: Optional[str], **kwargs):
        return text

    def join(self, values):
        values = ensure_list(values)
        return "; ".join(values)

    def _specificity(self, value):
        return 1.0

    def specificity(self, value):
        if not self.matchable or value is None:
            return 0.0
        return self._specificity(value)

    def compare_safe(self, left, right):
        left = stringify(left)
        right = stringify(right)
        if left is None or right is None:
            return 0.0
        return self.compare(left, right)

    def compare(self, left, right):
        """Comparisons are a float between 0 and 1. They can assume
        that the given data is cleaned, but not normalised."""
        if left.lower() == right.lower():
            return 1.0 * self.specificity(left)
        return 0.0

    def compare_sets(self, left, right, func=max):
        """Compare two sets of values and select a specific result."""
        results = []
        for (l, r) in product(ensure_list(left), ensure_list(right)):
            results.append(self.compare_safe(l, r))
        if not len(results):
            return 0
        return func(results)

    def country_hint(self, value):
        """Determine if the given value allows us to infer a country
        that it may be related to."""
        return None

    def rdf(self, value):
        return Literal(value)

    def node_id(self, value):
        return str(self.rdf(value))

    def node_id_safe(self, value):
        if value is not None:
            return self.node_id(value)

    def caption(self, value):
        return value

    def to_dict(self):
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
    def __init__(self, *args):
        self._names = {}
        self.codes = set(self.names.keys())

    def _locale_names(self, locale):
        return {}

    @property
    def names(self):
        locale = get_locale()
        if locale not in self._names:
            self._names[locale] = self._locale_names(locale)
        return self._names[locale]

    def validate(self, code, **kwargs):
        code = sanitize_text(code)
        if code is None:
            return False
        return code.lower() in self.codes

    def clean_text(self, code, guess=False, **kwargs):
        code = code.lower().strip()
        if code in self.codes:
            return code

    def caption(self, value):
        return self.names.get(value, value)

    def to_dict(self):
        data = super(EnumType, self).to_dict()
        data["values"] = self.names
        return data
