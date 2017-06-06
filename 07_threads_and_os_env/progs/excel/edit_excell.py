import xlrd
from xlutils.copy import copy

rb = xlrd.open_workbook('example.xls', on_demand=True, formatting_info=True)
wb = copy(rb)
wb.save("final_complete.xls")