# -*- coding: utf-8 -*-
# @Time    : 2024/12/9 17:52
# @Author  : ShiChun Li
# @Email   : 571182073@qq.com
# @File    : 
# @Software:

# from ._tidb import TidbConnector
# from ._redis import RedisClient
import os
package_dir = os.path.dirname(os.path.abspath(__file__))


def get_file_path(filename):
    return os.path.join(package_dir, filename)