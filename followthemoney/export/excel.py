from openpyxl import Workbook


def get_workbook():
    workbook = Workbook()
    workbook.remove_sheet(workbook.active)
    return workbook


def get_sheet(schema, workbook):
    try:
        sheet = workbook.get_sheet_by_name(name=schema.plural)
    except KeyError:
        sheet = workbook.create_sheet(title=schema.plural)
        fieldnames = [prop.label for prop in schema.sorted_properties]
        fieldnames = ['id', ] + fieldnames
        sheet.append(fieldnames)
    return sheet


def write_entity(sheet, entity):
    prop_dict = {'id': entity.id}
    for prop in entity.schema.sorted_properties:
        prop_dict[prop.label] = prop.type.join(entity.get(prop))
    sheet.append(list(prop_dict.values()))
