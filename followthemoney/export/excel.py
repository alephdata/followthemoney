from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook


def get_workbook():
    workbook = Workbook()
    workbook.remove_sheet(workbook.active)
    return workbook


def write_entity(workbook, entity, extra_headers=None, extra_fields=None):
    if extra_headers is None:
        extra_headers = []
    try:
        sheet = workbook.get_sheet_by_name(name=entity.schema.plural)
    except KeyError:
        sheet = workbook.create_sheet(title=entity.schema.plural)
        fieldnames = [prop.label for prop in entity.schema.sorted_properties]
        fieldnames = ['id', ] + extra_headers + fieldnames
        sheet.append(fieldnames)
    if extra_fields is None:
        extra_fields = dict()
    prop_dict = {
        'id': entity.id,
        **extra_fields
    }
    for prop in entity.schema.sorted_properties:
        prop_dict[prop.label] = prop.type.join(entity.get(prop))
    sheet.append(list(prop_dict.values()))


def get_workbook_content(workbook):
    return save_virtual_workbook(workbook)
