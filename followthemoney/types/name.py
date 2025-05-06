from typing import TYPE_CHECKING, Optional, Sequence
from normality import slugify
from normality.cleaning import collapse_spaces, strip_quotes
from rigour.env import MAX_NAME_LENGTH
from rigour.names import pick_name, tokenize_name
from rigour.text.distance import levenshtein_similarity

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
    max_length = MAX_NAME_LENGTH

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
        return pick_name(list(values))

    def _specificity(self, value: str) -> float:
        # TODO: insert artificial intelligence here.
        return dampen(3, 50, value)

    def compare(self, left: str, right: str) -> float:
        """Compare two names for similarity."""
        left_clean = " ".join(tokenize_name(left.lower()))
        right_clean = " ".join(tokenize_name(right.lower()))
        if not len(left_clean) or not len(right_clean):
            return 0.0
        return levenshtein_similarity(
            left_clean,
            right_clean,
            max_length=self.max_length,
        )

    def node_id(self, value: str) -> Optional[str]:
        slug = slugify(value)
        if slug is None:
            return None
        return f"name:{slug}"
