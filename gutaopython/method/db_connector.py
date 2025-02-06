# -*- coding: utf-8 -*-
# @Time    : 2024/7/30 17:57
# @Author  : gutao
# @Email   : 1370391119@qq.com
# @File    : 
# @Software:

# db_connector.py

import pymysql
from pymysql import MySQLError


def connect_to_database(host, port, user, password, database):
    try:
        # 连接到 MySQL 数据库
        db_connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        print("连接成功")
        return db_connection
    except MySQLError as e:
        print(f"连接失败: {e}")
        return None

