# -*- coding:utf-8 -*-
from selenium import webdriver
import unittest,xlwt,xlrd,time
from xlutils.copy import copy
from selenium.webdriver.common.by import By
class Login(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.baseurl = "http://alpha.veryci.cc:3061"
    def testGetExcel(self,excel_path):
        """
        该函数主要是获取需要读取数据的excel，如果找到就返回该excel，如果找不到给出提示信息
        :param excelfile: 
        :return: 
        """
        data = xlrd.open_workbook(excel_path)  #获取通过excel路径工作表
        table = data.sheets()[0]  #制定需要操作的excel的sheet
        return table  #返回需要操作的excel的sheet
    def testGetRows(self):
        """
        该方法主要是得到要读取数据的excel的行
        :return: 
        """
        table = self.testGetExcel("D:\\testfile\\sbmlogin.xlsx")
        if table:
            rows = table.nrows
            print("该文档的有%i行"%rows)
            return rows
        else:
            print("该excel文件不存在")
    def testGetCols(self):
        """
        该方法主要是得到要读取数据的excel的列
        :return: 
        """
        table = self.testGetExcel("D:\\testfile\\sbmlogin.xlsx")
        if table:
            cols = table.ncols
            print("该文档的有%i行"%cols)
            return cols
        else:
            print("该excel文件不存在")
    def testGetLoginDict(self):
        """
        该方法主要是得到要读取数据的excel的列
        :return: 
        """
        table = self.testGetExcel("D:\\testfile\\sbmlogin.xlsx")
        logindict = {}  #定义一个字典
        rows = self.testGetRows()
        rows = int(rows)
        cols = self.testGetCols()
        cols = int(cols)
        for i in range(1,rows):
            for m in range(cols-1):
                logindict[table.cell(i,m).value] = table.cell(i,i).value
        return list(logindict.items())
    def testLoginin(self):
        resultlist = []  #定义一个测试结果的列表
        truee = u'登录成功'
        faile = u'登录失败'
        driver = self.driver
        driver.get(self.baseurl)
        loginlist = self.testGetLoginDict()
        print(loginlist)
        driver.find_element_by_link_text(u'登录').click()
        print(driver.current_url)
        for k,v in loginlist:
            driver.find_element_by_name('email').send_keys(k)
            driver.find_element_by_name('password').send_keys(v)
        driver.find_element_by_xpath('//*[@id="hampshire-web-ui"]/div/div[2]/div/div/form/div[1]/div[3]').click()
        time.sleep(10)
        if driver.current_url == "http://alpha.veryci.cc:3061":
            resultlist.append(truee)
            resultlist.append(driver.current_url)
            self.testWriteData(resultlist)
        else:
            print(faile)
            resultlist.append(faile)
            self.testWriteData(resultlist)
    def testWriteData(self,result):
        rb = xlrd.open_workbook("D:\\testfile\\sbmloginqqq.xlsx")
        wb = copy(rb)
        wbk = wb.get_sheet(0)
        for i in range(len(result)):
            wbk.write(0,i,result[i])
        wb.save("D:\\testfile\\sbmloginqqq.xlsx")
    def tearDown(self):
        pass
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(Login("testLoginin"))
    runner = unittest.TextTestRunner()
    runner.run(suite)