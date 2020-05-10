import re
from normality import normalize  # type: ignore
from typing import List

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen, shortest
from followthemoney.util import defer as _


class IdentifierType(PropertyType):
    """Used for registration numbers, codes etc."""
    COMPARE_CLEAN = re.compile(r'[\W_]+')
    name: str = 'identifier'
    group: str = 'identifiers'
    label: str = _('Identifier')
    plural: str = _('Identifiers')
    matchable: bool = True
    pivot: bool = True

    def normalize(self, text, cleaned: bool = False, **kwargs) -> List:
        """Normalize for comparison."""
        ids = super(IdentifierType, self).normalize(text, **kwargs)
        return [normalize(i) for i in ids]

    def clean_compare(self, value: str) -> str:
        # TODO: should this be used for normalization?
        value = self.COMPARE_CLEAN.sub('', value)
        return value.lower()

    def compare(self, left: str, right: str) -> float:
        left = self.clean_compare(left)
        right = self.clean_compare(right)
        specificity = self.specificity(shortest(left, right))
        if left == right:
            return specificity
        if left in right or right in left:
            return .8 * specificity
        return 0

    def _specificity(self, value: str) -> float:
        return dampen(4, 10, value)

    def node_id(self, value: str) -> str:
        return 'id:%s' % value
