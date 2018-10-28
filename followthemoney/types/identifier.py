import re
from normality import normalize

from followthemoney.types.common import PropertyType


class IdentifierType(PropertyType):
    """Used for registration numbers, codes etc."""
    COMPARE_CLEAN = re.compile('[\W_]+')
    name = 'identifier'
    group = 'identifiers'
    strong = False

    def normalize(self, text, **kwargs):
        """Normalize for comparison."""
        ids = super(IdentifierType, self).normalize(text, **kwargs)
        return [normalize(i) for i in ids]

    def clean_compare(self, value):
        # TODO: should this be used for normalization?
        value = self.COMPARE_CLEAN.sub('', value)
        return value.lower()

    def compare(self, left, right):
        left = self.clean_compare(left)
        right = self.clean_compare(right)
        if left == right:
            return .9
        if left in right:
            return .7
        if right in left:
            return .7
        return 0
