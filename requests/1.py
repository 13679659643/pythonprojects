import requests

# 导入了 PIL 库的 Image 模块，该模块提供了图像处理功能
from PIL import Image
# io 库的 BytesIO 模块，该模块提供了在内存中读写字节流的功能
from io import BytesIO
r1 = requests.get('https://img.alicdn.com/imgextra/i3/O1CN018EXXuz1ETiZM8aowr_!!6000000000353-2-tps-192-192.png')
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