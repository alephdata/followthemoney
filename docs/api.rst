.. _api: 

Entity and schema API
=======================

The core interfaces of `followthemoney` are simple: each running instance of the
library has a :class:`~followthemoney.model.Model` singleton, which holds a set of
:class:`~followthemoney.schema.Schema` definitions (e.g. :ref:`schema-Person`).
Each schema defines a set of :class:`properties <followthemoney.property.Property>`
(e.g. `name`, `birthDate`) which give meaning to how values can be associated with
entities of a given schema.

The :class:`model <followthemoney.model.Model>` is also used to instantiate
:class:`entity proxies <followthemoney.proxy.EntityProxy>` - objects that allow
the creation and use of entity data, based on the rules defined by an associated
:class:`schema <followthemoney.schema.Schema>`.

Example
--------

For an illustration of how these objects interact, imagine the following script:

.. code-block:: python

    # Load the standard instance of the model
    from followthemoney import model
    
    ## Schema metadata
    # Access a schema metadata object
    schema = model.get('Person')

    # Access a property metadata object
    prop = schema.get('birthDate')

    # You can also import the type registry that lets you access type info easily:
    from followthemoney.types import registry
    assert prop.type == registry.date

    ## Working with entities and entity proxies
    # Next, let's instantiate a proxy object for a new Person entity:
    entity = model.make_entity(schema)

    # First, you'll want to assign an ID to the entity. You can do this directly:
    entity.id = 'john-smith'

    # Or you can use a hashing function to make a safe ID:
    entity.make_id('John Smith', '1979')

    # Now, let's assign this entity a birthDate property (see above):
    entity.add(prop, '1979-08-23')

    # You can also assign properties by name:
    entity.add('firstName', 'John')
    entity.add('lastName', 'Smith')
    entity.add('name', 'John Smith')

    # Adding a property value will perform some validation:
    entity.add('nationality', 'Atlantis')
    assert not entity.has('nationality')
    entity.add('nationality', 'Germani', fuzzy=True)
    assert 'de' == entity.first('nationality')

    # Lets make a second entity, this time for a passport:
    passport_entity = model.make_entity('Passport')
    passport_entity.make_id(entity.id, 'C716818')
    passport_entity.add('number', 'C716818')

    # Entities can link to other entities like this:
    passport_entity.add('holder', entity)
    # Which is the same as:
    passport_entity.add('holder', entity.id)

    # Finally, you can turn the contents of the entity proxy into a plain dictionary
    # that is suitable for JSON serialization or storage in a database:
    data = entity.to_dict()
    assert data.get('id') == entity.id

    # If you want to turn this back into an entity proxy:
    entity2 = model.get_proxy(data)
    assert entity2 == entity


The library offers a much more complex set of operations - but entity proxies, 
schemata, properties, and the model are the key elements to understand.

Entity proxy
-------------

The entity proxy is a wrapper object for FtM data. It can be used as a factory
in order to build an entity, or as a simple abstraction to query the properties
of an existing entity.

.. autoclass:: followthemoney.proxy.EntityProxy
   :members:
   :undoc-members:

Schema management
------------------

.. autoclass:: followthemoney.schema.Schema
   :members:
   :undoc-members:

.. autoclass:: followthemoney.property.Property
   :members:
   :undoc-members:

.. autoclass:: followthemoney.model.Model
   :members:
   :undoc-members:

Helper utilities
----------------

.. automodule:: followthemoney.helpers
    :members:

.. automodule:: followthemoney.util
    :members: