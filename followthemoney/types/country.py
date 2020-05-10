from typing import Dict, Optional

import countrynames  # type: ignore
from rdflib import URIRef  # type: ignore

from followthemoney.types.common import EnumType
from followthemoney.util import gettext, defer as _


class CountryType(EnumType):
    name: str = 'country'
    group: str = 'countries'
    label: str = _('Country')
    plural: str = _('Countries')
    matchable: bool = True

    def _locale_names(self, locale) -> Dict[str, str]:
        # extra territories that OCCRP is interested in.
        names = {
            'zz': gettext('Global'),
            'eu': gettext('European Union'),
            # Overwrite "Czechia" label:
            'cz': gettext('Czech Republic'),
            'xk': gettext('Kosovo'),
            'yucs': gettext('Yugoslavia'),
            'csxx': gettext('Serbia and Montenegro'),
            'suhh': gettext('Soviet Union'),
            'ge-ab': gettext('Abkhazia'),
            'x-so': gettext('South Ossetia'),
            'so-som': gettext('Somaliland'),
            'gb-wls': gettext('Wales'),
            'gb-sct': gettext('Scotland'),
            'gb-nir': gettext('Northern Ireland'),
            'md-pmr': gettext('Transnistria')
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

    def clean_text(self, country: str, guess: bool = False, **kwargs) -> Optional[str]:  # type: ignore[override] # noqa
        """Determine a two-letter country code based on an input.

        The input may be a country code, a country name, etc.
        """
        code = country.lower().strip()
        if code in self.codes:
            return code
        country = countrynames.to_code(country, fuzzy=guess)
        if country is not None:
            return country.lower()
        return None

    def country_hint(self, value: str) -> str:
        return value

    def rdf(self, value: str) -> URIRef:
        return URIRef('iso-3166-1:%s' % value)
