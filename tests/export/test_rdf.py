import os
from unittest import TestCase
from tempfile import mkstemp

from followthemoney import model
from followthemoney.export.rdf import RDFExporter


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


class ExcelExportTestCase(TestCase):

    def setUp(self):
        _, self.temp = mkstemp(suffix='.rdf')

    def tearDown(self):
        os.unlink(self.temp)

    def test_rdf_export(self):
        fh = open(self.temp, 'w+')
        entity = model.get_proxy(ENTITY)
        exporter = RDFExporter(fh)
        exporter.write(entity)
        exporter.finalize()
        fh.seek(0)
        data = fh.readlines()
        assert len(data) == 8, len(data)
