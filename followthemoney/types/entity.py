import re
from rdflib import URIRef  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import get_entity_id, sanitize_text
from followthemoney.util import defer as _


class EntityType(PropertyType):
    ID_RE = re.compile(r"^[0-9a-zA-Z]([0-9a-zA-Z\.\-]*[0-9a-zA-Z])?$")
    name = "entity"
    group = "entities"
    label = _("Entity")
    plural = _("Entities")
    matchable = True
    pivot = True

    def validate(self, text, **kwargs):
        text = sanitize_text(text)
        if text is None:
            return False
        return self.ID_RE.match(text) is not None

    def clean(self, text, **kwargs):
        entity_id = get_entity_id(text)
        if entity_id is None:
            return
        entity_id = str(entity_id)
        if self.ID_RE.match(entity_id) is not None:
            return entity_id

    def rdf(self, value):
        return URIRef("entity:%s" % value)

    def caption(self, value):
        return None
