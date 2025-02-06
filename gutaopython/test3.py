# -*- coding: utf-8 -*-
# @Time    : 2024/7/29 15:47
# @Author  : gu tao
# @Email   : 1370391119@qq.com
# @File    :
# @Software:
import requests
import redis
from logistics_init.Dao import TimestampFormatter
from logistics_init.Dao import RegularExpressionHtml
from logistics_init.Dao import DatabaseConnector
from datetime import datetime
import concurrent.futures

# 1.发送 HTTP 请求：支持各种 HTTP 方法，如 GET、POST、PUT、DELETE、HEAD、OPTIONS 等。
# 2.处理响应：能够轻松处理服务器返回的响应，包括获取响应状态码、响应头和响应内容。
# 3.处理 URL 参数：能够方便地处理查询参数和 URL 编码。
# 4.会话管理：支持会话对象，可以在多个请求之间保持会话（例如，保持 cookies）。
# 5.文件上传：支持文件上传。
# 6.认证：支持多种认证方式，如基本认证、OAuth 等。
# 7.超时和重试：可以设置请求的超时时间和重试策略。

# 在 redis-py 库中，decode_responses=True 参数的作用是将从 Redis 返回的字节数据自动解码为 Python 字符串。
# 默认情况下，Redis 返回的数据是字节类型（bytes），如果设置了 decode_responses=True，则返回的数据会被解码为字符串（str）。

# decode_responses=True：自动将从 Redis 获取的字节数据解码为字符串，简化数据处理
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# 创建一个 session 对象
session = requests.session()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}
# 设置会话对象的 headers 属性
session.headers = headers

# 使用哈希存储多个键值对
folder = "crawler-deliverr-logistics"
subfolder = "common"
HASH_AUTH_TOKEN = f"{folder}:{subfolder}"
key = "ges_auth_token"

if not redis_client.exists(f"{folder}:{subfolder}:{key}"):
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
    # 设置哈希存储键值对：将 token 存储到 Redis 中
    redis_client.hset(HASH_AUTH_TOKEN, "ges_auth_token", token_data)
    # 使用单独的键存储过期时间：并设置过期时间为86400s即1天
    redis_client.setex(f"{HASH_AUTH_TOKEN}:{key}", 43200, "1")
    # 获取哈希字段的值：返回 Redis 中 名称为key的string的value
    redis_token_data = redis_client.hget(HASH_AUTH_TOKEN, "ges_auth_token")
    # 设置 HTTP 头中的 'token' 字段
    session.headers['token'] = redis_token_data
else:
    # 获取哈希中的键值：返回 Redis 中 名称为key的string的value
    redis_token_data = redis_client.hget(HASH_AUTH_TOKEN, "ges_auth_token")
    # 如果 token 存在，直接从 Redis 中获取并设置到 headers 中
    session.headers['token'] = redis_token_data

# 获取所有页的数据：
all_data = []


def fetch_page_data(page):
    try:
        # 发送后续请求:写在函数里面，避免共享变量在多线程环境下被意外修改或重用
        fetch_json_data = {
            'timeLimit': 0,
            'page': page,
            'activeTab': 'all',
            'isActiveTab': 'all',
            'scenes': 1,
        }
        # requests.Session 对象允许你跨多个请求保持某些参数（如 headers、cookies 等）
        # 当你在 session 对象上设置 headers 时，这些 headers 会在所有使用该 session 对象发送的请求中自动应用。
        response_data = session.post('http://xmdfhq.nextsls.com/rest/tms/wos/shipment/lists', json=fetch_json_data, )
        # 检查请求是否成功
        response_data.raise_for_status()
        # print(response_data.status_code)
        # print(page)
        return response_data.json()
    except requests.exceptions.RequestException as requests_e:
        print(f"Request failed for page {page}: {requests_e}")
        return None
    except ValueError as json_e:
        print(f"Failed to parse JSON for page {page}: {json_e}")
        return None


# 获取第一页，确定总页数
initial_response = fetch_page_data(1)

# 找到第一页的数据列表
ges_data = initial_response['data']['components']['gridView']['table']['dataSource']
all_data.extend(ges_data)
# 总条数
total_rows = initial_response['data']['components']['gridView']['table']['pagination']['total']
# 每页的条数
pageSize = initial_response['data']['components']['gridView']['table']['pagination']['pageSize']
# 分页数：// 符号表示整除操作，结果为整数
total_pages = (total_rows + pageSize - 1) // pageSize

