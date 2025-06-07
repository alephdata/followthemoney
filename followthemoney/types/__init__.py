from banal import ensure_list
from typing import Dict, Iterable, List, Set, cast

from followthemoney.types.url import UrlType
from followthemoney.types.name import NameType
from followthemoney.types.email import EmailType
from followthemoney.types.ip import IpType
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
from followthemoney.types.gender import GenderType
from followthemoney.types.json import JsonType
from followthemoney.types.string import TextType
from followthemoney.types.string import HTMLType
from followthemoney.types.string import StringType
from followthemoney.types.number import NumberType
from followthemoney.types.common import PropertyType


class Registry(object):
    """This registry keeps the processing helpers for all property types in the system. The
    registry can be used to get a type, which can itself then clean, validate or format values
    of that type."""

    url = UrlType()
    name = NameType()
    email = EmailType()
    ip = IpType()
    address = AddressType()
    date = DateType()
    phone = PhoneType()
    country = CountryType()
    language = LanguageType()
    mimetype = MimeType()
    checksum = ChecksumType()
    identifier = IdentifierType()
    entity = EntityType()
    topic = TopicType()
    gender = GenderType()
    json = JsonType()
    text = TextType()
    html = HTMLType()
    string = StringType()
    number = NumberType()

    def __init__(self) -> None:
        self.matchable: Set[PropertyType] = set()
        self.types: Set[PropertyType] = set()
        self.groups: Dict[str, PropertyType] = {}
        self.pivots: Set[PropertyType] = set()
        for name in dir(self):
            type_ = getattr(self, name)
            if not isinstance(type_, PropertyType):
                continue
            assert type_.name == name
            self.types.add(type_)
            if type_.matchable:
                self.matchable.add(type_)
            if type_.pivot:
                self.pivots.add(type_)
            if type_.group is not None:
                self.groups[type_.group] = type_

    def get(self, name: str) -> PropertyType:
        """For a given property type name, get its type object. This can also
        be used via getattr, e.g. ``registry.phone``."""
        # Allow transparent re-checking.
        if isinstance(name, PropertyType):
            return name
        return cast(PropertyType, getattr(self, name))

    def get_types(self, names: Iterable[str]) -> List[PropertyType]:
        """Get a list of all property type objects linked to a set of names."""
        names = ensure_list(names)
        types = [self.get(n) for n in names]
        return [t for t in types if t is not None]

    def __getitem__(self, name: str) -> PropertyType:
        return cast(PropertyType, getattr(self, name))


registry = Registry()

__all__ = ["PropertyType", "registry"]
