.. _entities:

Introduction
==================

`followthemoney` (FtM) defines a simple data model for storing complex object 
graphs. You will need to understand three concepts: `entities`,
`entity references`, and `entity streams`.

Entities
---------

Entities are often expressed as snippets of JSON, with three standard fields: a
unique ``id``, a specification of the type of the entity called ``schema``,
and a set of ``properties``. ``properties`` are multi-valued and values are
always strings.

.. code-block:: json

    {
        "id": "1b38214f88d139897bbd13eabde464043d84bbf9",
        "schema": "Person",
        "properties": {
            "name": ["John Doe"],
            "nationality": ["us", "au"],
            "birthDate": ["1982"]
        }
    }

Property names are defined by the :ref:`schemata`. For example, a 
:ref:`schema-Person` has a `nationality`, while a :ref:`schema-Company` allows 
for setting a `jurisdiction`. Both properties, however, have the same 
`property type`, :ref:`type-country`.

.. _references:

References
-----------

Entities can reference other entities. This is achieved via a special property
type, :ref:`type-entity`. Properties of this type simply store the ID of another 
entity. For example, a :ref:`schema-Passport` entity can be linked to a 
:ref:`schema-Person` entity via its `holder` property:

.. code-block:: json

    {
        "id": "passport-entity-id",
        "schema": "Passport",
        "properties": {
            "holder": ["person-entity-id"],
            "number": ["CJ 7261817"]
        }
    }

.. note::

    Applications using `FtM` data usually need to resolve references
    bi-directionally. In the context of the example above, they will need to
    access the person based on it's ID in order to follow the `holder` link,
    but also query an inverted index to retrieve all the passports which
    reference a given person.

    In Aleph this is achieved using ElasticSearch and exposed via the
    ``/api/2/entities/<id>/expand`` API endpoint.

Interstitial entities
^^^^^^^^^^^^^^^^^^^^^^^

A link between two entities will have its own attributes. For example,
an investigator looking at a person that owns a company might want to know when
that interest was acquired, and also what percentage of shares the person holds.

This is addressed by making interstitial entities. In the example above, an
:ref:`schema-Ownership` entity would be created, with references to the person
as its `owner` property and to the company as its `asset` property. That
entity can then define further properties, including `startDate` and
`percentage`:

.. code-block:: json

    {
        "id": "ownership-entity-id",
        "schema": "Ownership",
        "properties": {
            "owner": ["person-entity-id"],
            "asset": ["company-entity-id"],
            "startDate": ["2020-01-01"],
            "percentage": ["51%"],
        }
    }

.. warning::

    It is tempting to simplify this model by assuming that entities derived from
    :ref:`schema-Thing` are node entities, and those derived from
    :ref:`schema-Interval` are edges. This assumption is false and will lead to 
    nasty bugs in your code.


.. _streams:

Streams
---------

Many tools in the `FtM` ecosystem use streams of entities to transfer
or store information. Entity streams are simply sequences of entity objects that
have been serialised to JSON as single lines without any indentation, each entity
separated by a newline.

Entity streams are read and produced by virtually every part of the :ref:`cli`,
the Aleph API, and they're also supported by the `ingestors`. When stored to
disk as a file, the extensions `.ftm` or `.ijson` should be used.
