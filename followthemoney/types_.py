import followthemoney.types
from collections import namedtuple

PropType = namedtuple('PropType', ['type', 'invert'])

TYPES = {
    'string': PropType(followthemoney.types.texts, None),
    'name': PropType(followthemoney.types.names, 'names'),
    'entity': PropType(followthemoney.types.texts, 'entities'),
    'url': PropType(followthemoney.types.urls, 'urls'),
    'date': PropType(followthemoney.types.dates, 'dates'),
    'address': PropType(followthemoney.types.addresses, 'addresses'),
    'country': PropType(followthemoney.types.countries, 'countries'),
    'email': PropType(followthemoney.types.emails, 'emails'),
    'phone': PropType(followthemoney.types.phones, 'phones'),
    'identifier': PropType(followthemoney.types.identifiers, 'identifiers'),
    'iban': PropType(followthemoney.types.ibans, 'ibans'),
    'ip': PropType(followthemoney.types.ips, 'ips'),
}
