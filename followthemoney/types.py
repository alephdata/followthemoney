import exactitude
from collections import namedtuple

PropType = namedtuple('PropType', ['type', 'invert'])

TYPES = {
    'string': PropType(exactitude.texts, None),
    'name': PropType(exactitude.names, 'names'),
    'entity': PropType(exactitude.texts, 'entities'),
    'url': PropType(exactitude.urls, 'urls'),
    'uri': PropType(exactitude.urls, 'urls'),
    'date': PropType(exactitude.dates, 'dates'),
    'address': PropType(exactitude.addresses, 'addresses'),
    'country': PropType(exactitude.countries, 'countries'),
    'email': PropType(exactitude.emails, 'emails'),
    'phone': PropType(exactitude.phones, 'phones'),
    'identifier': PropType(exactitude.identifiers, 'identifiers'),
}
