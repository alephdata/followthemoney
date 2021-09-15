import re
from typing import Any, Optional, TYPE_CHECKING
from rdflib import URIRef  # type: ignore
from rdflib.term import Identifier  # type: ignore

from followthemoney.types.common import PropertyType
from followthemoney.util import get_entity_id, sanitize_text
from followthemoney.util import defer as _

if TYPE_CHECKING:
    from followthemoney.proxy import EntityProxy


class EntityType(PropertyType):
    """A reference to another entity via its ID. This is how entities in FtM
    become a graph: by pointing at each other using :ref:`references`.

    Entity IDs can either be `namespaced` or `plain`, depending on the context.
    When setting properties of this type, you can pass in an entity proxy or
    dict of the entity, the ID will then be extracted and stored.
    """

    REGEX_RAW = r"^[0-9a-zA-Z]([0-9a-zA-Z\.\-]*[0-9a-zA-Z])?$"
    REGEX = re.compile(REGEX_RAW)
    name = "entity"
    group = "entities"
    label = _("Entity")
    plural = _("Entities")
    matchable = True
    pivot = True

    def validate(self, value: str) -> bool:
        text = sanitize_text(value)
        if text is None:
            return False
        return self.REGEX.match(text) is not None

    def clean(
        self,
        raw: Any,
        fuzzy: bool = False,
        format: Optional[str] = None,
        proxy: Optional["EntityProxy"] = None,
    ) -> Optional[str]:
        entity_id = get_entity_id(raw)
        if entity_id is None:
            return None
        if self.REGEX.match(entity_id) is not None:
            return entity_id
        return None

    def rdf(self, value: str) -> Identifier:
        return URIRef(f"entity:{value}")

    def caption(self, value: str) -> None:
        return None
