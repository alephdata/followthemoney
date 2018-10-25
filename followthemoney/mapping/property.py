import re
from copy import deepcopy
from normality import stringify
from banal import unique_list, ensure_list

from followthemoney.exc import InvalidMapping
from followthemoney.util import get_entity_id


class PropertyMapping(object):
    """Map values from a given record (e.g. a CSV row or SQL result) to the
    schema form."""
    FORMAT_PATTERN = re.compile('{{([^(}})]*)}}')

    def __init__(self, query, data, schema):
        self.query = query
        data = deepcopy(data)
        self.data = data
        self.schema = schema
        self.name = schema.name
        self.type = schema.type

        self.refs = ensure_list(data.pop('column', []))
        self.refs.extend(ensure_list(data.pop('columns', [])))

        self.literals = ensure_list(data.pop('literal', []))
        self.literals.extend(ensure_list(data.pop('literals', [])))

        self.join = data.pop('join', None)
        self.split = data.pop('split', None)
        self.entity = data.pop('entity', None)
        self.required = data.pop('required', False)

        self.template = stringify(data.pop('template', None))
        self.replacements = {}
        if self.template is not None:
            # this is hacky, trying to generate refs from template
            for ref in self.FORMAT_PATTERN.findall(self.template):
                self.refs.append(ref)
                self.replacements['{{%s}}' % ref] = ref

    def bind(self):
        if self.schema.stub:
            raise InvalidMapping("Property for [%s] is a stub" % self.name)

        if self.entity is None:
            return

        # Figure out if the schema types of the referenced entities
        # are of a type compatible with the range of this property.
        # For example, an asset can be owned by a legal entity, but
        # by a bank payment or a ship.
        for entity in self.query.entities:
            if entity.name != self.entity:
                continue
            if not entity.schema.is_a(self.schema.range):
                raise InvalidMapping("The entity [%s] must be a %s (not %s)" %
                                     (self.name, self.schema.range, entity.schema.name))  # noqa
            return

        raise InvalidMapping("No entity [%s] for property [%s]"
                             % (self.entity, self.name))

    def record_values(self, record):
        if self.template is not None:
            # replace mentions of any refs with the values present in the
            # current record
            value = self.template
            for repl, ref in self.replacements.items():
                ref_value = record.get(ref) or ''
                value = value.replace(repl, ref_value)
            return [value.strip()]

        values = list(self.literals)
        values.extend([record.get(r) for r in self.refs])
        return values

    def map(self, record, entities, **kwargs):
        kwargs.update(self.data)

        if self.entity is not None:
            entity = entities.get(self.entity)
            return ensure_list(get_entity_id(entity))

        # clean the values returned by the query, or by using literals, or
        # formats.
        values = []
        for value in self.record_values(record):
            value = self.type.clean(value, **kwargs)
            if value is not None:
                values.append(value)

        if self.join is not None:
            values = [self.join.join(values)]

        if self.split is not None:
            splote = []
            for value in values:
                splote = splote + value.split(self.split)
            values = splote

        return unique_list(values)
