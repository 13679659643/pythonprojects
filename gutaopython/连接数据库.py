import pymysql
from pymysql import MySQLError


def connect_to_database():
    try:
        # 连接到 MySQL 数据库
        db_connection = pymysql.connect(
            host='192.168.0.201',
            port=4000,
            user='root',
            password='DoocnProTidb200.',
            database='ods'
        )
        print("连接成功")
        return db_connection
    except MySQLError as e:
        print(f"连接失败: {e}")
        return None


# 调用函数连接到数据库
db_connection = connect_to_database()

# if db_connection:
#     # 如果连接成功，执行其他数据库操作
#     cursor = db_connection.cursor()
#
#     # 你的数据库操作代码
#     # ...
#     DELETE_table_query = """
#     DELETE TABLE ods.`ods_scg_wld_ges_logistics_trace_table_i_d_bak;
#     """
#     cursor.execute(DELETE_table_query)
#     # 关闭连接
#     cursor.close()
#     db_connection.close()
# else:
#     print("无法连接到数据库")


# try:
#     # 连接到 MySQL 数据库
#     db_connection = pymysql.connect(
#         host='192.168.0.201',
#         port=4000,
#         user='root',
#         password='DoocnProTidb200.',
#         database='ods'
#     )
#     print("连接成功")
# except MySQLError as e:
#     print(f"连接失败: {e}")