# 使用多线程获取所有页的数据:创建线程池:使用 ThreadPoolExecutor 创建一个包含 10 个线程的线程池
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    # 使用列表推导式生成一个任务列表 futures，每个任务都是调用 fetch_page_data 函数获取特定页码的数据。
    # executor.submit(fetch_page_data, page) 提交任务到线程池，page 从 2 到 total_pages（因为第一页已经获取）
    futures = [executor.submit(fetch_page_data, page) for page in range(2, total_pages + 1)]
    # 使用 concurrent.futures.as_completed(futures) 遍历已完成的任务
    for future in concurrent.futures.as_completed(futures):
        try:
            # 对于每个已完成的任务，调用 future.result() 获取任务的返回值（即页面数据）
            page_data = future.result()
            if page_data is not None:
                if 'data' in page_data and 'components' in page_data['data']:
                    ges_data = page_data['data']['components']['gridView']['table']['dataSource']
                    # 提取数据源 dataSource 并扩展到 all_data 列表中
                    all_data.extend(ges_data)
                    print(f"Successfully fetched data for page {page_data['data']['components']['gridView']['table']['pagination']['page']}")
                else:
                    print(f"Unexpected data format for page {page_data['data']['components']['gridView']['table']['pagination']['page']}")
            else:
                print("Received None for page data")
        # 捕获并打印任何可能的异常
        except Exception as e:
            print(f"Failed to fetch page data: {e}")

# 获取当前时间
current_time = datetime.now().strftime('%Y%m%d')

# 准备批量插入的数据：这是一个列表推导式中的循环，item 是 data['data'] 列表中的每个字典（即每一条记录）
# values 是一个包含多个元组的列表，每个元组对应一条要插入的记录
values = [
    (
        current_time,  # 添加当前时间 2024-07-31 17:37:01.038610
        item['id'],
        RegularExpressionHtml.extract_logistics_codes(item['shipment_id']),
        item['shipment_number'],
        item['service'],
        item['to_warehouse_code'],
        item['to_address_name'],
        RegularExpressionHtml.extract_replace_str(item['to_address_country']),
        RegularExpressionHtml.extract_html_font(item['parcel_count']),
        item['declaration_value'],
        item['client_weight'],
        item['client_volume'],
        RegularExpressionHtml.extract_html_font(item['actual_weight']),
        RegularExpressionHtml.extract_html_font(item['actual_volume']),
        RegularExpressionHtml.extract_html_font(item['actual_volume_weight']),
        item['chargeable_weight'],
        item['sell_charge_amount'],
        item['is_insurance'],
        item['elec'],
        RegularExpressionHtml.extract_html_sapn(item['exportwith']),
        item['importwith'],
        item['taxwith'],
        item['vat_number'],
        item['deliverywith'],
        RegularExpressionHtml.extract_html_info(item['outer_carrier']),
        RegularExpressionHtml.extract_print_str(item['printed']),
        item['remark'],
        RegularExpressionHtml.extract_replace_str(item['last_tracking']),
        item['depot_id'],
        TimestampFormatter.format_timestamp(item['created']),
        TimestampFormatter.format_timestamp(item['picking_time']),
        TimestampFormatter.format_timestamp(item['delivered_time']),
    )
    # all_data是一个列表,从循环中得到的所有数据的列表，列表中的每个元素都是一个字典.这些字典表示需要插入数据库的每条记录
    for item in all_data
]

"""
    # 连接到 MySQL 数据库
    db_params = {
        'host': '192.168.0.201',
        'port': 4000,
        'user': 'root',
        'password': 'DoocnProTidb200.',
        'database': 'ods'
    }
    # 调用连接函数:** 解包操作符用于将字典形式的参数传递给函数 connect_to_database必须是类方法
    # db_connection = connect_to_database(**db_params)
"""

