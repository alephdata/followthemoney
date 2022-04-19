# This module serves exclusively to mitigate the type checking clusterfuck
# that is rdflib 6.0.
from rdflib import Namespace
from rdflib.term import Identifier, URIRef, Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._SKOS import SKOS
from rdflib.namespace._XSD import XSD

NS = Namespace("https://w3id.org/ftm#")  # type: ignore

__all__ = ["NS", "XSD", "RDF", "SKOS", "Identifier", "URIRef", "Literal"]
