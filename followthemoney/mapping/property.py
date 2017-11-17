import re
from copy import deepcopy
from normality import stringify
from banal import unique_list, ensure_list

from followthemoney.exc import InvalidMapping


class PropertyMapping(object):
    """Map values from a given record (e.g. a CSV row or SQL result) to the
    schema form."""
    FORMAT_PATTERN = re.compile('{{([^(}})]*)}}')

    def __init__(self, mapper, data, schema):
        data = deepcopy(data)
        self.mapper = mapper
        self.data = data
        self.schema = schema
        self.name = schema.name
        self.type = schema.type
        self.range = schema.range

        self.refs = ensure_list(data.pop('column', []))
        self.refs.extend(ensure_list(data.pop('columns', [])))

        self.literals = ensure_list(data.pop('literal', []))
        self.literals.extend(ensure_list(data.pop('literals', [])))

        self.join = stringify(data.pop('join', None))
        self.entity = data.pop('entity', None)

        if self.entity is not None:
            # Check entity schema against model constraints
            try:
                entity_schema = mapper.mappings[self.entity].schema.name
            except KeyError:
                raise InvalidMapping(
                    "No entity [%s] for property [%s]" % (self.entity, self.name))
            if not mapper.model.is_descendant(self.range, entity_schema):
              # Check the schema of the entity in the mapping is or descends
              # from the range of this property
                raise InvalidMapping(
                    "The entity for property [%s] must be a %s (not %s)" % (self.name, self.range, entity_schema))

        self.template = stringify(data.pop('template', None))
        self.replacements = {}
        if self.template is not None:
            # this is hacky, trying to generate refs from template
            for ref in self.FORMAT_PATTERN.findall(self.template):
                self.refs.append(ref)
                self.replacements['{{%s}}' % ref] = ref

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

    def map(self, record, **kwargs):
        kwargs.update(self.data)
        values = []
        # clean the values returned by the query, or by using literals, or
        # formats.
        for value in self.record_values(record):
            # TODO: should we add unclean here?
            value = self.type.clean(value, **kwargs)
            if value is not None:
                values.append(value)

        if self.join is not None:
            values = [self.join.join(values)]
        return unique_list(values)

    def resolve(self, entities):
        if self.entity is None:
            return
        entity = entities.get(self.entity)
        if entity is not None:
            return entity.get('id')
