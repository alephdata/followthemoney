from itertools import product
from rdflib import Literal
from banal import ensure_list
from normality import stringify

from followthemoney.util import gettext


class PropertyType(object):
    """Base class for all types."""
    name = None
    group = None
    label = None
    plural = None
    matchable = True
    max_size = None

    def validate(self, text, **kwargs):
        """Returns a boolean to indicate if this is a valid instance of
        the type."""
        cleaned = self.clean(text, **kwargs)
        return cleaned is not None

    def clean(self, text, **kwargs):
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        text = stringify(text)
        if text is not None:
            return self.clean_text(text, **kwargs)

    def clean_text(self, text, **kwargs):
        return text

    def normalize(self, text, cleaned=False, **kwargs):
        """Create a represenation ideal for comparisons, but not to be
        shown to the user."""
        if not cleaned:
            text = self.clean(text, **kwargs)
        return ensure_list(text)

    def normalize_set(self, items, **kwargs):
        """Utility to normalize a whole set of values and get unique
        values."""
        values = set()
        for item in ensure_list(items):
            values.update(self.normalize(item, **kwargs))
        return list(values)

    def join(self, values):
        values = ensure_list(values)
        return '; '.join(values)

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

    def values_size(self, values):
        return sum((len(v) for v in ensure_list(values)))

    def rdf(self, value):
        return Literal(value)

    def to_dict(self):
        data = {
            'label': gettext(self.label),
            'plural': gettext(self.plural)
        }
        if self.group:
            data['group'] = self.group
        if self.matchable:
            data['matchable'] = True
        return data

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s()>' % type(self).__name__
