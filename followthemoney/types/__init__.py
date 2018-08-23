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
from followthemoney.types.entity import EntityType
from followthemoney.types.common import TextType, Registry

types = Registry()
urls = types.add(UrlType())
domains = types.add(DomainType())
emails = types.add(EmailType())
ips = types.add(IpType())
ibans = types.add(IbanType())
addresses = types.add(AddressType())
dates = types.add(DateType())
phones = types.add(PhoneType())
countries = types.add(CountryType())
languages = types.add(LanguageType())
identifiers = types.add(IdentifierType())
entities = types.add(EntityType())
texts = types.add(TextType())
names = types.add(NameType())
