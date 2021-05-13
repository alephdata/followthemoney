.. _cli: 

Command-line functions
=======================

Many of the functions of `followthemoney` (FtM) can be used interactively or in
scripts via the command line. Please first refer to the `Aleph documentation`_ 
for an intro to the ``ftm`` utility.

.. _Aleph documentation: https://docs.alephdata.org/developers/followthemoney/ftm

Key to understanding the ``ftm`` tool is the notion of :ref:`streams`: entities can be
transferred between programs and processing steps as a series of JSON objects, one per
line. This notion is supported by the related `alephclient`_ command, which can serve
as a source, and a sink for entity streams, backed by the Aleph API.

.. _alephclient: https://docs.alephdata.org/developers/alephclient

Examples
----------

The command line sequence below uses shell pipes to a) :ref:`map data <mappings>`
into entities from a database, b) apply a :ref:`namespace <namespace>` to the entity IDs,
c) aggregate :ref:`entity fragments <fragments>` created by the mapping, and d) export
the resulting entity stream into a sequence of CYPHER statements that can be executed on a
Neo4J database to generate a property graph:

.. code-block:: bash

    ftm map companies_from_db.yml | \
        ftm sign -s my_namespace | \
        ftm aggregate | \
        ftm export-cypher -o graph.cypher

Here's another example that fetches pre-generated entities from a URL and loads
them into a local Aleph instance:

.. code-block:: bash

    export URL=https://public.data.occrp.org/datasets/icij/panama_papers.ijson
    curl -s $URL | \
        ftm validate | \
        alephclient write-entities -f icij_panama_papers


Command reference
------------------

.. click:: followthemoney.cli.cli:cli
    :prog: ftm
    :nested: full