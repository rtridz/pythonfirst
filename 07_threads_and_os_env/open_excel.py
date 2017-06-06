import xlrd
file = xlrd.open_workbook('file.xls',formatting_info=True)
sheet = file.sheet_by_index(0)
for rownum in range(sheet.nrows):
row = sheet.row_values(rownum)
for cell in row:
print cell