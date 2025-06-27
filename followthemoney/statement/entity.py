from hashlib import sha1
from collections.abc import Mapping
from typing import Any, Dict, List, Optional, Set, Type
from typing import Generator, Iterable, Tuple, TypeVar

from followthemoney.model import Model
from followthemoney.exc import InvalidData
from followthemoney.types.common import PropertyType
from followthemoney.property import Property
from followthemoney.util import gettext
from followthemoney.proxy import P
from followthemoney.types import registry
from followthemoney.value import string_list, Values
from followthemoney.proxy import EntityProxy
from followthemoney.dataset import Dataset, DefaultDataset
from followthemoney.statement.statement import Statement
from followthemoney.statement.util import BASE_ID

SE = TypeVar("SE", bound="StatementEntity")


class StatementEntity(EntityProxy):
    """An entity object that can link to a set of datasets that it is sourced from."""

    __slots__ = (
        "schema",
        "id",
        "_caption",
        "extra_referents",
        "dataset",
        "last_change",
        "_statements",
    )

    def __init__(self, dataset: Dataset, data: Dict[str, Any], cleaned: bool = True):
        data = dict(data or {})
        schema = Model.instance().get(data.pop("schema", None))
        if schema is None:
            raise InvalidData(gettext("No schema for entity."))
        self.schema = schema

        self._caption: Optional[str] = None
        """A pre-computed label for this entity."""

        self.extra_referents: Set[str] = set(data.pop("referents", []))
        """The IDs of all entities which are included in this canonical entity."""

        self.last_change: Optional[str] = data.get("last_change", None)
        """The last time this entity was changed."""

        self.dataset = dataset
        """The default dataset for new statements."""

        self.id: Optional[str] = data.pop("id", None)
        self._statements: Dict[str, Set[Statement]] = {}

        properties = data.pop("properties", None)
        if isinstance(properties, Mapping):
            for key, value in properties.items():
                self.add(key, value, cleaned=cleaned, quiet=True)

        for stmt_data in data.pop("statements", []):
            stmt = Statement.from_dict(stmt_data)
            if self.id is not None:
                stmt.canonical_id = self.id
            self.add_statement(stmt)

    @property
    def _properties(self) -> Dict[str, List[str]]:  # type: ignore
        return {p: [s.value for s in v] for p, v in self._statements.items()}

    def _iter_stmt(self) -> Generator[Statement, None, None]:
        for stmts in self._statements.values():
            for stmt in stmts:
                if stmt.entity_id is None and self.id is not None:
                    stmt.entity_id = self.id
                    stmt.id = stmt.generate_key()
                if stmt.id is None:
                    stmt.id = stmt.generate_key()
                yield stmt

    @property
    def statements(self) -> Generator[Statement, None, None]:
        """Return all statements for this entity, with extra ID statement."""
        ids: List[str] = []
        last_seen: Set[str] = set()
        first_seen: Set[str] = set()
        for stmt in self._iter_stmt():
            yield stmt
            if stmt.id is not None:
                ids.append(stmt.id)
            if stmt.last_seen is not None:
                last_seen.add(stmt.last_seen)
            if stmt.first_seen is not None:
                first_seen.add(stmt.first_seen)
        if self.id is not None:
            digest = sha1(self.schema.name.encode("utf-8"))
            for id in sorted(ids):
                digest.update(id.encode("utf-8"))
            checksum = digest.hexdigest()
            # This is to make the last_change value stable across
            # serialisation:
            first = self.last_change or min(first_seen, default=None)
            yield Statement(
                canonical_id=self.id,
                entity_id=self.id,
                prop=BASE_ID,
                schema=self.schema.name,
                value=checksum,
                dataset=self.dataset.name,
                first_seen=first,
                last_seen=max(last_seen, default=None),
            )

    @property
    def first_seen(self) -> Optional[str]:
        seen = (s.first_seen for s in self._iter_stmt() if s.first_seen is not None)
        return min(seen, default=None)

    @property
    def last_seen(self) -> Optional[str]:
        seen = (s.last_seen for s in self._iter_stmt() if s.last_seen is not None)
        return max(seen, default=None)

    @property
    def datasets(self) -> Set[str]:
        datasets: Set[str] = set()
        for stmt in self._iter_stmt():
            datasets.add(stmt.dataset)
        return datasets

    @property
    def referents(self) -> Set[str]:
        referents: Set[str] = set(self.extra_referents)
        for stmt in self._iter_stmt():
            if stmt.entity_id is not None and stmt.entity_id != self.id:
                referents.add(stmt.entity_id)
        return referents

    @property
    def key_prefix(self) -> Optional[str]:
        return self.dataset.name

    @key_prefix.setter
    def key_prefix(self, dataset: Optional[str]) -> None:
        raise NotImplementedError()

    def add_statement(self, stmt: Statement) -> None:
        schema = self.schema
        if not schema.is_a(stmt.schema):
            try:
                self.schema = schema.model.common_schema(schema, stmt.schema)
            except InvalidData as exc:
                raise InvalidData(f"{self.id}: {exc}") from exc

        if stmt.prop == BASE_ID:
            if stmt.first_seen is not None:
                # The last_change attribute describes the latest checksum change
                # of any emitted component of the entity, which is stored in the BASE
                # field.
                if self.last_change is None:
                    self.last_change = stmt.first_seen
                else:
                    self.last_change = max(self.last_change, stmt.first_seen)
        else:
            self._statements.setdefault(stmt.prop, set())
            self._statements[stmt.prop].add(stmt)

    def get(self, prop: P, quiet: bool = False) -> List[str]:
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None or prop_name not in self._statements:
            return []
        return list({s.value for s in self._statements[prop_name]})

    def get_statements(self, prop: P, quiet: bool = False) -> List[Statement]:
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None or prop_name not in self._statements:
            return []
        return list(self._statements[prop_name])

    def set(
        self,
        prop: P,
        values: Values,
        cleaned: bool = False,
        quiet: bool = False,
        fuzzy: bool = False,
        format: Optional[str] = None,
        lang: Optional[str] = None,
        original_value: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> None:
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None:
            return
        self._statements.pop(prop_name, None)
        return self.add(
            prop,
            values,
            cleaned=cleaned,
            quiet=quiet,
            fuzzy=fuzzy,
            format=format,
            lang=lang,
            original_value=original_value,
            origin=origin,
        )

    def add(
        self,
        prop: P,
        values: Values,
        cleaned: bool = False,
        quiet: bool = False,
        fuzzy: bool = False,
        format: Optional[str] = None,
        lang: Optional[str] = None,
        original_value: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> None:
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None:
            return None
        prop = self.schema.properties[prop_name]
        for value in string_list(values, sanitize=not cleaned):
            self.unsafe_add(
                prop,
                value,
                cleaned=cleaned,
                fuzzy=fuzzy,
                format=format,
                quiet=quiet,
                lang=lang,
                original_value=original_value,
                origin=origin,
            )
        return None

    def unsafe_add(
        self,
        prop: Property,
        value: Optional[str],
        cleaned: bool = False,
        fuzzy: bool = False,
        format: Optional[str] = None,
        quiet: bool = False,
        schema: Optional[str] = None,
        dataset: Optional[str] = None,
        seen: Optional[str] = None,
        lang: Optional[str] = None,
        original_value: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> Optional[str]:
        """Add a statement to the entity, possibly the value."""
        if value is None or len(value) == 0:
            return None

        # Don't allow setting the reverse properties:
        if prop.stub:
            if quiet:
                return None
            msg = gettext("Stub property (%s): %s")
            raise InvalidData(msg % (self.schema, prop))

        if lang is not None:
            lang = registry.language.clean_text(lang)

        clean: Optional[str] = value
        if not cleaned:
            clean = prop.type.clean_text(value, proxy=self, fuzzy=fuzzy, format=format)

        if clean is None:
            return None

        if original_value is None and clean != value:
            original_value = value

        if self.id is None:
            raise InvalidData("Cannot add statement to entity without ID!")
        stmt = Statement(
            entity_id=self.id,
            prop=prop.name,
            schema=schema or self.schema.name,
            value=clean,
            dataset=dataset or self.dataset.name,
            lang=lang,
            original_value=original_value,
            first_seen=seen,
            origin=origin,
        )
        self.add_statement(stmt)
        return clean

    def pop(self, prop: P, quiet: bool = True) -> List[str]:
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is None or prop_name not in self._statements:
            return []
        return list({s.value for s in self._statements.pop(prop_name, [])})

    def remove(self, prop: P, value: str, quiet: bool = True) -> None:
        prop_name = self._prop_name(prop, quiet=quiet)
        if prop_name is not None and prop_name in self._properties:
            stmts = {s for s in self._statements[prop_name] if s.value != value}
            self._statements[prop_name] = stmts

    def itervalues(self) -> Generator[Tuple[Property, str], None, None]:
        for name, statements in self._statements.items():
            prop = self.schema.properties[name]
            for value in set((s.value for s in statements)):
                yield (prop, value)

    def get_type_values(
        self, type_: PropertyType, matchable: bool = False
    ) -> List[str]:
        combined: Set[str] = set()
        for stmt in self.get_type_statements(type_, matchable=matchable):
            combined.add(stmt.value)
        return list(combined)

    def get_type_statements(
        self, type_: PropertyType, matchable: bool = False
    ) -> List[Statement]:
        combined = []
        for prop_name, statements in self._statements.items():
            prop = self.schema.properties[prop_name]
            if matchable and not prop.matchable:
                continue
            if prop.type == type_:
                for statement in statements:
                    combined.append(statement)
        return combined

    @property
    def properties(self) -> Dict[str, List[str]]:
        return {p: list({s.value for s in vs}) for p, vs in self._statements.items()}

    def iterprops(self) -> List[Property]:
        return [self.schema.properties[p] for p in self._statements.keys()]

    def clone(self: SE) -> SE:
        data = {"schema": self.schema.name, "id": self.id}
        cloned = type(self)(self.dataset, data)
        for stmt in self._iter_stmt():
            cloned.add_statement(stmt)
        return cloned

    def merge(self: SE, other: EntityProxy) -> SE:
        try:
            self.schema = self.schema.model.common_schema(self.schema, other.schema)
        except InvalidData as e:
            msg = "Cannot merge entities with id %s: %s"
            raise InvalidData(msg % (self.id, e))

        if not isinstance(other, StatementEntity):
            for prop, values in other._properties.items():
                self.add(prop, values, cleaned=True, quiet=True)
            return self
        for stmt in other._iter_stmt():
            if self.id is not None:
                stmt.canonical_id = self.id
            self.add_statement(stmt)
        self.extra_referents.update(other.extra_referents)
        return self

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.id,
            "caption": self.caption,
            "schema": self.schema.name,
            "properties": self.properties,
            "referents": list(self.referents),
            "datasets": list(self.datasets),
        }
        if self.first_seen is not None:
            data["first_seen"] = self.first_seen
        if self.last_seen is not None:
            data["last_seen"] = self.last_seen
        if self.last_change is not None:
            data["last_change"] = self.last_change
        return data

    def to_statement_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the entity's statements."""
        data: Dict[str, Any] = {
            "id": self.id,
            "caption": self.caption,
            "schema": self.schema.name,
            "statements": [stmt.to_dict() for stmt in self.statements],
            "referents": list(self.referents),
            "datasets": list(self.datasets),
        }
        if self.first_seen is not None:
            data["first_seen"] = self.first_seen
        if self.last_seen is not None:
            data["last_seen"] = self.last_seen
        if self.last_change is not None:
            data["last_change"] = self.last_change
        return data

    def __len__(self) -> int:
        return len(list(self._iter_stmt())) + 1

    @classmethod
    def from_dict(
        cls: Type[SE],
        data: Dict[str, Any],
        cleaned: bool = True,
        default_dataset: Optional[Dataset] = None,
    ) -> SE:
        # Exists only for backwards compatibility.
        dataset = default_dataset or DefaultDataset
        return cls(dataset, data, cleaned=cleaned)

    @classmethod
    def from_data(
        cls: Type[SE],
        dataset: Dataset,
        data: Dict[str, Any],
        cleaned: bool = True,
    ) -> SE:
        return cls(dataset, data, cleaned=cleaned)

    @classmethod
    def from_statements(
        cls: Type[SE],
        dataset: Dataset,
        statements: Iterable[Statement],
    ) -> SE:
        obj: Optional[SE] = None
        for stmt in statements:
            if obj is None:
                data = {"schema": stmt.schema, "id": stmt.canonical_id}
                obj = cls(dataset, data)
            obj.add_statement(stmt)
        if obj is None:
            raise ValueError("No statements given!")
        return obj
