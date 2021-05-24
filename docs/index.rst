FollowTheMoney Reference Documentation
==========================================

`FollowTheMoney` (FtM) is a data model for anti-corruption investigations. It contains
definitions of the entities relevant in such research (like :ref:`people <schema-person>`
or :ref:`companies <schema-company>`) and tools that let you generate, validate, and export such
data easily. Entities can reference each other, thus creating a graph of relationships. 

FtM can be used in three contexts: as a :ref:`command-line utility <cli>`, a :ref:`Python
library <api>`, and as a `TypeScript/JavaScript library`_. The ontology defined by FtM also
includes a model for various types of :ref:`documents <schema-document>` that might be
used as evidence in investigations [#ingest]_.

All data stored by the `Aleph search engine`_ is expressed as FtM entities. Aleph itself
adds functions for searching, viewing, and manipulating such entities. It also introduces
higher-level notions of datasets and access control.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   entity.rst
   api.rst
   fragments.rst
   namespace.rst
   mapping.rst
   custom.rst
   cli.rst
   graph.rst
   model.rst
   types.rst
   faq.rst
   credits.rst


.. [#ingest] The Aleph toolchain includes a separate project, ``ingestors``, which
   can extract and analyse the content of many document types and emit them as FtM
   entities. For example, if you were to process an archive of emails, it would
   generate a complex graph of E-Mail entities that connect the people sending and
   receiving them.

.. _Aleph search engine: https://docs.alephdata.org/

.. _TypeScript/JavaScript library: https://www.npmjs.com/package/@alephdata/followthemoney