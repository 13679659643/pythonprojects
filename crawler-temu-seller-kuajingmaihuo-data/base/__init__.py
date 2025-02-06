# -*- coding: utf-8 -*-
# @Time    : 2024/12/31 17:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:

import os
package_dir = os.path.dirname(os.path.abspath(__file__))


def get_file_path(filename):
    return os.path.join(package_dir, filename)