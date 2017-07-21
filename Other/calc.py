#!/usr/bin/env python

import json

#Python 字典类型转换为JSON对象
data = {
    'no':1,
    'name':'dongcoder',
    'url':'http://www.bubuko.com'
}

json_str = json.dumps(data)
print("Python原始数据：",repr(data))
print("JSON对象：",json_str)

#将JSON对象转换为Python字典
data2 = json.loads(json_str)
print ("data2['name']: ", data2['name'])
print ("data2['url']: ", data2['url'])