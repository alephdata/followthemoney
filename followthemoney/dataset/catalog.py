import yaml
from typing import Optional, Dict, Any, Generic, Set, Type, List

from followthemoney.types import registry
from followthemoney.dataset.dataset import DS
from followthemoney.exc import MetadataException
from followthemoney.dataset.util import type_check
from followthemoney.util import PathLike


class DataCatalog(Generic[DS]):
    """A data catalog is a collection of datasets. It provides methods for retrieving or
    creating datasets, and for checking if a dataset exists in the catalog."""

    def __init__(self, dataset_type: Type[DS], data: Dict[str, Any]) -> None:
        self.dataset_type = dataset_type
        self.datasets: List[DS] = []
        for ddata in data.get("datasets", []):
            self.make_dataset(ddata)
        self.updated_at = type_check(registry.date, data.get("updated_at"))

    def add(self, dataset: "DS") -> None:
        """Add a dataset to the catalog. If the dataset already exists, it will be updated."""
        for existing in self.datasets:
            if existing.name in dataset._children:
                dataset.children.add(existing)
            if dataset.name in existing._children:
                existing.children.add(dataset)
        self.datasets.append(dataset)

    def make_dataset(self, data: Dict[str, Any]) -> "DS":
        """Create a new dataset from the given data. If a dataset with the same name already
        exists, it will be updated."""
        dataset = self.dataset_type(data)
        self.add(dataset)
        return dataset

    def get(self, name: str) -> Optional["DS"]:
        """Get a dataset by name. Returns None if the dataset does not exist."""
        for ds in self.datasets:
            if ds.name == name:
                return ds
        return None

    def require(self, name: str) -> "DS":
        """Get a dataset by name. Raises MetadataException if the dataset does not exist."""
        dataset = self.get(name)
        if dataset is None:
            raise MetadataException("No such dataset: %s" % name)
        return dataset

    def has(self, name: str) -> bool:
        """Check if a dataset exists in the catalog."""
        return name in self.names

    @property
    def names(self) -> Set[str]:
        """Get the names of all datasets in the catalog."""
        return {d.name for d in self.datasets}

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DataCatalog[{self.dataset_type.__name__}]({self.names!r})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "datasets": [d.to_dict() for d in self.datasets],
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_path(cls, dataset_type: Type[DS], path: PathLike) -> "DataCatalog[DS]":
        with open(path, "r") as fh:
            return cls(dataset_type, yaml.safe_load(fh))
