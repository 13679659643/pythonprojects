# -*- coding: utf-8 -*-
# @Time    : 2024/7/29 17:07
# @Author  : gutao
# @Email   : 571182073@qq.com
# @File    : 
# @Software:
import requests
import redis

# 1.发送 HTTP 请求：支持各种 HTTP 方法，如 GET、POST、PUT、DELETE、HEAD、OPTIONS 等。
# 2.处理响应：能够轻松处理服务器返回的响应，包括获取响应状态码、响应头和响应内容。
# 3.处理 URL 参数：能够方便地处理查询参数和 URL 编码。
# 4.会话管理：支持会话对象，可以在多个请求之间保持会话（例如，保持 cookies）。
# 5.文件上传：支持文件上传。
# 6.认证：支持多种认证方式，如基本认证、OAuth 等。
# 7.超时和重试：可以设置请求的超时时间和重试策略。
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

session = requests.session()
#
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
# }
# session.headers = headers
# json_data = {
#     'username': '道诚',
#     'password': 'DC123',
# }
#
# response = session.post(
#     'http://auasian.nextsls.com/rest/tms/wos/auth/login',
#     json=json_data
# )
#
# json_data = response.json()
# token_data = json_data['data']['token']
# redis_client.set('auasian_auth_token', token_data)

redis_token_data = redis_client.get('auasian_auth_token')
session.headers['token'] = redis_token_data

json_data = {
    'timeLimit': 0,
    'page': 1,
    'activeTab': 'all',
    'scenes': 1,
}
response = session.post('http://auasian.nextsls.com/rest/tms/wos/shipment/lists', json=json_data,
                        )

print(response.json())
