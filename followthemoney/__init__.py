import os

from followthemoney.model import Model
from followthemoney.util import set_model_locale

model_path = os.path.dirname(__file__)
model_path = os.path.join(model_path, 'schema')

# Data model singleton
model = Model(model_path)

__all__ = [model, set_model_locale]
