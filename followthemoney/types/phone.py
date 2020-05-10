from typing import Iterable, Set, Iterator, Optional

from rdflib import URIRef  # type: ignore
from banal import ensure_list
from phonenumbers import geocoder  # type: ignore
from phonenumbers import parse as parse_number
from phonenumbers import is_valid_number, format_number
from phonenumbers import PhoneNumberFormat
from phonenumbers.phonenumberutil import NumberParseException  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import defer as _
from followthemoney.util import dampen


class PhoneType(PropertyType):
    name: str = 'phone'
    group: str = 'phones'
    label: str = _('Phone number')
    plural: str = _('Phone numbers')
    matchable: bool = True
    pivot: bool = True

    def _clean_countries(self, countries: Optional[Iterable],
                         country: Optional[Iterable]) -> Set[str]:
        result: Set = set([None])
        countries = ensure_list(countries)
        countries.extend(ensure_list(country))
        for country in countries:
            if isinstance(country, str):
                country = country.strip().upper()
                result.add(country)
        return result

    def _parse_number(self, number: str, countries: Iterable = None,
                      country: Iterable = None, **kwargs) -> Iterator[str]:
        """Parse a phone number and return in international format.

        If no valid phone number can be detected, None is returned. If
        a country code is supplied, this will be used to infer the
        prefix.

        https://github.com/daviddrysdale/python-phonenumbers
        """
        for code in self._clean_countries(countries, country):
            try:
                yield parse_number(number, code)
            except NumberParseException:
                pass

    def clean_text(self, number: str, **kwargs) -> Optional[str]:  # type: ignore[override] # noqa
        for num in self._parse_number(number, **kwargs):
            if is_valid_number(num):
                return format_number(num, PhoneNumberFormat.E164)
        return None

    def validate(self, number: str, **kwargs) -> bool:  # type: ignore[override] # noqa
        for num in self._parse_number(number, **kwargs):
            if is_valid_number(num):
                return True
        return False

    def country_hint(self, value: str) -> Optional[str]:
        try:
            number = parse_number(value)
            return geocoder.region_code_for_number(number).lower()
        except NumberParseException:
            return None

    def _specificity(self, value: str) -> float:
        # TODO: insert artificial intelligence here.
        return dampen(6, 11, value)

    def rdf(self, value: str) -> URIRef:
        return URIRef('tel:%s' % value)

    def caption(self, value: Optional[str]) -> str:
        number = parse_number(value)
        return format_number(number, PhoneNumberFormat.INTERNATIONAL)
