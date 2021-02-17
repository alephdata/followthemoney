from banal import ensure_list, first
from normality import slugify
from normality.cleaning import collapse_spaces, strip_quotes
from Levenshtein import jaro_winkler, setmedian  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen, sanitize_text
from followthemoney.util import defer as _


class NameType(PropertyType):
    """A name used for a person or company. This is assumed to be as complete
    a name as available - when a first name, family name or patronymic are given
    separately, these are stored to string-type properties instead.

    No validation rules apply, and things having multiple names must be considered
    a perfectly ordinary case."""

    name = "name"
    group = "names"
    label = _("Name")
    plural = _("Names")
    matchable = True
    pivot = True

    def clean_text(self, name, **kwargs):
        """Basic clean-up."""
        name = strip_quotes(name)
        return collapse_spaces(name)

    def pick(self, values):
        values = [sanitize_text(v) for v in ensure_list(values)]
        values = [v for v in values if v is not None]
        if len(values) <= 1:
            return first(values)
        return setmedian(sorted(values))

    def _specificity(self, value):
        # TODO: insert artificial intelligence here.
        return dampen(3, 50, value)

    def compare(self, left, right):
        return jaro_winkler(left, right)

    def node_id(self, value):
        return "name:%s" % slugify(value)
