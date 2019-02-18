from rdflib import URIRef

from followthemoney.types.common import PropertyType
from followthemoney.util import get_entity_id


class EntityType(PropertyType):
    name = 'entity'
    group = 'entities'
    matchable = True

    def clean(self, text, **kwargs):
        return get_entity_id(text)

    def rdf(self, value):
        return URIRef('urn:entity:%s' % value)
