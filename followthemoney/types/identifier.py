from normality import normalize

from followthemoney.types.common import PropertyType


class IdentifierType(PropertyType):
    """Used for registration numbers, codes etc."""

    def normalize(self, text, **kwargs):
        """Normalize for comparison."""
        identifiers = []
        for ident in super(IdentifierType, self).normalize(text, **kwargs):
            identifiers.append(normalize(ident))
        return identifiers
