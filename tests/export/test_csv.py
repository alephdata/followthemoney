import io
import csv
from unittest import TestCase

from followthemoney import model
from followthemoney.export.csv import write_headers, write_entity


ENTITY = {
    'id': 'person',
    'schema': 'Person',
    'properties': {
        'name': 'Ralph Tester',
        'birthDate': '1972-05-01',
        'idNumber': ['9177171', '8e839023'],
        'website': 'https://ralphtester.me',
        'phone': '+12025557612',
        'email': 'info@ralphtester.me'
    }
    }


class CSVExportTestCase(TestCase):
    def test_csv_export(self):
        entity = model.get_proxy(ENTITY)
        buff = io.StringIO()
        write_headers(buff, entity.schema, extra_headers=['source'])
        write_entity(buff, entity, extra_fields={'source': 'test'})

        buff.seek(0)
        csv_reader = csv.reader(buff, delimiter=',')
        rows = list(csv_reader)
        self.assertListEqual(
            rows[0],
            ['id', 'source'] +
            [prop.label for prop in entity.schema.sorted_properties]
        )
        self.assertListEqual(rows[1][:3], ['person', 'test', 'Ralph Tester'])
