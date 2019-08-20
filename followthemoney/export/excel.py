from io import BytesIO
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font, PatternFill

from followthemoney.export.common import Exporter


class ExcelWriter(object):
    HEADER_FONT = Font(bold=True, color='FFFFFF')
    HEADER_FILL = PatternFill(start_color='982022',
                              end_color='982022',
                              fill_type='solid')

    def __init__(self):
        self.workbook = Workbook(write_only=True)

    def make_sheet(self, title, headers):
        sheet = self.workbook.create_sheet(title=title)
        sheet.freeze_panes = 'A2'
        sheet.sheet_properties.filterMode = True
        cells = []
        for header in headers:
            cell = WriteOnlyCell(sheet, value=header)
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cells.append(cell)
        sheet.append(cells)
        return sheet

    def get_bytesio(self):
        buffer = BytesIO()
        self.workbook.save(buffer)
        buffer.seek(0)
        return buffer


class ExcelExporter(ExcelWriter, Exporter):

    def __init__(self, file_path, extra=None):
        super(ExcelExporter, self).__init__()
        self.file_path = file_path
        self.extra = extra or []
        self.sheets = {}

    def write(self, proxy, extra=None, **kwargs):
        if proxy.schema not in self.sheets:
            title = proxy.schema.plural
            headers = ['ID']
            headers.extend(self.extra)
            for prop in proxy.schema.sorted_properties:
                headers.append(prop.label)
            sheet = self.make_sheet(title, headers)
            self.sheets[proxy.schema] = sheet
        sheet = self.sheets.get(proxy.schema)
        cells = [proxy.id]
        cells.extend(extra or [])
        for prop in proxy.schema.sorted_properties:
            cells.append(prop.type.join(proxy.get(prop)))
        sheet.append(cells)

    def finalize(self):
        self.workbook.save(self.file_path)
