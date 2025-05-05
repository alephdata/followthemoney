from followthemoney.model import Model
from followthemoney.types import registry
from followthemoney.proxy import EntityProxy, E
from followthemoney.statement import Statement, StatementEntity, SE
from followthemoney.util import set_model_locale

__version__ = "3.8.4"

# Data model singleton
model = Model.instance()

__all__ = [
    "model",
    "set_model_locale",
    "Model",
    "EntityProxy",
    "E",
    "registry",
    "Statement",
    "StatementEntity",
    "SE",
]
