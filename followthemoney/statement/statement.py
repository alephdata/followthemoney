import hashlib
import warnings
from sqlalchemy.engine import Row
from typing import cast
from typing import Union, Any, Dict, Generator, Optional
from typing_extensions import TypedDict, Self
from rigour.time import datetime_iso, iso_datetime
from rigour.boolean import bool_text

from followthemoney.proxy import EntityProxy
from followthemoney.statement.util import get_prop_type, BASE_ID

ExtrasValue = Union[str, int, float, bool, None]


class StatementDict(TypedDict):
    id: Optional[str]
    entity_id: str
    canonical_id: str
    prop: str
    schema: str
    value: str
    dataset: str
    lang: Optional[str]
    original_value: Optional[str]
    external: bool
    first_seen: Optional[str]
    last_seen: Optional[str]
    origin: Optional[str]
    extras: Optional[Dict[str, ExtrasValue]]


class Statement(object):
    """A single statement about a property relevant to an entity.

    For example, this could be used to say: "In dataset A, entity X has the
    property `name` set to 'John Smith'. I first observed this at K, and last
    saw it at L."

    Null property values are not supported. This might need to change if we
    want to support making property-less entities.
    """

    BASE = BASE_ID

    __slots__ = [
        "id",
        "entity_id",
        "canonical_id",
        "prop",
        "schema",
        "value",
        "dataset",
        "lang",
        "original_value",
        "external",
        "first_seen",
        "last_seen",
        "origin",
        "extras",
    ]

    def __init__(
        self,
        entity_id: str,
        prop: str,
        schema: str,
        value: str,
        dataset: str,
        lang: Optional[str] = None,
        original_value: Optional[str] = None,
        first_seen: Optional[str] = None,
        external: bool = False,
        id: Optional[str] = None,
        canonical_id: Optional[str] = None,
        last_seen: Optional[str] = None,
        origin: Optional[str] = None,
        extras: Optional[Dict[str, ExtrasValue]] = None,
    ):
        self.entity_id = entity_id
        self.canonical_id = canonical_id or entity_id
        self.prop = prop
        self.schema = schema
        self.value = value
        self.dataset = dataset
        self.lang = lang
        self.original_value = original_value
        self.first_seen = first_seen
        self.last_seen = last_seen or first_seen
        self.external = external
        self.origin = origin
        self.extras = extras
        if id is None:
            id = self.generate_key()
        self.id = id

    @property
    def prop_type(self) -> str:
        """The type of the property, e.g. 'string', 'number', 'url'."""
        return get_prop_type(self.schema, self.prop)

    def to_dict(self) -> StatementDict:
        return {
            "canonical_id": self.canonical_id,
            "entity_id": self.entity_id,
            "prop": self.prop,
            "schema": self.schema,
            "value": self.value,
            "dataset": self.dataset,
            "lang": self.lang,
            "original_value": self.original_value,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "external": self.external,
            "origin": self.origin,
            "extras": self.extras,
            "id": self.id,
        }

    def to_csv_row(self) -> Dict[str, Optional[str]]:
        data = cast(Dict[str, Optional[str]], self.to_dict())
        data.pop("extras", None)  # not supported in CSV
        data["external"] = bool_text(self.external)
        data["prop_type"] = self.prop_type
        return data

    def to_db_row(self) -> Dict[str, Any]:
        data = cast(Dict[str, Any], self.to_dict())
        data.pop("extras", None)  # not supported in SQL
        data["first_seen"] = iso_datetime(self.first_seen)
        data["last_seen"] = iso_datetime(self.last_seen)
        return data

    def __hash__(self) -> int:
        if self.id is None:
            warnings.warn(
                "Hashing a statement without an ID results in undefined behaviour",
                RuntimeWarning,
            )
        return hash(self.id)

    def __repr__(self) -> str:
        return "<Statement(%r, %r, %r)>" % (self.entity_id, self.prop, self.value)

    def __eq__(self, other: Any) -> bool:
        return not self.id != other.id

    def __lt__(self, other: Any) -> bool:
        self_key = (self.prop != BASE_ID, self.id or "")
        other_key = (other.prop != BASE_ID, other.id or "")
        return self_key < other_key

    def clone(self: Self) -> "Statement":
        """Make a deep copy of the given statement."""
        return Statement.from_dict(self.to_dict())

    def generate_key(self) -> Optional[str]:
        return self.make_key(
            self.dataset,
            self.entity_id,
            self.prop,
            self.value,
            self.external,
        )

    @classmethod
    def make_key(
        cls,
        dataset: str,
        entity_id: str,
        prop: str,
        value: str,
        external: Optional[bool],
    ) -> Optional[str]:
        """Hash the key properties of a statement record to make a unique ID."""
        if prop is None or value is None:
            return None
        key = f"{dataset}.{entity_id}.{prop}.{value}"
        if external:
            # We consider the external flag in key composition to avoid race conditions
            # where a certain entity might be emitted as external while it is already
            # linked in to the graph via another route.
            key = f"{key}.ext"
        return hashlib.sha1(key.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: StatementDict) -> "Statement":
        return cls(
            entity_id=data["entity_id"],
            prop=data["prop"],
            schema=data["schema"],
            value=data["value"],
            dataset=data["dataset"],
            lang=data.get("lang", None),
            original_value=data.get("original_value", None),
            first_seen=data.get("first_seen", None),
            external=data.get("external", False),
            id=data.get("id", None),
            canonical_id=data.get("canonical_id", None),
            last_seen=data.get("last_seen", None),
            origin=data.get("origin", None),
            extras=data.get("extras", None),
        )

    @classmethod
    def from_db_row(cls, row: Row) -> "Statement":
        return cls(
            id=row.id,
            canonical_id=row.canonical_id,
            entity_id=row.entity_id,
            prop=row.prop,
            schema=row.schema,
            value=row.value,
            dataset=row.dataset,
            lang=row.lang,
            original_value=row.original_value,
            first_seen=datetime_iso(row.first_seen),
            external=row.external,
            last_seen=datetime_iso(row.last_seen),
            origin=row.origin,
        )

    @classmethod
    def from_entity(
        cls,
        entity: "EntityProxy",
        dataset: str,
        first_seen: Optional[str] = None,
        last_seen: Optional[str] = None,
        external: bool = False,
        origin: Optional[str] = None,
    ) -> Generator["Statement", None, None]:
        from followthemoney.statement.entity import StatementEntity

        if entity.id is None:
            raise ValueError("Cannot create statements for entity without ID!")

        # If the entity is already a StatementEntity, we return its statements directly.
        if isinstance(entity, StatementEntity):
            yield from entity.statements
            return

        yield cls(
            entity_id=entity.id,
            prop=BASE_ID,
            schema=entity.schema.name,
            value=entity.id,
            dataset=dataset,
            external=external,
            first_seen=first_seen,
            last_seen=last_seen,
            origin=origin,
        )
        for prop, value in entity.itervalues():
            yield cls(
                entity_id=entity.id,
                prop=prop.name,
                schema=entity.schema.name,
                value=value,
                dataset=dataset,
                external=external,
                first_seen=first_seen,
                last_seen=last_seen,
                origin=origin,
            )
