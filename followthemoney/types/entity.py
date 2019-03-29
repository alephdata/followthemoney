from rdflib import URIRef

from followthemoney.types.common import PropertyType
from followthemoney.util import get_entity_id
from followthemoney.util import defer as _


class EntityType(PropertyType):
    name = 'entity'
    group = 'entities'
    label = _('Entity')
    plural = _('Entities')
    matchable = True

    def clean(self, text, **kwargs):
        return get_entity_id(text)

    def rdf(self, value):
        return URIRef('urn:entity:%s' % value)
