# -*- coding: utf-8 -*-
# @Time    : 2024/7/27 17:34
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    : 
# @Software:
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}
json_data = {
    'username': '泉州凤翎商贸有限公司',
    'password': '123456',
}

response = requests.post('http://xmdfhq.nextsls.com/rest/tms/wos/auth/login', headers=headers, json=json_data)
json_data = response.json()

# token_rowB=data_rowA.get('data',{}).get('token') 没有键值就会是None
token = json_data['data']['token']  # data_rowA.get('data')
# token_data=token_rowB['token']
# print(token_rowB)
print(token)
exit()
headers = {
    'Accept': 'application/json',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=utf-8',
    # 'Cookie': '_identity-os_wos=c5f3935b3e363cb0940291ccc20acbae3a82114a27026505158add66d07411d1a%3A2%3A%7Bi%3A0%3Bs%3A16%3A%22_identity-os_wos%22%3Bi%3A1%3Bs%3A45%3A%22%5B%2265d8542f84809c48130c6e56%22%2C%22ddd%22%2C1722108948%5D%22%3B%7D;',
    'Referer': 'http://xmdfhq.nextsls.com/tms/wos/home',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'token': 'qji8btdd8l2li1n5smh8r2ofd3',
}
# cookies={'os_wos':'qji8btdd8l2li1n5smh8r2ofd3','_identity-os_wos':'c5f3935b3e363cb0940291ccc20acbae3a82114a27026505158add66d07411d1a'}
# response = requests.get('http://xmdfhq.nextsls.com/rest/tms/wos/home/announcement?conditions=%7', headers=headers,cookies=cookies)
cookies = {'token': token}
response = requests.post('http://xmdfhq.nextsls.com/rest/tms/wos/home/lists', headers=headers, cookies=cookies)

print(response.json())
