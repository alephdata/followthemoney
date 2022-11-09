from typing import Iterable, Optional, TYPE_CHECKING
from phonenumbers import parse as parse_number
from phonenumbers import is_valid_number, format_number
from phonenumbers import PhoneNumber, PhoneNumberFormat
from phonenumbers.phonenumberutil import region_code_for_number, NumberParseException

from followthemoney.types.common import PropertyType
from followthemoney.rdf import URIRef, Identifier
from followthemoney.util import defer as _
from followthemoney.util import dampen

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


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

    def _clean_countries(
        self, proxy: Optional["EntityProxy"]
    ) -> Iterable[Optional[str]]:
        yield None
        if proxy is not None:
            for country in proxy.countries:
                yield country.upper()

    def _parse_number(
        self, number: str, proxy: Optional["EntityProxy"] = None
    ) -> Iterable[PhoneNumber]:
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

    def validate(self, value: str) -> bool:
        for num in self._parse_number(value):
            if is_valid_number(num):
                return True
        return False

    def clean_text(
        self,
        text: str,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        for num in self._parse_number(text, proxy=proxy):
            if is_valid_number(num):
                return str(format_number(num, PhoneNumberFormat.E164))
        return None

    def country_hint(self, value: str) -> Optional[str]:
        try:
            number = parse_number(value)
            code = region_code_for_number(number)
            if code is None:
                return None
            return str(code).lower()
        except NumberParseException:
            return None

    def _specificity(self, value: str) -> float:
        # TODO: insert artificial intelligence here.
        return dampen(7, 11, value)

    def rdf(self, value: str) -> Identifier:
        node_id = self.node_id(value)
        if node_id is not None:
            return URIRef(node_id)
        raise ValueError("Invalid phone number for serialisation: %s" % value)

    def node_id(self, value: str) -> Optional[str]:
        return f"tel:{value}"

    def caption(self, value: str) -> str:
        try:
            number = parse_number(value)
            formatted = format_number(number, PhoneNumberFormat.INTERNATIONAL)
            return str(formatted)
        except NumberParseException:
            return value
