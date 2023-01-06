# This module serves exclusively to mitigate the type checking clusterfuck
# that is rdflib 6.0.
from rdflib import Namespace
from rdflib.term import Identifier, URIRef, Literal
from rdflib import RDF, SKOS, XSD

NS = Namespace("https://w3id.org/ftm#")

__all__ = ["NS", "XSD", "RDF", "SKOS", "Identifier", "URIRef", "Literal"]
