from banal import ensure_list, first
from normality import slugify
from normality.cleaning import collapse_spaces, strip_quotes
from fuzzywuzzy import fuzz  # type: ignore
from Levenshtein import setmedian  # type: ignore

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
        """From a set of names, pick the most plausible user-facing one."""
        # Sort to get stable results when it's a coin toss:
        values = sorted(ensure_list(values))
        if not len(values):
            return None
        normalised = []
        lookup = {}
        # We're doing this in two stages, to avoid name forms with varied casing
        # (e.g. Smith vs. SMITH) are counted as widly different, leading to
        # implausible median outcomes.
        for value in values:
            norm = slugify(value, sep=" ")
            if norm is None:
                continue
            normalised.append(norm)
            lookup.setdefault(norm, [])
            lookup[norm].append(value)

        norm = setmedian(normalised)
        forms = lookup.get(norm, [])
        if len(forms) <= 1:
            return first(forms)
        return setmedian(forms)

    def _specificity(self, value):
        # TODO: insert artificial intelligence here.
        return dampen(3, 50, value)

    def compare(self, left, right):
        return fuzz.WRatio(left, right) / 100.0

    def node_id(self, value):
        return "name:%s" % slugify(value)
