import csv
import shutil
from tempfile import mkdtemp
from unittest import TestCase

from followthemoney import model
from followthemoney.export.csv import CSVExporter


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

    def setUp(self):
        self.outdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.outdir)

    def test_csv_export(self):
        entity = model.get_proxy(ENTITY)
        exporter = CSVExporter(self.outdir, extra=['source'])
        exporter.write(entity, extra=['test'])
        fh, writer = exporter.handles[entity.schema]
        outfile = fh.name
        exporter.finalize()
        fh = open(outfile, 'r')
        csv_reader = csv.reader(fh)
        rows = list(csv_reader)
        props = exporter.exportable_properties(entity.schema)
        self.assertListEqual(
            rows[0],
            ['id', 'source'] +
            [prop.name for prop in props]
        )
        self.assertListEqual(rows[1][:3], ['person', 'test', 'Ralph Tester'])
