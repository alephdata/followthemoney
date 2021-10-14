# This module serves exclusively to mitigate the type checking clusterfuck
# that is rdflib 6.0.
from typing import Any, Optional
from rdflib import term
from rdflib import Namespace
from rdflib.namespace._RDF import RDF
from rdflib.namespace._SKOS import SKOS
from rdflib.namespace._XSD import XSD

NS = Namespace("https://w3id.org/ftm#")  # type: ignore

Identifier = term.Identifier


def URIRef(value: Any) -> Identifier:
    return term.URIRef(value)  # type: ignore


def Literal(value: Any, datatype: Optional[Identifier] = None) -> Identifier:
    return term.Literal(value, datatype=datatype)  # type: ignore


__all__ = ["NS", "XSD", "RDF", "SKOS", "Identifier", "URIRef", "Literal"]
