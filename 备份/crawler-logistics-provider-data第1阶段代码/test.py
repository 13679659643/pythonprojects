# -*- coding: utf-8 -*-
# @Time    : 2024/9/7 16:09
# @Author  : Night
# @File    : test.py
# @Description:
from PIL import Image

# 打开图片
img = Image.open("img.png")

# 调整大小
new_size = (1200, 600)  # 替换为你想要的宽度和高度
img = img.resize(new_size, Image.LANCZOS)

# 保存图片
img.save("resized_image.png")
