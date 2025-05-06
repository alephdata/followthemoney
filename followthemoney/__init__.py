from followthemoney.model import Model
from followthemoney.schema import Schema
from followthemoney.property import Property
from followthemoney.types import registry
from followthemoney.value import Value, Values
from followthemoney.proxy import EntityProxy, E
from followthemoney.statement import Statement, StatementEntity, SE
from followthemoney.util import set_model_locale

__version__ = "3.8.2"

# Data model singleton
model = Model.instance()

__all__ = [
    "model",
    "set_model_locale",
    "Model",
    "Schema",
    "Property",
    "Value",
    "Values",
    "EntityProxy",
    "E",
    "registry",
    "Statement",
    "StatementEntity",
    "SE",
]
