# -*- coding:utf-8 -*-
import xlrd,time
from selenium import webdriver

class Excelutil:

    def __init__(self,excel_path,sheet_name):
        self.data = xlrd.open_workbook(excel_path)
        self.table = self.data.sheet_by_name(sheet_name)
        #获取第一行作为key值
        self.keys = self.table.row_values(0)
        # 获取总行数
        self.rowNum = self.table.nrows
        # 获取总列数
        self.colNum = self.table.ncols

    def dict_data(self):
        if self.rowNum <= 1:
            print("总行数小于1")
        else:
            r = []
            j = 1
            for i in range(self.rowNum - 1):
                s = {}
                # 从第二行取对应的values值
                values = self.table.row_values(j)
                for x in range(self.colNum):
                    values[x] = int(values[x])
                    s[self.keys[x]] = values[x]
                r.append(s)
                j += 1
            return r

if __name__ == '__main__':
    excelpath = "D:\\testfile\\smblogin.xlsx"
    sheetname = "Sheet1"
    data = Excelutil(excelpath,sheetname)
    print(data.dict_data())
    for i in data.dict_data():
        print(i)
        user = list(i.values())[list(i.keys()).index('username')]
        pwd = list(i.values())[list(i.keys()).index('password')]
        print(user,pwd)
        driver = webdriver.Chrome()
        driver.implicitly_wait(30)
        driver.get("http://alpha.veryci.cc:3061")
        #点击登录按钮
        driver.find_element_by_link_text("登录").click()
        time.sleep(2)
        driver.find_element_by_name("email").send_keys(user)
        time.sleep(2)
        driver.find_element_by_name("password").send_keys(pwd)
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="hampshire-web-ui"]/div/div[2]/div/div/form/div[1]/div[3]').click()
        driver.close()
