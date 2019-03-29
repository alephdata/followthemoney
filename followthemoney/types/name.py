from Levenshtein import jaro_winkler
from normality.cleaning import collapse_spaces, strip_quotes

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import dampen


class NameType(PropertyType):
    name = 'name'
    group = 'names'
    label = _('Name')
    plural = _('Names')
    matchable = True

    def clean_text(self, name, **kwargs):
        """Basic clean-up."""
        name = strip_quotes(name)
        name = collapse_spaces(name)
        return name

    def _specificity(self, value):
        # TODO: insert artificial intelligence here.
        return dampen(3, 50, value)

    def compare(self, left, right):
        return jaro_winkler(left, right)
