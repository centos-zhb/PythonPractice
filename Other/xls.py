# --*-- coding:utf-8 --*--
import xlrd

wb = xlrd.open_workbook("d://DataProvider.xlsx")
sh = wb.sheet_by_index(0)
cellName = sh.cell(0,0).value
print(cellName)
