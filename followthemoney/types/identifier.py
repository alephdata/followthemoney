import re

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen, shortest
from followthemoney.util import defer as _


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

    def clean_compare(self, value):
        # TODO: should this be used for normalization?
        value = self.COMPARE_CLEAN.sub("", value)
        return value.lower()

    def compare(self, left, right):
        left = self.clean_compare(left)
        right = self.clean_compare(right)
        specificity = self.specificity(shortest(left, right))
        if left == right:
            return specificity
        if left in right or right in left:
            return 0.8 * specificity
        return 0

    def _specificity(self, value):
        return dampen(6, 10, value)

    def node_id(self, value):
        return "id:%s" % value
