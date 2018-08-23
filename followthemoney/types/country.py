import countrynames
from normality import stringify

from followthemoney.types.common import PropertyType


class CountryType(PropertyType):

    def __init__(self, *args):
        super(CountryType, self).__init__(*args)
        # extra countries that OCCRP is interested in.
        self.names = {
            'zz': 'Global',
            'eu': 'European Union',
            'xk': 'Kosovo',
            'yucs': 'Yugoslavia',
            'csxx': 'Serbia and Montenegro',
            'suhh': 'Soviet Union',
            'ge-ab': 'Abkhazia',
            'x-so': 'South Ossetia',
            'so-som': 'Somaliland',
            'gb-wls': 'Wales',
            'gb-sct': 'Scotland',
            'md-pmr': 'Transnistria'
        }
        for code, label in self.locale.territories.items():
            self.names[code.lower()] = label

    def validate(self, country, **kwargs):
        country = stringify(country)
        if country is None:
            return False
        return country.lower() in self.names

    def clean_text(self, country, guess=False, **kwargs):
        """Determine a two-letter country code based on an input.

        The input may be a country code, a country name, etc.
        """
        code = country.lower().strip()
        if code in self.names:
            return code
        country = countrynames.to_code(country, fuzzy=guess)
        if country is not None:
            return country.lower()
