# -*- coding:utf-8 -*-
import requests

def baidu_func(url):
    headers = {}
    params = {}
    req = requests.post(url,headers=headers,params = params)
    print(req.text)

if __name__ == '__main__':
    url = "http://www.baidu.com"
    baidu_func(url)