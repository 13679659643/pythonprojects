# -*- coding: utf-8 -*-
# @Time    : 2024/7/29 15:47
# @Author  : gu tao
# @Email   : 571182073@qq.com
# @File    : 
# @Software:
import json

import requests
import redis
import pymysql
from pymysql import MySQLError
from method.db_connector import connect_to_database
from datetime import datetime
import pandas as pd

# 1.发送 HTTP 请求：支持各种 HTTP 方法，如 GET、POST、PUT、DELETE、HEAD、OPTIONS 等。
# 2.处理响应：能够轻松处理服务器返回的响应，包括获取响应状态码、响应头和响应内容。
# 3.处理 URL 参数：能够方便地处理查询参数和 URL 编码。
# 4.会话管理：支持会话对象，可以在多个请求之间保持会话（例如，保持 cookies）。
# 5.文件上传：支持文件上传。
# 6.认证：支持多种认证方式，如基本认证、OAuth 等。
# 7.超时和重试：可以设置请求的超时时间和重试策略。

# 在 redis-py 库中，decode_responses=True 参数的作用是将从 Redis 返回的字节数据自动解码为 Python 字符串。
# 默认情况下，Redis 返回的数据是字节类型（bytes），如果设置了 decode_responses=True，则返回的数据会被解码为字符串（str）。
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 创建一个 session 对象
session = requests.session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}
# 设置会话对象的 headers 属性
session.headers = headers

# 返回 Redis 中 名称为key的string的value
redis_token_data = redis_client.get('auth_token')

if not redis_token_data:
    json_data = {
        'username': '泉州凤翎商贸有限公司',
        'password': '123456',
    }
    response = session.post(
        'http://xmdfhq.nextsls.com/rest/tms/wos/auth/login',
        json=json_data
    )

    json_data = response.json()
    token_data = json_data['data']['token']
    # 将 token 存储到 Redis 中,并设置过期时间为86400s即1天
    redis_client.set('auth_token', token_data, ex=86400)
    # 返回 Redis 中 名称为key的string的value
    redis_token_data = redis_client.get('auth_token')
    # 设置 HTTP 头中的 'token' 字段
    session.headers['token'] = redis_token_data
else:
    # 如果 token 存在，直接从 Redis 中获取并设置到 headers 中
    session.headers['token'] = redis_token_data

# 发送后续请求
json_data = {
    'timeLimit': 0,
    'page': 1,
    'activeTab': 'all',
    'scenes': 1,
}

# requests.Session 对象允许你跨多个请求保持某些参数（如 headers、cookies 等）
# 当你在 session 对象上设置 headers 时，这些 headers 会在所有使用该 session 对象发送的请求中自动应用。
response = session.post('http://xmdfhq.nextsls.com/rest/tms/wos/shipment/lists', json=json_data,
                        )

# 获取响应 JSON 数据
ges_json_data = response.json()

# json字典转化为json字符串，再借助网站格式化输出，快速找得自己要的那一部分
# print(json.dumps(ges_json_data))


# 连接到 MySQL 数据库
db_params = {
    'host': '192.168.0.201',
    'port': 4000,
    'user': 'root',
    'password': 'DoocnProTidb200.',
    'database': 'ods'
}
# 调用连接函数:** 解包操作符用于将字典形式的参数传递给函数
db_connection = connect_to_database(**db_params)

