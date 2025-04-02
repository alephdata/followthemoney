import countrynames
from typing import Optional, TYPE_CHECKING
from babel.core import Locale
from rigour.territories import get_territory, get_ftm_countries

from followthemoney.rdf import URIRef, Identifier
from followthemoney.types.common import EnumType, EnumValues
from followthemoney.util import defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class CountryType(EnumType):
    """Properties to define countries and territories. This is completely
    descriptive and needs to deal with data from many origins, so we support
    a number of unusual and controversial designations (e.g. the Soviet Union,
    Transnistria, Somaliland, Kosovo)."""

    name = "country"
    group = "countries"
    label = _("Country")
    plural = _("Countries")
    matchable = True
    max_length = 16

    def _locale_names(self, locale: Locale) -> EnumValues:
        return {t.code: t.name for t in get_ftm_countries()}

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        """Determine a two-letter country code based on an input.

        The input may be a country code, a country name, etc.
        """
        territory = get_territory(text)
        if territory is not None:
            ftm_country = territory.ftm_country
            if ftm_country is not None:
                return ftm_country
        code = countrynames.to_code(text, fuzzy=fuzzy)
        if code is not None:
            territory = get_territory(code)
            if territory is not None:
                return territory.ftm_country
        return None

    def country_hint(self, value: str) -> str:
        return value

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"iso-3166:{value}")
