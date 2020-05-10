from itertools import product
from rdflib import Literal  # type: ignore
from banal import ensure_list
from normality import stringify  # type: ignore

from followthemoney.util import get_locale
from followthemoney.util import gettext, sanitize_text

from typing import Optional, List, Any, Dict, Callable, Iterable


class PropertyType(object):
    """Base class for all types."""
    name: str
    group: Optional[str] = None
    label: Optional[str] = None
    plural: Optional[str] = None
    matchable: bool = True
    pivot: bool = False
    max_size: Optional[int] = None

    def validate(self, text: str, **kwargs) -> bool:
        """Returns a boolean to indicate if this is a valid instance of
        the type."""
        cleaned = self.clean(text, **kwargs)
        return cleaned is not None

    def clean(self, text: Optional[str], **kwargs) -> Optional[str]:
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        s_text = sanitize_text(text)
        if s_text is not None:
            return self.clean_text(s_text, **kwargs)
        return None

    def clean_text(self, text: str, **kwargs) -> Optional[str]:
        return text

    def normalize(self, text, cleaned: bool = False, **kwargs) -> List:
        """Create a represenation ideal for comparisons, but not to be
        shown to the user."""
        if not cleaned:
            text = self.clean(text, **kwargs)
        return ensure_list(text)

    def normalize_set(self, items, **kwargs) -> List:
        """Utility to normalize a whole set of values and get unique
        values."""
        values = set()
        for item in ensure_list(items):
            values.update(self.normalize(item, **kwargs))
        return list(values)

    def join(self, values: Iterable[Any]) -> str:
        values = ensure_list(values)
        return '; '.join(values)

    def _specificity(self, value: str) -> float:
        return 1.0

    def specificity(self, value: Optional[str]) -> float:
        if not self.matchable or value is None:
            return 0.0
        return self._specificity(value)

    def compare_safe(self, left: Any, right: Any) -> float:
        left_string = stringify(left)
        right_string = stringify(right)
        if left_string is None or right_string is None:
            return 0.0
        return self.compare(left_string, right_string)

    def compare(self, left: str, right: str) -> float:
        """Comparisons are a float between 0 and 1. They can assume
        that the given data is cleaned, but not normalised."""
        if left.lower() == right.lower():
            return 1.0 * self.specificity(left)
        return 0.0

    def compare_sets(self, left: List, right: List,
                     func: Callable[[List], float] = max) -> float:
        """Compare two sets of values and select a specific result."""
        results: List[float] = []
        for (l, r) in product(ensure_list(left), ensure_list(right)):
            results.append(self.compare_safe(l, r))
        if not len(results):
            return 0
        return func(results)

    def country_hint(self, value: str) -> Optional[str]:
        """Determine if the given value allows us to infer a country
        that it may be related to."""
        return None

    def values_size(self, values: Iterable) -> int:
        return sum((len(v) for v in ensure_list(values)))

    def rdf(self, value) -> Literal:
        return Literal(value)

    def node_id(self, value) -> str:
        return str(self.rdf(value))

    def node_id_safe(self, value) -> Optional[str]:
        if value is not None:
            return self.node_id(value)
        return None

    def caption(self, value: str) -> str:
        return value

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'label': gettext(self.label),
            'plural': gettext(self.plural)
        }
        if self.group:
            data['group'] = self.group
        if self.matchable:
            data['matchable'] = True
        if self.pivot:
            data['pivot'] = True
        return data

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s()>' % type(self).__name__


class EnumType(PropertyType):

    def __init__(self, *args):
        self._names = {}

    def _locale_names(self, locale) -> Dict:
        return {}

    @property
    def names(self) -> Dict:
        locale = get_locale()
        if locale not in self._names:
            self._names[locale] = self._locale_names(locale)
        return self._names[locale]

    @property
    def codes(self):
        return self.names.keys()

    def validate(self, code: str, **kwargs) -> bool:  # type: ignore[override] # noqa
        s_code = sanitize_text(code)
        if s_code is None:
            return False
        return s_code.lower() in self.codes

    def clean_text(self, code: str, guess: bool = False, **kwargs
                   ) -> Optional[str]:  # type: ignore[override] # noqa
        code = code.lower().strip()
        if code in self.codes:
            return code
        return None

    def caption(self, value):
        return self.names.get(value, value)

    def to_dict(self) -> Dict:
        data = super(EnumType, self).to_dict()
        data['values'] = self.names
        return data
