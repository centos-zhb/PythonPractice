# -*- coding:utf-8 -*-
'''
手机号归属地查询
'''
from suds.client import Client

# 使用库suds_jurko: https://bitbucket.org/jurko/suds
# web service查询: http://www.webxml.com.cn/zh_cn/web_services.aspx

# 电话号码归属地查询
url = 'http://ws.webxml.com.cn/WebServices/MobileCodeWS.asmx?wsdl'
client = Client(url)
result = client.service.getMobileCodeInfo(13263297387)
print(result)