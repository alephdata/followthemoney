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
