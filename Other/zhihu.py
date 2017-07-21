# coding=utf-8
import requests

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36',
}
url = "http://daily.zhihu.com"
res = requests.get(url,headers=headers).text

print(res)
