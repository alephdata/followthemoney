import countrynames
from typing import Optional, TYPE_CHECKING
from babel.core import Locale  # type: ignore

from followthemoney.rdf import URIRef, Identifier
from followthemoney.types.common import EnumType, EnumValues
from followthemoney.util import gettext, defer as _

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

    def _locale_names(self, locale: Locale) -> EnumValues:
        # extra territories that OCCRP is interested in.
        names = {
            "zz": gettext("Global"),
            "eu": gettext("European Union"),
            "zr": gettext("Zaire"),
            # Overwrite "Czechia" label:
            "cz": gettext("Czech Republic"),
            "xk": gettext("Kosovo"),
            "dd": gettext("East Germany"),
            "yucs": gettext("Yugoslavia"),
            "csxx": gettext("Serbia and Montenegro"),
            "cshh": gettext("Czechoslovakia"),
            "suhh": gettext("Soviet Union"),
            "ge-ab": gettext("Abkhazia (Occupied Georgia)"),
            "x-so": gettext("South Ossetia (Occupied Georgia)"),
            "ua-lpr": gettext("Luhansk (Occupied Ukraine)"),
            "ua-dpr": gettext("Donetsk (Occupied Ukraine)"),
            "ua-cri": gettext("Crimea (Occupied Ukraine)"),
            "so-som": gettext("Somaliland"),
            "cy-trnc": gettext("Northern Cyprus"),
            "az-nk": gettext("Nagorno-Karabakh"),
            "cn-xz": gettext("Tibet"),
            "gg-srk": gettext("Sark"),
            "gb-wls": gettext("Wales"),
            "gb-sct": gettext("Scotland"),
            "gb-nir": gettext("Northern Ireland"),
            "md-pmr": gettext("Transnistria (PMR)"),
        }
        for code, label in locale.territories.items():
            code = code.lower()
            if code in names:
                continue
            try:
                int(code)
            except ValueError:
                names[code] = label
        return names

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
        code = countrynames.to_code(text, fuzzy=fuzzy)
        if code is not None:
            lower = code.lower()
            if lower in self.codes:
                return lower
        return None

    def country_hint(self, value: str) -> str:
        return value

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"iso-3166-1:{value}")
