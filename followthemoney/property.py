from rdflib import URIRef  # type: ignore
from banal import is_mapping
from normality import stringify

from followthemoney.exc import InvalidModel
from followthemoney.types import registry
from followthemoney.util import gettext, NS, get_entity_id


class Property(object):
    """A definition of a value-holding field on a schema. Properties define
    the field type and other possible constraints. They also serve as entity
    to entity references."""

    #: Invalid property names.
    RESERVED = ["id", "caption", "schema", "schemata"]

    def __init__(self, schema, name, data):
        self.model = schema.model

        #: The schema which the property is defined for. This is always the
        #: most abstract schema that has this property, not the possible
        #: child schemata that inherit it.
        self.schema = schema

        #: Machine-readable name for this property.
        self.name = stringify(name)

        #: Qualified property name, which also includes the schema name.
        self.qname = "%s:%s" % (schema.name, self.name)
        if self.name in self.RESERVED:
            raise InvalidModel("Reserved name: %s" % self.name)

        self._hash = hash("<Property(%r)>" % self.qname)

        self.data = data
        self._label = data.get("label", name)
        self._description = data.get("description")

        #: This property should not be shown or mentioned in the user interface.
        self.hidden = data.get("hidden", False)

        type_ = data.get("type", "string")
        #: The data type for this property.
        self.type = registry.get(type_)
        if self.type is None:
            raise InvalidModel("Invalid type: %s" % type_)

        #: Whether this property should be used for matching and cross-referencing.
        self.matchable = data.get("matchable", self.type.matchable)

        #: If the property is of type ``entity``, the set of valid schema to be added
        #: in this property can be constrained. For example, an asset can be owned,
        #: but a person cannot be owned.
        self.range = None

        #: When a property points to another schema, a reverse property is added for
        #: various administrative reasons. These properties are, however, not real
        #: and cannot be written to. That's why they are marked as stubs and adding
        #: values to them will raise an exception.
        self.stub = data.get("stub", False)

        #: When a property points to another schema, a stub reverse property is
        #: added as a place to store metadata to help display the link in inverted
        #: views.
        self.reverse = None

        #: RDF term for this property (i.e. the predicate URI).
        self.uri = URIRef(data.get("rdf", NS[self.qname]))

    def generate(self):
        """Setup method used when loading the model in order to build out the reverse
        links of the property."""
        self.model.properties.add(self)

        if self.range is None and self.type == registry.entity:
            self.range = self.model.get(self.data.get("range"))

        reverse_ = self.data.get("reverse")
        if self.reverse is None and self.range and reverse_:
            if not is_mapping(reverse_):
                raise InvalidModel("Invalid reverse: %s" % self)
            self.reverse = self.range._add_reverse(reverse_, self)

    @property
    def label(self):
        """User-facing title for this property."""
        return gettext(self._label)

    @property
    def description(self):
        """A longer description of the semantics of this property."""
        return gettext(self._description)

    def specificity(self, value):
        """Return a measure of how precise the given value is."""
        if not self.matchable:
            return 0
        return self.type.specificity(value)

    def validate(self, data):
        """Validate that the data should be stored.

        Since the types system doesn't really have validation, this currently
        tries to normalize the value to see if it passes strict parsing.
        """
        values = []
        for val in data:
            if self.stub:
                return gettext("Property cannot be written")
            val = get_entity_id(val)
            if not self.type.validate(val):
                return gettext("Invalid value")
            if val is not None:
                values.append(val)

    def __eq__(self, other):
        return self._hash == hash(other)

    def __hash__(self):
        return self._hash

    def to_dict(self):
        """Return property metadata in a serializable form."""
        data = {
            "name": self.name,
            "qname": self.qname,
            "label": self.label,
            "type": self.type.name,
        }
        if self.description:
            data["description"] = self.description
        if self.stub:
            data["stub"] = True
        if self.matchable:
            data["matchable"] = True
        if self.hidden:
            data["hidden"] = True
        if self.range:
            data["range"] = self.range.name
        if self.reverse:
            data["reverse"] = self.reverse.name
        return data

    def __repr__(self):
        return "<Property(%r)>" % self.qname

    def __str__(self):
        return self.qname
