from rdflib import URIRef
from banal import is_mapping

from followthemoney.types.common import PropertyType


class EntityType(PropertyType):
    name = 'entity'
    group = 'entities'

    def clean(self, text, **kwargs):
        if is_mapping(text):
            text = text.get('id')
        return super(EntityType, self).clean(text, **kwargs)

    def specificity(self, value):
        return 1

    def rdf(self, value):
        return URIRef('urn:entity:%s' % value)
