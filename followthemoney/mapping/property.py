import re
from copy import deepcopy
from banal import keys_values
from normality import stringify

from followthemoney.exc import InvalidMapping
from followthemoney.util import get_entity_id


class PropertyMapping(object):
    """Map values from a given record (e.g. a CSV row or SQL result) to the
    schema form."""
    FORMAT_PATTERN = re.compile('{{([^(}})]*)}}')

    def __init__(self, query, data, prop):
        self.query = query
        data = deepcopy(data)
        self.data = data
        self.prop = prop
        self.name = prop.name
        self.type = prop.type

        self.refs = keys_values(data, 'column', 'columns')
        self.literals = keys_values(data, 'literal', 'literals')
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
            if not entity.schema.is_a(self.prop.range):
                raise InvalidMapping("The entity [%r] must be a %s (not %s)" %
                                     (self.prop, self.prop.range, entity.schema.name))  # noqa
            return

        raise InvalidMapping("No entity [%s] for property [%r]"
                             % (self.entity, self.prop))

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

    def map(self, proxy, record, entities, **kwargs):
        kwargs.update(self.data)

        if self.entity is not None:
            entity = entities.get(self.entity)
            if entity is not None:
                proxy.add(self.prop, get_entity_id(entity))

                # This is really bad in theory, but really useful
                # in practice. Shoot me.
                text = proxy.schema.get('indexText')
                if text is not None:
                    for caption in entity.schema.caption:
                        proxy.add(text, entity.get(caption))

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

        proxy.add(self.prop, values)
