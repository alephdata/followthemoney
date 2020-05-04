from unittest import TestCase

from followthemoney import model
from followthemoney.export.misp import MISPExporter

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


class MISPExportTestCase(TestCase):

    def test_misp_simple(self):
        exporter = MISPExporter()
        for entity in ENTITIES:
            proxy = model.get_proxy(entity)
            exporter.add_entity(proxy)

        exporter.write_graph()

        # Test all objects imported
        self.assertEqual(len(exporter.misp_objects), 3, len(exporter.misp_objects))
        # Test using the right template
        self.assertEqual(exporter.misp_objects[0].name, 'ftm-Person', exporter.misp_objects[0].name)
        self.assertEqual(exporter.misp_objects[1].name, 'ftm-Sanction', exporter.misp_objects[1].name)
        self.assertEqual(exporter.misp_objects[2].name, 'ftm-Company', exporter.misp_objects[2].name)
        # Test all expected attributes are loaded
        self.assertEqual(len(exporter.misp_objects[0].attributes), 7, len(exporter.misp_objects[0].attributes))
        # Test relationship Person -> Company
        self.assertEqual(exporter.misp_objects[0].references[0].referenced_uuid, exporter.misp_objects[2].uuid)
        # Test relationship Sanction -> Person
        self.assertEqual(exporter.misp_objects[1].references[0].referenced_uuid, exporter.misp_objects[0].uuid)
