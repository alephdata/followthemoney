from banal import ensure_sequence
from normality import stringify
from followthemoney.types import resolve_type


class Property(object):

    def __init__(self, schema, name, data):
        self.schema = schema
        self.name = name.strip()
        self.data = data
        self.label = data.get('label', name)
        self.hidden = data.get('hidden', False)
        self.is_multiple = data.get('multiple', False)
        self.is_label = name == 'name'
        cls = resolve_type(data.get('type', 'string'))
        self.type = cls()

    def validate(self, data):
        """Validate that the data should be stored.

        Since the types system doesn't really have validation, this currently
        tries to normalize the value to see if it passes strict parsing.
        """
        value, error = [], None
        for val in ensure_sequence(data):
            val = stringify(val)
            if val is None:
                continue
            val = val.strip()
            if self.type.normalize_value(val) is None:
                error = "Invalid value"
            value.append(val)
        if not self.is_multiple:
            value = value[0] if len(value) else None
        else:
            value = list(set(value))
        if self.is_label and (value is None or not len(value)):
            error = "Field is required."
        return value, error

    def to_dict(self):
        return {
            'name': self.name,
            'label': self.label,
            'hidden': self.hidden,
            'type': self.type.name
        }

    def __repr__(self):
        return '<Property(%r, %r)>' % (self.schema, self.name)
