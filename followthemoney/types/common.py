from rdflib import Literal
from banal import ensure_list, is_mapping
from normality import stringify


class PropertyType(object):
    """Base class for all types."""
    name = None
    group = None
    prefix = None

    def validate(self, text, **kwargs):
        """Returns a boolean to indicate if this is a valid instance of
        the type."""
        cleaned = self.clean(text, **kwargs)
        return cleaned is not None

    def clean(self, text, **kwargs):
        """Create a more clean, but still user-facing version of an
        instance of the type."""
        text = stringify(text)
        if text is not None:
            return self.clean_text(text, **kwargs)

    def clean_text(self, text, **kwargs):
        return text

    def normalize(self, text, cleaned=False, **kwargs):
        """Create a represenation ideal for comparisons, but not to be
        shown to the user."""
        if not cleaned:
            text = self.clean(text, **kwargs)
        return ensure_list(text)

    def normalize_set(self, items, **kwargs):
        """Utility to normalize a whole set of values and get unique
        values."""
        values = set()
        for item in ensure_list(items):
            values.update(self.normalize(item, **kwargs))
        return list(values)

    def specificity(self, value):
        return 0

    def ref(self, value):
        """Generate a qualified form for storage in a triplestore."""
        value = stringify(value)
        if value is None:
            return
        if self.prefix is not None:
            if is_mapping(value):
                value = value.get('id')
            return ':'.join((self.prefix, value))

    def rdf(self, value):
        return Literal(value)


class TextType(PropertyType):
    name = 'text'


class Registry(object):

    def __init__(self):
        self.prefixes = {}
        self.groups = {}
        self.names = {}

    def add(self, instance):
        setattr(self, instance.name, instance)
        self.names[instance.name] = instance
        if instance.prefix is not None:
            self.prefixes[instance.prefix] = instance
        if instance.group is not None:
            self.groups[instance.group] = instance
        return instance

    def get(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            pass

    def deref(self, ref):
        prefix, value = ref.split(':', 1)
        return self.prefixes.get(prefix), value
