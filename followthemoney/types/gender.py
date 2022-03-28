from typing import Optional, TYPE_CHECKING
from babel.core import Locale  # type: ignore

from followthemoney.types.common import EnumType, EnumValues
from followthemoney.rdf import URIRef, Identifier
from followthemoney.util import gettext, defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class GenderType(EnumType):
    """A human gender. This is not meant to be a comprehensive model of
    the social realities of gender but a way to capture data from (mostly)
    government databases and represent it in a way that can be used by
    structured tools. I'm not sure this justifies the simplification."""

    name = "gender"
    group = "genders"
    label = _("Gender")
    plural = _("Genders")
    matchable = False

    def _locale_names(self, locale: Locale) -> EnumValues:
        return {
            "male": gettext("male"),
            "female": gettext("female"),
            "other": gettext("other"),
        }

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        code = text.lower().strip()
        if code not in self.codes:
            return None
        return code

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"gender:{value}")
