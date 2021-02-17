from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import MEGABYTE


class StringType(PropertyType):
    """A simple string property with no additional semantics."""

    name = "string"
    label = _("Label")
    plural = _("Labels")
    matchable = False

    def node_id(self, value):
        return None


class TextType(StringType):
    """Longer text fragments, such as descriptions or document text. Unlike
    string properties, it might make sense to treat properties of this type as
    full-text search material."""

    name = "text"
    label = _("Text")
    plural = _("Texts")
    max_size = 30 * MEGABYTE


class HTMLType(StringType):
    """Properties that contain raw hypertext markup (HTML).

    User interfaces rendering properties of this type need to take extreme
    care not to allow attacks such as cross-site scripting. It is recommended
    to perform server-side sanitisation, or to not render this property at all.
    """

    name = "html"
    label = _("HTML")
    plural = _("HTMLs")
    max_size = 30 * MEGABYTE
