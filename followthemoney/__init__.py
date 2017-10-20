import os

from followthemoney.model import Model

model_path = os.path.dirname(__file__)
model_path = os.path.join(model_path, 'schema')

# Data model singleton
model = Model(model_path)

__all__ = [model]
