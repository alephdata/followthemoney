from unittest import TestCase

from followthemoney import model
from followthemoney.export.excel import get_workbook, write_entity


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
    def test_excel_export(self):
        entity = model.get_proxy(ENTITY)
        workbook = get_workbook()
        write_entity(
            workbook, entity, extra_headers=['source'],
            extra_fields={'source': 'test'}
        )
        self.assertListEqual(workbook.sheetnames, ['People'])
        sheet = workbook["People"]
        rows = list(sheet)
        self.assertListEqual(
            [cell.value for cell in rows[0]],
            ['id', 'source'] +
            [prop.label for prop in entity.schema.sorted_properties]
        )
        self.assertListEqual(
            [cell.value for cell in rows[1][:3]],
            ['person', 'test', 'Ralph Tester']
        )
