import re
from copy import deepcopy
from normality import stringify
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast
from banal import keys_values, as_bool

from followthemoney.helpers import inline_names
from followthemoney.exc import InvalidMapping
from followthemoney.proxy import EntityProxy
from followthemoney.util import get_entity_id, sanitize_text
from followthemoney.property import Property
from followthemoney.mapping.source import Record

if TYPE_CHECKING:
    from followthemoney.mapping.query import QueryMapping


class PropertyMapping(object):
    """Map values from a given record (e.g. a CSV row or SQL result) to the
    schema form."""

    __slots__ = (
        "query",
        "prop",
        "refs",
        "join",
        "split",
        "entity",
        "format",
        "fuzzy",
        "required",
        "literals",
        "template",
        "replacements",
    )

    FORMAT_PATTERN = re.compile("{{([^(}})]*)}}")

    def __init__(
        self, query: "QueryMapping", data: Dict[str, Any], prop: Property
    ) -> None:
        self.query = query
        data = deepcopy(data)
        self.prop = prop

        self.refs = cast(List[str], keys_values(data, "column", "columns"))
        self.join = cast(Optional[str], data.pop("join", None))
        self.split = cast(Optional[str], data.pop("split", None))
        self.entity = stringify(data.pop("entity", None))
        self.format = stringify(data.pop("format", None))
        self.fuzzy = as_bool(data.pop("fuzzy", False))
        self.required = as_bool(data.pop("required", False))
        self.literals = cast(List[str], keys_values(data, "literal", "literals"))

        self.template = sanitize_text(data.pop("template", None))
        self.replacements: Dict[str, str] = {}
        if self.template is not None:
            # this is hacky, trying to generate refs from template
            for ref in self.FORMAT_PATTERN.findall(self.template):
                self.refs.append(ref)
                self.replacements["{{%s}}" % ref] = ref

    def bind(self) -> None:
        if self.prop.stub:
            raise InvalidMapping("Property for [%r] is a stub" % self.prop)

        if self.entity is None:
            return

        # Figure out if the schema types of the referenced entities
        # are of a type compatible with the range of this property.
        # For example, an asset can be owned by a legal entity, but
        # by a bank payment or a ship.
        for entity in self.query.entities:
            if entity.name != self.entity:
                continue
            if not self.prop.range or not entity.schema.is_a(self.prop.range):
                raise InvalidMapping(
                    "The entity [%r] must be a %s (not %s)"
                    % (self.prop, self.prop.range, entity.schema.name)
                )  # noqa
            return

        raise InvalidMapping(
            "No entity [%s] for property [%r]" % (self.entity, self.prop)
        )

    def record_values(self, record: Record) -> List[str]:
        if self.template is not None:
            # replace mentions of any refs with the values present in the
            # current record
            value = self.template
            for repl, ref in self.replacements.items():
                ref_value = record.get(ref) or ""
                value = value.replace(repl, ref_value)
            return [value.strip()]

        values = list(self.literals)
        for ref in self.refs:
            rec_value = record.get(ref)
            if rec_value is not None:
                values.append(rec_value)
        return values

    def map(
        self, proxy: EntityProxy, record: Record, entities: Dict[str, EntityProxy]
    ) -> None:
        if self.entity is not None:
            entity = entities.get(self.entity)
            if entity is not None:
                proxy.unsafe_add(self.prop, entity.id, cleaned=True)
                inline_names(proxy, entity)
            return None

        # clean the values returned by the query, or by using literals, or
        # formats.
        values: List[str] = self.record_values(record)

        if self.join is not None:
            values = [self.join.join(values)]

        if self.split is not None:
            splote = []
            for value in values:
                splote.extend(value.split(self.split))
            values = splote

        for value in values:
            proxy.unsafe_add(self.prop, value, fuzzy=self.fuzzy, format=self.format)
