Network graphs
===============

TODO: Import the graph tooling documentation into this documentation:

https://docs.alephdata.org/developers/followthemoney/ftm#exporting-data-to-a-network-graph

Implementation
---------------

.. autoclass:: followthemoney.graph.Graph
   :members:
   :undoc-members:

.. autoclass:: followthemoney.graph.Node
   :members:
   :undoc-members:

.. autoclass:: followthemoney.graph.Edge
   :members:
   :undoc-members:


How entities are translated to a graph
----------------------------------------

Below are some notes about the semantics of `followthemoney` (FtM) as a graph,
and how it might be converted to a (Neo4J-style) property graph model. This is
how we've been thinking about it in the past, and we can change it, but it would
almost certainly require adaptation of the FtM model and the complete 
re-generation of all Aleph data from scratch to do cleanly. 

1. The normal case for what a link is in FtM is a property value (see
   :ref:`references`). When turning this into a property graph model, both
   the :ref:`schema-Passport` and the :ref:`schema-Person` become nodes, and
   the `holder` property becomes an edge with no attributes attached to it.
2. Sometimes we want to talk about the inverse of one of these edges. That's
   why `holder` has an inverse, `passports` that is added to the
   :ref:`schema-Person` schema. This is mostly used to store  the labels that 
   should be used to talk about the passports linked to a person. But it's a
   :attr:`~followthemoney.property.Property.stub` that cannot be written.
3. The weakness of this model is that edges don't have properties, whereas
   relationships in society always have metadata :) Many of them are limited in
   time (hence :ref:`schema-Interval`). So we added a work-around that allows
   some schema to sort of contract upon generating a property graph and turn
   into an edge, rather than a node. For example, `Membership`, `Ownership`.
   But it's important to keep considering this a *special shortcut*, not the
   normal case for edges in FtM.
4. Because this is a work-around, it leaves the `stub` properties in a bit of an
   awkward place: it's not clear conceptually if they refer to the original
   edge (e.g. a link between a `Person.directorshipsDirector` ->
   `Directorship.director`) or the contracted edge (`Person` -> `directorOf`
   -> `Organization`)... It's not been a problem in practice as we get the
   required metadata from the edge annotation of the contracted schema, but it's
   a sort of weird "place".
