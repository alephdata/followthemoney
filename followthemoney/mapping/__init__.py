from followthemoney.mapping.sql import SQLSource
from followthemoney.mapping.csv import CSVSource
from followthemoney.mapping.query import QueryMapping
from followthemoney.exc import InvalidMapping


def get_source(mapping):
    """Select the appropriate mapper to execute the given mapping."""
    if 'database' in mapping.data:
        return SQLSource(mapping, mapping.data)
    elif 'csv_url' in mapping.data or 'csv_urls' in mapping.data:
        return CSVSource(mapping, mapping.data)
    raise InvalidMapping("Cannot determine mapping type")


__all__ = [QueryMapping, get_source]