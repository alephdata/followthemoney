from typing import Iterable

from banal import ensure_list, first
from normality import slugify  # type: ignore
from Levenshtein import jaro_winkler, setmedian  # type: ignore
from normality.cleaning import collapse_spaces, strip_quotes  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen, sanitize_text
from followthemoney.util import defer as _


class NameType(PropertyType):
    name: str = 'name'
    group: str = 'names'
    label: str = _('Name')
    plural: str = _('Names')
    matchable: bool = True
    pivot: bool = True

    def clean_text(self, name: str, **kwargs) -> str:  # type: ignore[override] # noqa
        """Basic clean-up."""
        name = strip_quotes(name)
        name = collapse_spaces(name)
        return name

    def pick(self, values: Iterable) -> str:
        values = [sanitize_text(v) for v in ensure_list(values)]
        values = [v for v in values if v is not None]
        if len(values) <= 1:
            return first(values)
        return setmedian(sorted(values))

    def _specificity(self, value) -> float:
        # TODO: insert artificial intelligence here.
        # NOTE: You sure? It's already pretty good.
        return dampen(3, 50, value)

    def compare(self, left: str, right: str) -> float:
        return jaro_winkler(left, right)

    def node_id(self, value: str) -> str:
        return 'name:%s' % slugify(value)
