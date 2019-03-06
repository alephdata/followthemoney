from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


def get_workbook():
    workbook = Workbook()
    workbook.remove_sheet(workbook.active)
    return workbook


def get_sheet(schema, workbook, extra_headers=list()):
    try:
        sheet = workbook.get_sheet_by_name(name=schema.plural)
    except KeyError:
        sheet = workbook.create_sheet(title=schema.plural)
        fieldnames = [prop.label for prop in schema.sorted_properties]
        fieldnames = ['id', ] + extra_headers + fieldnames
        sheet.append(fieldnames)
    return sheet


def write_entity(sheet, entity, extra_fields=dict()):
    prop_dict = {
        'id': entity.id,
        **extra_fields
    }
    for prop in entity.schema.sorted_properties:
        prop_dict[prop.label] = prop.type.join(entity.get(prop))
    sheet.append(list(prop_dict.values()))


def get_workbook_content(workbook):
    return save_virtual_workbook(workbook)
