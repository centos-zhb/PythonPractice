# -*- coding:utf-8 -*-
from selenium import webdriver

driver = webdriver.Firefox()
driver.get('https://www.baidu.com')
driver.close()