import re
from typing import Optional, TYPE_CHECKING
from rigour.ids import get_identifier_format_names, get_identifier_format

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen, shortest, longest
from followthemoney.util import defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class IdentifierType(PropertyType):
    """Used for registration numbers and other codes assigned by an authority
    to identify an entity. This might include tax identifiers and statistical
    codes.

    Since identifiers are high-value criteria when comparing two entities, numbers
    should only be modelled as identifiers if they are long enough to be meaningful.
    Four- or five-digit industry classifiers create more noise than value."""

    COMPARE_CLEAN = re.compile(r"[\W_]+")
    name = "identifier"
    group = "identifiers"
    label = _("Identifier")
    plural = _("Identifiers")
    matchable = True
    pivot = True
    max_length = 64

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        if format in get_identifier_format_names():
            format_ = get_identifier_format(format)
            return format_.normalize(text)
        return text

    def clean_compare(self, value: str) -> str:
        # TODO: should this be used for normalization?
        value = self.COMPARE_CLEAN.sub("", value)
        return value.lower()

    def compare(self, left: str, right: str) -> float:
        left = self.clean_compare(left)
        right = self.clean_compare(right)
        if left == right:
            return 1.0
        elif left in right or right in left:
            return len(shortest(left, right)) / len(longest(left, right))
        return 0.0

    def _specificity(self, value: str) -> float:
        return dampen(4, 10, value)

    def node_id(self, value: str) -> str:
        return f"id:{value}"
