from typing import Optional, TYPE_CHECKING
from babel.core import Locale

from followthemoney.types.common import EnumType, EnumValues
from followthemoney.rdf import URIRef, Identifier
from followthemoney.util import gettext, defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class OccupancyStatus(EnumType):
    """The status of occupation of the position as of the last update
    of data."""

    ACTIVE = "active"
    ENDED = "ended"

    LOOKUP = {}

    name = "occupancy_status"
    group = "occupancy_statuses"
    label = _("Occupancy status")
    plural = _("Occupancy statuses")
    matchable = False

    def _locale_names(self, locale: Locale) -> EnumValues:
        return {
            self.ACTIVE: gettext("active"),
            self.ENDED: gettext("ended"),
        }

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        code = text.lower().strip()
        code = self.LOOKUP.get(code, code)
        if code not in self.codes:
            return None
        return code

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"occupancy_status:{value}")
