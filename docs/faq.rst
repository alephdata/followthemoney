
Frequently asked questions
============================


Why not a propery graph model?
--------------------------------

Until Aleph 2.x, the `followthemoney` (FtM) system was based on edges and nodes, 
like you would expect if you're coming from a network analysis background. 
However, using that model forced us to make more and more random, opinionated, 
modelling decisions: what is the source of an ownership edge - the owner, or the
asset? Is an email message a node or a hypergraph edge with many targets? What
about a payment, or a customs declaration? Both often have more than two 
parties involved.

As soon as we started modelling FtM data as entities only, many of these semantics
could actually be expressed, rather than implicitly fudged. There's still
"funky" places, like familiar relations which would need to be modelled in much
more detail to be unambiguous. 

In general, property graphs are much more interpretative than we admit: they try
to reduce the complexity of a domain into something targeted at answering a
specific set of analytical queries. The entity-only model, on the other hand,
remains a bit more descriptive. 
