from followthemoney.dataset.dataset import Dataset, DS
from followthemoney.dataset.catalog import DataCatalog
from followthemoney.dataset.resource import DataResource
from followthemoney.dataset.publisher import DataPublisher
from followthemoney.dataset.coverage import DataCoverage

DefaultDataset = Dataset.make({"name": "default"})

__all__ = [
    "Dataset",
    "DefaultDataset",
    "DataCatalog",
    "DataResource",
    "DataPublisher",
    "DataCoverage",
    "DS",
]
