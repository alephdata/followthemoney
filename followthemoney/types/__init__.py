from followthemoney.types.registry import Registry
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
from followthemoney.types.mimetype import MimeType
from followthemoney.types.checksum import ChecksumType
from followthemoney.types.identifier import IdentifierType
from followthemoney.types.entity import EntityType
from followthemoney.types.topic import TopicType
from followthemoney.types.json import JsonType
from followthemoney.types.string import TextType
from followthemoney.types.string import HTMLType
from followthemoney.types.string import StringType
from followthemoney.types.number import NumberType

registry = Registry()
registry.add(UrlType)
registry.add(NameType)
registry.add(DomainType)
registry.add(EmailType)
registry.add(IpType)
registry.add(IbanType)
registry.add(AddressType)
registry.add(DateType)
registry.add(PhoneType)
registry.add(CountryType)
registry.add(LanguageType)
registry.add(MimeType)
registry.add(ChecksumType)
registry.add(IdentifierType)
registry.add(EntityType)
registry.add(TopicType)
registry.add(JsonType)
registry.add(TextType)
registry.add(HTMLType)
registry.add(StringType)
registry.add(NumberType)
