import re
from normality import stringify
from banal import unique_list, ensure_list


class PropertyMapping(object):
    """Map values from a given record (e.g. a CSV row or SQL result) to the
    schema form."""
    FORMAT_PATTERN = re.compile('{{([^(}})]*)}}')

    def __init__(self, mapper, data, schema):
        self.mapper = mapper
        self.data = data
        self.schema = schema
        self.name = schema.name
        self.type = schema.type

        self.refs = ensure_list(data.pop('column', []))
        self.refs.extend(ensure_list(data.pop('columns', [])))

        self.literals = ensure_list(data.pop('literal', []))
        self.literals.extend(ensure_list(data.pop('literals', [])))

        self.join = stringify(data.pop('join', None))
        self.entity = data.pop('entity', None)
        # TODO: check entity type against model constraints

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

    def map(self, record):
        values = []
        # clean the values returned by the query, or by using literals, or
        # formats.
        for value in self.record_values(record):
            # TODO: should we add unclean here?
            value = self.type.clean(value, **self.data)
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
