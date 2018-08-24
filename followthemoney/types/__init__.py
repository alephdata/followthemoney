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

registry = Registry()
urls = registry.add(UrlType())
domains = registry.add(DomainType())
emails = registry.add(EmailType())
ips = registry.add(IpType())
ibans = registry.add(IbanType())
addresses = registry.add(AddressType())
dates = registry.add(DateType())
phones = registry.add(PhoneType())
countries = registry.add(CountryType())
languages = registry.add(LanguageType())
identifiers = registry.add(IdentifierType())
entities = registry.add(EntityType())
texts = registry.add(TextType())
names = registry.add(NameType())
