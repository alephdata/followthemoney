from typing import Dict, List, Optional, Sequence, TYPE_CHECKING, cast
from banal import ensure_list, first
from normality import slugify
from normality.cleaning import collapse_spaces, strip_quotes
from fuzzywuzzy import fuzz  # type: ignore
from Levenshtein import setmedian  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen
from followthemoney.util import defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


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

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """Basic clean-up."""
        name = strip_quotes(text)
        return collapse_spaces(name)

    def pick(self, values: Sequence[str]) -> Optional[str]:
        """From a set of names, pick the most plausible user-facing one."""
        # Sort to get stable results when it's a coin toss:
        values = sorted(values)
        if not len(values):
            return None
        normalised = []
        lookup: Dict[str, List[str]] = {}
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
        if norm is None:
            return None
        forms = lookup.get(norm, [])
        if len(forms) <= 1:
            return first(forms)
        return cast(str, setmedian(forms))

    def _specificity(self, value: str) -> float:
        # TODO: insert artificial intelligence here.
        return dampen(3, 50, value)

    def compare(self, left: str, right: str) -> float:
        return cast(int, fuzz.WRatio(left, right)) / 100.0

    def node_id(self, value: str) -> Optional[str]:
        slug = slugify(value)
        if slug is None:
            return None
        return f"name:{slug}"
