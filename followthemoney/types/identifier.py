from normality import normalize

from followthemoney.types.common import PropertyType


class IdentifierType(PropertyType):
    """Used for registration numbers, codes etc."""
    name = 'identifier'
    group = 'identifiers'
    prefix = 'ident'

    def normalize(self, text, **kwargs):
        """Normalize for comparison."""
        ids = super(IdentifierType, self).normalize(text, **kwargs)
        return [normalize(i) for i in ids]
