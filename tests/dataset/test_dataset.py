import json
import pytest
from pathlib import Path
from typing import Any, Dict
from tempfile import TemporaryDirectory

from followthemoney.dataset import DataCatalog, Dataset
from followthemoney.exc import MetadataException


def test_donations_base(catalog_data: Dict[str, Any]):
    catalog = DataCatalog(Dataset, catalog_data)
    assert len(catalog.datasets) == 5, catalog.datasets
    ds = catalog.get("donations")
    assert ds is not None, ds
    assert ds.name == "donations"
    assert not ds == "donations"
    assert ds.publisher is None
    assert "publisher" not in ds.to_dict()
    assert len(ds.resources) == 2, ds.resources
    for res in ds.resources:
        assert res.name is not None
        if res.mime_type is None:
            assert res.mime_type_label is None

    assert ds.get_resource("donations.csv") is not None
    with pytest.raises(ValueError):
        ds.get_resource("donations.dbf")


def test_company_dataset(catalog_data: Dict[str, Any]):
    catalog = DataCatalog(Dataset, catalog_data)
    assert len(catalog.datasets) == 5, catalog.datasets
    ds = catalog.get("company_data")
    assert ds is not None, ds
    assert ds.name == "company_data"
    assert ds.publisher is not None
    assert ds.publisher.country == "us"
    assert ds.publisher.country_label == "United States of America"
    assert ds.coverage is not None
    assert "coverage" in ds.to_dict()
    assert ds.coverage.start == "2005"
    assert ds.coverage.end == "2010-01"
    assert "us" in ds.coverage.countries

    assert "company_data" in repr(ds)

    other = Dataset.make({"name": "company_data", "title": "Company data"})
    assert other == ds, other


def test_create(catalog_data: Dict[str, Any]):
    catalog = DataCatalog(Dataset, {})
    assert len(catalog.datasets) == 0, catalog.datasets

    with pytest.raises(MetadataException):
        catalog.make_dataset({})

    ds = catalog.make_dataset({"name": "test_dataset"})
    assert ds.name == "test_dataset"
    assert ds.title == "test_dataset"
    assert ds.license is None
    assert ds.summary is None


def test_hierarchy(catalog_data: Dict[str, Any]):
    catalog = DataCatalog(Dataset, catalog_data)
    all_datasets = catalog.require("all_datasets")
    collection_a = catalog.require("collection_a")
    leak = catalog.require("leak")
    assert leak not in collection_a.datasets
    assert collection_a not in collection_a.children
    assert leak in all_datasets.datasets
    assert len(all_datasets.children) == 2, all_datasets.children
    assert len(all_datasets.datasets) == 5, all_datasets.datasets
    assert len(all_datasets.dataset_names) == len(all_datasets.datasets)
    assert len(all_datasets.leaves) == len(all_datasets.leaf_names)


def test_from_path(catalog_path: Path):
    catalog = DataCatalog.from_path(Dataset, catalog_path)
    assert len(catalog.datasets) == 5, catalog.datasets

    data = catalog.to_dict()
    assert isinstance(data, dict)
    assert "datasets" in data

    ds = catalog.get("donations")
    assert ds is not None, ds
    assert ds.name == "donations"

    with TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "dataset.json"
        with open(path, "w") as fh:
            json.dump(ds.to_dict(), fh, indent=2)

        ds_load = Dataset.from_path(path)
        assert ds_load.name == ds.name
        assert ds_load.title == ds.title


def test_dataset_aleph_metadata(catalog_data: Dict[str, Any]):
    catalog = DataCatalog(Dataset, catalog_data)
    ds = catalog.require("leak")
    assert ds.category == "leak"
    assert ds.coverage is not None
    assert ds.coverage.frequency == "never"

    # invalid metadata
    with pytest.raises(MetadataException):
        meta = {
            "name": "invalid",
            "title": "Invalid metadata",
            "coverage": {"frequency": "foo"},
        }
        ds = Dataset(meta)


def test_dataset_name_validation():
    with pytest.raises(MetadataException):
        Dataset({"name": "my dataset"})
    with pytest.raises(MetadataException):
        Dataset({"name": "my-dataset"})
    with pytest.raises(MetadataException):
        Dataset({"name": "My_dataset"})
    with pytest.raises(MetadataException):
        Dataset({"name": "_test"})
    with pytest.raises(MetadataException):
        Dataset({"name": "ä_dataset"})
    with pytest.raises(MetadataException):
        Dataset({"name": "another.invalid.name"})