# 使用 DatabaseConnector 并且确保事务管理
try:
    # with 语句结合上下文管理器模式
    with DatabaseConnector(host="192.168.0.201", port=4000, user="root", password="DoocnProTidb200.",
                           database="ods") as db_connector:
        connection = db_connector.connection
        # 数据库操作： shift+tab整体往前一个tab距离
        # 如果连接成功，执行其他数据库操作:创建一个游标对象。游标对象用于执行SQL语句和获取结果。
        with connection.cursor() as cursor:
            # 执行任何数据库操作之前，显式地开始事务
            cursor.execute("BEGIN")
            # 数据库操作代码:三个双引号用于创建多行字符串
            create_table_query = """
                CREATE TABLE IF NOT EXISTS ods.`ods_scg_wld_ges_logistics_trace_table_i_d_bak`
                (
                    `dt`                   varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '采集日期',
                    `id`                   varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT 'id',
                    `shipment_id`          varchar(255) COLLATE utf8mb4_general_ci NOT NULL COMMENT 'FBA单号',
                    `shipment_number`      varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '快递单号',
                    `service`              varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '物流渠道',
                    `to_warehouse_code`    varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '地址库编码',
                    `to_address_name`      varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '收件人',
                    `to_address_country`   varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '国家',
                    `parcel_count`         varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '件数',
                    `declaration_value`    varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '价值',
                    `client_weight`        varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '客户重量',
                    `client_volume`        varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '客户体积',
                    `actual_weight`        varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '实重',
                    `actual_volume`        varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '体积',
                    `actual_volume_weight` varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '材重',
                    `chargeable_weight`    varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '收费重',
                    `sell_charge_amount`   varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '销售费用金额',
                    `is_insurance`         varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '购买保险',
                    `elec`                 varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '带电',
                    `exportwith`           varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '报关方式',
                    `importwith`           varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '清关方式',
                    `taxwith`              varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '交税方式',
                    `vat_number`           varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT 'VAT号',
                    `deliverywith`         varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '交货条款',
                    `outer_carrier`        varchar(512) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '承运',
                    `printed`              varchar(20) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '打标状态',
                    `remark`               varchar(512) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',
                    `last_tracking`        varchar(512) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '最后路由',
                    `depot_id`             varchar(50) COLLATE utf8mb4_general_ci  DEFAULT NULL COMMENT '仓库id',
                    `created`              varchar(50) COLLATE utf8mb4_general_ci  NOT NULL COMMENT '下单时间',
                    `picking_time`         varchar(50) COLLATE utf8mb4_general_ci  NOT NULL COMMENT '拣货时间',
                    `delivered_time`       varchar(50) COLLATE utf8mb4_general_ci  NOT NULL COMMENT '签收时间',
                    PRIMARY KEY (`shipment_id`, `created`) /*T![clustered_index] CLUSTERED */
                ) ENGINE = InnoDB
                  DEFAULT CHARSET = utf8mb4
                  COLLATE = utf8mb4_general_ci COMMENT ='ODS-GES物流数据-辜涛';
            """
            # 执行创建表语句
            cursor.execute(create_table_query)

            # DELETE_table_query = """
            # DELETE FROM ods.ods_scg_wld_ges_logistics_trace_table_i_d_bak;
            # """
            # cursor.execute(DELETE_table_query)

            # %s 作为占位符 不仅可以防止 SQL 注入，还能提高代码的清晰度和可维护性。
            insert_table_query = """
INSERT INTO ods.ods_scg_wld_ges_logistics_trace_table_i_d_bak (
                                                               `dt`,
                                                               `id`,
                                                               `shipment_id`,
                                                               `shipment_number`,
                                                               `service`,
                                                               `to_warehouse_code`,
                                                               `to_address_name`,
                                                               `to_address_country`,
                                                               `parcel_count`,
                                                               `declaration_value`,
                                                               `client_weight`,
                                                               `client_volume`,
                                                               `actual_weight`,
                                                               `actual_volume`,
                                                               `actual_volume_weight`,
                                                               `chargeable_weight`,
                                                               `sell_charge_amount`,
                                                               `is_insurance`,
                                                               `elec`,
                                                               `exportwith`,
                                                               `importwith`,
                                                               `taxwith`,
                                                               `vat_number`,
                                                               `deliverywith`,
                                                               `outer_carrier`,
                                                               `printed`,
                                                               `remark`,
                                                               `last_tracking`,
                                                               `depot_id`,
                                                               `created`,
                                                               `picking_time`,
                                                               `delivered_time`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
on duplicate key update dt                   = values(dt),
                        id                   = values(id),
                        shipment_id          = values(shipment_id),
                        shipment_number      = values(shipment_number),
                        service              = values(service),
                        to_warehouse_code    = values(to_warehouse_code),
                        to_address_name      = values(to_address_name),
                        to_address_country   = values(to_address_country),
                        parcel_count         = values(parcel_count),
                        declaration_value    = values(declaration_value),
                        client_weight        = values(client_weight),
                        client_volume        = values(client_volume),
                        actual_weight        = values(actual_weight),
                        actual_volume        = values(actual_volume),
                        actual_volume_weight = values(actual_volume_weight),
                        chargeable_weight    = values(chargeable_weight),
                        sell_charge_amount   = values(sell_charge_amount),
                        is_insurance         = values(is_insurance),
                        elec                 = values(elec),
                        exportwith           = values(exportwith),
                        importwith           = values(importwith),
                        taxwith              = values(taxwith),
                        vat_number           = values(vat_number),
                        deliverywith         = values(deliverywith),
                        outer_carrier        = values(outer_carrier),
                        printed              = values(printed),
                        remark               = values(remark),
                        last_tracking        = values(last_tracking),
                        depot_id             = values(depot_id),
                        created              = values(created),
                        picking_time         = values(picking_time),
                        delivered_time       = values(delivered_time);
            """
            cursor.executemany(insert_table_query, values)
            """
            # 查询当前数据库的版本
                        cursor.execute("SELECT VERSION()")
                        # 获取查询结果的第一行
                        result = cursor.fetchone()
                        print(f"Database version: {result}")
            """
except Exception as e:
    print(f"操作失败: {e}")
