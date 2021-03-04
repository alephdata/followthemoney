Network graph semantics
========================

TODO: Import the graph tooling documentation into this documentation:

https://docs.alephdata.org/developers/followthemoney/ftm#exporting-data-to-a-network-graph

How FtM data is translated to a network graph
----------------------------------------------

Below are some notes about the semantics of FtM as a graph, and how it might be
converted to a (Neo4J-style) property graph model. This is how we've been
thinking about it in the past, and we can change it, but it would almost
certainly require adaptation of the FtM model and the complete re-generation
of all Aleph data from scratch to do cleanly. 

1. The normal case for what an edge is in FtM is a property value. This is a
   consequence of FtM being a somewhat RDF-inspired data model. For example,
   consider the case of a `Person` and a `Passport`: the `Passport` simply has
   a `holder` property which contains the `Person.id`. When turning this
   construct into a property graph model, both the passport and the person
   become nodes, and the `holder` property becomes an edge with no properties
   attached to it.
2. Sometimes we want to talk about the inverse of one of these edges. That's
   why `holder` has an inverse, `passports` that is added to the `Person` schema.
   This is mostly used to store, for example, the labels that should be used
   to talk about the passports linked to a person. But it's a `stub` property
   that cannot be written (doing `Person.add('passports', value)` will throw
   an exception.
3. The weakness of this model is that edges don't have properties, whereas
   relationships in society always have metadata :) Many of them, for example,
   are limited in time (hence `Interval`). So we added a hacky work-around that
   allows some schema to sort of contract upon generating a property graph and
   turn into an edge, rather than a node. For example, `Membership`, `Ownership`.
   But it's important to keep considering this a *special shortcut*, not the
   normal case for edges in FtM.
4. Because this is a hack, it leaves the `stub` properties in a bit of an
   awkward place: it's not clear conceptually if they refer to the original
   edge (e.g. a link between a `Person.directorshipsDirector` ->
   `Directorship.director`) or the contracted edge (`Person` -> `directorOf`
   -> `Organization`)... It's not hurt us too much in practice since we get the
   required metadata from the edge annotation of the contracted schema, but it's
   a sort of weird "place".

Why not a propery graph model?
------------------------------------------------

Until some time in Aleph 2.x, the system was based on edges and nodes, like you
would expect if you're coming from a network analysis background. However, using
that model forced us to make more and more random, opinionated modelling
decisions: what is the source of an ownership edge - the owner, or the asset? Is
an email message a node or a hypergraph edge with many targets? What about a
payment, or a customs declaration? Both often have more than two parties involved.

As soon as we started modelling FtM data as entities only, many of these semantics
could actually be expressed, rather than implicitly fudged. There's still
"funky" places, like familiar relations which would need to be modelled in much
more detail to be unambiguous. 

In general, I think property graphs are much more interpretative than we admit:
they try to reduce the complexity of a domain into something targeted at answering
a specific set of analytical queries. The entity-only model, on the other hand,
remains a bit more descriptive. 

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
