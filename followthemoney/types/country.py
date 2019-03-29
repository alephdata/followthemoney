import countrynames
from rdflib import URIRef
from normality import stringify

from followthemoney.types.common import PropertyType
from followthemoney.util import gettext, get_locale
from followthemoney.util import defer as _


class CountryType(PropertyType):
    name = 'country'
    group = 'countries'
    label = _('Country')
    plural = _('Countries')
    matchable = True

    def __init__(self, *args):
        self._names = {}
        self.codes = self.names.keys()

    @property
    def names(self):
        locale = get_locale()
        if locale not in self._names:
            # extra territories that OCCRP is interested in.
            self._names[locale] = {
                'zz': gettext('Global'),
                'eu': gettext('European Union'),
                'xk': gettext('Kosovo'),
                'yucs': gettext('Yugoslavia'),
                'csxx': gettext('Serbia and Montenegro'),
                'suhh': gettext('Soviet Union'),
                'ge-ab': gettext('Abkhazia'),
                'x-so': gettext('South Ossetia'),
                'so-som': gettext('Somaliland'),
                'gb-wls': gettext('Wales'),
                'gb-sct': gettext('Scotland'),
                'md-pmr': gettext('Transnistria')
            }
            for code, label in locale.territories.items():
                self._names[locale][code.lower()] = label
        return self._names[locale]

    def validate(self, country, **kwargs):
        country = stringify(country)
        if country is None:
            return False
        return country.lower() in self.codes

    def clean_text(self, country, guess=False, **kwargs):
        """Determine a two-letter country code based on an input.

        The input may be a country code, a country name, etc.
        """
        code = country.lower().strip()
        if code in self.codes:
            return code
        country = countrynames.to_code(country, fuzzy=guess)
        if country is not None:
            return country.lower()

    def country_hint(self, value):
        return value

    def rdf(self, value):
        return URIRef('iso-3166-1:%s' % value)
