from Levenshtein import jaro_winkler
from normality.cleaning import collapse_spaces, strip_quotes

from followthemoney.types.common import PropertyType
from followthemoney.util import dampen


class NameType(PropertyType):
    name = 'name'
    group = 'names'

    def clean_text(self, name, **kwargs):
        """Basic clean-up."""
        name = strip_quotes(name)
        name = collapse_spaces(name)
        return name

    def specificity(self, value):
        # TODO: insert artificial intelligence here.
        return dampen(3, 50, value) * .8

    def compare(self, left, right):
        return jaro_winkler(left, right)
