# -*- coding: utf-8 -*-
# @Time    : 2024/7/27 17:46
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    : 
# @Software:
import requests

cookies = {
    'os_wos': 'qji8btdd8l2li1n5smh8r2ofd3',
    '_identity-os_wos': 'c5f3935b3e363cb0940291ccc20acbae3a82114a27026505158add66d07411d1a%3A2%3A%7Bi%3A0%3Bs%3A16%3A%22_identity-os_wos%22%3Bi%3A1%3Bs%3A45%3A%22%5B%2265d8542f84809c48130c6e56%22%2C%22ddd%22%2C1722108948%5D%22%3B%7D',
    'token': 'qji8btdd8l2li1n5smh8r2ofd3',
}

headers = {
    'Accept': 'application/json',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=utf-8',
    # 'Cookie': 'os_wos=qji8btdd8l2li1n5smh8r2ofd3; _identity-os_wos=c5f3935b3e363cb0940291ccc20acbae3a82114a27026505158add66d07411d1a%3A2%3A%7Bi%3A0%3Bs%3A16%3A%22_identity-os_wos%22%3Bi%3A1%3Bs%3A45%3A%22%5B%2265d8542f84809c48130c6e56%22%2C%22ddd%22%2C1722108948%5D%22%3B%7D; token=qji8btdd8l2li1n5smh8r2ofd3',
    'Origin': 'http://xmdfhq.nextsls.com',
    'Referer': 'http://xmdfhq.nextsls.com/tms/wos/home',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    #'token': 'qji8btdd8l2li1n5smh8r2ofd3',
}

json_data = {}

response = requests.post(
    'http://xmdfhq.nextsls.com/rest/tms/wos/home/lists',
    #cookies=cookies,
    headers=headers,
    json=json_data,
    verify=False,
)
print(response.json())