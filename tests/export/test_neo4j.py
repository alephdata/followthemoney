import io
import csv
import shutil
from tempfile import mkdtemp
from unittest import TestCase

from followthemoney import model
from followthemoney.export.neo4j import CypherGraphExporter
from followthemoney.export.neo4j import Neo4JCSVExporter
from followthemoney.export.graph import edge_types

ENTITIES = [
    {
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
    },
    {
        'id': 'sanction',
        'schema': 'Sanction',
        'properties': {
            'entity': 'person',
            'program': 'Hateys'
        }
    },
    {
        'id': 'company',
        'schema': 'Company',
        'properties': {
            'name': 'Ralph Industries, Inc.',
        }
    },
    {
        'id': 'owner',
        'schema': 'Ownership',
        'properties': {
            'startDate': '2003-04-01',
            'owner': 'person',
            'asset': 'company'
        }
    }
]


class CypherExportTestCase(TestCase):

    def test_cypher_simple(self):
        sio = io.StringIO()
        exporter = CypherGraphExporter(sio)
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        value = sio.getvalue()
        assert 'entity:company' in value, value
        assert 'startDate: "2003-04-01"' in value, value
        assert 'tel:+12025557612' not in value, value

    def test_cypher_full(self):
        sio = io.StringIO()
        exporter = CypherGraphExporter(sio, edge_types=edge_types())
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.write(proxy)

        value = sio.getvalue()
        assert 'entity:company' in value, value
        assert 'tel:+12025557612' in value, value


class Neo4JCSVTestCase(TestCase):

    def setUp(self):
        self.outdir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.outdir)

    def test_csv_export(self):
        exporter = Neo4JCSVExporter(self.outdir, extra=['source'],
                                    edge_types=edge_types())
        for entity in ENTITIES:
            entity = model.get_proxy(entity)
            exporter.write(entity, extra=['test'])
            fh, writer = exporter.handles[entity.schema]
            outfile = fh.name
        exporter.finalize()
        fh = open(outfile, 'r')
        csv_reader = csv.reader(fh)
        rows = list(csv_reader)
        headers = rows[0]
        assert ':TYPE' in headers, headers
        assert ':START_ID' in headers, headers
        assert ':END_ID' in headers, headers
        assert 'id' in headers, headers
        assert 'date' in headers, headers
        data = rows[1]
        assert 'OWNERSHIP' in data, data
        assert '2003-04-01' in data, data
