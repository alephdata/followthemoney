import re
from rdflib import URIRef   # type: ignore
from typing import Optional

from followthemoney.types.common import PropertyType
from followthemoney.util import get_entity_id, sanitize_text
from followthemoney.util import defer as _


class EntityType(PropertyType):
    ID_RE = re.compile(r'^[0-9a-zA-Z]([0-9a-zA-Z\.\-]*[0-9a-zA-Z])?$')
    name: str = 'entity'
    group: str = 'entities'
    label: str = _('Entity')
    plural: str = _('Entities')
    matchable: bool = True
    pivot: bool = True

    def validate(self, text: str, **kwargs) -> bool:
        _text = sanitize_text(text)
        if _text is None:
            return False
        return self.ID_RE.match(_text) is not None

    def clean(self, text: Optional[str], **kwargs) -> Optional[str]:
        entity_id = get_entity_id(text)
        if not entity_id:
            return None
        if self.validate(entity_id):
            return entity_id
        return None

    def rdf(self, value: str) -> URIRef:
        return URIRef('entity:%s' % value)

    def caption(self, value: Optional[str]) -> Optional[str]:
        return None
