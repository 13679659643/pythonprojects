# -*- coding: utf-8 -*-
# @Time    : 2025/1/7 10:52
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:
import os
package_dir = os.path.dirname(os.path.abspath(__file__))


def get_file_path(filename):
    return os.path.join(package_dir, filename)