if db_connection:
    # 如果连接成功，执行其他数据库操作:创建一个游标对象。游标对象用于执行SQL语句和获取结果。
    cursor = db_connection.cursor()

    # 数据库操作代码:三个双引号用于创建多行字符串
    create_table_query = """
    CREATE TABLE IF NOT EXISTS  ods.`ods_scg_wld_ges_logistics_trace_table_i_d_bak`(
        `id`                   varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT 'id',
        `dt`                   varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '采集日期',
        `shipment_id`          varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT 'FBA单号',
        `shipment_number`      varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '快递单号',
        `service`              varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '物流渠道',
        `to_address_name`      varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '收件人',
        `to_address_country`   varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '国家',
        `parcel_count`         varchar(20) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '件数',
        `declaration_value`    varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '价值',
        `client_weight`        varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '客户重量',
        `actual_weight`        varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '实重',
        `actual_volume_weight` varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '材重',
        `chargeable_weight`    varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '收费重',
        `sell_charge_amount`   varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '销售费用金额',
        `elec`                 varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '带电',
        `exportwith`           varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '报关方式',
        `taxwith`              varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '交税方式',
        `outer_carrier`        varchar(512) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '承运',
        `remark`               varchar(512) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',
        `depot_id`             varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '仓库id',
        `created`              varchar(50) COLLATE utf8mb4_general_ci   DEFAULT NULL COMMENT '下单时间',
        PRIMARY KEY (`shipment_id`) /*T![clustered_index] CLUSTERED */
    ) ENGINE = InnoDB
    DEFAULT CHARSET = utf8mb4
    COLLATE = utf8mb4_general_ci COMMENT ='ODS-GES物流数据-辜涛';
    """
    # 执行创建表语句
    cursor.execute(create_table_query)

    # 找到需要的数据列表
    ges_data = ges_json_data['data']['components']['gridView']['table']['dataSource']
    # 获取当前时间
    current_time = datetime.now()
    # print(type(ges_data))
    # print(ges_data)
    # exit()
    DELETE_table_query = """
    DELETE FROM ods.ods_scg_wld_ges_logistics_trace_table_i_d_bak;
    """
    cursor.execute(DELETE_table_query)

    # %s 作为占位符 不仅可以防止 SQL 注入，还能提高代码的清晰度和可维护性。
    insert_table_query = """
    INSERT INTO ods.ods_scg_wld_ges_logistics_trace_table_i_d_bak (`id`,
                                                                   `dt`,
                                                                   `shipment_id`,
                                                                   `shipment_number`,
                                                                   `service`,
                                                                   `to_address_name`,
                                                                   `to_address_country`,
                                                                   `parcel_count`,
                                                                   `declaration_value`,
                                                                   `client_weight`,
                                                                   `actual_weight`,
                                                                   `actual_volume_weight`,
                                                                   `chargeable_weight`,
                                                                   `sell_charge_amount`,
                                                                   `elec`,
                                                                   `exportwith`,
                                                                   `taxwith`,
                                                                   `outer_carrier`,
                                                                   `remark`,
                                                                   `depot_id`,
                                                                   `created`)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    # 准备批量插入的数据：这是一个列表推导式中的循环，item 是 data['data'] 列表中的每个字典（即每一条记录）
    # values 是一个包含多个元组的列表，每个元组对应一条要插入的记录
    values = [
        (
            item['id'],
            current_time,  # 添加当前时间 2024-07-31 17:37:01.038610
            item['shipment_id'],
            item['shipment_number'],
            item['service'],
            item['to_address_name'],
            item['to_address_country'],
            item['parcel_count'],
            item['declaration_value'],
            item['client_weight'],
            item['actual_weight'],
            item['actual_volume_weight'],
            item['chargeable_weight'],
            item['sell_charge_amount'],
            item['elec'],
            item['exportwith'],
            item['taxwith'],
            item['outer_carrier'],
            item['remark'],
            item['depot_id'],
            item['created']
        )
        # ges_data是一个列表，列表中的每个元素都是一个字典.这些字典表示需要插入数据库的每条记录
        for item in ges_data
    ]
    cursor.executemany(insert_table_query, values)

    try:
        # 执行批量插入
        cursor.executemany(insert_table_query, values)
        # 提交事务
        db_connection.commit()
        print("Data inserted successfully.")
    except MySQLError as e:
        print(f"Error during data insertion: {e}")
        # 回滚事务以防止数据不一致
        db_connection.rollback()

    finally:
        # 确保游标和数据库连接已关闭
        if cursor.is_closed:
            cursor.close()
        if db_connection.is_closed:
            db_connection.close()
        print("Database connection closed.")

else:
    print("无法连接到数据库")
