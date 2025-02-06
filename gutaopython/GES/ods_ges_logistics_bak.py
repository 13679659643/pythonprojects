# -*- coding: utf-8 -*-
# @Time    : 2024/7/29 15:47
# @Author  : gutao
# @Email   : 571182073@qq.com
# @File    :
# @Software:
import requests

# 1.发送 HTTP 请求：支持各种 HTTP 方法，如 GET、POST、PUT、DELETE、HEAD、OPTIONS 等。
# 2.处理响应：能够轻松处理服务器返回的响应，包括获取响应状态码、响应头和响应内容。
# 3.处理 URL 参数：能够方便地处理查询参数和 URL 编码。
# 4.会话管理：支持会话对象，可以在多个请求之间保持会话（例如，保持 cookies）。
# 5.文件上传：支持文件上传。
# 6.认证：支持多种认证方式，如基本认证、OAuth 等。
# 7.超时和重试：可以设置请求的超时时间和重试策略。


session = requests.session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}
session.headers = headers
json_data = {
    'username': '泉州凤翎商贸有限公司',
    'password': '123456',
}

response = session.post(
    'http://xmdfhq.nextsls.com/rest/tms/wos/auth/login',
    json=json_data
)

# crtl+alt+l格式化
# print(type(rsp.text))  type 判断类型
# print(type(response.json()))
# print(response.json())
json_data = response.json()


# token_rowB=data_rowA.get('data',{}).get('token') 没有键值就会是None
# data_rowA.get('data')
# token_data=token_rowB['token']
# print(token_rowB)
token_data = json_data['data']['token']
session.headers['token'] = token_data
# print(type(response.json()))
# # print(token_data)
# exit()
# headers = {
#     'Accept': 'application/json',
#     'Accept-Language': 'zh-CN,zh;q=0.9',
#     'Connection': 'keep-alive',
#     'Content-Type': 'application/json;charset=utf-8',
#     'Origin': 'http://xmdfhq.nextsls.com',
#     'Referer': 'http://xmdfhq.nextsls.com/tms/wos/home',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
#     'token': token_data,
# }
# cookies = {'token': token_data}
json_data = {
    'timeLimit': 0,
    'page': 1,
    'activeTab': 'all',
    'scenes': 1,
}
response = session.post('http://xmdfhq.nextsls.com/rest/tms/wos/shipment/lists', json=json_data,
                         # cookies=cookies
                         )

print(response.json())
