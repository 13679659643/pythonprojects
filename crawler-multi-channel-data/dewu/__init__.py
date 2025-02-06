# -*- coding: utf-8 -*-
# @Time    : 2024/12/10 10:26
# @Author  : Night
# @File    : __init__.py.py
# @Description:
import os
package_dir = os.path.dirname(os.path.abspath(__file__))


def get_file_path(filename):
    return os.path.join(package_dir, filename)