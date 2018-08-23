from collections import namedtuple

from followthemoney.types.url import UrlType
from followthemoney.types.name import NameType
from followthemoney.types.domain import DomainType
from followthemoney.types.email import EmailType
from followthemoney.types.ip import IpType
from followthemoney.types.iban import IbanType
from followthemoney.types.address import AddressType
from followthemoney.types.date import DateType
from followthemoney.types.phone import PhoneType
from followthemoney.types.country import CountryType
from followthemoney.types.language import LanguageType
from followthemoney.types.identifier import IdentifierType
from followthemoney.types.common import TextType

urls = UrlType()
names = NameType()
domains = DomainType()
emails = EmailType()
ips = IpType()
ibans = IbanType()
addresses = AddressType()
dates = DateType()
phones = PhoneType()
countries = CountryType()
languages = LanguageType()
identifiers = IdentifierType()
texts = TextType()

__all__ = [urls,
           names,
           domains,
           emails,
           ips,
           ibans,
           addresses,
           dates,
           phones,
           countries,
           languages,
           identifiers,
           texts]

PropType = namedtuple('PropType', ['type', 'invert'])

TYPES = {
    'string': PropType(texts, None),
    'name': PropType(names, 'names'),
    'entity': PropType(texts, 'entities'),
    'url': PropType(urls, 'urls'),
    'date': PropType(dates, 'dates'),
    'address': PropType(addresses, 'addresses'),
    'country': PropType(countries, 'countries'),
    'email': PropType(emails, 'emails'),
    'phone': PropType(phones, 'phones'),
    'identifier': PropType(identifiers, 'identifiers'),
    'iban': PropType(ibans, 'ibans'),
    'ip': PropType(ips, 'ips'),
}
