from rdflib import URIRef  # type: ignore
from phonenumbers import geocoder  # type: ignore
from phonenumbers import parse as parse_number  # type: ignore
from phonenumbers import is_valid_number, format_number  # type: ignore
from phonenumbers import PhoneNumberFormat  # type: ignore
from phonenumbers.phonenumberutil import NumberParseException  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import dampen

# TODO: for json schema export
# https://stackoverflow.com/questions/6478875/regular-expression-matching-e-164-formatted-phone-numbers


class PhoneType(PropertyType):
    """A phone number in E.164 format. This means that phone numbers always
    include an international country prefix (e.g. ``+38760183628``). The
    cleaning and validation functions for this try to be smart about by
    accepting a list of countries as an argument in order to add the number
    prefix.

    When adding a property of this type to an entity, any country-type properties
    defined for the entity are considered for validation. That means that adding a
    phone number to an entity before adding a country can have a different
    validation outcome from doing the two operations the other way around. Always
    define the country first."""

    name = "phone"
    group = "phones"
    label = _("Phone number")
    plural = _("Phone numbers")
    matchable = True
    pivot = True

    def _clean_countries(self, proxy):
        yield None
        if proxy is not None:
            for country in proxy.countries:
                yield country.upper()

    def _parse_number(self, number, proxy=None):
        """Parse a phone number and return in international format.

        If no valid phone number can be detected, None is returned. If
        a country code is supplied, this will be used to infer the
        prefix.

        https://github.com/daviddrysdale/python-phonenumbers
        """
        for code in self._clean_countries(proxy):
            try:
                yield parse_number(number, code)
            except NumberParseException:
                pass

    def clean_text(self, number, proxy=None, **kwargs):
        for num in self._parse_number(number, proxy=proxy):
            if is_valid_number(num):
                return format_number(num, PhoneNumberFormat.E164)

    def validate(self, number, proxy=None, **kwargs):
        for num in self._parse_number(number, proxy=proxy):
            if is_valid_number(num):
                return True
        return False

    def country_hint(self, value):
        try:
            number = parse_number(value)
            code = geocoder.region_code_for_number(number)
            if code is not None:
                return code.lower()
        except NumberParseException:
            return None

    def _specificity(self, value):
        # TODO: insert artificial intelligence here.
        return dampen(7, 11, value)

    def rdf(self, value):
        return URIRef(self.node_id(value))

    def node_id(self, value):
        return f"tel:{value}"

    def caption(self, value):
        number = parse_number(value)
        return format_number(number, PhoneNumberFormat.INTERNATIONAL)
