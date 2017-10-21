from normality import stringify
from banal import unique_list, ensure_list

from followthemoney.mapping.formatter import Formatter


class PropertyMapping(object):
    """Map values from a given record (e.g. a CSV row or SQL result) to the
    schema form."""

    def __init__(self, mapper, data, schema):
        self.mapper = mapper
        self.data = data
        self.schema = schema
        self.name = schema.name
        self.type = schema.type

        self.refs = ensure_list(data.get('column'))
        self.refs.extend(ensure_list(data.get('columns')))

        self.literals = ensure_list(data.get('literal'))
        self.literals.extend(ensure_list(data.get('literals')))

        self.join = stringify(data.get('join'))
        self.entity = data.get('entity')
        # TODO: check entity type against model constraints

        # this is hacky, trying to generate refs from template
        self.template = data.get('template')
        if self.template is not None:
            self.formatter = Formatter(self.template)
            self.refs.extend(self.formatter.refs)

    def map(self, record):
        values = list(self.literals)

        if self.template is not None:
            values.append(self.formatter.apply(record))
        else:
            for ref in self.refs:
                values.append(record.get(ref))

        values = [self.type.clean(v, record, self.data) for v in values]
        values = [v for v in values if v is not None]

        if self.join is not None:
            values = [self.join.join(values)]

        return unique_list(values)

    def resolve(self, entities):
        if self.entity is None:
            return
        entity = entities.get(self.entity)
        if entity is not None:
            return entity.get('id')
