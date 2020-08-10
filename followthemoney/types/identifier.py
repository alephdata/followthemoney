import re

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen, shortest
from followthemoney.util import defer as _


class IdentifierType(PropertyType):
    """Used for registration numbers, codes etc."""

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
        return dampen(4, 10, value)

    def node_id(self, value):
        return "id:%s" % value
