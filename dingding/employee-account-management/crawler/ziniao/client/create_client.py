# -*- coding: utf-8 -*-
# @Time     : 2023/12/12 14:39
# @Author   : 刘云飞
# @Email    : yfliu@doocm.com
# @Project  : dsd_user_management
# @FileName : create_client.py

"""
功能说明:

"""
from crawler.ziniao.client.api_config import Config
from crawler.ziniao.common.OpenClient import OpenClient


def __create_client():
    """
    可以以导入模块的方式获得一个单例对象
    Example:
    from rpa.OpenApiConfig import client
    response = client.execute(request)
    """
    # 应用id
    app_id = Config.app_id
    # 应用私钥
    private_key = Config.private_key
    # 请求URL
    url = Config.url
    # 创建请求客户端
    return OpenClient(app_id, private_key, url)


client = __create_client()

