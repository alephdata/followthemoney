from normality.cleaning import collapse_spaces, strip_quotes

from followthemoney.types.common import PropertyType


class NameType(PropertyType):

    def clean_text(self, name, **kwargs):
        """Basic clean-up."""
        name = strip_quotes(name)
        name = collapse_spaces(name)
        return name
