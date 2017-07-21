# coding=utf-8
import requests
import json

__author__ = 'Veryci'

def get_demo():
    '''
    requests 的get方法演示，不带参数
    by:Veryci
    :return: 
    '''
    url = 'http://alpha.veryci.cc:3061/#!/login'
    params = dict(
        email = '13263297387',
        password = '123456',
    )
    res = requests.post(url,data=params)
    print(res.text)

if __name__ == '__main__':
    get_demo()