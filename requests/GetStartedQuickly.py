import requests

# 7、定制请求头
from requests.auth import HTTPBasicAuth
url = 'https://api.github.com/some/endpoint'
headers = {'user-agent': 'my-app/0.0.1'}
r1 = requests.get(url, headers=headers)
# A.用户认证信息的优先级：
# 在 .netrc 文件中设置了用户认证信息
# 但是在这个请求中，我们设置了 auth 参数,基础的 HTTP 身份验证方法，它通过在 HTTP headers 中添加一个 Authorization 字段来传递用户名和密码。
r2 = requests.get('https://api.github.com/user', auth=HTTPBasicAuth('user', 'pass'))
# 因此，.netrc 文件中的设置会被忽略，使用我们在这里设置的 auth 参数

print(r2.json())
exit()



# 6、原始响应内容
r1 = requests.get('https://api.github.com/events', stream=True)
# # <urllib3.response.HTTPResponse object at 0x0000023C84FDE670>
# r1.raw
print(r1.raw)
# 读取前 5 个字节
r1.raw.read(5)
# 第 11 到 20 个字节
print(r1.raw.read(5))
url = 'https://api.github.com/events'
filename = '6'
chunk_size = 1024  # 每次读取 1KB 的数据
try:
    r1 = requests.get(url, stream=True)
    r1.raise_for_status()  # 检查请求是否成功

    # 不要在这里直接对 r1.raw 操作，因为这可能会影响后续的 iter_content 读取
    # 而是直接使用 iter_content 进行分块读取
    with open(filename, 'wb') as fd:
        for chunk in r1.iter_content(chunk_size):
            fd.write(chunk)

except requests.exceptions.RequestException as e:
    print(f"下载过程中出现错误: {e}")


# 5、JSON 响应内容

r1 = requests.get('https://api.github.com/events')
# [{u'repository': {u'open_issues': 0, u'url': 'https://github.com/..
# 成功调用，并不意味着响应的成功。有的服务器会在失败的响应中包含一个 JSON 对象（比如 HTTP 500 的错误细节）
r1.json()
# 使用 r.raise_for_status() 或者检查 r.status_code 是否和你的期望相同
print(r1.status_code)



# 4、二进制响应内容

# 导入了 PIL 库的 Image 模块，该模块提供了图像处理功能
from PIL import Image
# io 库的 BytesIO 模块，该模块提供了在内存中读写字节流的功能
from io import BytesIO
r1 = requests.get('https://api.github.com/events')
# unicode 字符集： u'[{"repository":{"open_issues":0,"url":"https://github.com/...
print(r1.text)
# 字节的方式访问请求响应体，对于非文本请求：b'[{"repository":{"open_issues":0,"url":"https://github.com/...
print(r1.content)
i = Image.open(BytesIO(r1.content))
# 显示图像
i.show()
# 将RGBA 模式的图像转换为 RGB 模式
i = i.convert('RGB')
# RGB模式才能将图像保存为 JPEG 文件。
i.save('yida.jpg')


# 3、响应内容

r1 = requests.get('https://api.github.com/events')
# list
print(type(r1.json()))
# str
print(type(r1.text))
# utf-8   r1.encoding = 'ISO-8859-1'直接可以更改
print(r1.encoding)


# 2、传递url参数：字典里值为 None 的键都不会被添加到 URL 的查询字符串里。

payload = {'key1': 'value1', 'key2': 'value2'}
r1 = requests.get("http://httpbin.org/get", params=payload)
# 列表作为值传入：http://httpbin.org/get?key1=value1&key2=value2&key2=value3
payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
r2 = requests.get('http://httpbin.org/get', params=payload)


# 1、获取Github的公共时间线

r1 = requests.get('https://api.github.com/events')
r2 = requests.post('http://httpbin.org/post', data={'key': 'value', 'key1': 'value1'})
r3 = requests.put('http://httpbin.org/put', data={'key': 'value'})
r4 = requests.delete('http://httpbin.org/delete')
r5 = requests.head('http://httpbin.org/get')
r6 = requests.options('http://httpbin.org/get')
"""
这些请求都是使用 Python 的 `requests` 库发出的 HTTP 请求，但每个请求的类型和目标 URL 不同。下面是每个请求的简单概述：
1. `r = requests.get('https://api.github.com/events')`: 这是一个 GET 请求，用于从 GitHub 的 API 获取最近的公共事件。
2. `r1 = requests.post('http://httpbin.org/post', data={'key': 'value', 'key1': 'value1'})`: 这是一个 POST 请求，发送到 httpbin.org 的 /post 端点。POST 请求通常用于向服务器发送数据。在这个例子中，发送的数据是一个包含两个键值对的字典。
3. `r2 = requests.put('http://httpbin.org/put', data={'key': 'value'})`: 这是一个 PUT 请求，发送到 httpbin.org 的 /put 端点。PUT 请求通常用于更新服务器上的资源。在这个例子中，发送的数据是一个包含一个键值对的字典。
4. `r3 = requests.delete('http://httpbin.org/delete')`: 这是一个 DELETE 请求，发送到 httpbin.org 的 /delete 端点。DELETE 请求通常用于删除服务器上的资源。
5. `r4 = requests.head('http://httpbin.org/get')`: 这是一个 HEAD 请求，发送到 httpbin.org 的 /get 端点。HEAD 请求与 GET 请求类似，但服务器只返回 HTTP 头部，不返回消息主体。这对于检查链接的有效性或获取资源的元数据（如大小、修改日期等）很有用。
6. `r5 = requests.options('http://httpbin.org/get')`: 这是一个 OPTIONS 请求，发送到 httpbin.org 的 /get 端点。OPTIONS 请求用于获取目标资源支持的通信选项。
在这些例子中，所有的请求都返回一个 Response 对象，你可以使用这个对象来访问服务器的响应，包括 HTTP 状态码、响应头和响应体。例如，`r.status_code` 会返回 GET 请求的 HTTP 状态码，`r.text` 或 `r.json()` 会返回响应体。
"""

